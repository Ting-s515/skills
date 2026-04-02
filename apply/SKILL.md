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
5. 宣告「Tx 完成 ✓」，直接繼續下一個任務（不等待使用者確認）

若任務有依賴關係（`依賴 Tx`），必須先確認依賴任務已完成（`[x]` 或 `[x][cr]`）再執行。

**`[manual]` 任務跳過規則：** 標記為 `[manual]` 的任務（如 `T_test`）不自動執行，apply 遇到時直接跳過，等待使用者在新 session 中手動指定觸發。

### 3. 實作規範

遵循專案 `CLAUDE.md` 的規範：

- 禁止三元嵌套
- 需要加註解的地方：後端業務邏輯、前端邏輯判斷、hook 邏輯、工具函式邏輯
- 不加註解：純 UI 樣式、簡單賦值

---

## 全部完成後

所有一般任務（無 `[manual]` 標記）皆為 `[x]` 後，統一執行一次 code review：

1. 使用 Agent tool 開啟 subagent，傳入：
   - 規格文檔路徑：`{root}/docs/propose/<feature-name>/`（含三份文檔）
   - 使用 Skill tool 呼叫 `code-reviewer` skill 執行審查，審查範圍涵蓋整個 feature 的架構與完整實作
2. subagent 回傳結果後，**立即** 用 Edit tool 將 `03-tasks.md` 中所有一般任務的 `[x]` 更新為 `[x][cr]`。`[manual]` 任務保持原狀，不納入此次 code review。這步不可遺漏——subagent 完成不等於 checkbox 已更新，必須主動執行 Edit。
3. 告知使用者所有任務已完成，並附上 code review 結果摘要。`[manual]` 任務（如 `T_test`）請在新 session 中手動指定觸發。

---

## 中途繼續

若使用者在任務進行到一半時重新開啟對話：

- 讀取 `03-tasks.md`，依整體狀態決定行動：
  - 所有任務皆為 `[x][cr]`：全部完成，告知使用者即可
  - 存在 `[ ]` 任務：從第一個 `[ ]` 繼續實作，完成後再統一執行 code review
  - 所有任務皆為 `[x]`（無 `[x][cr]`）：實作已全部完成但 code review 未執行，直接補跑一次統一 code review，subagent 回傳後立即用 Edit tool 將所有 `[x]` 更新為 `[x][cr]`
- 告知使用者目前進度，例如：「T1、T2 已完成實作，T3 尚未開始，從 T3 繼續實作」
