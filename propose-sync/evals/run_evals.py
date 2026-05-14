#!/usr/bin/env python3
"""Run propose-sync behavior evals using codex or claude CLI.

Usage: python evals/run_evals.py [eval-id]   # omit id to run all
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
EVALS_JSON = SCRIPT_DIR / "evals.json"


def fail(message: str) -> None:
    print(f"Error: {message}", file=sys.stderr)
    raise SystemExit(1)


def detect_runner() -> list[str]:
    codex = shutil.which("codex")
    if codex:
        print("[tool] codex")
        return [codex, "exec", "--dangerously-bypass-approvals-and-sandbox"]

    claude = shutil.which("claude")
    if claude:
        print("[tool] claude")
        return [claude, "-p"]

    fail("neither codex nor claude CLI found")


def run_prompt(command_prefix: list[str], prompt: str) -> None:
    process = subprocess.Popen([*command_prefix, prompt])
    return_code = process.wait()
    if return_code != 0:
        fail(f"AI CLI exited with code {return_code}")


def main() -> int:
    if not EVALS_JSON.is_file():
        fail(f"evals.json not found at {EVALS_JSON}")

    data = json.loads(EVALS_JSON.read_text(encoding="utf-8"))
    evals = data.get("evals", [])
    target_id = sys.argv[1] if len(sys.argv) > 1 else None
    command_prefix = detect_runner()

    print(f"=== {data.get('skill_name', '<skill-name>')} evals ({len(evals)} total) ===")

    for index, eval_case in enumerate(evals):
        eval_id = str(eval_case.get("id", index))
        name = eval_case.get("name") or f"eval-{eval_id}"
        prompt = eval_case.get("prompt")

        if target_id and eval_id != target_id:
            continue

        if not prompt:
            fail(f"eval {eval_id} is missing prompt")

        print()
        print(f"--- [{eval_id}] {name} ---")
        print(f"Prompt: {prompt}")
        print()
        run_prompt(command_prefix, prompt)
        print()
        print(f"--- end [{eval_id}] ---")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
