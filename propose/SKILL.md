---
name: propose
description: >
  當使用者提供規格需求文檔（自然語言描述的功能需求），並要求規劃實作方案時，必須載入此技能。
  識別文檔內的每個功能需求，依序為每個功能執行：1) clarify-flow 整理為結構化流程，
  2) 產出 Gherkin 驗收條件，3) 產出任務清單，每個功能各存為獨立資料夾。
  觸發情境包含但不限於：「幫我規劃這個功能」、「propose」、「把需求整理成實作計畫」、
  、「依照規格文檔產出 propose」。
  即使使用者只說「開始 propose」或提供規格文檔路徑，也應載入此技能開始規劃流程。
---

# Propose

將規格需求文檔（自然語言）轉換為多個獨立功能的實作提案，每個功能產出三份文檔。

## 輸出路徑規則

每個功能獨立一個資料夾：
```
docs/propose/
  <feature-a>/
    01-flow.md        ← 結構化流程
    02-gherkin.md     ← Gherkin 驗收條件
    03-tasks.md       ← 任務清單
  <feature-b>/
    01-flow.md
    02-gherkin.md
    03-tasks.md
```

`<feature-name>` 從功能描述自動推導，使用 kebab-case。

---

## 執行流程

### 前置：識別功能清單

讀取規格需求文檔，列出所有識別到的功能需求，告知使用者：

```
識別到以下功能需求，將依序處理：
1. <feature-a>：<一句話描述>
2. <feature-b>：<一句話描述>

資料夾命名：
  docs/propose/feature-a/
  docs/propose/feature-b/

確認後開始？
```

等待使用者確認（可調整命名或排除特定功能）後再繼續。

---

### 每個功能依序執行以下三個步驟

#### Step 1：結構化流程（01-flow.md）

讀取 `~/.claude/skills/clarify-flow/SKILL.md`，依照其規則將該功能的自然語言描述整理為結構化流程。

完成邊界確認互動後，寫入 `docs/propose/<feature-name>/01-flow.md`：

```markdown
# 功能流程：<功能名稱>

## 功能概述
<一句話描述功能目的>

## 流程說明
<依 clarify-flow 規則產出的結構化步驟，含判斷分支與邊界條件>
```

#### Step 2：Gherkin 驗收條件（02-gherkin.md）

依照 `01-flow.md` 撰寫 Gherkin 格式驗收條件，寫入 `docs/propose/<feature-name>/02-gherkin.md`：

規則：
- 每個主要路徑（happy path）一個 Scenario
- 每個邊界條件或錯誤路徑一個 Scenario
- 使用繁體中文撰寫 Given / When / Then

```markdown
# 驗收條件：<功能名稱>

```gherkin
Feature: <功能名稱>

  Scenario: <描述 happy path>
    Given <前置狀態>
    When <使用者操作>
    Then <預期結果>

  Scenario: <描述邊界或錯誤情境>
    Given ...
    When ...
    Then ...
```
```

#### Step 3：任務清單（03-tasks.md）

依照 `01-flow.md` 與 `02-gherkin.md` 拆解具體實作任務，寫入 `docs/propose/<feature-name>/03-tasks.md`：

規則：
- 每個任務對應一個可獨立完成的工作單位
- 標示影響的檔案或模組（從對話或專案結構推斷）
- 任務有先後依賴時，標示依賴關係

```markdown
# 任務清單：<功能名稱>

## 參考文檔
- 結構化流程：`docs/propose/<feature-name>/01-flow.md`
- 驗收條件：`docs/propose/<feature-name>/02-gherkin.md`

## 任務

- [ ] T1: <任務描述>（影響：`path/to/file.ts`）
- [ ] T2: <任務描述>（影響：`path/to/other.ts`）（依賴 T1）
- [ ] T3: <任務描述>
```

---

## 全部完成後

所有功能的三份文檔寫入後，輸出完整摘要：

```
propose 完成：

  docs/propose/feature-a/
    01-flow.md
    02-gherkin.md
    03-tasks.md

  docs/propose/feature-b/
    01-flow.md
    02-gherkin.md
    03-tasks.md

每個功能可獨立開啟新 session，use apply skill 實作。
```
