#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

from fleet_review_harness import (
    GREEN,
    RED,
    NC,
    Tracker,
    assert_contains,
    assert_exit_zero,
    assert_not_contains,
    run_fleet_review,
)


SCRIPT_DIR = Path(__file__).resolve().parent
FIXTURES = SCRIPT_DIR / "fixtures"
RESULTS_DIR = SCRIPT_DIR / "results"


def main() -> int:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    tracker = Tracker()

    print()
    print("TC-01: calculator-bugs（應找到 2 個 P1 問題）")
    print("────────────────────────────────────────────")

    tc01_output = RESULTS_DIR / "tc01-bugs.txt"
    tc01_exit = run_fleet_review(FIXTURES / "calculator-bugs.patch", FIXTURES / "spec.md", tc01_output)
    output01 = tc01_output.read_text(encoding="utf-8", errors="replace")

    assert_exit_zero(tracker, "測試函式執行成功（exit 0）", tc01_exit)
    assert_not_contains(tracker, "Claude 未跳過", "CLAUDE_SKIPPED:", output01)
    assert_not_contains(tracker, "Claude 未失敗", "CLAUDE_FAILED", output01)
    assert_contains(tracker, "Claude 記錄 agent model", "AGENT_MODEL:", output01)
    assert_contains(tracker, "至少一個 FINDING", "FINDING:", output01)
    assert_contains(tracker, "偵測到 add() 問題", "add", output01)
    assert_contains(tracker, "偵測到 divide() 問題", "divide", output01)
    assert_contains(tracker, "P1 嚴重度存在", "P1", output01)
    assert_contains(tracker, "Codex 記錄 requested model", "CODEX_REQUESTED_MODEL: gpt-5.5", output01)
    assert_contains(tracker, "輸出原始發現摘要", "艦隊審查 — 原始發現", output01)
    assert_contains(tracker, "輸出最終報告", "艦隊審查 — 最終報告", output01)
    assert_contains(tracker, "基礎分支顯示 main", "基礎分支：main", output01)
    assert_contains(tracker, "顯示 Diff 來源", "Diff 來源：fixture patch: calculator-bugs.patch", output01)
    assert_contains(tracker, "顯示代理原始回報", "代理原始回報：", output01)
    assert_contains(tracker, "去重後問題為 2 個", "去重後問題：2 個", output01)
    assert_contains(tracker, "兩個核心問題皆雙代理確認", "雙代理確認：2 個，單代理發現：0 個", output01)
    assert_contains(tracker, "輸出註解類 P3 區塊", "使用者自行決定（註解類 P3）", output01)
    assert_not_contains(tracker, "一般輸出不顯示模型來源", "CODEX_MODEL_SOURCE:", output01)
    assert_not_contains(tracker, "Codex 未失敗", "CODEX_FAILED", output01)

    print()
    print("TC-02: calculator-clean（應回報 NO_FINDINGS）")
    print("────────────────────────────────────────────")

    tc02_output = RESULTS_DIR / "tc02-clean.txt"
    tc02_exit = run_fleet_review(FIXTURES / "calculator-clean.patch", FIXTURES / "spec.md", tc02_output)
    output02 = tc02_output.read_text(encoding="utf-8", errors="replace")

    assert_exit_zero(tracker, "測試函式執行成功（exit 0）", tc02_exit)
    assert_not_contains(tracker, "Claude 未跳過", "CLAUDE_SKIPPED:", output02)
    assert_not_contains(tracker, "Claude 未失敗", "CLAUDE_FAILED", output02)
    assert_contains(tracker, "Claude 記錄 agent model", "AGENT_MODEL:", output02)
    assert_contains(tracker, "回報 NO_FINDINGS", "NO_FINDINGS", output02)
    assert_not_contains(tracker, "不應有 P0/P1", "severity: P0", output02)
    assert_not_contains(tracker, "不應有 P0/P1", "severity: P1", output02)
    assert_contains(tracker, "Codex 記錄 requested model", "CODEX_REQUESTED_MODEL: gpt-5.5", output02)
    assert_contains(tracker, "輸出原始發現摘要", "艦隊審查 — 原始發現", output02)
    assert_contains(tracker, "輸出最終報告", "艦隊審查 — 最終報告", output02)
    assert_contains(tracker, "基礎分支顯示 main", "基礎分支：main", output02)
    assert_contains(tracker, "顯示 Diff 來源", "Diff 來源：fixture patch: calculator-clean.patch", output02)
    assert_contains(tracker, "去重後問題為 0 個", "去重後問題：0 個", output02)
    assert_contains(tracker, "無雙代理確認或單代理發現", "雙代理確認：0 個，單代理發現：0 個", output02)
    assert_contains(tracker, "輸出審查通過", "審查通過", output02)
    assert_not_contains(tracker, "一般輸出不顯示模型來源", "CODEX_MODEL_SOURCE:", output02)
    assert_not_contains(tracker, "Codex 未失敗", "CODEX_FAILED", output02)

    print()
    print("════════════════════════════════════════════")
    print(f"測試結果：{tracker.pass_count}/{tracker.total_count} 通過，{tracker.fail_count} 失敗")
    print(f"輸出目錄：{RESULTS_DIR}")
    print("════════════════════════════════════════════")

    if tracker.fail_count == 0:
        print(f"{GREEN}ALL TESTS PASSED{NC}")
        return 0

    print(f"{RED}{tracker.fail_count} TEST(S) FAILED{NC}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
