---
name: apply
description: >
  當使用者指定 propose 產出的資料夾，並要求開始或繼續實作時，必須載入此技能。
  獨立讀取 docs/propose/<feature-name>/ 下的三份文檔，依序實作未完成任務，完成後更新 checkbox 狀態。
  觸發情境包含但不限於：「apply」、「開始實作」、「繼續實作」、「apply docs/propose/feature-name」、
  、「按照任務清單實作」。
  使用者通常會在新 session 中指定 feature-name 來呼叫此技能，不依賴 propose 的對話 context。
---

# Apply

依照 `propose` 產出的三份文檔，逐一實作任務並更新完成狀態。

## 前置確認

開始前，先確認以下文檔存在：

```
docs/propose/<feature-name>/
  01-flow.md      ← 結構化流程（實作依據）
  02-gherkin.md   ← 驗收條件（完成標準）
  03-tasks.md     ← 任務清單（執行順序）
```

若 `<feature-name>` 不明確，詢問使用者確認。

---

## 執行流程

### 1. 載入 context

讀取三份文檔：
- `01-flow.md`：了解業務邏輯與邊界
- `02-gherkin.md`：了解每個任務的完成標準
- `03-tasks.md`：取得待實作任務清單（`[ ]` 為未完成）

### 2. 逐任務實作

依照 `03-tasks.md` 的任務順序，每次實作一個任務：

1. 告知使用者目前執行哪個任務（`T1: <描述>`）
2. 實作該任務，依照 `01-flow.md` 的邏輯與 `02-gherkin.md` 的驗收條件
3. 實作完成後，將 `03-tasks.md` 中該任務的 `[ ]` 更新為 `[x]`
4. 告知使用者該任務完成，等待確認後繼續下一個

若任務有依賴關係（`依賴 Tx`），必須先確認依賴任務已完成（`[x]`）再執行。

### 3. 實作規範

遵循專案 `CLAUDE.md` 的規範：
- 禁止三元嵌套
- 需要加註解的地方：後端業務邏輯、前端邏輯判斷、hook 邏輯、工具函式邏輯
- 不加註解：純 UI 樣式、簡單賦值

---

## 全部完成後

所有任務（`[x]`）完成後：

1. 產生 commit message（格式：`<type>: <description>`）
2. 使用 Agent tool 開啟 subagent 執行 code review：
   - 規格文檔路徑：`docs/propose/<feature-name>/`（含三份文檔）
   - use `code-reviewer` skill 執行審查

---

## 中途繼續

若使用者在任務進行到一半時重新開啟對話：
- 讀取 `03-tasks.md`，找出已完成（`[x]`）與未完成（`[ ]`）的任務
- 從第一個未完成任務繼續，不重複已完成的部分
- 告知使用者：「目前進度：Tx 已完成，從 Ty 繼續」
