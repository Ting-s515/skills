#!/usr/bin/env python3
"""Run apply behavior evals using codex or claude CLI.

Usage: python evals/run_evals.py [eval-id] [--jobs 3] [--timeout 1800]
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import signal
import shutil
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any


SCRIPT_DIR = Path(__file__).resolve().parent
EVALS_JSON = SCRIPT_DIR / "evals.json"
RUNS_DIR = SCRIPT_DIR / "eval-runs"
DEFAULT_TIMEOUT_SECONDS = 30 * 60


def fail(message: str) -> None:
    print(f"Error: {message}", file=sys.stderr)
    raise SystemExit(1)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run apply behavior evals.")
    parser.add_argument("eval_id", nargs="?", help="Optional eval id to run")
    parser.add_argument("--jobs", type=int, default=3, help="Max eval runs to execute in parallel")
    parser.add_argument(
        "--timeout",
        type=int,
        default=DEFAULT_TIMEOUT_SECONDS,
        help="Per-run timeout in seconds",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=RUNS_DIR,
        help="Directory that stores eval run artifacts",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Create metadata and summary without invoking the AI CLI",
    )
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
    existing = []
    for child in output_dir.iterdir():
        if child.is_dir() and child.name.startswith("iteration-"):
            suffix = child.name.removeprefix("iteration-")
            if suffix.isdigit():
                existing.append(int(suffix))
    return output_dir / f"iteration-{max(existing, default=0) + 1}"


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def kill_process_tree(process: subprocess.Popen[str]) -> None:
    if process.poll() is not None:
        return

    # Windows child processes can survive Popen.kill(); taskkill keeps timeout cleanup local to this run.
    if os.name == "nt":
        subprocess.run(
            ["taskkill", "/PID", str(process.pid), "/T", "/F"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        )
        return

    os.killpg(os.getpgid(process.pid), signal.SIGKILL)


def run_prompt(
    runner_name: str,
    command_prefix: list[str],
    prompt: str,
    run_dir: Path,
    timeout_seconds: int,
    dry_run: bool,
) -> dict[str, Any]:
    started = dt.datetime.now(dt.timezone.utc)
    started_monotonic = time.monotonic()
    output_log = run_dir / "output.log"
    last_message = run_dir / "last-message.md"
    if runner_name == "codex":
        command = [*command_prefix, "--output-last-message", str(last_message), prompt]
    else:
        command = [*command_prefix, prompt]

    run_dir.mkdir(parents=True, exist_ok=True)

    if dry_run:
        output_log.write_text("[dry-run] " + " ".join(command) + "\n", encoding="utf-8")
        last_message.write_text("[dry-run] AI CLI was not invoked.\n", encoding="utf-8")
        ended = dt.datetime.now(dt.timezone.utc)
        return {
            "started_at": started.isoformat(),
            "ended_at": ended.isoformat(),
            "duration_seconds": round(time.monotonic() - started_monotonic, 3),
            "exit_code": 0,
            "timed_out": False,
            "timeout_seconds": timeout_seconds,
            "output_log": str(output_log),
            "last_message": str(last_message),
        }

    timed_out = False
    process: subprocess.Popen[str] | None = None

    with output_log.open("w", encoding="utf-8", errors="replace") as log:
        log.write("$ " + " ".join(command) + "\n\n")
        log.flush()
        process = subprocess.Popen(
            command,
            stdout=log,
            stderr=subprocess.STDOUT,
            text=True,
            start_new_session=os.name != "nt",
        )
        try:
            exit_code = process.wait(timeout=timeout_seconds)
        except subprocess.TimeoutExpired:
            timed_out = True
            kill_process_tree(process)
            exit_code = process.wait()
            log.write(f"\n[timeout] killed process after {timeout_seconds} seconds\n")

    if not last_message.exists():
        last_message.write_text(output_log.read_text(encoding="utf-8", errors="replace"), encoding="utf-8")

    ended = dt.datetime.now(dt.timezone.utc)
    return {
        "started_at": started.isoformat(),
        "ended_at": ended.isoformat(),
        "duration_seconds": round(time.monotonic() - started_monotonic, 3),
        "exit_code": exit_code,
        "timed_out": timed_out,
        "timeout_seconds": timeout_seconds,
        "output_log": str(output_log),
        "last_message": str(last_message),
    }


def run_eval_case(
    eval_case: dict[str, Any],
    index: int,
    runner_name: str,
    command_prefix: list[str],
    iteration_dir: Path,
    timeout_seconds: int,
    dry_run: bool,
) -> dict[str, Any]:
    eval_id = str(eval_case.get("id", index))
    name = eval_case.get("name") or f"eval-{eval_id}"
    prompt = eval_case.get("prompt")
    if not prompt:
        raise ValueError(f"eval {eval_id} is missing prompt")

    eval_dir = iteration_dir / f"{eval_id}-{safe_name(name)}"
    run_dir = eval_dir / "with_skill"
    metadata = {
        "eval_id": eval_id,
        "eval_name": name,
        "prompt": prompt,
        "configuration": "with_skill",
        "assertions": eval_case.get("assertions", []),
        "expected_output": eval_case.get("expected_output"),
        "files": eval_case.get("files", []),
    }
    write_json(eval_dir / "eval_metadata.json", metadata)

    print(f"[start] {name} -> {run_dir}")
    timing = run_prompt(runner_name, command_prefix, prompt, run_dir, timeout_seconds, dry_run)
    write_json(run_dir / "timing.json", timing)

    status = "timeout" if timing["timed_out"] else f"exit {timing['exit_code']}"
    print(f"[done] {name}: {status}, {timing['duration_seconds']}s")
    return {
        "eval_id": eval_id,
        "eval_name": name,
        "configuration": "with_skill",
        **timing,
    }


def failed_result(
    eval_case: dict[str, Any],
    index: int,
    iteration_dir: Path,
    timeout_seconds: int,
    error: BaseException,
) -> dict[str, Any]:
    eval_id = str(eval_case.get("id", index))
    name = eval_case.get("name") or f"eval-{eval_id}"
    run_dir = iteration_dir / f"{eval_id}-{safe_name(name)}" / "with_skill"
    output_log = run_dir / "output.log"
    started = dt.datetime.now(dt.timezone.utc).isoformat()

    run_dir.mkdir(parents=True, exist_ok=True)
    output_log.write_text(f"[runner-error] {type(error).__name__}: {error}\n", encoding="utf-8")
    result = {
        "eval_id": eval_id,
        "eval_name": name,
        "configuration": "with_skill",
        "started_at": started,
        "ended_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "duration_seconds": 0,
        "exit_code": 1,
        "timed_out": False,
        "timeout_seconds": timeout_seconds,
        "output_log": str(output_log),
        "last_message": str(run_dir / "last-message.md"),
        "error": f"{type(error).__name__}: {error}",
    }
    write_json(run_dir / "timing.json", result)
    return result


def print_summary(results: list[dict[str, Any]]) -> None:
    print()
    print("=== summary ===")
    print(f"{'eval':<24} {'config':<12} {'exit':<6} {'timeout':<8} {'seconds':<8} log")
    for result in results:
        print(
            f"{result['eval_name']:<24} "
            f"{result['configuration']:<12} "
            f"{result['exit_code']!s:<6} "
            f"{str(result['timed_out']):<8} "
            f"{result['duration_seconds']!s:<8} "
            f"{result['output_log']}"
        )


def sort_key(result: dict[str, Any]) -> tuple[int, int | str]:
    eval_id = str(result["eval_id"])
    if eval_id.isdigit():
        return (0, int(eval_id))
    return (1, eval_id)


def main() -> int:
    args = parse_args()
    if not EVALS_JSON.is_file():
        fail(f"evals.json not found at {EVALS_JSON}")

    data = json.loads(EVALS_JSON.read_text(encoding="utf-8"))
    target_id = args.eval_id
    evals = [
        (index, eval_case)
        for index, eval_case in enumerate(data.get("evals", []))
        if not target_id or str(eval_case.get("id", index)) == target_id
    ]
    if not evals:
        fail(f"no evals matched id: {target_id}")

    runner_name, command_prefix = detect_runner()
    iteration_dir = next_iteration_dir(args.output_dir)
    iteration_dir.mkdir(parents=True, exist_ok=True)

    print(f"=== {data.get('skill_name', '<skill-name>')} evals ({len(evals)} selected) ===")
    print(f"[output] {iteration_dir}")
    print(f"[jobs] {args.jobs}")
    print(f"[timeout] {args.timeout}s")
    if args.dry_run:
        print("[dry-run] AI CLI will not be invoked")

    max_workers = max(1, min(args.jobs, len(evals)))
    results: list[dict[str, Any]] = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(
                run_eval_case,
                eval_case,
                index,
                runner_name,
                command_prefix,
                iteration_dir,
                args.timeout,
                args.dry_run,
            ): (index, eval_case)
            for index, eval_case in evals
        }
        for future in as_completed(futures):
            index, eval_case = futures[future]
            try:
                results.append(future.result())
            except Exception as error:
                result = failed_result(eval_case, index, iteration_dir, args.timeout, error)
                print(f"[failed] {result['eval_name']}: {result['error']}")
                results.append(result)

    results.sort(key=sort_key)
    summary = {
        "skill_name": data.get("skill_name", "<skill-name>"),
        "configuration": "with_skill",
        "runs": results,
    }
    write_json(iteration_dir / "summary.json", summary)
    write_json(iteration_dir / "benchmark.json", summary)
    print_summary(results)

    failed = [result for result in results if result["timed_out"] or result["exit_code"] != 0]
    if failed:
        print()
        print(f"Error: {len(failed)} eval run(s) failed", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
