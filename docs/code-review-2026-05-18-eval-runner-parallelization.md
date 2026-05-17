# Code Review 紀錄 — 2026-05-18（第 1 輪）

## 📋 Code Review 摘要

**審查範圍：** `apply`、`propose`、`propose-sync`、`llm-repo`、`fleet-review`、`writing-training-doc` 的 `evals/run_evals.py`
**整體評估：** ✅ 符合需求可合併

---

### 🔴 必須修正（Critical）

未發現必須修正問題。

---

### 🟠 建議改善（Warning）

未發現建議改善問題。

---

### 🔵 型別安全

#### ✅ 符合項目
- `prepare_eval_case_metadata` 與 `run_eval_config` 的參數與回傳型別維持明確標註。
- `failed_result` 新增 `config` 參數後，錯誤結果會落在實際失敗的 configuration 目錄，不再固定歸類為 `with_skill`。

---

### ⚪ 使用者自行決定（註解類問題）

未發現新增 TODO、FIXME、被註解掉的程式碼或暫時偵錯註解。

---

### 審查結論

本次調整已將 6 個 runner 的並行單位從 eval case 對齊為實際 run，也就是 `(eval case, configuration)`。`with_skill` 與 `without_skill` 會展平成獨立 task 後交給 `ThreadPoolExecutor`，`--jobs` 也改為限制實際 run 數，符合「完全並行所有 run，等待最慢回應完成」的需求。
