#!/usr/bin/env python3
"""
==============================================================
 eval 結構驗證工具 — validate_structure.py
==============================================================

【用途】
  靜態驗證各 skill 的 run_evals_bdd.py 與對應 fixture 結構
  是否符合 eval-test/MAINTENANCE.md 所定義的維護風格。

  驗證項目：
    - run_evals_bdd.py 是否存在
    - run_evals_bdd.py 是否通過 Python 語法檢查
    - run_evals_bdd.py 採用 ThreadPoolExecutor 完全並行架構
    - run_evals_bdd.py 含 Windows UTF-8 re-exec 邏輯（PYTHONUTF8）
    - evals.json 是否存在且每個 eval 含 expectations 欄位
    - 每個 eval 的 fixtures/eval-<id>/staged/ 是否存在

  skill-creator-plus 額外驗證（指定 skill-creator-patches）：
    - SKILL.md 的 9 個本地 patch 是否仍有效套用
    - 本地擴充（local_extensions.md）是否正確注入 SKILL.md
    - frontmatter name 是否維持本地 `skill-creator-plus`

【使用時機】
  - 修改任何 skill 的 run_evals_bdd.py 之後
  - 新增 skill 並建立 run_evals_bdd.py 之後
  - 執行 update-skill-creator.py 之後（驗證 patch 仍有效）
  - MAINTENANCE.md 規範有異動，想確認所有腳本仍對齊時
  - CI/CD 流程中作為結構回歸測試

【使用方式】
  # 驗證全部 skill（eval 結構）
  python skill-creator-plus/eval-test/validate_structure.py

  # 只驗證單一 skill
  python skill-creator-plus/eval-test/validate_structure.py code-reviewer

  # 驗證 skill-creator 的 9 個 patch 是否有效
  python skill-creator-plus/eval-test/validate_structure.py skill-creator-patches

【退出碼】
  0 = 全部通過
  1 = 至少一個 skill 不符合結構規範
==============================================================
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
SKILLS_DIR = SCRIPT_DIR.parent.parent  # eval-test/ → skill-creator/ → skills/

SKILLS = [
    "apply",
    "code-reviewer",
    "propose",
    "propose-sync",
    "llm-repo",
    "writing-training-doc",
    "fleet-review",
    "skill-creator-plus",
]


# ---------- validators ----------

def validate_skill_creator_patches(errors: list[str]) -> None:
    """驗證 skill-creator-plus SKILL.md 的 9 個本地 patch 與本地擴充是否正確套用。"""
    skill_md = SKILLS_DIR / "skill-creator-plus" / "SKILL.md"
    if not skill_md.exists():
        errors.append("skill-creator-plus/SKILL.md not found")
        return

    content = skill_md.read_text(encoding="utf-8")
    lines = content.splitlines()

    if not any(line.strip() == "name: skill-creator-plus" for line in lines):
        errors.append("本地 metadata 失效：SKILL.md frontmatter 缺少 name: skill-creator-plus")
    if any(line.strip() == "name: skill-creator" for line in lines):
        errors.append("本地 metadata 失效：SKILL.md frontmatter 仍為官方 name: skill-creator")

    # 不應出現的字串（patch 應已移除）
    absent = [
        (
            "without_skill/outputs",
            "Patch 3 失效：仍含 without_skill/outputs（baseline run 未移除）",
        ),
        (
            '"expected_output"',
            "Patch 1 失效：evals.json 範例仍含 expected_output 欄位",
        ),
        (
            "including baseline runs",
            "Patch 6 失效：迭代迴圈仍含 including baseline runs",
        ),
        (
            "Skip the baseline runs",
            "Patch 7 失效：Claude.ai 說明仍含 Skip the baseline runs",
        ),
        (
            "run baselines, grade",
            "Patch 9 失效：Cowork 說明仍含 run baselines, grade",
        ),
    ]

    # 應出現的字串（patch 或本地擴充應已補入）
    present = [
        (
            '"expectations": []',
            "Patch 1/2 失效：evals.json 範例缺少 expectations 欄位",
        ),
        (
            "python evals/run_evals_bdd.py",
            "Patch 4 失效：Step 2 缺少 BDD runner 執行指令",
        ),
        (
            "requires subagents to run `run_evals_bdd.py`",
            "Patch 8 失效：Claude.ai benchmarking 說明未更新為 BDD runner 原因",
        ),
        (
            "do this proactively even if the user only asks for eval tests",
            "本地擴充失效：缺少 run_evals_bdd.py 自動產出的 proactive 指令",
        ),
        (
            "預設不得指定或新增 `--jobs`",
            "本地擴充失效：缺少 BDD runner 預設全並行執行規則",
        ),
    ]

    for pattern, message in absent:
        if pattern in content:
            errors.append(message)

    for pattern, message in present:
        if pattern not in content:
            errors.append(message)

def validate_runner_content(script_path: Path, errors: list[str]) -> None:
    """驗證 run_evals_bdd.py 採用完全並行架構（ThreadPoolExecutor(max_workers=len(...))）。"""
    content = script_path.read_text(encoding="utf-8", errors="replace")

    required = [
        (
            "ThreadPoolExecutor",
            "run_evals_bdd.py 缺少 ThreadPoolExecutor（未使用並行架構）",
        ),
        (
            "max_workers=len(",
            "run_evals_bdd.py 未使用 max_workers=len(evals) 完全並行模式",
        ),
        (
            "PYTHONUTF8",
            "run_evals_bdd.py 缺少 Windows UTF-8 re-exec 邏輯（PYTHONUTF8），Windows cp950 終端機將無法正確輸出中文",
        ),
    ]

    for pattern, message in required:
        if pattern not in content:
            errors.append(message)


def validate_syntax(script_path: Path, errors: list[str]) -> bool:
    result = subprocess.run(
        [sys.executable, "-m", "py_compile", str(script_path)],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        errors.append(f"syntax error: {result.stderr.strip()}")
        return False
    return True


def validate_evals_json(evals_json: Path, fixtures_dir: Path, errors: list[str]) -> None:
    if not evals_json.exists():
        errors.append("evals.json not found")
        return

    try:
        data = json.loads(evals_json.read_text(encoding="utf-8"))
    except Exception as exc:
        errors.append(f"evals.json parse error: {exc}")
        return

    evals = data.get("evals", [])
    if not evals:
        errors.append("evals.json has no eval cases")
        return

    for i, eval_case in enumerate(evals):
        eval_id = eval_case.get("id", i)
        label = f"eval-{eval_id}"

        if not eval_case.get("expectations"):
            errors.append(f"{label}: missing or empty expectations field")

        staged_dir = fixtures_dir / f"eval-{eval_id}" / "staged"
        if not staged_dir.exists():
            errors.append(f"{label}: fixtures/eval-{eval_id}/staged/ not found")


# ---------- main ----------

def main() -> int:
    target = sys.argv[1] if len(sys.argv) > 1 else None

    # skill-creator-patches 是獨立模式，只驗證 SKILL.md patch 套用結果
    if target == "skill-creator-patches":
        print("=== skill-creator-plus patch validator ===")
        print("Checking 9 local patches + local extension in skill-creator-plus/SKILL.md")
        print()
        errors: list[str] = []
        validate_skill_creator_patches(errors)
        if errors:
            print("  FAIL    skill-creator-patches")
            for msg in errors:
                print(f"           x {msg}")
            print()
            print("One or more patches failed.", file=sys.stderr)
            return 1
        print("  PASS    skill-creator-patches")
        print()
        print("All patches conform to skill-creator-plus/evals/MAINTENANCE.md.")
        return 0

    skills = [target] if target else SKILLS

    unknown = [s for s in skills if s not in SKILLS]
    if unknown:
        print(f"Error: unknown skill(s): {unknown}", file=sys.stderr)
        print(f"Available: {SKILLS} + skill-creator-patches")
        return 1

    print("=== eval structure conformance validator ===")
    print(f"Checking {len(skills)} skill(s) against MAINTENANCE.md style")
    print()

    col = max(len(s) for s in skills)
    all_passed = True

    for skill in skills:
        script_path = SKILLS_DIR / skill / "evals" / "run_evals_bdd.py"

        if not script_path.exists():
            print(f"  {'SKIP':<6}  {skill:<{col}}  (run_evals_bdd.py not found)")
            continue

        errors = []

        if validate_syntax(script_path, errors):
            validate_runner_content(script_path, errors)
            evals_json = SKILLS_DIR / skill / "evals" / "evals.json"
            fixtures_dir = SKILLS_DIR / skill / "evals" / "fixtures"
            validate_evals_json(evals_json, fixtures_dir, errors)

        passed = len(errors) == 0
        status = "PASS" if passed else "FAIL"
        print(f"  {status:<6}  {skill}")
        for msg in errors:
            print(f"           x {msg}")

        if not passed:
            all_passed = False

    print()
    if all_passed:
        print("All skills conform to MAINTENANCE.md structure.")
    else:
        print("One or more skills failed structure validation.", file=sys.stderr)

    return 0 if all_passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
