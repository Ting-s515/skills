---
name: skill-creator
description: >
  建立新技能、修改或優化既有技能、執行 eval 評測、進行效能基準測試時，必須載入此技能。
  技能資料夾位於 ~/.claude/skills/<skill-name>/，包含 SKILL.md 與可選的 evals/ 資料夾。
  觸發情境包含但不限於：「幫我建立一個新 skill」、「優化這個 skill 的描述」、「幫我跑 eval」、
  「測試這個 skill 的效能」、「skill-creator」、「建立本地技能」、「新增 skill」、「改善 skill 觸發準確度」。
---

# Skill Creator

管理 `~/.claude/skills/` 下的本地技能：建立、修改、評測、基準測試。

## 技能資料夾結構

```
~/.claude/skills/
└── <skill-name>/
    ├── SKILL.md          ← 必要：技能定義
    └── evals/            ← 可選：評測資料
        ├── evals.json
        └── files/        ← eval 所需的測試檔案
```

## 模式判斷

根據使用者意圖選擇對應模式：

| 使用者說 | 進入模式 |
|----------|----------|
| 建立新技能、新增 skill | **CREATE 模式** |
| 修改、優化、改善既有技能 | **MODIFY 模式** |
| 跑 eval、評測技能 | **EVAL 模式** |
| 基準測試、variance 分析 | **BENCHMARK 模式** |
| 優化描述、改善觸發準確度 | **OPTIMIZE-DESC 模式** |

---

## CREATE 模式：建立新技能

### 步驟 1：蒐集需求

詢問使用者（若未提供）：
1. **技能名稱**（slug，小寫 kebab-case，如 `export-gherkin`）
2. **技能目的**：這個技能要做什麼？
3. **觸發情境**：使用者說什麼話會用到這個技能？
4. **執行流程**：技能的主要執行步驟為何？

### 步驟 2：產生 SKILL.md

使用以下 frontmatter 格式：

```yaml
---
name: <skill-name>
description: >
  <一段話說明此技能的觸發條件，包含：何時必須載入、觸發情境範例>
  觸發情境包含但不限於：<列出 3-5 個使用者可能說的話>。
  <額外排除或特殊說明（可選）>
---
```

**Description 撰寫原則：**
- 第一句：「當使用者 [條件] 時，必須載入此技能」
- 列舉觸發情境：用引號包住每個範例詞句
- 排除說明：若有相似技能需要區分，加上「注意：」或「排除：」
- 長度控制在 5-8 行，避免過長導致讀取成本高

**SKILL.md 內容區塊（依需求選用）：**

```markdown
# <技能名稱>

<一句話說明>

## 執行流程

1. 步驟一
2. 步驟二
...

## <功能說明區塊>

...

## 輸出格式

...
```

### 步驟 3：建立檔案

```
~/.claude/skills/<skill-name>/SKILL.md
```

建立後輸出確認：
- 技能路徑
- 建議同步至 MEMORY.md 的索引（若有 skill 索引習慣）

---

## MODIFY 模式：修改既有技能

### 步驟 1：定位技能

```
~/.claude/skills/<skill-name>/SKILL.md
```

讀取現有內容，理解當前行為。

### 步驟 2：分析問題

根據使用者描述，識別需要改善的部分：
- description 觸發不精確？→ 進入 OPTIMIZE-DESC 模式
- 執行流程有遺漏？→ 補充流程步驟
- 輸出格式需調整？→ 修改輸出規範
- 新增使用情境？→ 擴充觸發說明與流程

### 步驟 3：修改並輸出 diff 摘要

修改後說明變更了哪些段落及原因。

---

## EVAL 模式：執行評測

### 前置確認

讀取 `~/.claude/skills/<skill-name>/evals/evals.json`，若不存在則詢問使用者是否要建立。

### evals.json 格式

```json
{
  "skill_name": "<skill-name>",
  "evals": [
    {
      "id": 1,
      "name": "<eval 名稱>",
      "prompt": "<觸發技能的使用者 prompt>",
      "expected_output": "<預期的執行結果說明>",
      "files": [
        "<eval 需要的測試檔案路徑（相對於技能資料夾）>"
      ],
      "assertions": [
        {
          "name": "<assertion 名稱>",
          "check": "<判斷條件，用自然語言描述 transcript 應包含的行為>"
        }
      ]
    }
  ]
}
```

### 評測流程

對每個 eval：
1. 顯示 eval 名稱與 prompt
2. 模擬執行（描述技能在此 prompt 下應觸發的行為）
3. 逐一核對 assertions：
   - ✅ 通過：assertion 條件在預期行為中滿足
   - ❌ 失敗：說明哪個 assertion 未滿足及原因
4. 統計通過率

### 評測結果格式

```markdown
## Eval 結果：<skill-name>

| # | Eval 名稱 | 結果 | 通過 assertions |
|---|-----------|------|-----------------|
| 1 | fresh-all-tasks | ✅ PASS | 5/5 |
| 2 | resume-partial  | ❌ FAIL | 3/5 |

**總通過率：50%**

### 失敗詳情

#### Eval 2：resume-partial
- ❌ `T1 被跳過不重複實作`：技能流程未明確說明已完成任務的跳過條件
```

---

## BENCHMARK 模式：效能基準測試

執行多次 eval（預設 3 次），分析技能行為的一致性：

1. 對每個 eval 場景執行 N 次模擬
2. 記錄每次的 assertion 通過狀況
3. 計算 variance（通過率標準差）
4. 識別不穩定的 assertions（高 variance）

### 結果格式

```markdown
## 基準測試：<skill-name>（N=3）

| Eval | 第1次 | 第2次 | 第3次 | 平均 | Variance |
|------|-------|-------|-------|------|----------|
| eval-1 | 5/5 | 5/5 | 4/5 | 93% | Low |
| eval-2 | 3/5 | 4/5 | 3/5 | 67% | Medium |

### 不穩定 Assertions（需改善）

- `T1 被跳過不重複實作`：3次中有2次失敗，建議在 SKILL.md 中加強跳過條件說明
```

---

## OPTIMIZE-DESC 模式：優化描述觸發準確度

### 問題診斷

分析現有 description 的問題：
- 觸發條件是否夠具體？
- 是否有歧義（跟其他技能描述重疊）？
- 排除條件是否清晰？

### 優化策略

1. **首句強化**：改為「當使用者 [精確條件] 時，**必須**載入此技能」
2. **觸發詞補充**：加入更多具體的使用者可能說的話
3. **排除說明**：加上「注意：若 X 則不觸發，應使用 Y 技能」
4. **避免歧義**：確保觸發詞不與其他技能重疊

輸出前後對比，供使用者確認後再寫入檔案。

---

## 技能 SKILL.md 品質清單

建立或修改技能後自動確認：

- [ ] `name` 為 kebab-case slug
- [ ] `description` 第一句包含「必須載入此技能」
- [ ] 觸發情境至少 3 個具體範例（用引號包住）
- [ ] 執行流程清晰（有編號步驟）
- [ ] 輸出格式有範例（若技能有固定輸出）
- [ ] 排除情境明確（若有相似技能）
