#!/usr/bin/env python3
"""
==============================================================
 eval 結構驗證工具 — validate_structure.py
==============================================================

【用途】
  驗證各 skill 的 run_evals.py 在執行後，產出的目錄與檔案結構
  是否符合 eval-test/MAINTENANCE.md 所定義的維護風格。

  不依賴文檔人工比對，改以程式自動執行 --dry-run 並檢查：
    - iteration-N/ 目錄是否建立
    - benchmark.json 欄位是否齊備
    - 每個 eval case 的 eval_metadata.json、with_skill/、without_skill/ 是否存在
    - timing.json、output.log、last-message.md 是否齊備
    - eval 目錄名是否為純 <eval-name>（無 id 前綴）

【使用時機】
  - 修改任何 skill 的 run_evals.py 之後
  - 新增 skill 並建立 run_evals.py 之後
  - MAINTENANCE.md 規範有異動，想確認所有腳本仍對齊時
  - CI/CD 流程中作為結構回歸測試

【使用方式】
  # 驗證全部 skill
  python eval-test/validate_structure.py

  # 只驗證單一 skill
  python eval-test/validate_structure.py propose

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
import tempfile
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
SKILLS_DIR = SCRIPT_DIR.parent

SKILLS = [
    "apply",
    "propose",
    "propose-sync",
    "llm-repo",
    "writing-training-doc",
    "fleet-review",
]

REQUIRED_TIMING_FIELDS = {
    "start", "end", "duration_seconds", "exit_code", "timed_out", "timeout_setting",
}
REQUIRED_METADATA_FIELDS = {
    "eval_id", "name", "prompt", "configurations", "workspace_path",
}
REQUIRED_BENCHMARK_FIELDS = {
    "iteration", "skill_name", "timestamp",
    "total", "passed", "failed", "timeout", "results",
}


# ---------- helpers ----------

def err(errors: list[str], msg: str) -> None:
    errors.append(msg)


def safe_name(value: str) -> str:
    allowed = []
    for char in value.lower():
        if char.isalnum() or char in ("-", "_"):
            allowed.append(char)
        elif char.isspace():
            allowed.append("-")
    return "".join(allowed).strip("-_") or "eval"


def load_json(path: Path, errors: list[str]) -> dict | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        err(errors, f"{path.name} parse error: {exc}")
        return None


# ---------- validators ----------

def validate_timing(timing_path: Path, config: str, errors: list[str]) -> None:
    if not timing_path.exists():
        err(errors, f"{config}/timing.json missing")
        return
    data = load_json(timing_path, errors)
    if data is None:
        return
    missing = REQUIRED_TIMING_FIELDS - data.keys()
    if missing:
        err(errors, f"{config}/timing.json missing fields: {sorted(missing)}")


def validate_config_dir(run_dir: Path, config: str, errors: list[str]) -> None:
    if not run_dir.is_dir():
        err(errors, f"{config}/ directory missing")
        return
    for fname in ("output.log", "last-message.md"):
        if not (run_dir / fname).exists():
            err(errors, f"{config}/{fname} missing")
    validate_timing(run_dir / "timing.json", config, errors)


def validate_eval_dir(eval_dir: Path, errors: list[str]) -> None:
    label = eval_dir.name

    # eval_metadata.json
    metadata_path = eval_dir / "eval_metadata.json"
    if not metadata_path.exists():
        err(errors, f"[{label}] eval_metadata.json missing")
        return

    metadata = load_json(metadata_path, errors)
    if metadata is None:
        return

    missing = REQUIRED_METADATA_FIELDS - metadata.keys()
    if missing:
        err(errors, f"[{label}] eval_metadata.json missing fields: {sorted(missing)}")

    # dir name must match safe_name(name) — no id prefix
    expected_dir_name = safe_name(metadata.get("name", ""))
    if expected_dir_name and eval_dir.name != expected_dir_name:
        err(errors, (
            f"[{label}] dir name mismatch: expected '{expected_dir_name}', "
            f"got '{eval_dir.name}' (possible id prefix)"
        ))

    # each declared configuration must have a valid run dir
    configurations = metadata.get("configurations", [])
    if not configurations:
        err(errors, f"[{label}] eval_metadata.json has empty 'configurations'")
    for config in configurations:
        config_errors: list[str] = []
        validate_config_dir(eval_dir / config, config, config_errors)
        for msg in config_errors:
            err(errors, f"[{label}] {msg}")


def validate_iteration(iteration_dir: Path, errors: list[str]) -> None:
    # benchmark.json
    benchmark_path = iteration_dir / "benchmark.json"
    if not benchmark_path.exists():
        err(errors, "benchmark.json missing at iteration level")
    else:
        data = load_json(benchmark_path, errors)
        if data is not None:
            missing = REQUIRED_BENCHMARK_FIELDS - data.keys()
            if missing:
                err(errors, f"benchmark.json missing fields: {sorted(missing)}")

    # at least one eval case dir
    eval_dirs = [d for d in iteration_dir.iterdir() if d.is_dir()]
    if not eval_dirs:
        err(errors, "no eval case directories found under iteration dir")
        return

    for eval_dir in sorted(eval_dirs):
        validate_eval_dir(eval_dir, errors)


# ---------- runner ----------

def run_dry_run(skill: str, script_path: Path, output_dir: Path) -> tuple[bool, list[str]]:
    errors: list[str] = []

    cmd = [
        sys.executable, str(script_path),
        "--dry-run",
        "--output-dir", str(output_dir),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        err(errors, f"script exited {result.returncode}")
        stderr = result.stderr.strip()
        if stderr:
            err(errors, f"stderr: {stderr}")
        return False, errors

    # locate the iteration dir that was just created
    iteration_dirs = sorted(
        (
            d for d in output_dir.iterdir()
            if d.is_dir()
            and d.name.startswith("iteration-")
            and d.name.removeprefix("iteration-").isdigit()
        ),
        key=lambda d: int(d.name.removeprefix("iteration-")),
    )
    if not iteration_dirs:
        err(errors, "no iteration-N/ directory created")
        return False, errors

    validate_iteration(iteration_dirs[-1], errors)
    return len(errors) == 0, errors


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
        script_path = SKILLS_DIR / skill / "evals" / "run_evals.py"

        if not script_path.exists():
            print(f"  {'SKIP':<6}  {skill:<{col}}  (run_evals.py not found)")
            continue

        with tempfile.TemporaryDirectory() as tmp:
            output_dir = Path(tmp) / "eval-runs"
            passed, errors = run_dry_run(skill, script_path, output_dir)

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
