#!/usr/bin/env python3
"""BDD-style self-grading eval runner for code-reviewer skill.

為什麼使用 Python：Python 可在 Windows/macOS/Linux 以相同程式碼讀取 JSON、處理路徑並呼叫 CLI；
避免依賴 Bash、jq、Git Bash 或平台特定 shell 語法。

本地規則：Codex eval runner 必須固定使用 `--dangerously-bypass-approvals-and-sandbox`，
不要改成 sandbox / approval 模式。這個 runner 預期只在一次性工作區或外部隔離環境中執行。

與 run_evals.py 的差異
-----------------------
run_evals.py   — 建立真實 git repo，讓 AI 自行執行 shell 指令取得 diff（需要 filesystem 存取）
run_evals_bdd.py — 在 Python 端計算 diff 並 embed 進 prompt，AI 只需推理不需執行任何指令
                   因此 Codex 與 Claude 均可在完全無 filesystem 存取的情境下執行本測試。

Usage:
    python evals/run_evals_bdd.py           # 執行全部 eval
    python evals/run_evals_bdd.py 1         # 只執行 eval id=1
    python evals/run_evals_bdd.py --help
"""
from __future__ import annotations

import difflib
import json
import re
import shutil
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    # Windows cp950 consoles cannot encode some grading prompt/output characters.
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


SCRIPT_DIR = Path(__file__).resolve().parent
EVALS_JSON = SCRIPT_DIR / "evals.json"
SKILL_MD = SCRIPT_DIR.parent / "SKILL.MD"
FIXTURES_DIR = SCRIPT_DIR / "fixtures"
OUTPUT_DIR = SCRIPT_DIR.parent / "eval-results-bdd"

DEFAULT_TIMEOUT = 300


_GRADING_SUFFIX_TEMPLATE = """\

---

## 評分任務

請在完成上方的 Code Review 後，接著評分以下每一條 Expectation。
每條獨立一行，格式固定為：

En: PASS — 從你的 review 摘錄的證據（一句話）
En: FAIL — 說明為何未達到

（n 為 Expectation 編號，例如 E1: PASS — ...）

### Expectations 清單

__EXPECTATIONS_BLOCK__

---

## 輸出規範

1. 先完整輸出 Code Review（格式遵照 skill 指示）
2. 輸出一行分隔線：`---`
3. 輸出標題 `## Grading`
4. 逐行輸出評分結果（E1、E2 … 順序對應上方清單）
"""


@dataclass
class GradingResult:
    eval_id: str
    eval_name: str
    expectations: list[str]
    grades: list[tuple[str, str]]   # (PASS|FAIL, evidence)
    raw_output: str
    duration_seconds: float
    timed_out: bool
    exit_code: int
    error: str = ""

    @property
    def pass_count(self) -> int:
        return sum(1 for status, _ in self.grades if status.upper() == "PASS")

    @property
    def total(self) -> int:
        return len(self.expectations)


def fail(message: str) -> None:
    print(f"Error: {message}", file=sys.stderr)
    raise SystemExit(1)


def load_evals() -> dict:
    if not EVALS_JSON.is_file():
        fail(f"evals.json not found at {EVALS_JSON}")
    with EVALS_JSON.open("r", encoding="utf-8") as f:
        return json.load(f)


def read_skill_instructions() -> str:
    if not SKILL_MD.is_file():
        fail(f"SKILL.MD not found at {SKILL_MD}")
    return SKILL_MD.read_text(encoding="utf-8")


def detect_ai_tool() -> tuple[str, list[str]]:
    codex = shutil.which("codex")
    if codex:
        print("[tool] codex")
        return "codex", [codex, "exec", "--dangerously-bypass-approvals-and-sandbox"]
    claude = shutil.which("claude")
    if claude:
        print("[tool] claude")
        return "claude", [claude, "-p"]
    fail("neither codex nor claude CLI found")


def compute_unified_diff(base_dir: Path, staged_dir: Path) -> str:
    """計算 base → staged 的 unified diff，純 Python 實作不需 git。"""
    base_files: set[Path] = set()
    staged_files: set[Path] = set()

    if base_dir.exists():
        base_files = {f.relative_to(base_dir) for f in base_dir.rglob("*") if f.is_file()}
    if staged_dir.exists():
        staged_files = {f.relative_to(staged_dir) for f in staged_dir.rglob("*") if f.is_file()}

    all_rel = sorted(base_files | staged_files)
    chunks: list[str] = []

    for rel in all_rel:
        base_path = base_dir / rel
        staged_path = staged_dir / rel

        base_lines = base_path.read_text(encoding="utf-8", errors="replace").splitlines(keepends=True) if base_path.exists() else []
        staged_lines = staged_path.read_text(encoding="utf-8", errors="replace").splitlines(keepends=True) if staged_path.exists() else []

        diff_lines = list(difflib.unified_diff(
            base_lines,
            staged_lines,
            fromfile=f"a/{rel.as_posix()}",
            tofile=f"b/{rel.as_posix()}",
        ))
        if diff_lines:
            chunks.extend(diff_lines)

    return "".join(chunks)


def read_spec_files(spec_dir: Path) -> dict[str, str]:
    """回傳 {檔名: 內容} 的 dict。"""
    if not spec_dir.exists():
        return {}
    return {
        f.name: f.read_text(encoding="utf-8", errors="replace")
        for f in spec_dir.rglob("*") if f.is_file()
    }


def build_prompt(
    skill_instructions: str,
    eval_prompt: str,
    unified_diff: str,
    spec_files: dict[str, str],
    expectations: list[str],
) -> str:
    spec_section = ""
    if spec_files:
        parts = []
        for name, content in spec_files.items():
            parts.append(f"### 規格文檔：{name}\n\n{content}")
        spec_section = "\n\n".join(parts) + "\n\n"

    expectations_block = "\n".join(
        f"E{i + 1}. {exp}" for i, exp in enumerate(expectations)
    )

    grading_suffix = _GRADING_SUFFIX_TEMPLATE.replace("__EXPECTATIONS_BLOCK__", expectations_block)

    return (
        f"{skill_instructions}\n\n"
        f"---\n\n"
        f"Apply the above skill instructions to this task.\n\n"
        f"## 重要說明\n\n"
        f"以下已提供所有審查所需資訊（diff、規格文檔），不需要執行 shell 指令或讀取檔案來取得審查內容；"
        f"但若 skill 指示要求輸出存檔，仍須依該指示建立審查 Markdown 檔案。\n\n"
        f"{spec_section}"
        f"## Git diff（base → staged）\n\n"
        f"```diff\n{unified_diff}```\n\n"
        f"## 使用者的請求\n\n"
        f"{eval_prompt}"
        f"{grading_suffix}"
    )


def run_ai(command_prefix: list[str], prompt: str, output_file: Path, timeout: int) -> tuple[int, bool]:
    output_file.parent.mkdir(parents=True, exist_ok=True)

    process = subprocess.Popen(
        command_prefix,
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
    except subprocess.TimeoutExpired as exc:
        process.kill()
        stdout, _ = process.communicate()
        partial = exc.output or stdout or ""
        output_file.write_text(f"{partial}\n[timeout] killed after {timeout}s\n", encoding="utf-8")
        return -1, True


def parse_grading(raw: str, expected_count: int) -> list[tuple[str, str]]:
    """從 AI 輸出解析 E1: PASS/FAIL — evidence 行。"""
    pattern = re.compile(r"E(\d+):\s*(PASS|FAIL)\s*[—\-–]\s*(.+)", re.IGNORECASE)
    found: dict[int, tuple[str, str]] = {}

    for line in raw.splitlines():
        m = pattern.search(line)
        if m:
            idx = int(m.group(1))
            status = m.group(2).upper()
            evidence = m.group(3).strip()
            found[idx] = (status, evidence)

    # 依序回傳，找不到的視為 FAIL（未評分）
    return [
        found.get(i + 1, ("FAIL", "（未找到對應評分行）"))
        for i in range(expected_count)
    ]


def run_bdd_eval(
    eval_id: str,
    eval_name: str,
    prompt: str,
    fixture_dir: Path,
    expectations: list[str],
    skill_instructions: str,
    command_prefix: list[str],
    timeout: int,
) -> GradingResult:
    base_dir = fixture_dir / "base"
    staged_dir = fixture_dir / "staged"
    spec_dir = fixture_dir / "spec"

    unified_diff = compute_unified_diff(base_dir, staged_dir)
    spec_files = read_spec_files(spec_dir)

    full_prompt = build_prompt(
        skill_instructions=skill_instructions,
        eval_prompt=prompt,
        unified_diff=unified_diff,
        spec_files=spec_files,
        expectations=expectations,
    )

    output_file = OUTPUT_DIR / f"eval-{eval_id}" / "output.txt"
    start = time.time()
    exit_code, timed_out = run_ai(command_prefix, full_prompt, output_file, timeout)
    duration = time.time() - start

    raw = output_file.read_text(encoding="utf-8", errors="replace") if output_file.exists() else ""
    grades = parse_grading(raw, len(expectations))

    return GradingResult(
        eval_id=eval_id,
        eval_name=eval_name,
        expectations=expectations,
        grades=grades,
        raw_output=raw,
        duration_seconds=duration,
        timed_out=timed_out,
        exit_code=exit_code,
    )


def main() -> int:
    data = load_evals()
    skill_instructions = read_skill_instructions()
    _tool_name, command_prefix = detect_ai_tool()

    skill_name = data.get("skill_name", "<skill-name>")
    evals = data.get("evals", [])
    target_id = sys.argv[1] if len(sys.argv) > 1 else None

    if target_id:
        evals = [e for e in evals if str(e.get("id", "")) == target_id]

    if not evals:
        print("No eval tasks to run.")
        return 0

    print(f"=== {skill_name} BDD evals ({len(evals)} total) ===")
    print(f"Launching {len(evals)} runs in parallel...\n")

    results: list[GradingResult] = []
    with ThreadPoolExecutor(max_workers=len(evals)) as executor:
        futures = {
            executor.submit(
                run_bdd_eval,
                str(e.get("id", i)),
                e.get("name") or f"eval-{e.get('id', i)}",
                e.get("prompt", ""),
                FIXTURES_DIR / f"eval-{e.get('id', i)}",
                e.get("expectations") or e.get("assertions", []),
                skill_instructions,
                command_prefix,
                DEFAULT_TIMEOUT,
            ): str(e.get("id", i))
            for i, e in enumerate(evals)
        }

        for future in as_completed(futures):
            eval_id = futures[future]
            try:
                result = future.result()
                status = "TIMEOUT" if result.timed_out else ("OK" if result.exit_code == 0 else "FAIL")
                print(f"  [{status}] eval-{result.eval_id} {result.eval_name} ({result.duration_seconds:.1f}s) "
                      f"— {result.pass_count}/{result.total} passed")
                results.append(result)
            except Exception as exc:
                print(f"  [ERROR] eval-{eval_id}: {exc}")

    # 詳細結果
    print()
    print("=== Detailed Results ===")
    total_pass = 0
    total_expectations = 0

    for result in sorted(results, key=lambda r: r.eval_id):
        print(f"\n[eval-{result.eval_id}] {result.eval_name}  ({result.pass_count}/{result.total})")
        for i, (exp, (status, evidence)) in enumerate(zip(result.expectations, result.grades)):
            icon = "PASS" if status == "PASS" else "FAIL"
            print(f"  {icon} E{i+1}: {status}")
            print(f"       Exp: {exp[:80]}")
            print(f"       Evi: {evidence[:80]}")
        total_pass += result.pass_count
        total_expectations += result.total

    print()
    print(f"=== Summary: {total_pass}/{total_expectations} expectations passed ===")
    print(f"Results: {OUTPUT_DIR}")

    return 0 if total_pass == total_expectations else 1


if __name__ == "__main__":
    raise SystemExit(main())
