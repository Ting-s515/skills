#!/usr/bin/env python3
"""BDD-style self-grading eval runner for build-static-docs-site skill.

【用途】
  讀取 evals/fixtures/eval-<id>/ 下的 base、staged、spec 目錄，
  以 Python difflib 計算 base→staged 的 unified diff，連同 spec 文檔、
  evals.json 的 expectations 清單，一起嵌入單一 prompt 傳給 AI。

【為什麼用 Python】
  Python 可在 Windows/macOS/Linux 以相同程式碼讀取 JSON、處理路徑並呼叫 CLI；
  避免依賴 Bash、jq、Git Bash 或平台特定 shell 語法。

本地規則：Codex eval runner 固定使用 --dangerously-bypass-approvals-and-sandbox。
這個 runner 預期只在一次性工作區或外部隔離環境中執行。

所有 eval 全部並行啟動；預設不得新增 --jobs 限流。

Usage:
    python evals/run_evals_bdd.py
    python evals/run_evals_bdd.py 1
"""
from __future__ import annotations

import difflib
import json
import os
import re
import shutil
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
EVALS_JSON = SCRIPT_DIR / "evals.json"
SKILL_MD = SCRIPT_DIR.parent / "SKILL.md"
FIXTURES_DIR = SCRIPT_DIR / "fixtures"
OUTPUT_DIR = SCRIPT_DIR.parent / "eval-results-bdd"
DEFAULT_TIMEOUT = 300


_GRADING_SUFFIX_TEMPLATE = """\

---

## 評分任務

請在完成上方任務後，接著評分以下每一條 Expectation。
每條獨立一行，格式固定為：

En: PASS — 從輸出摘錄的證據（一句話）
En: FAIL — 說明為何未達到

### Expectations 清單

__EXPECTATIONS_BLOCK__

---

## 輸出規範

1. 先完整輸出任務結果
2. 輸出一行分隔線：`---`
3. 輸出標題 `## Grading`
4. 逐行輸出 E1、E2 等評分結果
"""


@dataclass
class GradingResult:
    eval_id: str
    eval_name: str
    expectations: list[str]
    grades: list[tuple[str, str]]
    duration_seconds: float
    timed_out: bool
    exit_code: int

    @property
    def pass_count(self) -> int:
        return sum(1 for status, _ in self.grades if status == "PASS")

    @property
    def total(self) -> int:
        return len(self.expectations)


def fail(message: str) -> None:
    print(f"Error: {message}", file=sys.stderr)
    raise SystemExit(1)


def load_evals() -> dict:
    if not EVALS_JSON.is_file():
        fail(f"evals.json not found at {EVALS_JSON}")
    with EVALS_JSON.open("r", encoding="utf-8") as file:
        return json.load(file)


def validate_evals(data: dict) -> None:
    if data.get("skill_name") != "build-static-docs-site":
        fail("evals.json skill_name must be build-static-docs-site")

    evals = data.get("evals", [])
    ids = [str(item.get("id", "")) for item in evals]
    if not evals or len(ids) != len(set(ids)):
        fail("eval ids must be present and unique")

    for item, eval_id in zip(evals, ids):
        fixture_dir = FIXTURES_DIR / f"eval-{eval_id}"
        if not item.get("name") or not item.get("prompt"):
            fail(f"eval-{eval_id} requires name and prompt")
        if not item.get("expectations"):
            fail(f"eval-{eval_id} requires non-empty expectations")
        if not (fixture_dir / "staged").is_dir():
            fail(f"eval-{eval_id} requires staged directory")
        if not (fixture_dir / "spec").is_dir():
            fail(f"eval-{eval_id} requires spec directory")


def read_skill_instructions() -> str:
    if not SKILL_MD.is_file():
        fail(f"SKILL.md not found at {SKILL_MD}")
    return SKILL_MD.read_text(encoding="utf-8")


def detect_ai_tool() -> list[str]:
    codex = shutil.which("codex")
    if codex:
        print("[tool] codex")
        return [codex, "exec", "--dangerously-bypass-approvals-and-sandbox"]

    claude = shutil.which("claude")
    if claude:
        print("[tool] claude")
        return [claude, "-p"]

    fail("neither codex nor claude CLI found")


def collect_files(directory: Path) -> set[Path]:
    if not directory.exists():
        return set()
    return {
        path.relative_to(directory)
        for path in directory.rglob("*")
        if path.is_file() and path.name != ".gitkeep"
    }


def compute_unified_diff(base_dir: Path, staged_dir: Path) -> str:
    base_files = collect_files(base_dir)
    staged_files = collect_files(staged_dir)
    chunks: list[str] = []

    for relative_path in sorted(base_files | staged_files):
        base_path = base_dir / relative_path
        staged_path = staged_dir / relative_path
        base_lines = (
            base_path.read_text(encoding="utf-8", errors="replace").splitlines(keepends=True)
            if base_path.exists()
            else []
        )
        staged_lines = (
            staged_path.read_text(encoding="utf-8", errors="replace").splitlines(keepends=True)
            if staged_path.exists()
            else []
        )
        chunks.extend(
            difflib.unified_diff(
                base_lines,
                staged_lines,
                fromfile=f"a/{relative_path.as_posix()}",
                tofile=f"b/{relative_path.as_posix()}",
            )
        )
    return "".join(chunks)


def read_spec_files(spec_dir: Path) -> dict[str, str]:
    return {
        path.relative_to(spec_dir).as_posix(): path.read_text(
            encoding="utf-8",
            errors="replace",
        )
        for path in sorted(spec_dir.rglob("*"))
        if path.is_file()
    }


def build_prompt(
    skill_instructions: str,
    eval_prompt: str,
    unified_diff: str,
    spec_files: dict[str, str],
    expectations: list[str],
) -> str:
    spec_section = "\n\n".join(
        f"### 規格或輸入檔案：{name}\n\n{content}"
        for name, content in spec_files.items()
    )
    expectations_block = "\n".join(
        f"E{index}. {expectation}"
        for index, expectation in enumerate(expectations, start=1)
    )
    grading_suffix = _GRADING_SUFFIX_TEMPLATE.replace(
        "__EXPECTATIONS_BLOCK__",
        expectations_block,
    )
    return (
        f"{skill_instructions}\n\n"
        "---\n\n"
        "Apply the above skill instructions to this task.\n\n"
        "## 重要說明\n\n"
        "以下已提供所有所需資訊，不需要執行 shell 指令、讀取檔案或修改工作區。"
        "請根據輸入說明你會產生的結果與驗證證據。\n\n"
        f"{spec_section}\n\n"
        "## Git diff（base → staged）\n\n"
        f"```diff\n{unified_diff}```\n\n"
        "## 使用者的請求\n\n"
        f"{eval_prompt}"
        f"{grading_suffix}"
    )


def run_ai(
    command_prefix: list[str],
    prompt: str,
    output_file: Path,
    timeout: int,
) -> tuple[int, bool]:
    output_file.parent.mkdir(parents=True, exist_ok=True)
    process = subprocess.Popen(
        command_prefix,
        cwd=SKILL_MD.parent,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    try:
        stdout, _ = process.communicate(input=prompt, timeout=timeout)
        output_file.write_text(stdout, encoding="utf-8")
        return process.returncode, False
    except subprocess.TimeoutExpired as error:
        process.kill()
        stdout, _ = process.communicate()
        partial = error.output or stdout or ""
        output_file.write_text(
            f"{partial}\n[timeout] killed after {timeout}s\n",
            encoding="utf-8",
        )
        return -1, True


def parse_grading(raw_output: str, expected_count: int) -> list[tuple[str, str]]:
    pattern = re.compile(r"E(\d+):\s*(PASS|FAIL)\s*[—\-–]\s*(.+)", re.IGNORECASE)
    found: dict[int, tuple[str, str]] = {}
    for line in raw_output.splitlines():
        match = pattern.search(line)
        if match:
            found[int(match.group(1))] = (
                match.group(2).upper(),
                match.group(3).strip(),
            )
    return [
        found.get(index, ("FAIL", "未找到對應評分行"))
        for index in range(1, expected_count + 1)
    ]


def run_bdd_eval(
    item: dict,
    skill_instructions: str,
    command_prefix: list[str],
) -> GradingResult:
    eval_id = str(item["id"])
    fixture_dir = FIXTURES_DIR / f"eval-{eval_id}"
    expectations = item["expectations"]
    prompt = build_prompt(
        skill_instructions,
        item["prompt"],
        compute_unified_diff(fixture_dir / "base", fixture_dir / "staged"),
        read_spec_files(fixture_dir / "spec"),
        expectations,
    )
    output_file = OUTPUT_DIR / f"eval-{eval_id}" / "output.txt"
    started_at = time.time()
    exit_code, timed_out = run_ai(
        command_prefix,
        prompt,
        output_file,
        DEFAULT_TIMEOUT,
    )
    duration = time.time() - started_at
    raw_output = output_file.read_text(encoding="utf-8", errors="replace")
    return GradingResult(
        eval_id=eval_id,
        eval_name=item["name"],
        expectations=expectations,
        grades=parse_grading(raw_output, len(expectations)),
        duration_seconds=duration,
        timed_out=timed_out,
        exit_code=exit_code,
    )


def main() -> int:
    data = load_evals()
    validate_evals(data)
    skill_instructions = read_skill_instructions()
    command_prefix = detect_ai_tool()
    evals = data["evals"]
    target_id = sys.argv[1] if len(sys.argv) > 1 else None
    if target_id:
        evals = [item for item in evals if str(item["id"]) == target_id]
    if not evals:
        fail("no matching eval tasks")

    expected_total = sum(len(item["expectations"]) for item in evals)
    results: list[GradingResult] = []
    execution_failed = False
    print(f"=== {data['skill_name']} BDD evals ({len(evals)} total) ===")
    print(f"Launching {len(evals)} runs in parallel...\n")
    with ThreadPoolExecutor(max_workers=len(evals)) as executor:
        futures = {
            executor.submit(
                run_bdd_eval,
                item,
                skill_instructions,
                command_prefix,
            ): str(item["id"])
            for item in evals
        }
        for future in as_completed(futures):
            eval_id = futures[future]
            try:
                result = future.result()
                status = "TIMEOUT" if result.timed_out else (
                    "OK" if result.exit_code == 0 else "FAIL"
                )
                print(
                    f"  [{status}] eval-{result.eval_id} {result.eval_name} "
                    f"({result.duration_seconds:.1f}s) — "
                    f"{result.pass_count}/{result.total} passed"
                )
                results.append(result)
            except Exception as error:
                execution_failed = True
                print(f"  [ERROR] eval-{eval_id}: {error}")

    total_pass = 0
    print("\n=== Detailed Results ===")
    for result in sorted(results, key=lambda item: item.eval_id):
        print(
            f"\n[eval-{result.eval_id}] {result.eval_name} "
            f"({result.pass_count}/{result.total})"
        )
        for index, (expectation, grade) in enumerate(
            zip(result.expectations, result.grades),
            start=1,
        ):
            status, evidence = grade
            print(f"  E{index}: {status}")
            print(f"       Exp: {expectation[:80]}")
            print(f"       Evi: {evidence[:80]}")
        total_pass += result.pass_count

    print(f"\n=== Summary: {total_pass}/{expected_total} expectations passed ===")
    print(f"Results: {OUTPUT_DIR}")
    all_runs_succeeded = (
        not execution_failed
        and len(results) == len(evals)
        and all(not result.timed_out for result in results)
        and all(result.exit_code == 0 for result in results)
    )
    return 0 if all_runs_succeeded and total_pass == expected_total else 1


if __name__ == "__main__":
    if sys.platform == "win32" and not sys.flags.utf8_mode:
        env = os.environ.copy()
        env["PYTHONUTF8"] = "1"
        completed = subprocess.run(
            [sys.executable, "-X", "utf8", __file__, *sys.argv[1:]],
            env=env,
            check=False,
        )
        raise SystemExit(completed.returncode)
    raise SystemExit(main())
