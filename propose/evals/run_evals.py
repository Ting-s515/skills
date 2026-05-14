#!/usr/bin/env python3
"""Run propose behavior evals using codex or claude CLI.

Usage:
  python evals/run_evals.py [options] [eval-id]

Options:
  --jobs N          Parallel workers (default: 2)
  --timeout N       Per-run timeout in seconds (default: 300)
  --with-skill-only Only run with_skill configuration
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import threading
import time
from datetime import datetime, timezone
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
EVALS_JSON = SCRIPT_DIR / "evals.json"
EVAL_RUNS_DIR = SCRIPT_DIR / "eval-runs"

DEFAULT_JOBS = 2
DEFAULT_TIMEOUT = 300
CONFIGURATIONS = ["with_skill", "without_skill"]


def fail(message: str) -> None:
    print(f"Error: {message}", file=sys.stderr)
    raise SystemExit(1)


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


def next_iteration_dir() -> Path:
    existing = [
        d for d in EVAL_RUNS_DIR.glob("iteration-*")
        if d.is_dir() and d.name.split("-")[-1].isdigit()
    ]
    next_n = len(existing) + 1
    return EVAL_RUNS_DIR / f"iteration-{next_n}"


def kill_process_tree(pid: int) -> None:
    try:
        if sys.platform == "win32":
            subprocess.run(
                ["taskkill", "/F", "/T", "/PID", str(pid)],
                capture_output=True,
            )
        else:
            import os
            import signal
            os.killpg(os.getpgid(pid), signal.SIGTERM)
    except Exception:
        pass


def run_single(
    runner_name: str,
    command_prefix: list[str],
    prompt: str,
    run_dir: Path,
    timeout: int,
) -> dict:
    run_dir.mkdir(parents=True, exist_ok=True)
    log_path = run_dir / "output.log"
    last_message_path = run_dir / "last-message.md"
    timing_path = run_dir / "timing.json"

    # codex supports --output-last-message to write the final assistant turn directly
    if runner_name == "codex":
        cmd = [*command_prefix, "--output-last-message", str(last_message_path), prompt]
    else:
        cmd = [*command_prefix, prompt]

    start_dt = datetime.now(timezone.utc)
    start_ts = time.monotonic()
    timed_out = False
    exit_code: int | None = None

    with log_path.open("w", encoding="utf-8") as log_file:
        log_file.write("$ " + " ".join(cmd) + "\n\n")
        log_file.flush()
        process = subprocess.Popen(
            cmd,
            stdout=log_file,
            stderr=subprocess.STDOUT,
            start_new_session=sys.platform != "win32",
        )
        try:
            exit_code = process.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            timed_out = True
            kill_process_tree(process.pid)
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
            exit_code = -1

    duration = time.monotonic() - start_ts

    if not last_message_path.exists():
        try:
            content = log_path.read_text(encoding="utf-8", errors="replace")
            last_message_path.write_text(content, encoding="utf-8")
        except Exception:
            last_message_path.write_text("", encoding="utf-8")

    timing_path.write_text(
        json.dumps(
            {
                "start": start_dt.isoformat(),
                "end": datetime.now(timezone.utc).isoformat(),
                "duration_seconds": round(duration, 2),
                "exit_code": exit_code,
                "timed_out": timed_out,
                "timeout_setting": timeout,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    return {
        "exit_code": exit_code,
        "timed_out": timed_out,
        "duration": round(duration, 2),
        "log_path": str(log_path),
    }


def run_eval_case(
    eval_case: dict,
    iteration_dir: Path,
    runner_name: str,
    command_prefix: list[str],
    timeout: int,
    configurations: list[str],
    results: list[dict],
    lock: threading.Lock,
) -> None:
    eval_id = str(eval_case.get("id", "?"))
    name = eval_case.get("name") or f"eval-{eval_id}"
    prompt = eval_case.get("prompt", "")

    if not prompt:
        with lock:
            results.append({
                "eval_id": eval_id,
                "name": name,
                "configuration": "-",
                "exit_code": -1,
                "duration": 0.0,
                "timed_out": False,
                "log_path": "",
                "status": "fail",
                "error": "missing prompt",
            })
        return

    eval_dir = iteration_dir / name
    eval_dir.mkdir(parents=True, exist_ok=True)

    (eval_dir / "eval_metadata.json").write_text(
        json.dumps(
            {
                "eval_id": eval_id,
                "name": name,
                "prompt": prompt,
                "expected_output": eval_case.get("expected_output", ""),
                "assertions": eval_case.get("assertions", []),
                "configurations": configurations,
                "workspace_path": str(eval_dir),
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    for config in configurations:
        run_dir = eval_dir / config
        # without_skill: prefix tells the model to answer without invoking any skill pattern
        effective_prompt = (
            f"[baseline — do not apply any skill pattern] {prompt}"
            if config == "without_skill"
            else prompt
        )

        print(f"  [start] {name}/{config}")
        result = run_single(runner_name, command_prefix, effective_prompt, run_dir, timeout)

        status = (
            "timeout" if result["timed_out"]
            else ("pass" if result["exit_code"] == 0 else "fail")
        )
        print(
            f"  [done]  {name}/{config}"
            f" — exit={result['exit_code']}"
            f" duration={result['duration']}s"
            f" status={status}"
        )

        with lock:
            results.append(
                {
                    "eval_id": eval_id,
                    "name": name,
                    "configuration": config,
                    "exit_code": result["exit_code"],
                    "duration": result["duration"],
                    "timed_out": result["timed_out"],
                    "log_path": result["log_path"],
                    "status": status,
                }
            )


def print_summary(results: list[dict]) -> bool:
    if not results:
        print("No results.")
        return True

    col_name = max(len(r["name"]) for r in results)
    col_cfg = max(len(r["configuration"]) for r in results)
    sep = "-" * (col_name + col_cfg + 46)

    print()
    print("=== SUMMARY ===")
    print(sep)
    print(
        f"{'EVAL':<{col_name}}  {'CONFIG':<{col_cfg}}"
        f"  {'STATUS':<8}  {'EXIT':>4}  {'DURATION':>10}  LOG"
    )
    print(sep)

    all_passed = True
    for r in sorted(results, key=lambda x: (x["name"], x["configuration"])):
        if r["status"] != "pass":
            all_passed = False
        print(
            f"{r['name']:<{col_name}}  "
            f"{r['configuration']:<{col_cfg}}  "
            f"{r['status'].upper():<8}  "
            f"{r['exit_code']:>4}  "
            f"{r['duration']:>9.1f}s  "
            f"{r['log_path']}"
        )

    print(sep)
    passed = sum(1 for r in results if r["status"] == "pass")
    print(f"Result: {passed}/{len(results)} passed")
    print()
    return all_passed


def write_benchmark(iteration_dir: Path, results: list[dict]) -> None:
    path = iteration_dir / "benchmark.json"
    path.write_text(
        json.dumps(
            {
                "iteration": iteration_dir.name,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "total": len(results),
                "passed": sum(1 for r in results if r["status"] == "pass"),
                "failed": sum(1 for r in results if r["status"] == "fail"),
                "timeout": sum(1 for r in results if r["status"] == "timeout"),
                "results": results,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    print(f"[benchmark] {path}")


def parse_args(argv: list[str]) -> dict:
    jobs = DEFAULT_JOBS
    timeout = DEFAULT_TIMEOUT
    with_skill_only = False
    target_id: str | None = None

    i = 0
    while i < len(argv):
        if argv[i] == "--jobs" and i + 1 < len(argv):
            jobs = int(argv[i + 1])
            i += 2
        elif argv[i] == "--timeout" and i + 1 < len(argv):
            timeout = int(argv[i + 1])
            i += 2
        elif argv[i] == "--with-skill-only":
            with_skill_only = True
            i += 1
        else:
            target_id = argv[i]
            i += 1

    return {
        "jobs": jobs,
        "timeout": timeout,
        "with_skill_only": with_skill_only,
        "target_id": target_id,
    }


def main() -> int:
    if not EVALS_JSON.is_file():
        fail(f"evals.json not found at {EVALS_JSON}")

    opts = parse_args(sys.argv[1:])
    configurations = ["with_skill"] if opts["with_skill_only"] else CONFIGURATIONS

    data = json.loads(EVALS_JSON.read_text(encoding="utf-8"))
    evals = data.get("evals", [])

    if opts["target_id"]:
        evals = [e for e in evals if str(e.get("id", "")) == opts["target_id"]]
        if not evals:
            fail(f"eval id '{opts['target_id']}' not found")

    runner_name, command_prefix = detect_runner()

    EVAL_RUNS_DIR.mkdir(parents=True, exist_ok=True)
    iteration_dir = next_iteration_dir()
    iteration_dir.mkdir(parents=True, exist_ok=True)

    skill_name = data.get("skill_name", "<skill-name>")
    print(
        f"=== {skill_name} evals"
        f" ({len(evals)} cases × {len(configurations)} configs) ==="
    )
    print(f"[iteration] {iteration_dir}")
    print(
        f"[jobs] {opts['jobs']}"
        f"  [timeout] {opts['timeout']}s"
        f"  [configs] {', '.join(configurations)}"
    )
    print()

    results: list[dict] = []
    lock = threading.Lock()

    threads = [
        threading.Thread(
            target=run_eval_case,
            args=(
                eval_case,
                iteration_dir,
                runner_name,
                command_prefix,
                opts["timeout"],
                configurations,
                results,
                lock,
            ),
            daemon=True,
        )
        for eval_case in evals
    ]

    # Fan-out with concurrency cap
    running: list[threading.Thread] = []
    pending = list(threads)

    while pending or running:
        while pending and len(running) < opts["jobs"]:
            t = pending.pop(0)
            t.start()
            running.append(t)
        time.sleep(0.5)
        running = [t for t in running if t.is_alive()]

    def sort_key(r: dict) -> tuple[int, int | str]:
        eid = str(r["eval_id"])
        return (0, int(eid)) if eid.isdigit() else (1, eid)

    results.sort(key=sort_key)
    all_passed = print_summary(results)
    write_benchmark(iteration_dir, results)

    return 0 if all_passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
