已完成 apply 流程：T1 保留既有 `[x][BDD]`，未重建 `currency.js`；T2 先新增 BDD 測試並更新為 `[BDD]`，確認紅燈原因是 `index.js` 尚不存在後，才新增 `src/utils/index.js` 匯出 `formatCurrency`，測試通過後更新為 `[x][BDD]`。

驗證結果：`npm test -- src/utils/__tests__/index.test.js` 通過，`npm test` 通過。已執行 code review，無 findings，報告已存於 `apply/evals/files/workspace-partial/docs/code-review-report/code-review-2026-05-30-feature-partial.md`。已產生 commit message，但依 eval 規則且此 workspace 不是 git repository，未執行 commit。

Commit message:
```text
feat: export formatCurrency from utils index

原本 formatCurrency 已完成實作與 BDD 狀態，但 utils index 尚未提供匯出入口，外部模組無法從統一入口取得貨幣格式化函式。

本次調整：
- 新增 utils index 匯出 formatCurrency
- 新增 index 匯出入口的 BDD 測試
- 將 T2 任務狀態依 TDD 流程更新為 [x][BDD]
```

---
## Grading
E1: PASS - T1 原本為 `[x][BDD]`，本次保留既有狀態，未重建 `src/utils/currency.js`。
E2: PASS - T2 先透過 `bdd-unit-test` 流程新增 `src/utils/__tests__/index.test.js`，再進行實作。
E3: PASS - `03-tasks.md` 先將 T2 更新為 `[BDD]`，之後才新增 `src/utils/index.js`。
E4: PASS - 已讀取並依 `bdd-unit-test` skill 流程撰寫 T2 的 BDD 測試。
E5: PASS - `03-tasks.md` 中 T2 最終為 `[x][BDD]`。