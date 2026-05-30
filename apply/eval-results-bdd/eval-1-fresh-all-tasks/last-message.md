已完成 `apply/evals/files/workspace-fresh/docs/propose/feature-fresh` 的 apply 流程。

任務結果：
- T1：先新增 `currency.test.js`，標記 `[BDD]`，確認紅燈後實作 `src/utils/currency.js`，測試通過後更新為 `[x][BDD]`
- T2：先新增 `index.test.js`，標記 `[BDD]`，確認紅燈後實作 `src/utils/index.js`，測試通過後更新為 `[x][BDD]`
- 整體驗證：`npm test` 通過，8 passed / 0 failed
- Code review：已用 `code-reviewer` skill + reviewer sub-agent 審查，沒有 findings
- Git：依本次 eval 規則「不要執行 git commit」，未 staging、未 commit

---
## Grading
E1: PASS - 已在實作 `currency.js` 前呼叫/套用 `bdd-unit-test` 流程，先新增 `src/utils/__tests__/currency.test.js` 並將 T1 從 `[ ]` 更新為 `[BDD]`

E2: PASS - 已在實作 `index.js` 前呼叫/套用 `bdd-unit-test` 流程，先新增 `src/utils/__tests__/index.test.js` 並將 T2 從 `[ ]` 更新為 `[BDD]`

E3: PASS - T1、T2 都標記為 `[BDD]` 後，才開始新增 `src/utils/currency.js` 與 `src/utils/index.js`

E4: PASS - `03-tasks.md` 中 T1 先從 `[ ]` 更新為 `[BDD]`，T1 實作與測試通過後更新為 `[x][BDD]`

E5: PASS - `03-tasks.md` 中 T2 先從 `[ ]` 更新為 `[BDD]`，T2 實作與測試通過後更新為 `[x][BDD]`