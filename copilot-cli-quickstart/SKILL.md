---
name: copilot-cli-quickstart
description: 提供 GitHub Copilot CLI 新手指令速查，從本地文件查詢 Slash Commands、CLI 主命令、常用啟動旗標、Plan／Autopilot 模式與權限設定。當使用者查詢 GitHub Copilot CLI、copilot 指令、Copilot 斜線命令、啟動旗標、Plan Mode、Autopilot、權限模式或 YOLO/allow-all 時使用。
---

# GitHub Copilot CLI Quickstart

回答 GitHub Copilot CLI 指令問題前，先讀取[本地指令速查表](references/copilot-cli-quickstart.md)。預設以繁體中文回答；一般查詢直接依本地清單提供完整或指定指令的用途。

## 本地查詢規則

- 一般查詢以本地參考文件記載的 CLI 版本與命令清單為準，不瀏覽網路，也不必每次執行 CLI。
- 使用者詢問本機版本或相容性時，唯讀執行 copilot --version、copilot --help 或 copilot help <topic>。
- 只有使用者明確要求「更新速查表」、「查最新」或確認最新官方行為時，才查閱官方文件與 release note 並核對本機 CLI，再更新參考表的版本與查核日期。
- 若本地參考文件遺失，說明缺少該檔案；未獲明確更新要求時，不自動改用網路資料。
- 簡短區分 /command 是互動介面的 Slash Command、copilot command 是終端機主命令、--option 是啟動旗標。
- 不要與 GitHub CLI 的 gh 指令混淆；gh copilot 只是透過 gh 啟動 Copilot CLI 的包裝。
- 此技能只查詢與說明指令；不可為展示指令而啟動 Copilot、開啟 --yolo/--allow-all 或執行會改變狀態的命令。
