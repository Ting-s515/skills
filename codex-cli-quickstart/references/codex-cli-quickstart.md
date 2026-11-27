# Codex CLI 指令速查表

> 查核日期：2026-11-23<br>
> 本機 CLI 版本：`codex-cli 0.171.0`<br>
> CLI 主命令與旗標：以本機 `codex --help` 為準。Slash Commands：依下方官方 CLI 文件查核；實際選單可能因版本、帳戶與功能而異。

## 先分清命令種類

| 寫法 | 輸入位置 | 用途 |
| --- | --- | --- |
| `codex <command>` | 終端機 | 執行 CLI 主命令，例如 `codex resume`。 |
| `codex --option` | 終端機 | 啟動 CLI 時設定旗標，例如 `--model`。 |
| `/command` | Codex 互動介面的輸入框 | 控制目前對話，例如 `/plan` 或 `/status`。 |

在互動介面輸入 `/` 可開啟命令選單，再輸入名稱篩選。命令選單是目前安裝版本可用 Slash Commands 的直接檢查方式。

## Slash Commands

以下列出官方 Codex CLI 文件中的內建命令。部分命令依 CLI 版本、平台、帳戶或功能開放狀態而異。

### 模式、權限與任務

| 命令 | 用途 |
| --- | --- |
| `/plan [需求]` | 切換至 Plan Mode；可附上第一個規劃需求。任務執行中無法切換。接受計畫後，選擇 **Yes, clear context and implement** 開始實作。 |
| `/goal [目標]` | 設定、查看、編輯、暫停、恢復或清除長期目標。 |
| `/permissions` | 調整 Codex 在目前工作階段可執行的操作與核准方式。 |
| `/approve` | 在自動審查拒絕某項操作後，核准重試一次。 |
| `/experimental` | 開啟或關閉實驗性功能。 |
| `/review` | 檢查目前工作樹的程式碼變更。 |
| `/model` | 選擇模型與可用的推理強度。 |
| `/fast` | 切換目前模型提供的 Fast 服務層級；僅在可用時出現。 |
| `/daybreak` | 切換符合帳戶與模型資格的 Daybreak 功能。 |
| `/voice` | 開始或停止語音對話，或調整語音設定；需版本支援。 |

### 對話、工作目錄與工作樹

| 命令 | 用途 |
| --- | --- |
| `/new` | 在同一個 CLI 中開始新對話。 |
| `/clear` | 清除目前畫面並開始新對話。 |
| `/resume` | 從清單選取並繼續已儲存的對話。 |
| `/fork` | 從目前對話分支出一個新對話，保留原對話。 |
| `/rename [名稱]` | 重新命名目前對話。 |
| `/archive` | 封存目前對話，不刪除紀錄。 |
| `/delete` | 永久刪除目前對話與其後續分支。 |
| `/worktree` | 在 Git worktree 中開始或繼續對話。 |
| `/cd <路徑>` | 將目前對話的工作目錄切換至指定路徑。 |
| `/pwd`、`/cwd` | 顯示目前工作目錄。 |
| `/app` | 在 macOS 或 Windows 的 ChatGPT 桌面應用程式繼續目前對話。 |
| `/exit`、`/quit` | 離開 Codex CLI。 |

### 對話內容與上下文

| 命令 | 用途 |
| --- | --- |
| `/compact` | 摘要目前對話以釋放上下文空間。 |
| `/recap` | 產生目前對話摘要，不壓縮上下文。 |
| `/export [路徑]` | 將完整對話匯出為 Markdown 或複製到剪貼簿。 |
| `/copy` | 複製回覆、程式碼區塊或引用文字。 |
| `/diff` | 顯示 Git diff，包含尚未追蹤的檔案。 |
| `/mention` | 將檔案或資料夾加入目前提示。 |
| `/ide` | 將 IDE 的開啟檔案、選取範圍等內容帶入對話。 |
| `/raw` | 切換純文字捲動模式，方便選取與複製終端機內容。 |

### Agent、背景工作與側邊對話

| 命令 | 用途 |
| --- | --- |
| `/agents` | 開啟 agent 控制中心並切換對話或 agent。 |
| `/subagents` | 查看或切換目前工作階段的 subagent 對話。 |
| `/ps` | 查看背景終端機及近期輸出。 |
| `/stop` | 停止目前工作階段啟動的所有背景終端機。 |
| `/side`、`/btw` | 開啟側邊對話，提出問題而不打斷主對話。 |

### Skills、整合與設定

| 命令 | 用途 |
| --- | --- |
| `/skills` | 瀏覽並使用本機 skills。 |
| `/apps` | 瀏覽連接器並將 app 加入提示。 |
| `/plugins` | 瀏覽、安裝或管理 plugins。 |
| `/hooks` | 檢視與管理生命週期 hooks。 |
| `/mcp [verbose|login <name>]` | 列出 MCP 工具；可顯示伺服器詳細資訊或登入指定伺服器。 |
| `/import` | 匯入支援的 Claude Code 或 Cursor 設定、專案與對話。 |
| `/init` | 在目前目錄建立 `AGENTS.md` 起始範本。 |
| `/logout` | 登出 Codex 並清除本機登入憑證。 |
| `/feedback` | 提交產品意見或儲存診斷資料。 |
| `/config` | 搜尋與調整終端機偏好設定。 |
| `/keymap` | 檢視或調整 TUI 鍵盤快捷鍵。 |
| `/vim` | 切換輸入框的 Vim 編輯模式。 |
| `/tui` | 選擇下次啟動使用捲動或全螢幕介面。 |
| `/setup-default-sandbox` | 設定 Windows 提權 agent sandbox；僅在支援的 Windows 環境使用。 |

### 狀態與終端機外觀

| 命令 | 用途 |
| --- | --- |
| `/status` | 顯示工作階段設定、token 用量與上下文狀態。 |
| `/usage` | 查看帳戶使用量或可用的用量重設。 |
| `/debug-config` | 顯示設定來源與 policy 條件，協助追查設定差異。 |
| `/statusline` | 設定終端機底部狀態列欄位。 |
| `/title` | 設定終端機視窗或分頁標題欄位。 |
| `/theme` | 選擇語法醒目提示主題。 |
| `/pets`、`/pet` | 選擇或隱藏終端機寵物。 |
| `/memories` | 設定是否使用或產生記憶。 |
| `/warnings` | 查看工作階段保留的警告與診斷資訊。 |
| `/daemon` | 檢查背景伺服器連線並管理本機伺服器。 |

## CLI 主命令

以下清單來自本機 Codex CLI `0.171.0` 的 `codex --help`。

| 命令 | 用途 |
| --- | --- |
| `codex agents` | 開啟 agent 控制中心。 |
| `codex exec`、`codex e` | 非互動模式執行 Codex。 |
| `codex review` | 非互動模式檢查程式碼。 |
| `codex login` | 管理登入。 |
| `codex logout` | 移除已儲存的登入憑證。 |
| `codex mcp` | 管理外部 MCP 伺服器。 |
| `codex plugin` | 管理 Codex plugins。 |
| `codex app-server` | 執行 app server 或相關工具；實驗性。 |
| `codex remote-control` | 管理啟用 remote control 的 app-server daemon；實驗性。 |
| `codex app` | 開啟 ChatGPT 桌面應用程式。 |
| `codex completion` | 產生 shell 自動補全指令。 |
| `codex update` | 更新 Codex CLI。 |
| `codex doctor` | 診斷安裝、設定、登入與執行環境。 |
| `codex sandbox` | 在 Codex sandbox 中執行命令。 |
| `codex debug` | 使用除錯工具。 |
| `codex apply`、`codex a` | 將 agent 最近產生的 diff 套用至工作目錄。 |
| `codex resume` | 選取並繼續先前的對話；可使用 `--last`。 |
| `codex queue` | 將提示排入既有工作階段。 |
| `codex archive` | 依 ID 或名稱封存工作階段。 |
| `codex delete` | 依 ID 或名稱永久刪除工作階段。 |
| `codex migrate-rollouts` | 檢視或遷移舊版本機工作階段資料。 |
| `codex migrate-nfs-db` | 原地遷移設定的 SQLite 資料庫；實驗性。 |
| `codex unarchive` | 取消封存工作階段。 |
| `codex fork` | 從先前工作階段建立分支對話；可使用 `--last`。 |
| `codex cloud` | 瀏覽或執行 Codex Cloud 工作；實驗性。 |
| `codex exec-server` | 執行獨立 exec-server 服務；實驗性。 |
| `codex features` | 檢視 feature flags。 |
| `codex help` | 顯示 CLI 或指定子命令的說明。 |

查看巢狀子命令用法：`codex <command> --help`。查看整體用法：`codex --help`。

## 常用啟動旗標

| 旗標 | 用途 |
| --- | --- |
| `-C`、`--cd <DIR>` | 指定 Codex 使用的工作目錄。 |
| `-m`、`--model <MODEL>` | 指定模型。 |
| `-i`、`--image <FILE>` | 附加圖片至初始提示。 |
| `-s`、`--sandbox <MODE>` | 選擇 `read-only`、`workspace-write` 或 `danger-full-access`。 |
| `-a`、`--ask-for-approval <POLICY>` | 選擇 `on-request` 或 `never` 核准策略。 |
| `--worktree` | 在新的 managed Git worktree 中啟動工作階段。 |
| `--search` | 啟用即時網路搜尋。 |
| `--no-alt-screen` | 以 inline 模式顯示 TUI，保留終端機捲動紀錄。 |
| `--no-daemon` | 不使用共用背景伺服器；不能與 `--remote` 或 `codex agents` 搭配。 |
| `-c`、`--config <key=value>` | 為這次執行覆寫設定。 |
| `-p`、`--profile <NAME>` | 疊加指定的 Codex 設定 profile。 |
| `--add-dir <DIR>` | 加入可寫入的額外目錄。 |
| `--approve-for-me` | 透過自動審查處理核准，使用 `workspace-write` sandbox。 |
| `--dangerously-bypass-approvals-and-sandbox` | 略過核准並停用 sandbox；CLI 標示為極度危險。 |

官方 CLI 參考列出 `--yolo` 作為 `--dangerously-bypass-approvals-and-sandbox` 的別名，以及 `codex cloud-tasks` 作為 `codex cloud` 的別名；本機 `0.171.0` 的 `codex --help` 未列出這兩個別名，此快照以本機確認的主命令和完整旗標為準。

### 指定的 YOLO + no-daemon 範例

```sh
codex --dangerously-bypass-approvals-and-sandbox --no-daemon
```

此命令會略過所有核准並在沒有 sandbox 的狀態下執行；`--no-daemon` 同時停用共用背景伺服器。只在了解其影響且執行環境已隔離時使用。

## Plan Mode 操作

1. 在終端機執行 `codex` 進入互動介面。
2. 在輸入框輸入 `/plan` 並按 Enter；也可輸入 `/plan <規劃需求>` 直接開始規劃。
3. Codex 正在執行工作時，`/plan` 暫時不可用；等待該工作完成再切換。
4. 檢視計畫後，選擇 **Yes, clear context and implement** 開始實作。

`/plan` 是互動介面的 Slash Command，不是 `codex --plan` 終端機旗標。

## 常用入門指令

```sh
codex                         # 開啟互動介面
codex "說明這個專案"          # 以提示啟動工作階段
codex --help                  # 查看主命令與全域旗標
codex <command> --help        # 查看指定主命令的用法
codex --version               # 查看本機 CLI 版本
```

## 來源

- [OpenAI：Slash commands in Codex CLI](https://learn.chatgpt.com/docs/developer-commands?surface=cli)，查核日期：2026-11-23。
- [OpenAI：Command line options – Codex CLI](https://learn.chatgpt.com/docs/cli/reference)，查核日期：2026-11-23。
- 本機驗證：`codex --version` 與 `codex --help`，`codex-cli 0.171.0`，日期：2026-11-23。
