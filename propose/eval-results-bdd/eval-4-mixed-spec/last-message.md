已完成 propose，未等待確認，使用後端路徑 `backend/docs/propose/`。

跳過項目：
- `使用者認證`、`權限管理`：已列在 `## 已完成`
- `商品管理`、`訂單管理`：已存在 `> propose:` 標記
- `登入頁面 Enter 鍵無法送出表單`：列為 `[quick-fix]` 直接實作清單，未建立 folder

已建立：
- `backend/docs/propose/report-export/01-flow.md`
- `backend/docs/propose/report-export/02-gherkin.md`
- `backend/docs/propose/report-export/03-tasks.md`
- `backend/docs/propose/fix-concurrent-inventory-race-condition/01-flow.md`
- `backend/docs/propose/fix-concurrent-inventory-race-condition/02-gherkin.md`
- `backend/docs/propose/fix-concurrent-inventory-race-condition/03-tasks.md`

已回寫 `propose/evals/files/spec-mixed.md`：
- `報表匯出` 新增 `> propose: backend/docs/propose/report-export/`
- 並發庫存 bug 新增 `> propose: backend/docs/propose/fix-concurrent-inventory-race-condition/`

Workflow Gate：
- 本次變更僅 Markdown 文件，跳過 build。
- 本次變更僅文檔檔案，跳過 code review。
- 未執行 git commit，原因：eval 規則明確要求「不要執行 git commit」，且此 workspace 不是 git repository。
- 產生的 commit message：

```text
docs: 新增後台報表匯出與庫存併發修正提案

規格文件中仍有尚未提案的報表匯出需求，以及需要走 propose 流程的並發庫存扣減問題；已完成與已標記提案的功能需避免重複建立文檔。

本次調整：
- 為報表匯出建立 flow、Gherkin 與 tasks 三份提案文檔
- 為並發下單庫存 race condition 建立修正後行為的提案文檔
- 回寫規格文件中的 propose 標記，保留 quick-fix bug 為直接實作項目
```

---
## Grading
E1: PASS - `## 已完成` 表格包含 `使用者認證` 與 `權限管理`，本次結果明確列為跳過。
E2: PASS - `商品管理` 與 `訂單管理` 原規格已有 `> propose:` 標記，本次結果明確列為跳過。
E3: PASS - 已建立 `backend/docs/propose/report-export/01-flow.md`、`02-gherkin.md`、`03-tasks.md`。
E4: PASS - `登入頁面 Enter 鍵無法送出表單` 保留為 `[quick-fix]` 直接實作項目，未建立 folder。
E5: PASS - 已建立 `backend/docs/propose/fix-concurrent-inventory-race-condition/`，包含三份 propose 文檔。