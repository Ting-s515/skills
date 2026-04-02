---
name: propose
description: >
  當使用者提供規格需求文檔，並要求規劃實作方案時，必須載入此技能。
  處理規格文檔內的所有待辦項目：新功能需求走完整流程（clarify-flow → Gherkin → 任務清單），
  ## bug fix list 依標記分流（[quick-fix] 直接實作、[propose] 走完整流程、無標記自動判斷），
  已完成功能（## 已完成）與已有 > propose: 標記的項目自動跳過不重複提案。
  觸發情境包含但不限於：「幫我規劃這個功能」、「propose」、「把需求整理成實作計畫」、
  「依照規格文檔產出 propose」、「fix bug」。
  即使使用者只說「開始 propose」、提供規格文檔路徑、或規格文檔含有 bug fix list，也應載入此技能。
---

# Propose

將規格需求文檔（自然語言）轉換為多個獨立功能的實作提案，每個功能產出三份文檔。

## 輸出路徑規則

### 根路徑確認（只需一次）

開始前先確認根路徑前綴：

- 使用者已指定「前端」或「frontend」→ 路徑前綴為 `frontend/`
- 使用者已指定「後端」或「backend」→ 路徑前綴為 `backend/`
- 未指定 → **主動詢問**：「請問此規格文檔為前端還是後端，或是不區分？」，依回答決定前綴（不區分則無前綴，直接使用 `docs/propose/`）

確認後，後續所有功能皆沿用相同路徑，不再重複判斷。

### 路徑格式

```
# 未指定前綴
docs/propose/<feature-a>/

# 前端
frontend/docs/propose/<feature-a>/

# 後端
backend/docs/propose/<feature-a>/
```

`<feature-name>` 從功能描述自動推導，使用 kebab-case。

---

## 執行流程

### 前置：識別功能清單與分組

讀取規格需求文檔，識別所有功能需求並判斷分組：

**跳過規則（依序檢查）：**
- 出現在 `## 已完成` 表格中的功能 → 跳過，不重複提案
- 已有 `> propose: \`docs/propose/<feature-name>/\`` 標記的功能 → 跳過

**分組原則（一般功能需求）：**
- 共享同一個主體操作或資料流的相關子功能 → 合併至同一個 feature folder，子任務在 `03-tasks.md` 內拆分
- 功能目的、操作主體、資料流明顯不同 → 各自獨立 feature folder

**Bug Fix 處理（`## bug fix list` 區塊）：**

讀取 `~/.claude/skills/propose/references/issue-doc-spec.md`，對每個 bug item 套用標記判斷：

| 標記 | 判斷方式 | propose 行為 |
|---|---|---|
| `[quick-fix]` | 明確標記 | 列入「直接實作清單」，不建 folder，由使用者確認後直接實作 |
| `[propose]` | 明確標記 | 建立 `fix-<slug>/` folder，走完整三步驟流程 |
| 無標記 | AI 自動判斷（依 issue-doc-spec 準則） | 歸類為 quick-fix 或 propose 後同上處理 |

識別完成後告知使用者：

```
識別到以下功能需求，將依序處理：

【新功能】
1. <feature-a>：<一句話描述>（含：子功能1、子功能2）
2. <feature-b>：<一句話描述>

【Bug Fix — 走 propose 流程】
3. fix-<slug-a>：<bug 描述>
4. fix-<slug-b>：<bug 描述>

【Bug Fix — quick-fix 直接實作】
- <bug 描述>
- <bug 描述>

資料夾命名：
  <base>/docs/propose/feature-a/
  <base>/docs/propose/feature-b/
  <base>/docs/propose/fix-slug-a/
  <base>/docs/propose/fix-slug-b/
（<base> 為 frontend、backend，或省略）

確認後開始？
```

等待使用者確認（可調整命名、分組方式、或將 quick-fix 升級為 propose）後再繼續。

確認後，**立即回寫規格文檔**，在每個功能對應段落下方插入區塊標記：

```markdown
> propose: `{root}/docs/propose/<feature-name>/`
```

若規格文檔已有舊標記，更新為新的 folder name。回寫完成後才開始執行各功能步驟。

---

### 每個功能依序執行以下三個步驟

#### Step 1：結構化流程（01-flow.md）

使用 Skill tool 呼叫 `clarify-flow` 技能，輸入為該功能的自然語言描述，完成邊界確認互動後，將產出寫入 `{root}/docs/propose/<feature-name>/01-flow.md`：

```markdown
# 功能流程：<功能名稱>

## 功能概述
<一句話描述功能目的>

## 流程說明
<clarify-flow 產出的結構化步驟，含判斷分支與邊界條件>
```

**Bug Fix 特別規則：** `fix-<slug>/` 的 `01-flow.md` 只描述**修正後的正確行為**，不描述 bug 重現步驟。

#### Step 2：Gherkin 驗收條件（02-gherkin.md）

使用 Skill tool 呼叫 `export-gherkin` 技能，輸入為 `01-flow.md` 的內容，指定輸出路徑為 `{root}/docs/propose/<feature-name>/02-gherkin.md`。

#### Step 3：任務清單（03-tasks.md）

依照 `01-flow.md` 與 `02-gherkin.md` 拆解具體實作任務，寫入 `{root}/docs/propose/<feature-name>/03-tasks.md`：

規則：
- 每個任務對應一個可獨立完成的工作單位
- 標示影響的檔案或模組（從對話或專案結構推斷）
- 任務有先後依賴時，標示依賴關係

```markdown
# 任務清單：<功能名稱>

## 參考文檔
- 結構化流程：`{root}/docs/propose/<feature-name>/01-flow.md`
- 驗收條件：`{root}/docs/propose/<feature-name>/02-gherkin.md`

## 任務

- [ ] T1: <任務描述>（影響：`path/to/file.ts`）
- [ ] T2: <任務描述>（影響：`path/to/other.ts`）（依賴 T1）
- [ ] T3: <任務描述>
- [ ] [manual] T_test: 補上單元測試，使用 Skill tool 呼叫 `bdd-unit-test` skill 分析實作檔案產出測試（依賴所有前置任務）
```

`[manual]` 標記表示此任務**不由 apply 自動執行**，須由使用者手動在新 session 中指定觸發。

---

## 全部完成後

所有功能的三份文檔寫入後，輸出完整摘要：

```
propose 完成：

  {root}/docs/propose/feature-a/
    01-flow.md
    02-gherkin.md
    03-tasks.md

  {root}/docs/propose/feature-b/
    01-flow.md
    02-gherkin.md
    03-tasks.md

每個功能可獨立開啟新 session，use apply skill 實作。
```
