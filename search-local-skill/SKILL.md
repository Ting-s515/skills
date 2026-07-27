---
name: search-local-skill
description: Search or find local Codex skills in the user's Codex skills directory (~/.codex/skills/), list all available skills with their descriptions, and optionally filter by skill name. Use this skill whenever the user wants to find, list, search, or browse available Codex skills.
---

# 搜尋 Local Codex Skills

## 路徑解析策略

此 skill 專門搜尋 `~/.codex/skills/`，不改為其他工具的 skills 目錄。採用「環境明確就直接使用；不明確才偵測」的策略解析實際絕對路徑：

1. 若目前 agent context 已明確提供作業系統與使用者 home，直接依下方平台分支組合 Codex skills 目錄。
2. 若環境資訊不明確，先以唯讀方式偵測作業系統，再取得目前使用者的 home；不得猜測使用者名稱或磁碟代號。
3. 若仍無法解析 home，說明缺少的資訊並請使用者提供，不可改掃其他工具或任意目錄。

平台分支：

- **macOS/Linux**：`$HOME/.codex/skills/`
- **Windows PowerShell**：以 `[Environment]::GetFolderPath('UserProfile')` 取得 home，再組合 `.codex/skills/`
- **Windows bash**：`$USERPROFILE/.codex/skills/`；若 `$USERPROFILE` 不可用，再使用 `$HOME/.codex/skills/`

所有顯示與文件中的相對路徑統一使用正斜線。實際目錄列舉則交由目前 agent 的檔案工具，或已確認作業系統適用的唯讀 shell 指令處理。

## 參數說明

| 參數 | 類型 | 必填 | 說明 |
| --- | --- | --- | --- |
| `skillName` | string | N | 指定要搜尋的 skill 名稱，支援不分大小寫的部分匹配 |

### 使用範例

```text
# 列出所有 Codex skills
find local skill

# 只搜尋特定 skill
find local skill skill-name
```

## 執行流程

### 無參數：列出全部

1. **解析路徑**：依路徑解析策略取得目前平台的 `~/.codex/skills/` 絕對路徑。
2. **掃描目錄**：以唯讀方式列出 Codex skills 根目錄下的所有子目錄。
3. **讀取定義**：只將包含精確 `SKILL.md` 入口的目錄視為 skill。
4. **提取資訊**：從 frontmatter 取得 `name` 和 `description`；缺少必要欄位時標示異常，不自行補值。
5. **去重排序**：以正規化完整路徑去重，再依 skill 名稱排序。
6. **格式化輸出**：以表格呈現名稱、說明與實際來源路徑。

### 有參數：篩選搜尋

1. 先依無參數流程解析並掃描 Codex skills 目錄。
2. 對目錄名稱與 frontmatter `name` 執行不分大小寫的部分匹配。
3. 顯示每個匹配 skill 的名稱、說明、實際入口路徑與完整內容。

## 輸出格式

```markdown
## 📋 可用的 Local Codex Skills

| Skill 名稱 | 說明 | 路徑 |
| --- | --- | --- |
| skill-name | skill description | `~/.codex/skills/skill-name/` |
```

## 補充資訊

### Skill 結構

每個 skill 資料夾應包含：

```text
~/.codex/skills/
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
