---
name: search-local-skill
description: Search local Claude Code or Codex skills, list their names and descriptions, and optionally filter by skill name. Use the active tool's skills directory; search both directories when the user requests both or the active tool is unclear.
---

# 搜尋本機 Agent Skills

## 技能目錄

依目前使用的工具選擇對應目錄：

| 工具 | macOS/Linux | Windows PowerShell | Windows bash |
| --- | --- | --- | --- |
| Claude Code | `$HOME/.claude/skills/` | 使用 UserProfile 組合 `.claude/skills/` | `$USERPROFILE/.claude/skills/`，否則使用 `$HOME/.claude/skills/` |
| Codex | `$HOME/.codex/skills/` | 使用 UserProfile 組合 `.codex/skills/` | `$USERPROFILE/.codex/skills/`，否則使用 `$HOME/.codex/skills/` |

若目前 agent context 明確指出使用 Claude Code 或 Codex，只掃描該工具的目錄。使用者明確要求比較兩種工具，或目前環境無法判斷時，掃描兩個可存取的目錄，並在輸出中標示來源工具。不要因目錄不存在而改掃其他位置。

若作業系統或 home 不明確，先以唯讀方式偵測；不得猜測使用者名稱或磁碟代號。Windows PowerShell 使用 `[Environment]::GetFolderPath('UserProfile')` 取得 home。顯示路徑時統一使用正斜線，實際目錄操作使用目前 agent 可用的檔案工具或已確認適用的 shell 指令。

## 參數說明

| 參數 | 類型 | 必填 | 說明 |
| --- | --- | --- | --- |
| `skillName` | string | 否 | 依目錄名稱或 frontmatter `name` 不分大小寫部分匹配 |

## 執行流程

### 列出技能

1. 依目前工具選擇技能目錄；若使用者要求兩邊或工具不明，使用兩個預設目錄並分別標記來源。
2. 以唯讀方式列出目錄下的子目錄。
3. 只將包含精確 `SKILL.md` 入口的目錄視為 skill。
4. 從 frontmatter 讀取 `name` 和 `description`；缺少欄位時標示異常，不自行補值。
5. 依正規化完整路徑去重，再依工具和技能名稱排序。

### 篩選技能

1. 依列出技能流程解析並掃描目錄。
2. 對目錄名稱與 frontmatter `name` 執行不分大小寫的部分匹配。
3. 顯示匹配技能的來源工具、名稱、說明、入口路徑與完整內容。

## 輸出格式

| 工具 | Skill 名稱 | 說明 | 路徑 |
| --- | --- | --- | --- |
| Claude Code | `skill-name` | `skill description` | `~/.claude/skills/skill-name/` |
| Codex | `skill-name` | `skill description` | `~/.codex/skills/skill-name/` |

## Skill 結構

每個 skill 資料夾應包含：

```text
<skills-root>/
└── <skill-name>/
    ├── SKILL.md
    └── references/       # 可選：補充資源
```

```yaml
---
name: skill-name
description: skill 的簡短說明
---

# Skill 標題
```
