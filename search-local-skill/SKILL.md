---
name: search-local-skill
description: Search or find local Claude skills in the user's skills directory (~/.claude/skills/), list all available skills with their descriptions. Supports optional parameter to filter by skill name. Use this skill whenever the user wants to find, list, search, or browse available skills.
---

# 搜尋 Local Skills

## 路徑說明

Skills 根目錄為 `~/.claude/skills/`，請在執行時動態解析實際路徑：

- **Unix/macOS/Linux**：`$HOME/.claude/skills/`
- **Windows (bash)**：`$USERPROFILE/.claude/skills/` 或 `$HOME/.claude/skills/`

執行時使用 shell 展開，例如：`ls "$HOME/.claude/skills/"`，勿硬編碼任何使用者名稱或絕對路徑。

## 參數說明

| 參數 | 類型 | 必填 | 說明 |
|------|------|------|------|
| `skillName` | string | N | 指定要搜尋的 skill 名稱（支援部分匹配） |

### 使用範例

```
# 列出所有 skills
find local skill

# 只搜尋特定 skill
find local skill skill-name
```

## 執行流程

### 無參數（列出全部）
1. **解析路徑**：動態取得 `$HOME/.claude/skills/` 或 `$USERPROFILE/.claude/skills/`
2. **掃描目錄**：讀取 skills 根目錄下的所有子資料夾
3. **讀取定義**：解析每個資料夾內的 `SKILL.md` 檔案
4. **提取資訊**：從 frontmatter 取得 `name` 和 `description`
5. **格式化輸出**：以表格形式呈現所有 skills

### 有參數（篩選搜尋）
1. **解析路徑**：動態取得 skills 根目錄
2. **掃描目錄**：讀取 skills 根目錄下的所有子資料夾
3. **名稱匹配**：篩選出資料夾名稱包含參數關鍵字的 skills
4. **讀取定義**：解析匹配到的 `SKILL.md` 檔案
5. **詳細輸出**：顯示匹配 skill 的完整內容（包含執行流程、範例等）

## 輸出格式

```markdown
## 📋 可用的 Local Skills

| Skill 名稱 | 說明 | 路徑 |
|------------|------|------|
| skill-name | skill description | `~/.claude/skills/skill-name/` |
```

## 補充資訊

### Skill 結構

每個 skill 資料夾應包含：
```
~/.claude/skills/
└── [skill-name]/
    ├── SKILL.md          # 必要：skill 定義與說明
    └── references/       # 可選：範例檔案
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
