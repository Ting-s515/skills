#!/usr/bin/env python3
"""Workspace-style BDD eval runner for apply.

Runs each eval in an isolated workspace, invokes Codex with the apply skill
instructions, then asks the model to self-grade the expectations from evals.json.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
EVALS_JSON = SCRIPT_DIR / "evals.json"
SKILL_MD = SKILL_DIR / "SKILL.md"
FILES_DIR = SCRIPT_DIR / "files"
OUTPUT_DIR = SKILL_DIR / "eval-results-bdd"
DEFAULT_TIMEOUT = 300


@dataclass
class EvalResult:
    eval_id: str
    eval_name: str
    exit_code: int
    timed_out: bool
    duration_seconds: float
    grades: list[tuple[str, str]]
    output_dir: Path

    @property
    def pass_count(self) -> int:
        return sum(1 for status, _ in self.grades if status == "PASS")

    @property
    def total(self) -> int:
        return len(self.grades)


def fail(message: str) -> None:
    print(f"Error: {message}", file=sys.stderr)
    raise SystemExit(1)


def load_json(path: Path) -> dict:
    if not path.is_file():
        fail(f"file not found: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def detect_codex_command(workspace: Path, last_message: Path) -> list[str]:
    codex = shutil.which("codex")
    if not codex:
        fail("codex CLI not found; eval runner requires codex exec")
    return [
        codex,
        "exec",
        "--dangerously-bypass-approvals-and-sandbox",
        "--skip-git-repo-check",
        "--cd",
        str(workspace),
        "--output-last-message",
        str(last_message),
        "-",
    ]


def copy_workspace() -> Path:
    temp_root = Path(tempfile.mkdtemp(prefix="apply-eval-"))
    workspace = temp_root / "workspace"
    (workspace / "apply" / "evals").mkdir(parents=True)
    shutil.copytree(FILES_DIR, workspace / "apply" / "evals" / "files")
    return workspace


def build_prompt(skill: str, eval_case: dict) -> str:
    assertions = eval_case.get("assertions", [])
    expectations = "\n".join(
        f"E{i + 1}. {item['name']}: {item['check']}"
        for i, item in enumerate(assertions)
    )
    return f"""{skill}

---

Apply the above apply skill instructions to this isolated eval workspace.

使用者請求：
{eval_case.get("prompt", "")}

執行規則：
- 直接執行 apply，不要等待使用者確認。
- 可以讀寫目前隔離工作區內的檔案。
- 不要執行 git commit。
- 若需要呼叫 bdd-unit-test，請依 apply 技能流程執行；本 eval 重點是流程順序與 task 標記。

完成後請輸出任務結果，接著輸出：

---
## Grading
請逐條評分以下 expectations，格式固定為：
E1: PASS - 證據
E1: FAIL - 原因

{expectations}
"""


def run_codex(command: list[str], prompt: str, output_file: Path, timeout: int) -> tuple[int, bool]:
    output_file.parent.mkdir(parents=True, exist_ok=True)
    process = subprocess.Popen(
        command,
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


def parse_grades(text: str, count: int) -> list[tuple[str, str]]:
    pattern = re.compile(r"E(\d+):\s*(PASS|FAIL)\s*[-—–]\s*(.+)", re.IGNORECASE)
    found: dict[int, tuple[str, str]] = {}
    for line in text.splitlines():
        match = pattern.search(line)
        if match:
            found[int(match.group(1))] = (match.group(2).upper(), match.group(3).strip())
    return [found.get(i + 1, ("FAIL", "missing grading line")) for i in range(count)]


def run_eval(eval_case: dict, skill: str, timeout: int) -> EvalResult:
    eval_id = str(eval_case["id"])
    eval_name = eval_case["name"]
    case_dir = OUTPUT_DIR / f"eval-{eval_id}-{eval_name}"
    if case_dir.exists():
        shutil.rmtree(case_dir)
    case_dir.mkdir(parents=True)

    workspace = copy_workspace()
    try:
        last_message = case_dir / "last-message.md"
        output_file = case_dir / "output.txt"
        start = time.time()
        exit_code, timed_out = run_codex(
            detect_codex_command(workspace, last_message),
            build_prompt(skill, eval_case),
            output_file,
            timeout,
        )
        duration = time.time() - start
        combined = output_file.read_text(encoding="utf-8", errors="replace")
        if last_message.is_file():
            combined += "\n" + last_message.read_text(encoding="utf-8", errors="replace")
        grades = parse_grades(combined, len(eval_case.get("assertions", [])))
        (case_dir / "grading.txt").write_text(
            "\n".join(f"E{i + 1}: {status} - {evidence}" for i, (status, evidence) in enumerate(grades)) + "\n",
            encoding="utf-8",
        )
        return EvalResult(eval_id, eval_name, exit_code, timed_out, duration, grades, case_dir)
    finally:
        shutil.rmtree(workspace.parent, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run apply BDD evals")
    parser.add_argument("eval_id", nargs="?", help="Optional eval id to run")
    parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT)
    parser.add_argument("--jobs", type=int, default=0)
    args = parser.parse_args()

    data = load_json(EVALS_JSON)
    skill = SKILL_MD.read_text(encoding="utf-8")
    evals = data["evals"]
    if args.eval_id:
        evals = [case for case in evals if str(case["id"]) == args.eval_id]
    jobs = args.jobs or len(evals)
    jobs = max(1, min(jobs, len(evals)))

    print(f"=== apply BDD evals ({len(evals)} total) ===")
    results: list[EvalResult] = []
    with ThreadPoolExecutor(max_workers=jobs) as executor:
        futures = {executor.submit(run_eval, case, skill, args.timeout): case for case in evals}
        for future in as_completed(futures):
            result = future.result()
            results.append(result)
            status = "TIMEOUT" if result.timed_out else ("OK" if result.exit_code == 0 else "FAIL")
            print(f"[{status}] eval-{result.eval_id} {result.eval_name}: {result.pass_count}/{result.total}")

    total_pass = sum(result.pass_count for result in results)
    total = sum(result.total for result in results)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUTPUT_DIR / "summary.json").write_text(
        json.dumps({"passed": total_pass, "total": total}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"=== Summary: {total_pass}/{total} expectations passed ===")
    return 0 if total_pass == total and len(results) == len(evals) else 1


if __name__ == "__main__":
    if sys.platform == "win32" and not sys.flags.utf8_mode:
        import os

        env = os.environ.copy()
        env["PYTHONUTF8"] = "1"
        result = subprocess.run([sys.executable, "-X", "utf8", __file__] + sys.argv[1:], env=env)
        sys.exit(result.returncode)
    raise SystemExit(main())
