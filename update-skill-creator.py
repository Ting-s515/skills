#!/usr/bin/env python3
from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


REPO_URL = "https://github.com/anthropics/claude-plugins-official.git"
SKILL_PATH = Path("plugins/skill-creator/skills/skill-creator")
TARGET_DIR = Path.home() / ".claude" / "skills" / "skill-creator-plus"
PROTECTED_ITEMS = ["agents", "assets", "eval-viewer", "references", "scripts", "LICENSE.txt", "SKILL.md"]
ANCHOR = "references/schemas.md` for the full schema"


def fail(message: str) -> None:
    print(f"Error: {message}", file=sys.stderr)
    raise SystemExit(1)


def run(command: list[str], cwd: Path | None = None) -> None:
    subprocess.run(command, cwd=cwd, check=True)


def copy_children(source: Path, target: Path) -> None:
    target.mkdir(parents=True, exist_ok=True)
    for item in source.iterdir():
        destination = target / item.name
        if item.is_dir():
            shutil.copytree(item, destination, dirs_exist_ok=True)
        else:
            shutil.copy2(item, destination)


def remove_target_items() -> None:
    for item_name in PROTECTED_ITEMS:
        path = TARGET_DIR / item_name
        if path.is_dir():
            shutil.rmtree(path)
        elif path.exists():
            path.unlink()


def extract_local_extension(local_ext: Path) -> str:
    lines = local_ext.read_text(encoding="utf-8").splitlines()
    try:
        start = lines.index("## 插入內容") + 1
    except ValueError:
        fail("找不到 local_extensions.md 的「## 插入內容」區塊，無法套用本地擴充。")

    insert_content = "\n".join(lines[start:]).strip("\n")
    if not insert_content.strip():
        fail("local_extensions.md 的「## 插入內容」區塊沒有可插入內容，無法套用本地擴充。")
    return insert_content


def apply_local_extension() -> None:
    local_ext = TARGET_DIR / "evals" / "local_extensions.md"
    if not local_ext.is_file():
        return

    skill_md = TARGET_DIR / "SKILL.md"
    insert_content = extract_local_extension(local_ext)
    skill_content = skill_md.read_text(encoding="utf-8")
    anchor_index = skill_content.find(ANCHOR)
    if anchor_index < 0:
        fail(f"找不到 SKILL.md 錨點：{ANCHOR}，無法套用本地擴充。")

    end_of_line = skill_content.find("\n", anchor_index)
    if end_of_line < 0:
        end_of_line = len(skill_content)

    updated = skill_content[: end_of_line + 1] + "\n" + insert_content + "\n" + skill_content[end_of_line + 1 :]
    skill_md.write_text(updated, encoding="utf-8", newline="\n")

    checks = {
        "evals/run_evals_bdd.py": "本地擴充未成功插入 SKILL.md。",
        "本地規則：Codex eval runner": "本地擴充缺少 Codex eval runner 本地規則。",
        "--dangerously-bypass-approvals-and-sandbox": "本地擴充缺少 Codex bypass sandbox 參數。",
    }
    for pattern, message in checks.items():
        if pattern not in updated:
            fail(message)

    print(">>> 已套用本地擴充 (local_extensions.md)")


def patch_skill_md(content: str, old: str, new: str, name: str) -> str:
    old_norm = old.replace("\r\n", "\n")
    if old_norm not in content:
        raise SystemExit(
            f"Patch [{name}] 失敗：找不到目標字串，官方 SKILL.md 可能已更動，請確認此 patch 是否仍適用。"
        )
    return content.replace(old_norm, new.replace("\r\n", "\n"))


def apply_patches() -> None:
    skill_md = TARGET_DIR / "SKILL.md"
    if not skill_md.is_file():
        return

    print(">>> 套用本地 patches...")
    content = skill_md.read_text(encoding="utf-8").replace("\r\n", "\n")

    # Patch 1: evals.json 範例移除 expected_output / files，補 name + expectations
    content = patch_skill_md(
        content,
        """\
    {
      "id": 1,
      "prompt": "User's task prompt",
      "expected_output": "Description of expected result",
      "files": []
    }
""",
        """\
    {
      "id": 1,
      "name": "descriptive-eval-name",
      "prompt": "User's task prompt",
      "expectations": []
    }
""",
        "evals.json 範例欄位",
    )

    # Patch 2: schema 備註 assertions → expectations
    content = patch_skill_md(
        content,
        "See `references/schemas.md` for the full schema (including the `assertions` field, which you'll add later).",
        "See `references/schemas.md` for the full schema (including the `expectations` field, which you'll fill in later).",
        "schema 備註術語",
    )

    # Patch 3: Step 1 標題 + 說明，移除 Baseline run 區塊
    content = patch_skill_md(
        content,
        """\
### Step 1: Spawn all runs (with-skill AND baseline) in the same turn

For each test case, spawn two subagents in the same turn — one with the skill, one without. This is important: don't spawn the with-skill runs first and then come back for baselines later. Launch everything at once so it all finishes around the same time.

**With-skill run:**

```
Execute this task:
- Skill path: <path-to-skill>
- Task: <eval prompt>
- Input files: <eval files if any, or "none">
- Save outputs to: <workspace>/iteration-<N>/eval-<ID>/with_skill/outputs/
- Outputs to save: <what the user cares about — e.g., "the .docx file", "the final CSV">
```

**Baseline run** (same prompt, but the baseline depends on context):
- **Creating a new skill**: no skill at all. Same prompt, no skill path, save to `without_skill/outputs/`.
- **Improving an existing skill**: the old version. Before editing, snapshot the skill (`cp -r <skill-path> <workspace>/skill-snapshot/`), then point the baseline subagent at the snapshot. Save to `old_skill/outputs/`.
""",
        """\
### Step 1: Spawn all with-skill runs in the same turn

For each test case, spawn one subagent with the skill. Launch all of them at once so they finish around the same time.

**With-skill run:**

```
Execute this task:
- Skill path: <path-to-skill>
- Task: <eval prompt>
- Input files: <eval files if any, or "none">
- Save outputs to: <workspace>/iteration-<N>/eval-<ID>/with_skill/outputs/
- Outputs to save: <what the user cares about — e.g., "the .docx file", "the final CSV">
```
""",
        "Step 1 with-skill only",
    )

    # Patch 4: Step 2 assertions → expectations，加 run_evals_bdd.py 執行指令
    content = patch_skill_md(
        content,
        """\
### Step 2: While runs are in progress, draft assertions

Don't just wait for the runs to finish — you can use this time productively. Draft quantitative assertions for each test case and explain them to the user. If assertions already exist in `evals/evals.json`, review them and explain what they check.

Good assertions are objectively verifiable and have descriptive names — they should read clearly in the benchmark viewer so someone glancing at the results immediately understands what each one checks. Subjective skills (writing style, design quality) are better evaluated qualitatively — don't force assertions onto things that need human judgment.

Update the `eval_metadata.json` files and `evals/evals.json` with the assertions once drafted. Also explain to the user what they'll see in the viewer — both the qualitative outputs and the quantitative benchmark.
""",
        """\
### Step 2: While runs are in progress, draft expectations

Don't just wait for the runs to finish — you can use this time productively. Draft quantitative expectations for each test case and explain them to the user. If expectations already exist in `evals/evals.json`, review them and explain what they check.

Good expectations are objectively verifiable and have descriptive names — they should read clearly in the benchmark viewer so someone glancing at the results immediately understands what each one checks. Subjective skills (writing style, design quality) are better evaluated qualitatively — don't force expectations onto things that need human judgment.

Update the workspace `eval_metadata.json` files with `assertions` (used by the grader subagent) and `evals/evals.json` with `expectations` (used by the BDD runner). Also explain to the user what they'll see in the viewer — both the qualitative outputs and the quantitative benchmark.

Once `expectations` are filled in and fixture directories populated, run the BDD runner to get a quantitative pass rate:

```bash
python evals/run_evals_bdd.py
```

This outputs `X/Y expectations passed` — the most direct quality metric per iteration.
""",
        "Step 2 expectations + BDD runner",
    )

    # Patch 5: benchmark delta
    content = patch_skill_md(
        content,
        """\
   This produces `benchmark.json` and `benchmark.md` with pass_rate, time, and tokens for each configuration, with mean ± stddev and the delta. If generating benchmark.json manually, see `references/schemas.md` for the exact schema the viewer expects.
Put each with_skill version before its baseline counterpart.
""",
        "   This produces `benchmark.json` and `benchmark.md` with pass_rate, time, and tokens for each test run. If generating benchmark.json manually, see `references/schemas.md` for the exact schema the viewer expects.\n",
        "benchmark delta",
    )

    # Patch 6: 迭代迴圈移除 including baseline runs
    content = patch_skill_md(
        content,
        "2. Rerun all test cases into a new `iteration-<N+1>/` directory, including baseline runs. If you're creating a new skill, the baseline is always `without_skill` (no skill) — that stays the same across iterations. If you're improving an existing skill, use your judgment on what makes sense as the baseline: the original version the user came in with, or the previous iteration.\n",
        "2. Rerun all test cases into a new `iteration-<N+1>/` directory with the updated skill.\n",
        "迭代迴圈 baseline",
    )

    # Patch 7: Claude.ai 移除 Skip baseline runs
    content = patch_skill_md(
        content,
        "**Running test cases**: No subagents means no parallel execution. For each test case, read the skill's SKILL.md, then follow its instructions to accomplish the test prompt yourself. Do them one at a time. This is less rigorous than independent subagents (you wrote the skill and you're also running it, so you have full context), but it's a useful sanity check — and the human review step compensates. Skip the baseline runs — just use the skill to complete the task as requested.\n",
        "**Running test cases**: No subagents means no parallel execution. For each test case, read the skill's SKILL.md, then follow its instructions to accomplish the task yourself. Do them one at a time. This is less rigorous than independent subagents (you wrote the skill and you're also running it, so you have full context), but it's a useful sanity check — and the human review step compensates.\n",
        "Claude.ai baseline",
    )

    # Patch 8: Claude.ai Benchmarking
    content = patch_skill_md(
        content,
        "**Benchmarking**: Skip the quantitative benchmarking — it relies on baseline comparisons which aren't meaningful without subagents. Focus on qualitative feedback from the user.\n",
        "**Benchmarking**: Skip the quantitative benchmarking — it requires subagents to run `run_evals_bdd.py`. Focus on qualitative feedback from the user.\n",
        "Claude.ai benchmarking",
    )

    # Patch 9: Cowork 移除 run baselines
    content = patch_skill_md(
        content,
        "- You have subagents, so the main workflow (spawn test cases in parallel, run baselines, grade, etc.) all works. (However, if you run into severe problems with timeouts, it's OK to run the test prompts in series rather than parallel.)\n",
        "- You have subagents, so the main workflow (spawn test cases in parallel, grade, etc.) all works. (However, if you run into severe problems with timeouts, it's OK to run the test prompts in series rather than parallel.)\n",
        "Cowork baseline",
    )

    skill_md.write_text(content, encoding="utf-8", newline="\n")

    if "without_skill/outputs" in content:
        raise SystemExit(
            "Patch 驗證失敗：SKILL.md 仍含 'without_skill/outputs'，請檢查 Step 1 patch 是否仍匹配官方 SKILL.md。"
        )
    if "python evals/run_evals_bdd.py" not in content:
        raise SystemExit(
            "Patch 驗證失敗：SKILL.md 缺少 BDD runner 執行指令，Step 2 patch 可能失敗。"
        )

    print(">>> 已套用本地 patches (9 項)")


def main() -> int:
    print(">>> 拉取最新 skill-creator...")
    with tempfile.TemporaryDirectory() as temp_dir, tempfile.TemporaryDirectory() as evals_backup_dir:
        temp_path = Path(temp_dir)
        evals_backup = Path(evals_backup_dir)

        run(["git", "clone", "--depth=1", "--filter=blob:none", "--sparse", REPO_URL, str(temp_path), "--quiet"])
        run(["git", "sparse-checkout", "set", str(SKILL_PATH).replace("\\", "/")], cwd=temp_path)

        print(f">>> 覆蓋本地 {TARGET_DIR} ...")
        evals_dir = TARGET_DIR / "evals"
        if evals_dir.is_dir():
            copy_children(evals_dir, evals_backup)

        remove_target_items()
        copy_children(temp_path / SKILL_PATH, TARGET_DIR)

        if evals_dir.exists():
            shutil.rmtree(evals_dir)
        (evals_dir / "files").mkdir(parents=True, exist_ok=True)
        if any(evals_backup.iterdir()):
            copy_children(evals_backup, evals_dir)

    apply_local_extension()
    apply_patches()
    print(">>> 完成！skill-creator 已更新至最新版本。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
