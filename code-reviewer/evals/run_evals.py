#!/usr/bin/env python3
"""Run code-reviewer behavior evals using codex or claude CLI.

Each eval runs twice: with_skill (SKILL.MD injected) and without_skill (baseline).
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
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
EVALS_JSON = SCRIPT_DIR / "evals.json"
SKILL_MD = SCRIPT_DIR.parent / "SKILL.MD"
FIXTURES_DIR = SCRIPT_DIR / "fixtures"
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


def run_git(args: list[str], cwd: Path) -> None:
    subprocess.run(
        ["git"] + args,
        cwd=cwd,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )


def setup_git_repo(eval_fixture_dir: Path) -> Path:
    """建立一個獨立的 temp git repo，模擬有 staged diff 的開發環境。

    目錄結構（eval_fixture_dir）：
      base/    — 初始版本，作為 initial commit
      staged/  — 修改後版本，git add 但尚未 commit（即 code review 的對象）
      spec/    — 規格文檔，直接複製至 docs/specs/（不納入 git 追蹤）
    """
    temp_dir = Path(tempfile.mkdtemp(prefix="code-reviewer-eval-"))

    run_git(["init"], cwd=temp_dir)
    run_git(["config", "user.email", "eval@test.com"], cwd=temp_dir)
    run_git(["config", "user.name", "Eval Runner"], cwd=temp_dir)

    base_dir = eval_fixture_dir / "base"
    if base_dir.exists():
        for src_file in base_dir.rglob("*"):
            if src_file.is_file():
                rel_path = src_file.relative_to(base_dir)
                dest_file = temp_dir / rel_path
                dest_file.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src_file, dest_file)
        run_git(["add", "-A"], cwd=temp_dir)
        run_git(["commit", "-m", "Initial commit"], cwd=temp_dir)

    staged_dir = eval_fixture_dir / "staged"
    if staged_dir.exists():
        for src_file in staged_dir.rglob("*"):
            if src_file.is_file():
                rel_path = src_file.relative_to(staged_dir)
                dest_file = temp_dir / rel_path
                dest_file.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src_file, dest_file)
        run_git(["add", "-A"], cwd=temp_dir)

    spec_dir = eval_fixture_dir / "spec"
    if spec_dir.exists():
        for src_file in spec_dir.rglob("*"):
            if src_file.is_file():
                dest_file = temp_dir / "docs" / "specs" / src_file.name
                dest_file.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src_file, dest_file)

    return temp_dir


def run_ai(command_prefix: list[str], prompt: str, output_file: Path, cwd: Path, timeout: int) -> tuple[int, bool]:
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
        cwd=str(cwd),
    )

    try:
        stdout, _ = process.communicate(input=prompt, timeout=timeout)
        output_file.write_text(stdout, encoding="utf-8")
        return process.returncode, False
    except subprocess.TimeoutExpired:
        process.kill()
        process.communicate()
        return -1, True


def run_eval_task(
    eval_id: str,
    name: str,
    prompt: str,
    config: str,
    skill_instructions: str,
    command_prefix: list[str],
    fixture_dir: Path,
    timeout: int,
) -> RunResult:
    """Run one eval config in an isolated temp git repo."""
    output_file = OUTPUT_DIR / f"eval-{eval_id}" / config / "output.txt"
    temp_dir = setup_git_repo(fixture_dir)

    try:
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
        exit_code, timed_out = run_ai(command_prefix, full_prompt, output_file, temp_dir, timeout)
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
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


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

    # Validate all fixtures exist before launching
    tasks: list[tuple[str, str, str, str, Path]] = []
    for index, eval_case in enumerate(evals):
        eval_id = str(eval_case.get("id", index))
        name = eval_case.get("name") or f"eval-{eval_id}"
        prompt = eval_case.get("prompt")

        if not prompt:
            fail(f"eval {eval_id} is missing prompt")

        fixture_dir = FIXTURES_DIR / f"eval-{eval_id}"
        if not fixture_dir.exists():
            fail(f"Fixture directory not found: {fixture_dir}")

        for config in ("with_skill", "without_skill"):
            tasks.append((eval_id, name, prompt, config, fixture_dir))

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
                skill_instructions, command_prefix, fixture_dir, DEFAULT_TIMEOUT,
            ): (eval_id, config)
            for eval_id, name, prompt, config, fixture_dir in tasks
        }

        for future in as_completed(futures):
            eval_id, config = futures[future]
            try:
                result = future.result()
                status = "TIMEOUT" if result.timed_out else ("OK" if result.exit_code == 0 else "FAIL")
                print(f"  [{status}] eval-{eval_id} {config} ({result.duration_seconds:.1f}s)")
                results.append(result)
            except Exception as exc:
                print(f"  [ERROR] eval-{eval_id} {config}: {exc}")
                task_name = next((t[1] for t in tasks if t[0] == eval_id), f"eval-{eval_id}")
                results.append(RunResult(
                    eval_id=eval_id,
                    name=task_name,
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
