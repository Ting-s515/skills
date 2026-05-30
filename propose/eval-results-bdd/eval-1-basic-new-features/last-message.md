propose 完成：

  `backend/docs/propose/product-management/`
    `01-flow.md`
    `02-gherkin.md`
    `03-tasks.md`

  `backend/docs/propose/order-management/`
    `01-flow.md`
    `02-gherkin.md`
    `03-tasks.md`

已回寫 `propose/evals/files/spec-basic.md`，加入兩個 `> propose:` 標記。

驗證狀態：本次僅變更 `.md` 文檔，build 與 code review 依規則跳過。`git diff --check` 與 `git status` 因 workspace 不是 git repository 無法執行；也依 eval 規則未執行 git commit。

產生的 commit message（未提交）：

```text
docs: add backend propose plans

本次依照後台管理系統規格，為商品管理與訂單管理建立後端實作提案文件，供後續 apply 流程拆分實作。

本次調整：
- 新增商品管理的流程、Gherkin 驗收條件與任務清單
- 新增訂單管理的流程、Gherkin 驗收條件與任務清單
- 在原始規格文件回寫對應 propose folder 標記
```

---
## Grading
E1: PASS - 已建立 `backend/docs/propose/product-management/01-flow.md`
E2: PASS - 已建立 `backend/docs/propose/product-management/02-gherkin.md`
E3: PASS - 已建立 `backend/docs/propose/product-management/03-tasks.md`
E4: PASS - 已建立 `backend/docs/propose/order-management/01-flow.md`
E5: PASS - 已建立 `backend/docs/propose/order-management/02-gherkin.md`
E6: PASS - 已建立 `backend/docs/propose/order-management/03-tasks.md`
E7: PASS - `propose/evals/files/spec-basic.md` 已包含 `> propose:` 標記
E8: PASS - 本輸出包含 `propose 完成` 摘要並列出建立的 feature folders