# Code Review 紀錄 — 2026-07-25（第 2 輪）

## 📋 Code Review 摘要

### Findings

本輪沒有發現 Critical 或 Warning findings。第 1 輪兩項問題均已修正。

**審查範圍：** `build-static-docs-site/evals/` 的 3 個回覆層 eval 情境、expectations、fixtures 與 BDD runner。
**整體評估：** ✅ 符合規格，可合併。

---

### 📐 規格符合度

#### ✅ 符合規格的項目

- 三案 prompt 均明確定義為回覆層情境測試，只要求說明具體作法、測試設計與驗證命令。
- 18 條 expectations 均限縮為 stdout 可直接判定的設計契約，不再將網站 artifact、測試、build 或 validator 宣稱為已實際完成。
- 三案都要求不得把未執行命令宣稱為成功；實際 eval 輸出亦清楚聲明未建立檔案、未執行命令且未宣稱驗證通過。
- eval 1 涵蓋專案識別、動態教材數量、build-time render、無 runtime fetch 及教材不變性驗證設計。
- eval 2 涵蓋相似檔名、Unicode canonical-equivalent、跨文件 fragment、Mermaid dialog 與 Escape／非 Escape 測試設計。
- eval 3 涵蓋既有站台窄範圍維護、移除固定專案內容、動態文件數量及保留客製 banner。
- 變更僅包含 eval runner、設定與 fixtures，未新增 workspace、grader、benchmark 或 viewer。
- `base/`、`staged/`、`spec/` 必要目錄完整；nested spec path 仍保留相對於 `spec/` 的完整路徑。
- Windows UTF-8 重啟與 Codex CLI 旗標維持正確。
- `expected_total` 現在於啟動 futures 前固定計算，Summary 與最終成功判定使用相同完整分母。
- timeout、nonzero exit、future exception、缺少結果或任何 expectation FAIL 都會使 runner 回傳非零 exit code。

#### ❌ 不符合或缺漏的項目

- 無。

---

### 🔴 必須修正（Critical）

無。

---

### 🟠 建議改善（Warning）

無。

---

### 驗證紀錄

- 完整 eval 結果：3 cases、18/18 PASS。
- AST、JSON 與 fixture 結構驗證：PASS。
- 儲存輸出重新解析：
  - eval 1：6/6 PASS
  - eval 2：6/6 PASS
  - eval 3：6/6 PASS
- future exception 注入：
  - 第二個 future 拋出例外。
  - Summary 正確維持 `1/2 expectations passed`。
  - runner 正確回傳 exit code 1。
- 第 1 輪 false-green finding：已透過回覆層測試定位及 expectations 限縮排除。
- 第 1 輪 Summary 分母 finding：已修正並以注入測試確認。

### Residual risks / testing gaps

- 這些案例刻意只驗證模型的回覆層設計判斷，不驗證真實網站 artifact 或命令執行；此限制已在 prompt 與 expectations 中清楚揭露，因此不構成本輪缺陷。
- runner 仍屬模型自評架構，結果可能受模型版本影響；目前與指定 reference runner 的定位一致。
- `--dangerously-bypass-approvals-and-sandbox` 只應在一次性工作區或外部隔離環境使用。
- `build-static-docs-site/eval-results-bdd/` 是執行產物，不在本次審查變更範圍內，提交時應避免納入。
