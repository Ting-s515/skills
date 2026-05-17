#!/usr/bin/env python3
"""Run code-reviewer behavior evals using codex or claude CLI.

Each eval runs twice: with_skill (SKILL.MD injected) and without_skill (baseline).
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
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
EVALS_JSON = SCRIPT_DIR / "evals.json"
SKILL_MD = SCRIPT_DIR.parent / "SKILL.MD"
FIXTURES_DIR = SCRIPT_DIR / "fixtures"
OUTPUT_DIR = SCRIPT_DIR.parent / "eval-results"


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

    # 複製 base 檔案並建立 initial commit
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

    # 複製 staged 檔案並 git add（模擬即將提交的變更）
    staged_dir = eval_fixture_dir / "staged"
    if staged_dir.exists():
        for src_file in staged_dir.rglob("*"):
            if src_file.is_file():
                rel_path = src_file.relative_to(staged_dir)
                dest_file = temp_dir / rel_path
                dest_file.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src_file, dest_file)
        run_git(["add", "-A"], cwd=temp_dir)

    # 複製規格文檔至 docs/specs/（不納入 git，讓 skill 透過 Read 工具讀取）
    spec_dir = eval_fixture_dir / "spec"
    if spec_dir.exists():
        for src_file in spec_dir.rglob("*"):
            if src_file.is_file():
                dest_file = temp_dir / "docs" / "specs" / src_file.name
                dest_file.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src_file, dest_file)

    return temp_dir


def run_ai(command_prefix: list[str], prompt: str, output_file: Path, cwd: Path) -> None:
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with output_file.open("w", encoding="utf-8") as f:
        process = subprocess.Popen(
            [*command_prefix, prompt],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            cwd=str(cwd),
        )

        if process.stdout is not None:
            for line in process.stdout:
                print(line, end="")
                f.write(line)

        return_code = process.wait()
        if return_code != 0:
            fail(f"AI CLI exited with code {return_code}")


def run_with_skill(
    command_prefix: list[str],
    skill_instructions: str,
    prompt: str,
    output_file: Path,
    cwd: Path,
) -> None:
    full_prompt = (
        f"{skill_instructions}\n\n"
        f"---\n\n"
        f"Apply the above skill instructions to this task:\n\n"
        f"{prompt}"
    )
    run_ai(command_prefix, full_prompt, output_file, cwd)


def run_without_skill(
    command_prefix: list[str],
    prompt: str,
    output_file: Path,
    cwd: Path,
) -> None:
    run_ai(command_prefix, prompt, output_file, cwd)


def main() -> int:
    data = load_evals()
    skill_instructions = read_skill_instructions()
    _tool_name, command_prefix = detect_ai_tool()

    skill_name = data.get("skill_name", "<skill-name>")
    evals = data.get("evals", [])
    target_id = sys.argv[1] if len(sys.argv) > 1 else None

    print(f"=== {skill_name} evals ({len(evals)} total) ===")

    for index, eval_case in enumerate(evals):
        eval_id = str(eval_case.get("id", index))
        name = eval_case.get("name") or f"eval-{eval_id}"
        prompt = eval_case.get("prompt")

        if target_id and eval_id != target_id:
            continue

        if not prompt:
            fail(f"eval {eval_id} is missing prompt")

        fixture_dir = FIXTURES_DIR / f"eval-{eval_id}"
        if not fixture_dir.exists():
            fail(f"Fixture directory not found: {fixture_dir}")

        eval_dir = OUTPUT_DIR / f"eval-{eval_id}"

        print()
        print(f"=== [{eval_id}] {name} ===")
        print(f"Prompt: {prompt}")

        # --- with_skill ---
        print("\nSetting up temp git repo (with_skill)...")
        temp_dir_with = setup_git_repo(fixture_dir)
        print(f"[repo] {temp_dir_with}")

        print()
        print("--- with_skill ---")
        run_with_skill(
            command_prefix,
            skill_instructions,
            prompt,
            eval_dir / "with_skill" / "output.txt",
            temp_dir_with,
        )
        print("--- end with_skill ---")

        shutil.rmtree(temp_dir_with, ignore_errors=True)

        # --- without_skill (baseline) ---
        print("\nSetting up temp git repo (without_skill)...")
        temp_dir_without = setup_git_repo(fixture_dir)
        print(f"[repo] {temp_dir_without}")

        print()
        print("--- without_skill (baseline) ---")
        run_without_skill(
            command_prefix,
            prompt,
            eval_dir / "without_skill" / "output.txt",
            temp_dir_without,
        )
        print("--- end without_skill ---")

        shutil.rmtree(temp_dir_without, ignore_errors=True)

        print()
        print(f"[results saved] {eval_dir}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
