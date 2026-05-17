#!/usr/bin/env python3
"""Run skill-creator behavior evals using codex or claude CLI.

Each eval runs twice: with_skill (SKILL.md injected) and without_skill (baseline).
All runs launch in parallel — total time ≈ slowest single run, not sum of all runs.
Usage: python evals/run_evals.py [eval-id]   # omit id to run all

為什麼使用 Python：Python 可在 Windows/macOS/Linux 以相同程式碼讀取 JSON、處理路徑並呼叫 CLI；
避免依賴 Bash、jq、Git Bash 或平台特定 shell 語法。

本地規則：Codex eval runner 必須固定使用 `--dangerously-bypass-approvals-and-sandbox`，
不要改成 sandbox / approval 模式。這個 runner 預期只在一次性工作區或外部隔離環境中執行。
"""

from __future__ import annotations

import json
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
OUTPUT_DIR = SCRIPT_DIR.parent / "eval-results"

DEFAULT_TIMEOUT = 300  # seconds per run


@dataclass
class RunResult:
    eval_id: str
    name: str
    config: str
    exit_code: int
    duration_seconds: float
    timed_out: bool
    output_file: Path
    error: str = ""


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
        fail(f"SKILL.md not found at {SKILL_MD}")

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


def run_ai(command_prefix: list[str], prompt: str, output_file: Path, timeout: int) -> tuple[int, bool]:
    """Run AI CLI via stdin to avoid Windows command line length limits. Returns (exit_code, timed_out)."""
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
    except subprocess.TimeoutExpired as error:
        process.kill()
        stdout, _ = process.communicate()
        partial_output = error.output or stdout or ""
        output_file.write_text(f"{partial_output}\n[timeout] killed after {timeout}s\n", encoding="utf-8")
        return -1, True


def run_eval_task(
    eval_id: str,
    name: str,
    prompt: str,
    config: str,
    skill_instructions: str,
    command_prefix: list[str],
    timeout: int,
) -> RunResult:
    """Run one eval config (with_skill or without_skill)."""
    output_file = OUTPUT_DIR / f"eval-{eval_id}" / config / "output.txt"

    if config == "with_skill":
        full_prompt = (
            f"{skill_instructions}\n\n"
            f"---\n\n"
            f"Apply the above skill instructions to this task:\n\n"
            f"{prompt}"
        )
    else:
        full_prompt = prompt

    start = time.time()
    exit_code, timed_out = run_ai(command_prefix, full_prompt, output_file, timeout)
    duration = time.time() - start

    timing_file = output_file.parent / "timing.json"
    timing_file.write_text(json.dumps({
        "start": start,
        "end": start + duration,
        "duration_seconds": round(duration, 2),
        "exit_code": exit_code,
        "timed_out": timed_out,
        "timeout_setting": timeout,
    }, indent=2))

    return RunResult(
        eval_id=eval_id,
        name=name,
        config=config,
        exit_code=exit_code,
        duration_seconds=duration,
        timed_out=timed_out,
        output_file=output_file,
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

    print(f"=== {skill_name} evals ({len(evals)} total) ===")

    tasks: list[tuple[str, str, str, str]] = []
    for index, eval_case in enumerate(evals):
        eval_id = str(eval_case.get("id", index))
        name = eval_case.get("name") or f"eval-{eval_id}"
        prompt = eval_case.get("prompt")

        if not prompt:
            fail(f"eval {eval_id} is missing prompt")

        for config in ("with_skill", "without_skill"):
            tasks.append((eval_id, name, prompt, config))

    if not tasks:
        print("No eval tasks to run.")
        return 0

    print(f"Launching {len(tasks)} runs in parallel...\n")

    results: list[RunResult] = []
    with ThreadPoolExecutor(max_workers=len(tasks)) as executor:
        futures = {
            executor.submit(
                run_eval_task,
                eval_id, name, prompt, config,
                skill_instructions, command_prefix, DEFAULT_TIMEOUT,
            ): (eval_id, name, config)
            for eval_id, name, prompt, config in tasks
        }

        for future in as_completed(futures):
            eval_id, name, config = futures[future]
            try:
                result = future.result()
                status = "TIMEOUT" if result.timed_out else ("OK" if result.exit_code == 0 else "FAIL")
                print(f"  [{status}] eval-{eval_id} {config} ({result.duration_seconds:.1f}s)")
                results.append(result)
            except Exception as exc:
                print(f"  [ERROR] eval-{eval_id} {config}: {exc}")
                results.append(RunResult(
                    eval_id=eval_id,
                    name=name,
                    config=config,
                    exit_code=-1,
                    duration_seconds=0.0,
                    timed_out=False,
                    output_file=Path(),
                    error=str(exc),
                ))

    # Summary table
    print()
    print("=== Summary ===")
    name_w = max((len(r.name) for r in results), default=8)
    print(f"  {'name':<{name_w}}  {'config':<16}  {'status':<7}  {'duration':>9}  log")
    print(f"  {'-'*name_w}  {'-'*16}  {'-'*7}  {'-'*9}  ---")

    failed = 0
    for result in sorted(results, key=lambda r: (r.eval_id, r.config)):
        if result.timed_out:
            status = "TIMEOUT"
            failed += 1
        elif result.exit_code != 0:
            status = "FAIL"
            failed += 1
        else:
            status = "OK"
        log = result.output_file if result.output_file != Path() else "—"
        print(f"  {result.name:<{name_w}}  {result.config:<16}  {status:<7}  {result.duration_seconds:>8.1f}s  {log}")

    print()
    if failed:
        print(f"{failed}/{len(results)} run(s) failed.", file=sys.stderr)
        return 1

    print(f"All {len(results)} runs completed.")
    print(f"Results: {OUTPUT_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
