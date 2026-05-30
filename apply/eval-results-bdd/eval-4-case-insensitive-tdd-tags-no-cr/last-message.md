任務結果：

已完成 `feature-case-tags` apply 流程。`T1` 的 `[bDd]` 已視為既有 BDD 標記，未重新送回測試撰寫階段；`T2` 先新增 `src/utils/__tests__/currency.test.js`，跑出預期紅燈後才實作 `src/utils/currency.js`；`T_manual` 的 `[MANUAL]` 已以大小寫不敏感方式辨識為人工任務並跳過。

驗證已通過：`npm test -- src/utils/__tests__/currency.test.js`，結果 `2 pass / 0 fail`。未執行 git commit，符合本 eval 規則。

---
## Grading
E1: PASS - `T1` 的 `[bDd]` 被保留為既有 BDD 狀態處理，未對 T1 重新撰寫測試。
E2: PASS - `T_manual` 的 `[MANUAL]` 被辨識為人工任務，未納入自動測試與實作。
E3: PASS - `T2` 先新增 BDD 測試並標記 `[BDD]`，確認紅燈後才開始實作 `formatCurrency`。
E4: PASS - `03-tasks.md` 目前只使用 `T1/T2 [x][BDD]` 與 `T_manual [MANUAL]`，輸出與任務檔未產生額外完成標記或審查流程文字。