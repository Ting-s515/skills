#!/usr/bin/env python3
"""Run code-reviewer behavior evals using codex or claude CLI.

為什麼使用 Python：Python 可在 Windows/macOS/Linux 以相同程式碼讀取 JSON、處理路徑並呼叫 CLI；避免依賴 Bash、`jq`、Git Bash 或平台特定 shell 語法。

本地規則：Codex eval runner 必須固定使用 `--dangerously-bypass-approvals-and-sandbox`，不要改成 sandbox / approval 模式。這個 runner 預期只在一次性工作區或外部隔離環境中執行。

Usage:
  python evals/run_evals.py [options] [eval-id]

Options:
  --jobs N          Parallel workers (default: 2)
  --timeout N       Per-run timeout in seconds (default: 900)
  --with-skill-only Only run with_skill configuration
  --output-dir DIR  Directory that stores eval run artifacts
  --dry-run         Create metadata and fixture workspaces without invoking the AI CLI
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import signal
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
EVALS_JSON = SCRIPT_DIR / "evals.json"
FILES_DIR = SCRIPT_DIR / "files"
EVAL_RUNS_DIR = SCRIPT_DIR / "eval-runs"

DEFAULT_JOBS = 2
DEFAULT_TIMEOUT = 15 * 60
CONFIGURATIONS = ["with_skill", "without_skill"]


def fail(message: str) -> None:
    print(f"Error: {message}", file=sys.stderr)
    raise SystemExit(1)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run code-reviewer behavior evals.")
    parser.add_argument("eval_id", nargs="?", help="Optional eval id to run")
    parser.add_argument("--jobs", type=int, default=DEFAULT_JOBS, help="Max parallel runs")
    parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT, help="Per-run timeout in seconds")
    parser.add_argument("--output-dir", type=Path, default=EVAL_RUNS_DIR, help="Eval run artifacts directory")
    parser.add_argument("--with-skill-only", action="store_true", help="Only run with_skill configuration")
    parser.add_argument("--dry-run", action="store_true", help="Create metadata without invoking the AI CLI")
    return parser.parse_args()


def detect_runner() -> tuple[str, list[str]]:
    codex = shutil.which("codex")
    if codex:
        print("[tool] codex")
        return "codex", [codex, "exec", "--dangerously-bypass-approvals-and-sandbox"]

    claude = shutil.which("claude")
    if claude:
        print("[tool] claude")
        return "claude", [claude, "-p"]

    fail("neither codex nor claude CLI found")
    return "", []


def find_skill_md() -> Path:
    for name in ("SKILL.md", "SKILL.MD"):
        candidate = SKILL_DIR / name
        if candidate.is_file():
            return candidate
    fail(f"SKILL.md not found under {SKILL_DIR}")
    return SKILL_DIR / "SKILL.md"


def read_skill_instructions() -> str:
    return find_skill_md().read_text(encoding="utf-8")


def safe_name(value: str) -> str:
    allowed = []
    for char in value.lower():
        if char.isalnum() or char in ("-", "_"):
            allowed.append(char)
        elif char.isspace():
            allowed.append("-")
    return "".join(allowed).strip("-_") or "eval"


def next_iteration_dir(output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    existing = [
        int(d.name.removeprefix("iteration-"))
        for d in output_dir.iterdir()
        if d.is_dir() and d.name.startswith("iteration-") and d.name.removeprefix("iteration-").isdigit()
    ]
    return output_dir / f"iteration-{max(existing, default=0) + 1}"


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def copy_overlay(source: Path, destination: Path) -> None:
    if not source.exists():
        return
    shutil.copytree(source, destination, dirs_exist_ok=True)


def run_git(workspace: Path, args: list[str]) -> None:
    result = subprocess.run(
        ["git", *args],
        cwd=workspace,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if result.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} failed: {result.stderr.strip()}")


def prepare_workspace(eval_case: dict[str, Any], run_dir: Path) -> Path:
    fixture_name = eval_case.get("fixture")
    if not fixture_name:
        raise ValueError(f"eval {eval_case.get('id')} is missing fixture")

    fixture_dir = FILES_DIR / fixture_name
    base_dir = fixture_dir / "base"
    changes_dir = fixture_dir / "changes"
    if not base_dir.is_dir():
        raise FileNotFoundError(f"fixture base directory not found: {base_dir}")
    if not changes_dir.is_dir():
        raise FileNotFoundError(f"fixture changes directory not found: {changes_dir}")

    workspace = run_dir / "workspace"
    if workspace.exists():
        shutil.rmtree(workspace)
    shutil.copytree(base_dir, workspace)

    run_git(workspace, ["init"])
    run_git(workspace, ["config", "user.email", "eval@example.local"])
    run_git(workspace, ["config", "user.name", "Eval Runner"])
    run_git(workspace, ["add", "."])
    run_git(workspace, ["commit", "-m", "baseline fixture"])
    copy_overlay(changes_dir, workspace)
    return workspace


def kill_process_tree(process: subprocess.Popen) -> None:
    if process.poll() is not None:
        return
    if os.name == "nt":
        subprocess.run(
            ["taskkill", "/PID", str(process.pid), "/T", "/F"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        )
    else:
        os.killpg(os.getpgid(process.pid), signal.SIGKILL)


def build_prompt(configuration: str, skill_instructions: str, prompt: str) -> str:
    if configuration == "with_skill":
        return f"""{skill_instructions}

---

Apply the code-reviewer skill above to this eval task.
Use the current workspace git diff as the review target.
Do not create a git commit during this eval run.

{prompt}"""

    return f"""[baseline - do not apply the code-reviewer skill instructions]
Use your general code review behavior only. Review the current workspace git diff.
Do not create a git commit during this eval run.

{prompt}"""


def build_command(
    runner_name: str,
    command_prefix: list[str],
    workspace: Path,
    last_message_path: Path,
) -> list[str]:
    if runner_name == "codex":
        return [
            *command_prefix,
            "--cd",
            str(workspace.resolve()),
            "--output-last-message",
            str(last_message_path.resolve()),
            "-",
        ]
    return command_prefix


def run_single(
    runner_name: str,
    command_prefix: list[str],
    prompt: str,
    run_dir: Path,
    workspace: Path,
    timeout: int,
    dry_run: bool,
) -> dict[str, Any]:
    run_dir.mkdir(parents=True, exist_ok=True)
    log_path = run_dir / "output.log"
    last_message_path = run_dir / "last-message.md"
    cmd = build_command(runner_name, command_prefix, workspace, last_message_path)
    stdin_text = prompt if runner_name == "codex" else None
    if runner_name != "codex":
        cmd = [*cmd, prompt]

    start_dt = datetime.now(timezone.utc)
    start_ts = time.monotonic()

    if dry_run:
        log_path.write_text("[dry-run] " + " ".join(cmd) + "\n", encoding="utf-8")
        last_message_path.write_text("[dry-run] AI CLI was not invoked.\n", encoding="utf-8")
        return {
            "start": start_dt.isoformat(),
            "end": datetime.now(timezone.utc).isoformat(),
            "duration_seconds": round(time.monotonic() - start_ts, 3),
            "exit_code": 0,
            "timed_out": False,
            "timeout_setting": timeout,
            "output_log": str(log_path),
            "last_message": str(last_message_path),
            "workspace": str(workspace),
        }

    timed_out = False
    exit_code = -1

    with log_path.open("w", encoding="utf-8", errors="replace") as log_file:
        log_file.write("$ " + " ".join(cmd) + "\n\n")
        log_file.flush()
        process = subprocess.Popen(
            cmd,
            cwd=workspace,
            stdin=subprocess.PIPE if stdin_text is not None else None,
            stdout=log_file,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            start_new_session=os.name != "nt",
        )
        try:
            process.communicate(stdin_text, timeout=timeout)
            exit_code = process.returncode
        except subprocess.TimeoutExpired:
            timed_out = True
            kill_process_tree(process)
            process.communicate()
            exit_code = process.returncode
            log_file.write(f"\n[timeout] killed process after {timeout}s\n")

    if not last_message_path.exists():
        last_message_path.write_text(
            log_path.read_text(encoding="utf-8", errors="replace"),
            encoding="utf-8",
        )

    return {
        "start": start_dt.isoformat(),
        "end": datetime.now(timezone.utc).isoformat(),
        "duration_seconds": round(time.monotonic() - start_ts, 3),
        "exit_code": exit_code,
        "timed_out": timed_out,
        "timeout_setting": timeout,
        "output_log": str(log_path),
        "last_message": str(last_message_path),
        "workspace": str(workspace),
    }


def run_eval_case(
    eval_case: dict[str, Any],
    index: int,
    runner_name: str,
    command_prefix: list[str],
    skill_instructions: str,
    iteration_dir: Path,
    timeout: int,
    configurations: list[str],
    dry_run: bool,
) -> list[dict[str, Any]]:
    eval_id = str(eval_case.get("id", index))
    name = eval_case.get("name") or f"eval-{eval_id}"
    prompt = eval_case.get("prompt")
    if not prompt:
        raise ValueError(f"eval {eval_id} is missing prompt")

    eval_dir = iteration_dir / safe_name(name)
    write_json(
        eval_dir / "eval_metadata.json",
        {
            "eval_id": eval_id,
            "name": name,
            "prompt": prompt,
            "expected_output": eval_case.get("expected_output", ""),
            "assertions": eval_case.get("assertions", []),
            "files": eval_case.get("files", []),
            "fixture": eval_case.get("fixture", ""),
            "configurations": configurations,
            "workspace_path": str(eval_dir),
        },
    )

    rows: list[dict[str, Any]] = []
    for config in configurations:
        run_dir = eval_dir / config
        workspace = prepare_workspace(eval_case, run_dir)
        effective_prompt = build_prompt(config, skill_instructions, prompt)

        print(f"  [start] {name}/{config}")
        timing = run_single(runner_name, command_prefix, effective_prompt, run_dir, workspace, timeout, dry_run)
        write_json(run_dir / "timing.json", timing)

        status = "timeout" if timing["timed_out"] else ("pass" if timing["exit_code"] == 0 else "fail")
        print(f"  [done]  {name}/{config} - exit={timing['exit_code']} {timing['duration_seconds']}s {status}")

        rows.append(
            {
                "eval_id": eval_id,
                "eval_name": name,
                "configuration": config,
                "exit_code": timing["exit_code"],
                "duration_seconds": timing["duration_seconds"],
                "timed_out": timing["timed_out"],
                "output_log": timing["output_log"],
                "workspace": timing["workspace"],
                "status": status,
            }
        )
    return rows


def failed_result(
    eval_case: dict[str, Any],
    index: int,
    iteration_dir: Path,
    timeout: int,
    error: BaseException,
) -> dict[str, Any]:
    eval_id = str(eval_case.get("id", index))
    name = eval_case.get("name") or f"eval-{eval_id}"
    run_dir = iteration_dir / safe_name(name) / "with_skill"
    run_dir.mkdir(parents=True, exist_ok=True)

    log_path = run_dir / "output.log"
    log_path.write_text(f"[runner-error] {type(error).__name__}: {error}\n", encoding="utf-8")

    now = datetime.now(timezone.utc).isoformat()
    result = {
        "eval_id": eval_id,
        "eval_name": name,
        "configuration": "with_skill",
        "exit_code": 1,
        "duration_seconds": 0,
        "timed_out": False,
        "output_log": str(log_path),
        "status": "fail",
        "error": f"{type(error).__name__}: {error}",
    }
    write_json(run_dir / "timing.json", {"start": now, "end": now, **result, "timeout_setting": timeout})
    return result


def sort_key(result: dict[str, Any]) -> tuple[int, int | str, int]:
    eval_id = str(result["eval_id"])
    config_order = 0 if result["configuration"] == "with_skill" else 1
    if eval_id.isdigit():
        return 0, int(eval_id), config_order
    return 1, eval_id, config_order


def print_summary(results: list[dict[str, Any]]) -> bool:
    if not results:
        print("No results.")
        return True

    col_name = max(len(r["eval_name"]) for r in results)
    col_cfg = max(len(r["configuration"]) for r in results)
    sep = "-" * (col_name + col_cfg + 46)

    print()
    print("=== SUMMARY ===")
    print(sep)
    print(f"{'EVAL':<{col_name}}  {'CONFIG':<{col_cfg}}  {'STATUS':<8}  {'EXIT':>4}  {'DURATION':>10}  LOG")
    print(sep)

    all_passed = True
    for result in results:
        if result["status"] != "pass":
            all_passed = False
        print(
            f"{result['eval_name']:<{col_name}}  "
            f"{result['configuration']:<{col_cfg}}  "
            f"{result['status'].upper():<8}  "
            f"{result['exit_code']:>4}  "
            f"{result['duration_seconds']:>9.1f}s  "
            f"{result['output_log']}"
        )

    print(sep)
    passed = sum(1 for result in results if result["status"] == "pass")
    print(f"Result: {passed}/{len(results)} passed")
    print()
    return all_passed


def main() -> int:
    if not EVALS_JSON.is_file():
        fail(f"evals.json not found at {EVALS_JSON}")

    args = parse_args()
    configurations = ["with_skill"] if args.with_skill_only else CONFIGURATIONS
    data = json.loads(EVALS_JSON.read_text(encoding="utf-8"))
    evals = [
        (index, eval_case)
        for index, eval_case in enumerate(data.get("evals", []))
        if not args.eval_id or str(eval_case.get("id", index)) == args.eval_id
    ]
    if not evals:
        fail(f"no evals matched id: {args.eval_id}")

    runner_name, command_prefix = detect_runner()
    skill_instructions = read_skill_instructions()
    iteration_dir = next_iteration_dir(args.output_dir)
    iteration_dir.mkdir(parents=True, exist_ok=True)

    skill_name = data.get("skill_name", "<skill-name>")
    print(f"=== {skill_name} evals ({len(evals)} cases x {len(configurations)} configs) ===")
    print(f"[iteration] {iteration_dir}")
    print(f"[jobs] {args.jobs}  [timeout] {args.timeout}s  [configs] {', '.join(configurations)}")
    if args.dry_run:
        print("[dry-run] AI CLI will not be invoked")
    print()

    all_rows: list[dict[str, Any]] = []
    max_workers = max(1, min(args.jobs, len(evals)))

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(
                run_eval_case,
                eval_case,
                index,
                runner_name,
                command_prefix,
                skill_instructions,
                iteration_dir,
                args.timeout,
                configurations,
                args.dry_run,
            ): (index, eval_case)
            for index, eval_case in evals
        }
        for future in as_completed(futures):
            index, eval_case = futures[future]
            try:
                all_rows.extend(future.result())
            except Exception as error:
                result = failed_result(eval_case, index, iteration_dir, args.timeout, error)
                print(f"  [failed] {result['eval_name']}: {result['error']}")
                all_rows.append(result)

    all_rows.sort(key=sort_key)
    all_passed = print_summary(all_rows)

    write_json(
        iteration_dir / "benchmark.json",
        {
            "iteration": iteration_dir.name,
            "skill_name": skill_name,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "total": len(all_rows),
            "passed": sum(1 for result in all_rows if result["status"] == "pass"),
            "failed": sum(1 for result in all_rows if result["status"] == "fail"),
            "timeout": sum(1 for result in all_rows if result["status"] == "timeout"),
            "results": all_rows,
        },
    )
    print(f"[benchmark] {iteration_dir / 'benchmark.json'}")

    return 0 if all_passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
