---
name: codex-cli-quickstart
description: 提供 Codex CLI 新手指令速查，從本地參考文件查詢 Slash Commands、CLI 主命令、常用旗標、Plan Mode 與 YOLO 啟動方式。當使用者查詢 Codex CLI quick start、斜線命令、CLI 命令、Plan Mode、YOLO 或 no-daemon 時使用。
---

# Codex CLI Quickstart

為新手提供可快速查閱的 Codex CLI 指令參考。回答前讀取[本地指令速查表](reference/codex-cli-quickstart.md)，預設輸出完整清單；若使用者只詢問特定命令，優先回答該命令及必要的相鄰概念。使用繁體中文，將每項用途濃縮為一句話。

## 本地查詢規則

- 一般查詢以本地參考文件記載的版本和命令清單為準，不瀏覽網路，也不必每次執行 CLI。
- 回答本機版本相容性時，可執行唯讀的 `codex --version` 或 `codex --help`；Slash Command 的實際選單可在互動介面輸入 `/` 查看。
- 若使用者明確要求「更新速查表」、「查最新」或確認最新官方行為，才查閱官方文件並核對本機 CLI，再依查證結果更新本地參考文件與版本日期。
- 若參考文件遺失，說明缺少該檔案；未獲明確更新要求時，不自動改用網路資料。

- 簡短說明 `/command` 是互動介面的斜線命令、`codex command` 是終端機主命令、`--option` 是啟動旗標。
- 此技能只查詢和說明命令；不得為展示而執行 YOLO 或其他會改變執行狀態的命令。
