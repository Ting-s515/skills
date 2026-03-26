---
name: apply
description: >
  當使用者指定 propose 產出的功能資料夾路徑，並要求開始或繼續實作時，必須載入此技能。
  從路徑自動推斷根路徑，讀取資料夾下的三份文檔，自動逐一實作未完成任務並更新 checkbox 狀態。
  觸發情境包含但不限於：「apply」、「開始實作」、「繼續實作」、「apply frontend/docs/propose/feature-name」、
  「apply backend/docs/propose/feature-name」、「apply docs/propose/feature-name」、「按照任務清單實作」。
  使用者通常會在新 session 中指定功能路徑來呼叫此技能，不依賴 propose 的對話 context。
---

# Apply

依照 `propose` 產出的三份文檔，逐一實作任務並更新完成狀態。

## 前置確認

### 根路徑與文檔定位

從使用者提供的路徑或指令中自動推斷根路徑 `{root}`，依序嘗試：

1. 路徑包含 `frontend/` 前綴 → `{root}` = `frontend`
2. 路徑包含 `backend/` 前綴 → `{root}` = `backend`
3. 未指定前綴 → 依序嘗試 `frontend/docs/propose/<feature-name>/`、`backend/docs/propose/<feature-name>/`、`docs/propose/<feature-name>/`，找到三份文檔（`01-flow.md`、`02-gherkin.md`、`03-tasks.md`）的路徑即為正確根路徑

三個路徑都找不到文檔，才詢問使用者確認路徑。

---

## 執行流程

### 1. 載入 context

讀取三份文檔：

- `01-flow.md`：了解業務邏輯與邊界
- `02-gherkin.md`：了解每個任務的完成標準
- `03-tasks.md`：取得任務清單，依以下格式判斷狀態：
  - `- [ ] Tx:` → 未開始
  - `- [x] Tx:` → 實作完成，code review 尚未執行
  - `- [x][cr] Tx:` → 實作 + code review 全部完成，跳過

### 2. 逐任務實作

依照 `03-tasks.md` 的任務順序，每次實作一個任務：

1. 告知使用者目前執行哪個任務（`T1: <描述>`）
2. 實作該任務，依照 `01-flow.md` 的邏輯與 `02-gherkin.md` 的驗收條件
3. 實作完成後，將 `03-tasks.md` 中該任務的 `[ ]` 更新為 `[x]`
4. 產生該任務的 commit message（格式：`<type>: <description>`）
5. 使用 Agent tool 開啟 subagent 執行 code review（每個單一任務完成後立即執行）：
   - 規格文檔路徑：`{root}/docs/propose/<feature-name>/`（含三份文檔）
   - use `code-reviewer` skill 執行審查
6. subagent 回傳結果後，**立即** 用 Edit tool 將 `03-tasks.md` 中該任務的 `[x]` 改為 `[x][cr]`，作為 code review 已完成的持久記錄。這一步不可遺漏——subagent 完成不等於 checkbox 已更新，必須主動執行 Edit。
7. 宣告「Tx 完成 ✓」，直接繼續下一個任務（不等待使用者確認）

若任務有依賴關係（`依賴 Tx`），必須先確認依賴任務已完成（`[x]` 或 `[x][cr]`）再執行。

### 3. 實作規範

遵循專案 `CLAUDE.md` 的規範：

- 禁止三元嵌套
- 需要加註解的地方：後端業務邏輯、前端邏輯判斷、hook 邏輯、工具函式邏輯
- 不加註解：純 UI 樣式、簡單賦值

---

## 全部完成後

所有任務（`[x]`）完成後，告知使用者所有任務已完成。

---

## 中途繼續

若使用者在任務進行到一半時重新開啟對話：

- 讀取 `03-tasks.md`，依任務狀態決定行動：
  - `[x][cr]`：實作與 code review 皆完成，完全跳過
  - `[x]`：實作完成但 code review 未執行，**直接補跑 code review**，subagent 回傳後立即用 Edit tool 更新為 `[x][cr]`
  - `[ ]`：從此任務開始實作
- 告知使用者目前進度，例如：「T1 已完成（含 code review），T2 實作完成但 code review 未執行，從補跑 T2 code review 開始」
