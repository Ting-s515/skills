# Benchmark — Iteration 2

**時間：** 2026-03-26
**變更：**
- `propose` Step 1：invoke `clarify-flow` skill（原：讀取 SKILL.md）
- `propose` Step 2：invoke `export-gherkin` skill（原：inline 產出 Gherkin）
- `propose-sync` Step 1：從 `> propose:` 標記自動推斷掃描目錄（原：詢問前端/後端）

---

## 結果摘要

| eval | 說明 | assertions | 通過 | pass rate | 時間(s) | tokens |
|------|------|-----------|------|-----------|---------|--------|
| 1 | propose 新功能 | 3 | 3 | 100% | 278.2 | 44,838 |
| 2 | propose bugfix 分流 | 3 | 3 | 100% | 165.8 | 28,598 |
| 3 | propose 回寫標記 | 3 | 3 | 100% | 251.2 | 42,022 |
| 4 | propose bugfix 回寫 | 2 | 2 | 100% | 153.9 | 27,731 |
| 7 | propose-sync 部分完成 | 4 | 4 | 100% | 67.4 | 16,604 |
| 8 | propose-sync 建立區塊 | 2 | 2 | 100% | 58.9 | 14,846 |
| **合計** | | **17** | **17** | **100%** | | |

eval 5、6（apply skill）未修改，沿用 iteration-1 結果。

---

## 分析

### 功能正確性
所有 assertions 全數通過，三個技能改動均正確執行：
- `propose` invoke `clarify-flow`：結構化流程品質一致
- `propose` invoke `export-gherkin`：Gherkin 產出符合沙漏原則
- `propose-sync` 自動推斷路徑：正確識別 `docs/propose/` 前綴

### Token 消耗觀察
propose 類 eval（1-4）平均 token 比 iteration-1 增加約 20-30%。
原因：invoke skill 需額外讀取 clarify-flow/SKILL.md 和 export-gherkin/SKILL.md，增加約 5,000-10,000 token 上下文。
這是預期的取捨：**準確性換取效率**，以正確 invoke 機制取代自行解讀 skill 規則的不確定性。

propose-sync 類 eval（7-8）token 低且穩定（14K-16K），
自動推斷路徑的邏輯不增加 token 消耗，且省去一輪使用者確認的互動。
