propose 完成。識別結果：

- 跳過：`商品管理`，因既有 `> ProPose:` 標記已大小寫不敏感識別為 propose 標記，未建立 `product-management/`
- 新功能：`backend/docs/propose/report-management/`
- Bug Fix propose：`backend/docs/propose/fix-report-cache-invalidation/`
- Bug Fix quick-fix：`[Quick-Fix] 匯出按鈕文字顯示為「下載」，應統一改為「匯出」`
- 未標記 Bug 自動分流為 propose：金額四捨五入規則不一致，因涉及前端顯示與 CSV 匯出的共用金額規則，屬跨輸出資料流一致性問題

已產出：

```text
backend/docs/propose/report-management/
  01-flow.md
  02-gherkin.md
  03-tasks.md

backend/docs/propose/fix-report-cache-invalidation/
  01-flow.md
  02-gherkin.md
  03-tasks.md

backend/docs/propose/fix-amount-rounding-consistency/
  01-flow.md
  02-gherkin.md
  03-tasks.md
```

已回寫 `propose/evals/files/spec-case-insensitive.md` 的 propose 標記。Code Review 跳過原因：本次僅新增/修改 Markdown 文檔。Build/測試跳過原因：未修改應用程式實作或測試檔。未執行 git commit：依本次 eval 規則要求不要 commit，且此 workspace 不是 git repository。

---
## Grading
E1: PASS - `商品管理` 的 `> ProPose:` 被視為既有 propose 標記並跳過，實際未建立 `backend/docs/propose/product-management/`

E2: PASS - `[Quick-Fix] 匯出按鈕文字顯示為「下載」，應統一改為「匯出」` 被列為 quick-fix 直接實作清單，未建立 folder

E3: PASS - `[PROPOSE] 報表快取失效機制缺漏` 已建立 `backend/docs/propose/fix-report-cache-invalidation/`，內含 `01-flow.md`、`02-gherkin.md`、`03-tasks.md`

E4: PASS - 未標記的「金額四捨五入規則不一致」已自動分流為 propose，原因是涉及前端顯示與 CSV 匯出的共用金額規則與資料流一致性，並建立 `backend/docs/propose/fix-amount-rounding-consistency/`