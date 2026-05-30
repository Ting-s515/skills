propose 完成。

識別結果：
- 【新功能】1. 訂單管理：查看訂單列表、依狀態篩選、更新訂單狀態
- 【跳過】商品管理：已存在 `> propose: backend/docs/propose/product-management/` 標記

已建立：
- `backend/docs/propose/order-management/01-flow.md`
- `backend/docs/propose/order-management/02-gherkin.md`
- `backend/docs/propose/order-management/03-tasks.md`

已回寫規格：
- `propose/evals/files/spec-partial.md` 已在「訂單管理」下新增 `> propose: backend/docs/propose/order-management/`

驗證狀態：
- 本次只修改 Markdown 文件，build 與 code review 跳過。
- 依 eval 指示未執行 git commit。
- 工作區不是 git repository，因此 `git status` / `git diff --check` 無法執行。

---
## Grading
E1: PASS - 只處理一個新功能：訂單管理，輸出路徑為 `backend/docs/propose/order-management/`
E2: PASS - 商品管理已明確跳過，原因是已有 `> propose: backend/docs/propose/product-management/` 標記
E3: PASS - 已為訂單管理建立 `01-flow.md`、`02-gherkin.md`、`03-tasks.md` 三份文檔