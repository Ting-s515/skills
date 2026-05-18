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
    - evals.json 是否存在且每個 eval 含 expectations 欄位
    - 每個 eval 的 fixtures/eval-<id>/staged/ 是否存在

【使用時機】
  - 修改任何 skill 的 run_evals_bdd.py 之後
  - 新增 skill 並建立 run_evals_bdd.py 之後
  - MAINTENANCE.md 規範有異動，想確認所有腳本仍對齊時
  - CI/CD 流程中作為結構回歸測試

【使用方式】
  # 驗證全部 skill
  python eval-test/validate_structure.py

  # 只驗證單一 skill
  python eval-test/validate_structure.py code-reviewer

  # 從專案根目錄執行（skills/）
  python eval-test/validate_structure.py llm-repo

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
SKILLS_DIR = SCRIPT_DIR.parent

SKILLS = [
    "apply",
    "code-reviewer",
    "propose",
    "propose-sync",
    "llm-repo",
    "writing-training-doc",
    "fleet-review",
    "skill-creator",
]


# ---------- validators ----------

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
    skills = [target] if target else SKILLS

    unknown = [s for s in skills if s not in SKILLS]
    if unknown:
        print(f"Error: unknown skill(s): {unknown}", file=sys.stderr)
        print(f"Available: {SKILLS}")
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

        errors: list[str] = []

        if validate_syntax(script_path, errors):
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
