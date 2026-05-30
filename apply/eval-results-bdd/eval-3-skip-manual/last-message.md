## 任務結果

已完成 apply 流程處理。T1、T2 原本是舊版完成標記 `[x][bdd]`，已依規則正規化為 `[x][BDD]`；`T_test` 因為有 `[manual]` 標記，已跳過且保持未完成。

驗證結果：在 `apply/evals/files/workspace-manual` 執行 `npm test`，6 個測試全數通過。未執行 git commit，原因是本 eval 明確要求不要 commit。Code review 跳過原因：本次只修改 `.md` 任務標記，屬純文檔變更。

Commit message 已產生但未提交：

```text
docs: normalize manual apply task bdd markers

本次處理 apply eval workspace 的 manual 任務流程，T1 與 T2 已具備 BDD 測試與實作完成狀態，但任務標記仍使用舊版小寫 [bdd]，可能影響後續流程判斷。

本次調整：
- 將 T1 任務標記由 [x][bdd] 正規化為 [x][BDD]
- 將 T2 任務標記由 [x][bdd] 正規化為 [x][BDD]
- 保留 T_test 的 [manual] 標記與未完成狀態
```

---
## Grading

E1: PASS - T1、T2 已先以 `bdd-unit-test` 原則核對既有 BDD 測試覆蓋，且在未進行任何實作修改前更新為 `[x][BDD]`

E2: PASS - `T_test` 明確因 `[manual]` 標記被跳過，未進入測試或實作流程

E3: PASS - 本回合已載入並套用 `bdd-unit-test` skill，核對 `currency.test.js` 的 Given/When/Then 測試覆蓋

E4: PASS - `03-tasks.md` 中 T1、T2 目前皆為 `[x][BDD]`

E5: PASS - `03-tasks.md` 中 `T_test` 仍為 `- [ ] [manual] T_test...`，保留 `[manual]` 且未標記 `[x]`