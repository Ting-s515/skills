#!/usr/bin/env python3
"""Run propose behavior evals using codex or claude CLI.

Usage:
  python evals/run_evals.py [options] [eval-id]

Options:
  --jobs N          Parallel workers (default: 2)
  --timeout N       Per-run timeout in seconds (default: 300)
  --with-skill-only Only run with_skill configuration
  --output-dir DIR  Directory that stores eval run artifacts
  --dry-run         Create metadata without invoking the AI CLI
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
EVALS_JSON = SCRIPT_DIR / "evals.json"
EVAL_RUNS_DIR = SCRIPT_DIR / "eval-runs"

DEFAULT_JOBS = 2
DEFAULT_TIMEOUT = 300
CONFIGURATIONS = ["with_skill", "without_skill"]


def fail(message: str) -> None:
    print(f"Error: {message}", file=sys.stderr)
    raise SystemExit(1)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run propose behavior evals.")
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
    return "", []  # unreachable, satisfies type checker


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


def run_single(
    runner_name: str,
    command_prefix: list[str],
    prompt: str,
    run_dir: Path,
    timeout: int,
    dry_run: bool,
) -> dict[str, Any]:
    run_dir.mkdir(parents=True, exist_ok=True)
    log_path = run_dir / "output.log"
    last_message_path = run_dir / "last-message.md"

    if runner_name == "codex":
        cmd = [*command_prefix, "--output-last-message", str(last_message_path)]
    else:
        cmd = [*command_prefix]

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
        }

    timed_out = False
    exit_code = -1

    with log_path.open("w", encoding="utf-8", errors="replace") as log_file:
        log_file.write("$ " + " ".join(cmd) + "\n\n")
        log_file.flush()
        process = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=log_file,
            stderr=subprocess.STDOUT,
            start_new_session=os.name != "nt",
        )
        process.stdin.write(prompt.encode("utf-8"))
        process.stdin.close()
        try:
            exit_code = process.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            timed_out = True
            kill_process_tree(process)
            exit_code = process.wait()
            log_file.write(f"\n[timeout] killed after {timeout}s\n")

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
    }


def prepare_eval_case_metadata(
    eval_case: dict[str, Any],
    index: int,
    iteration_dir: Path,
    configurations: list[str],
) -> None:
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
            "configurations": configurations,
            "workspace_path": str(eval_dir),
        },
    )


def run_eval_config(
    eval_case: dict[str, Any],
    index: int,
    config: str,
    runner_name: str,
    command_prefix: list[str],
    iteration_dir: Path,
    timeout: int,
    dry_run: bool,
) -> dict[str, Any]:
    eval_id = str(eval_case.get("id", index))
    name = eval_case.get("name") or f"eval-{eval_id}"
    prompt = eval_case.get("prompt")
    if not prompt:
        raise ValueError(f"eval {eval_id} is missing prompt")

    eval_dir = iteration_dir / safe_name(name)
    run_dir = eval_dir / config
    effective_prompt = (
        f"[baseline — do not apply any skill pattern] {prompt}"
        if config == "without_skill"
        else prompt
    )

    print(f"  [start] {name}/{config}")
    timing = run_single(runner_name, command_prefix, effective_prompt, run_dir, timeout, dry_run)
    write_json(run_dir / "timing.json", timing)

    status = "timeout" if timing["timed_out"] else ("pass" if timing["exit_code"] == 0 else "fail")
    print(f"  [done]  {name}/{config} — exit={timing['exit_code']} {timing['duration_seconds']}s {status}")

    return {
        "eval_id": eval_id,
        "eval_name": name,
        "configuration": config,
        "exit_code": timing["exit_code"],
        "duration_seconds": timing["duration_seconds"],
        "timed_out": timing["timed_out"],
        "output_log": timing["output_log"],
        "status": status,
    }


def failed_result(
    eval_case: dict[str, Any],
    index: int,
    config: str,
    iteration_dir: Path,
    timeout: int,
    error: BaseException,
) -> dict[str, Any]:
    eval_id = str(eval_case.get("id", index))
    name = eval_case.get("name") or f"eval-{eval_id}"
    run_dir = iteration_dir / safe_name(name) / config
    run_dir.mkdir(parents=True, exist_ok=True)

    log_path = run_dir / "output.log"
    log_path.write_text(f"[runner-error] {type(error).__name__}: {error}\n", encoding="utf-8")

    now = datetime.now(timezone.utc).isoformat()
    result = {
        "eval_id": eval_id,
        "eval_name": name,
        "configuration": config,
        "exit_code": 1,
        "duration_seconds": 0,
        "timed_out": False,
        "output_log": str(log_path),
        "status": "fail",
        "error": f"{type(error).__name__}: {error}",
    }
    write_json(run_dir / "timing.json", {"start": now, "end": now, **result, "timeout_setting": timeout})
    return result


def sort_key(r: dict[str, Any]) -> tuple[int, int | str]:
    eid = str(r["eval_id"])
    return (0, int(eid)) if eid.isdigit() else (1, eid)


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
    for r in results:
        if r["status"] != "pass":
            all_passed = False
        print(
            f"{r['eval_name']:<{col_name}}  "
            f"{r['configuration']:<{col_cfg}}  "
            f"{r['status'].upper():<8}  "
            f"{r['exit_code']:>4}  "
            f"{r['duration_seconds']:>9.1f}s  "
            f"{r['output_log']}"
        )

    print(sep)
    passed = sum(1 for r in results if r["status"] == "pass")
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
        (i, e)
        for i, e in enumerate(data.get("evals", []))
        if not args.eval_id or str(e.get("id", i)) == args.eval_id
    ]
    if not evals:
        fail(f"no evals matched id: {args.eval_id}")

    runner_name, command_prefix = detect_runner()
    iteration_dir = next_iteration_dir(args.output_dir)
    iteration_dir.mkdir(parents=True, exist_ok=True)

    skill_name = data.get("skill_name", "<skill-name>")
    print(f"=== {skill_name} evals ({len(evals)} cases × {len(configurations)} configs) ===")
    print(f"[iteration] {iteration_dir}")
    print(f"[jobs] {args.jobs}  [timeout] {args.timeout}s  [configs] {', '.join(configurations)}")
    if args.dry_run:
        print("[dry-run] AI CLI will not be invoked")
    print()

    all_rows: list[dict[str, Any]] = []
    tasks = [
        (index, eval_case, config)
        for index, eval_case in evals
        for config in configurations
    ]
    for index, eval_case in evals:
        prepare_eval_case_metadata(eval_case, index, iteration_dir, configurations)

    with ThreadPoolExecutor(max_workers=len(tasks)) as executor:
        futures = {
            executor.submit(
                run_eval_config,
                eval_case,
                index,
                config,
                runner_name,
                command_prefix,
                iteration_dir,
                args.timeout,
                args.dry_run,
            ): (index, eval_case, config)
            for index, eval_case, config in tasks
        }
        for future in as_completed(futures):
            index, eval_case, config = futures[future]
            try:
                all_rows.append(future.result())
            except Exception as error:
                result = failed_result(eval_case, index, config, iteration_dir, args.timeout, error)
                print(f"  [failed] {result['eval_name']}/{config}: {result['error']}")
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
            "passed": sum(1 for r in all_rows if r["status"] == "pass"),
            "failed": sum(1 for r in all_rows if r["status"] == "fail"),
            "timeout": sum(1 for r in all_rows if r["status"] == "timeout"),
            "results": all_rows,
        },
    )
    print(f"[benchmark] {iteration_dir / 'benchmark.json'}")

    return 0 if all_passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
