---
name: task-session
description: 產生帶有指定任務清單 ID 的 Claude Code 啟動指令
argument-hint: [task-list-id]
disable-model-invocation: true
---

# 任務清單會話啟動器

用戶想要使用任務清單 ID: `$ARGUMENTS`

請執行以下操作：

1. 產生適用於不同終端機的啟動指令：

## PowerShell
```powershell
$env:CLAUDE_CODE_TASK_LIST_ID="$ARGUMENTS"; claude
```

## CMD
```cmd
set CLAUDE_CODE_TASK_LIST_ID=$ARGUMENTS && claude
```

## Bash / Zsh
```bash
CLAUDE_CODE_TASK_LIST_ID="$ARGUMENTS" claude
```

2. 告訴用戶複製上述指令到終端機執行，即可啟動帶有該任務清單的新 Claude Code 會話。

3. 如果用戶想要在當前會話查看任務清單，使用 TaskList 工具顯示現有任務。
