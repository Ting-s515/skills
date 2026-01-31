---
name: search-user-skill
description: Search or find user skills in the specified directory, list all available skills with their descriptions. Supports optional parameter to filter by skill name.
---

# 搜尋 User Skills

## 路徑說明

| 項目 | 值 |
|------|-----|
| Skills 根目錄 | `C:\Users\<username>\.claude\skills\` |
| Skill 定義檔 | 每個 skill 資料夾內的 `SKILL.md` |

## 參數說明

| 參數 | 類型 | 必填 | 說明 |
|------|------|------|------|
| `skillName` | string | N | 指定要搜尋的 skill 名稱（支援部分匹配） |

### 使用範例

```
# 列出所有 skills
find user skill

# 只搜尋特定 skill
find user skill skill-name
```

## 執行流程

### 無參數（列出全部）
1. **掃描目錄**：讀取 `C:\Users\<username>\.claude\skills\` 下的所有子資料夾
2. **讀取定義**：解析每個資料夾內的 `SKILL.md` 檔案
3. **提取資訊**：從 frontmatter 取得 `name` 和 `description`
4. **格式化輸出**：以表格形式呈現所有 skills

### 有參數（篩選搜尋）
1. **掃描目錄**：讀取 `C:\Users\<username>\.claude\skills\` 下的所有子資料夾
2. **名稱匹配**：篩選出資料夾名稱包含參數關鍵字的 skills
3. **讀取定義**：解析匹配到的 `SKILL.md` 檔案
4. **詳細輸出**：顯示匹配 skill 的完整內容（包含執行流程、範例等）

## 輸出格式

```markdown
## 📋 可用的 User Skills

| Skill 名稱 | 說明 | 路徑 |
|------------|------|------|
| skill-name | skill description | `skills/skill-name/` |
```

## 補充資訊

### Skill 結構

每個 skill 資料夾應包含：
```
skills/
└── [skill-name]/
    ├── SKILL.md          # 必要：skill 定義與說明
    └── examples/         # 可選：範例檔案
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
