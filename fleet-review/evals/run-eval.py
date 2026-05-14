#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
sys.path.insert(0, str(SKILL_DIR / "test"))

from fleet_review_harness import (  # noqa: E402
    GREEN,
    RED,
    NC,
    Tracker,
    assert_contains,
    assert_contains_any,
    assert_not_contains,
    run_fleet_review,
)


FIXTURES = SKILL_DIR / "test" / "fixtures"
RESULTS_DIR = SCRIPT_DIR / "results"


def main() -> int:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    tracker = Tracker()

    print()
    print("EVAL-01: calculator-bugs（應輸出艦隊審查最終報告，含 P1 發現）")
    print("────────────────────────────────────────────")

    eval01_output = RESULTS_DIR / "eval01-bugs.txt"
    run_fleet_review(FIXTURES / "calculator-bugs.patch", FIXTURES / "spec.md", eval01_output)
    output01 = eval01_output.read_text(encoding="utf-8", errors="replace")

    assert_contains(tracker, "輸出艦隊審查報告標頭", "艦隊審查", output01)
    assert_contains(tracker, "輸出步驟 3 最終報告", "最終報告", output01)
    assert_contains(tracker, "偵測到 add() 邏輯錯誤", "add", output01)
    assert_contains(tracker, "偵測到 divide() 缺除零", "divide", output01)
    assert_contains(tracker, "存在 P1 嚴重度", "P1", output01)
    assert_contains(tracker, "Codex 使用 gpt-5.5", "gpt-5.5", output01)
    assert_contains(tracker, "基礎分支顯示 main", "基礎分支：main", output01)
    assert_contains(tracker, "顯示 Diff 來源", "Diff 來源：", output01)
    assert_contains(tracker, "去重後問題為 2 個", "去重後問題：2 個", output01)
    assert_contains(tracker, "兩個核心問題皆雙代理確認", "雙代理確認：2 個，單代理發現：0 個", output01)
    assert_not_contains(tracker, "不顯示 debug 模型來源", "CODEX_MODEL_SOURCE:", output01)
    assert_not_contains(tracker, "Codex 未失敗", "CODEX_FAILED", output01)

    print()
    print("EVAL-02: calculator-clean（應回報審查通過或 NO_FINDINGS）")
    print("────────────────────────────────────────────")

    eval02_output = RESULTS_DIR / "eval02-clean.txt"
    run_fleet_review(FIXTURES / "calculator-clean.patch", FIXTURES / "spec.md", eval02_output)
    output02 = eval02_output.read_text(encoding="utf-8", errors="replace")

    assert_contains(tracker, "輸出艦隊審查報告標頭", "艦隊審查", output02)
    assert_contains_any(tracker, "回報審查通過或 NO_FINDINGS", "審查通過", "NO_FINDINGS", output02)
    assert_not_contains(tracker, "無 P0 問題", "severity: P0", output02)
    assert_not_contains(tracker, "無 P1 問題", "severity: P1", output02)
    assert_contains(tracker, "Codex 使用 gpt-5.5", "gpt-5.5", output02)
    assert_contains(tracker, "基礎分支顯示 main", "基礎分支：main", output02)
    assert_contains(tracker, "顯示 Diff 來源", "Diff 來源：", output02)
    assert_contains(tracker, "去重後問題為 0 個", "去重後問題：0 個", output02)
    assert_contains(tracker, "無雙代理確認或單代理發現", "雙代理確認：0 個，單代理發現：0 個", output02)
    assert_not_contains(tracker, "不顯示 debug 模型來源", "CODEX_MODEL_SOURCE:", output02)
    assert_not_contains(tracker, "Codex 未失敗", "CODEX_FAILED", output02)

    print()
    print("════════════════════════════════════════════")
    print(f"Eval 結果：{tracker.pass_count}/{tracker.total_count} 通過，{tracker.fail_count} 失敗")
    print(f"輸出目錄：{RESULTS_DIR}")
    print("════════════════════════════════════════════")

    if tracker.fail_count == 0:
        print(f"{GREEN}ALL EVALS PASSED{NC}")
        return 0

    print(f"{RED}{tracker.fail_count} EVAL(S) FAILED{NC}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
