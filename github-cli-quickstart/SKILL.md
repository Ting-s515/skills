---
name: github-cli-quickstart
description: 提供 GitHub CLI（gh）新手指令速查，從本地文件查詢登入驗證、Repo、PR、Issue、Actions、Release、API 與常用旗標。當使用者查詢 GitHub CLI quick start、gh 指令、gh pr、gh issue、gh run、gh api、gh auth 或 GitHub 命令列操作時使用。
---

# GitHub CLI Quickstart

回答 GitHub CLI（gh）指令問題前，先讀取[本地指令速查表](reference/github-cli-quickstart.md)。預設以繁體中文回答；一般查詢直接依本地清單提供完整或指定指令的用途。

## 本地查詢規則

- 一般查詢以本地參考文件記載的 CLI 版本與命令清單為準，不瀏覽網路，也不必每次執行 CLI。
- 使用者詢問本機版本或相容性時，唯讀執行 gh --version、gh --help 或 gh <command> <subcommand> --help。
- 只有使用者明確要求「更新速查表」、「查最新」或確認最新官方行為時，才查閱官方手冊與 release note 並核對本機 CLI，再更新參考表的版本與查核日期。
- 若本地參考文件遺失，說明缺少該檔案；未獲明確更新要求時，不自動改用網路資料。
- 簡短區分 gh <command> 是主命令、gh <command> <subcommand> 是子命令、--option 是旗標；-R/--repo 可指定其他 repository。
- 此技能只查詢與說明指令；不可為展示指令而執行 gh auth login/logout、建立或合併 PR、刪除 repo/release/secret 等會改變狀態的命令，也不可輸出 gh auth token 的內容。
