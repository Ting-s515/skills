propose 已完成，使用後端路徑 `backend/docs/propose/`。

【Bug Fix — quick-fix 直接實作】
- 商品列表每頁顯示筆數寫死 10，應改為可設定（預設 20）
- 新增商品成功後 toast 訊息顯示「刪除成功」，文字應為「新增成功」

【Bug Fix — 走 propose 流程】
- `backend/docs/propose/fix-order-batch-update-rollback/`
  - `01-flow.md`
  - `02-gherkin.md`
  - `03-tasks.md`
- `backend/docs/propose/fix-product-search-special-character-sql/`
  - `01-flow.md`
  - `02-gherkin.md`
  - `03-tasks.md`

無標記的 SQL 特殊字元 bug 已自動歸類為 propose，理由是它涉及後端查詢 escape、參數化查詢與 API 錯誤行為，屬於可能有 side effect 的資料流修正。

已回寫規格標記到 `propose/evals/files/spec-bugfix.md`。本次只變更 Markdown 文件，code review 與 build 驗證跳過；依 eval 規則未執行 git commit。

產生的 commit message 如下，但未提交：

```text
docs: 新增後端 bugfix propose 文件

規格中的後端 bug fix 清單包含 quick-fix 與需設計的修正項目，需先完成分流並為較高風險問題建立可後續 apply 的實作提案。

本次調整：
- 將分頁設定與 toast 文字問題保留為 quick-fix 直接實作項目，不建立 propose folder
- 為訂單狀態批次更新 transaction rollback 問題建立 fix-order-batch-update-rollback 提案文件
- 將商品搜尋 SQL 特殊字元 500 問題自動歸類為 propose，並建立 fix-product-search-special-character-sql 提案文件
- 回寫 spec-bugfix.md 的 propose 路徑標記
```

---
## Grading
E1: PASS - 輸出將「商品列表每頁顯示筆數寫死 10」與「新增商品成功後 toast 訊息」列在【Bug Fix — quick-fix 直接實作】，且未建立對應 feature folder
E2: PASS - 已建立 `backend/docs/propose/fix-order-batch-update-rollback/`，包含 `01-flow.md`、`02-gherkin.md`、`03-tasks.md` 三份文件
E3: PASS - SQL 特殊字元 bug 無標記，已自動歸類為 propose，理由是涉及查詢 escape、參數化查詢與 API 錯誤行為
E4: PASS - 輸出以【Bug Fix — quick-fix 直接實作】與【Bug Fix — 走 propose 流程】分段呈現分流結果