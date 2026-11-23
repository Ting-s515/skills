---
name: codex-cli-quickstart
description: 提供 Codex CLI 新手指令速查，整理 Slash Commands、CLI 主命令與常用旗標，並說明 Plan Mode 和 YOLO 啟動方式。當使用者查詢 Codex CLI quick start、斜線命令、CLI 命令、Plan Mode、YOLO 或 no-daemon 時使用。
---

# Codex CLI Quickstart

為新手提供可快速查閱的 Codex CLI 指令參考。預設輸出完整速查表；若使用者只詢問特定命令，優先回答該命令及必要的相鄰概念。使用繁體中文，將每項用途濃縮為一句話。

## 查核來源與版本

每次回答涉及命令是否存在、語法或支援狀態時，都要先查證：

1. 查閱 OpenAI 官方 [Codex CLI Slash Commands 文件](https://learn.chatgpt.com/docs/developer-commands?surface=cli) 與 [CLI 命令和旗標參考](https://learn.chatgpt.com/docs/cli/reference)。
2. 若目前環境可執行 Codex，執行 `codex --version` 和 `codex --help`。CLI 主命令以本機版本的 help 為準；Slash Commands 以官方文件為基準，並提醒使用者在互動介面輸入 `/` 查看該安裝版本的實際選單。
3. 在完整速查表標示查核日期及本機版本。標示實驗性命令，以及依帳戶、模型、功能或版本而異的命令。
4. 官方文件與本機輸出不一致時，清楚區分「本機版本可用」和「官方文件另有記載」，不要把較新文件中的命令說成本機已支援。
5. 若無法瀏覽官方文件或執行本機 CLI，說明哪些部分未能即時核實；不要猜測最新命令清單。

## 完整速查表內容

完整速查表依序包含：

1. **先分清兩種命令**：`/command` 是互動介面中的 Slash Command；`codex command` 是終端機 CLI 主命令；`--option` 是啟動旗標。
2. **Slash Commands**：列出官方文件中的所有內建命令，按用途分組並簡述功能。保留別名、參數概要和條件式可用標記；不自行刪減為「常用命令」。
3. **CLI 主命令**：完整列出本機 `codex --help` 的主命令與別名，每項以一句話說明；標示 experimental。巢狀子命令與完整旗標不展開，提供 `codex <command> --help` 作為查閱方式。
4. **常用啟動旗標**：依本機 help 列出工作目錄、模型、圖片、網路搜尋、sandbox、worktree、daemon 等新手常用旗標。僅列出本機版本確認支援的語法。
5. **Plan Mode**：明確說明在互動介面輸入 `/plan` 並按 Enter；可輸入 `/plan <規劃需求>` 一併開始規劃。工作進行中時不能切換。完成規劃後，選擇 Codex 提供的「Yes, clear context and implement」流程開始實作。不要將它描述成 `codex --plan` 旗標。
6. **YOLO 啟動範例**：原樣列出使用者要求的命令，並分別解釋兩個旗標：

   ```sh
   codex --dangerously-bypass-approvals-and-sandbox --no-daemon
   ```

   `--dangerously-bypass-approvals-and-sandbox` 會略過核准與 sandbox；`--no-daemon` 會停用共用背景伺服器。只有本機版本確認支援 `--yolo` 時才列為短寫；若只在官方新文件中出現，標示版本差異。清楚說明此組合的執行效果，不要將它設定為一般新手建議。

## 回答方式

- 以分組表格呈現命令與簡短用途；範例只保留能說明輸入位置或切換方式的內容。
- 說明 Slash Command 的可用性可能隨版本、登入狀態、模型或功能而變；建議輸入 `/` 開啟選單並搜尋命令名稱。
- 在有版本差異、條件限制或特殊執行效果的項目旁放置官方文件連結。
- 此技能只提供查詢與說明；不得為展示而執行 YOLO 或其他會改變執行狀態的命令。只讀的 `codex --version` 與 `codex --help` 可用於查核。
