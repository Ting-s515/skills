---
name: claude-code-quickstart
description: 提供 Claude Code CLI 新手指令速查，從本地文件查詢 Slash Commands、CLI 主命令、常用啟動旗標、Plan Mode 與權限模式。當使用者查詢 Claude Code CLI quick start、斜線命令、啟動旗標、Plan Mode、權限模式或 YOLO/bypass 權限時使用。
---

# Claude Code CLI Quickstart

回答 Claude Code CLI 指令問題前，先讀取[本地指令速查表](references/claude-code-quickstart.md)。預設以繁體中文回答；一般查詢直接依本地清單提供完整或指定指令的用途。

## 本地查詢規則

- 一般查詢以本地參考文件記載的 CLI 版本與命令清單為準，不瀏覽網路，也不必每次執行 CLI。
- 使用者詢問本機版本或相容性時，唯讀執行 claude --version 或 claude --help。若目前 PowerShell 找不到 claude，本機已知執行檔可用 & "$env:USERPROFILE\.local\bin\claude.exe" --version 查詢；其他安裝位置依實際環境判斷。
- 只有使用者明確要求「更新速查表」、「查最新」或確認最新官方行為時，才查閱官方文件並核對本機 CLI，再更新參考表的版本與查核日期。
- 若本地參考文件遺失，說明缺少該檔案；未獲明確更新要求時，不自動改用網路資料。
- 簡短區分 /command 是互動介面的 Slash Command、claude command 是終端機主命令、--option 是啟動旗標。
- 此技能只查詢與說明指令；不可為展示指令而啟動 Claude、bypass 權限或執行會改變狀態的命令。
