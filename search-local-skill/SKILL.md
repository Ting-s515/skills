---
name: search-local-skill
description: Search or find local skills from the skill roots exposed by the current agent or runtime, list all available skills with their descriptions, and optionally filter by skill name. Use this skill whenever the user wants to find, list, search, or browse available skills. Do not assume a fixed Claude, Codex, Windows, or macOS installation path.
---

# 搜尋 Local Skills

## 路徑解析策略

採用「環境明確就直接使用；不明確才偵測」的策略，不固定假設 skill 安裝位置：

1. 若目前 agent context 已提供 `Skill roots`、`Available skills` 或 skill 的完整入口路徑，直接將這些資訊視為權威來源。
2. 若只知道本技能的 `SKILL.md` 路徑，從本檔所在的 skill 目錄向上一層推導目前的 skill root。
3. 若環境資訊仍不明確，先以唯讀方式偵測作業系統與目前 runtime 公開的設定或環境變數，再選擇適用的目錄列舉方式。
4. 若存在多個 skill roots，全部掃描並以正規化後的完整路徑去重；不要只取第一個目錄。
5. 若仍無法確認 skill roots，說明缺少的資訊並請使用者提供路徑，不可猜測使用者名稱、磁碟代號或固定 home 子目錄。

所有顯示與文件中的相對路徑統一使用正斜線。實際檔案操作則交由目前 agent 的檔案工具或已確認作業系統適用的唯讀 shell 指令處理。

## 參數說明

| 參數 | 類型 | 必填 | 說明 |
| --- | --- | --- | --- |
| `skillName` | string | N | 指定要搜尋的 skill 名稱，支援不分大小寫的部分匹配 |

### 使用範例

```text
# 列出所有 skills
find local skill

# 只搜尋特定 skill
find local skill skill-name
```

## 執行流程

### 無參數：列出全部

1. **解析 roots**：依路徑解析策略取得一個或多個實際 skill roots。
2. **掃描目錄**：以唯讀方式列出每個 root 下的 skill 子目錄。
3. **讀取定義**：只將包含精確 `SKILL.md` 入口的目錄視為 skill。
4. **提取資訊**：從 frontmatter 取得 `name` 和 `description`；缺少必要欄位時標示異常，不自行補值。
5. **去重排序**：以正規化完整路徑去重，再依 skill 名稱排序。
6. **格式化輸出**：以表格呈現名稱、說明與實際來源路徑。

### 有參數：篩選搜尋

1. 先依無參數流程解析並掃描全部 roots。
2. 對目錄名稱與 frontmatter `name` 執行不分大小寫的部分匹配。
3. 顯示每個匹配 skill 的名稱、說明、實際入口路徑與完整內容。
4. 若不同 roots 含有同名 skill，全部保留並清楚標示來源，不任意判定優先順序。

## 輸出格式

```markdown
## 📋 可用的 Local Skills

| Skill 名稱 | 說明 | 路徑 |
| --- | --- | --- |
| skill-name | skill description | `<skill-root>/skill-name/` |
```

## 補充資訊

### Skill 結構

每個 skill 資料夾應包含：

```text
<skill-root>/
└── <skill-name>/
    ├── SKILL.md          # 必要：skill 定義與說明
    └── references/       # 可選：補充資源
```

### SKILL.md 格式

```yaml
---
name: skill-name
description: skill 的簡短說明
---

# Skill 標題

（詳細說明內容）
```
