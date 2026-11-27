# GitHub Copilot CLI 指令速查表

> 查核日期：2026-11-26<br>
> 本機 CLI 版本：GitHub Copilot CLI 1.0.116，與官方 Releases 最新版（2026-11-25）一致。<br>
> 本機執行檔：VS Code 提供的 shim，位於 %LOCALAPPDATA%\Programs\Microsoft VS Code\bin\copilot-shim\copilot；已在 PATH 中。<br>
> CLI 主命令、旗標與 Slash Commands 以本機 copilot --help 與 copilot help commands 為準；安裝方式與訂閱需求依官方文件整理。命令實際可用性可能依版本、方案、組織政策與 experimental 設定而異。

## 先分清命令種類

| 寫法 | 輸入位置 | 用途 |
| --- | --- | --- |
| copilot &lt;command&gt; | 終端機 | 執行 CLI 主命令，例如 copilot login。 |
| copilot --option | 終端機 | 啟動 Copilot CLI 時設定旗標，例如 --model。 |
| /command | Copilot CLI 互動介面 | 控制目前工作階段，例如 /plan、/model。 |
| copilot help &lt;topic&gt; | 終端機 | 查看主題說明，例如 copilot help permissions。 |

Copilot CLI 是獨立的 AI coding agent，指令是 copilot；不要與 GitHub CLI 的 gh 混淆。gh copilot 只是透過 gh 下載並啟動同一個 Copilot CLI（preview）。

## 安裝與前置需求

以下依官方安裝文件整理：

| 方式 | 指令 |
| --- | --- |
| npm（所有平台，需 Node.js 22+） | npm install -g @github/copilot |
| WinGet（Windows） | winget install GitHub.Copilot |
| Homebrew（macOS／Linux） | brew install --cask copilot-cli |
| 安裝腳本（macOS／Linux） | curl -fsSL https://gh.io/copilot-install \| bash |

- 需要有效的 GitHub Copilot 訂閱；使用自備模型供應商或符合資格的 Microsoft Entra 帳戶時例外。
- 組織或企業管理員可停用 Copilot CLI。
- 本機已透過 VS Code shim 提供 copilot 指令，不需另外安裝。

## 快速啟動

| 指令 | 用途 |
| --- | --- |
| copilot | 開啟互動工作階段。 |
| copilot -i "修正 main.js 的錯誤" | 開啟互動工作階段並自動送出初始提示。 |
| copilot -p "說明這段函式" | 非互動模式執行後結束。 |
| copilot -p "整理變更" -s | 非互動模式只輸出回答，不輸出統計，適合腳本。 |
| copilot --continue | 繼續最近的工作階段。 |
| copilot --resume | 開啟工作階段選擇清單；可接 ID、ID 前綴或名稱。 |
| copilot --name "my feature" | 為新工作階段命名。 |
| copilot --plan | 以 Plan 模式啟動。 |
| copilot login | 登入 Copilot。 |
| copilot init | 為 repository 建立 Copilot 指引檔。 |
| copilot --help、copilot &lt;command&gt; --help | 顯示旗標與主命令說明。 |
| copilot --version | 顯示本機 CLI 版本。 |

## Slash Commands

以下依本機 copilot help commands 分組整理。在互動介面輸入 /help，或在空白提示列輸入 ? 可查看快捷鍵。

### Agent 環境

| 命令 | 用途 |
| --- | --- |
| **/init** | 建立 Copilot 指引檔；可在後面補充指引。 |
| **/agent [name]** | 瀏覽並選擇自訂 agent。 |
| **/skills** | 管理 Skills。 |
| **/mcp** | 管理 MCP 伺服器設定。 |
| **/plugin** | 管理 Plugins 與 marketplace。 |

### Agents 與 Subagents

| 命令 | 用途 |
| --- | --- |
| **/model** | 切換本工作階段模型；auto 由 Copilot 自動選擇；保留對話紀錄。 |
| **/delegate** | 將工作階段送到 GitHub，由 Copilot 建立 PR；--base 指定目標分支。 |
| **/fleet** | 啟用 fleet 模式，平行執行 subagents。 |
| **/autopilot** | 切換 Autopilot 模式，或設定目標與 AI credit 上限（--max-ai-credits）。 |
| **/tasks** | 查看 subagents、背景 shell 與 workflow run；選取後按 x 停止。 |
| **/subagents** | 設定各 subagent 的模型、開關與設定。 |

### 程式碼

| 命令 | 用途 |
| --- | --- |
| **/ide** | 連接 IDE 工作區。 |
| **/diff** | 檢視目前目錄的變更。 |
| **/pr** | 操作目前分支的 pull request。 |
| **/review** | 執行 code review agent 分析變更。 |
| **/security-review** | 掃描未提交變更的安全漏洞；工作樹乾淨時改掃分支差異。 |
| **/rubber-duck** | 由 rubber duck agent 對目前工作提出獨立評論。 |
| **/lsp** | 管理 language server 設定。 |
| **/terminal-setup** | 設定終端機支援 Shift+Enter 多行輸入。 |

### 權限

| 命令 | 用途 |
| --- | --- |
| **/permissions** | 切換權限模式，例如 /permissions manual、/permissions allow-all。 |
| **/allow-all** | 開啟全部權限（工具、路徑、URL）。 |
| **/sandbox** | 管理 sandbox 設定；加 session 只套用本工作階段。 |
| **/add-dir** | 允許存取額外目錄並載入其 .github skills 與 agents。 |
| **/list-dirs** | 顯示允許的目錄與路徑授權。 |
| **/cwd** | 切換或顯示工作目錄。 |
| **/reset-allowed-tools** | 重設工作階段授權、關閉 allow-all，並清除此位置的已存授權。 |

### 工作階段

| 命令 | 用途 |
| --- | --- |
| **/new** | 開始新對話。 |
| **/clear** | 放棄目前工作階段並重新開始。 |
| **/resume** | 依本機或雲端紀錄 ID、task ID 或名稱切換工作階段。 |
| **/rename** | 重新命名工作階段，或依對話自動命名。 |
| **/fork** | 複製目前工作階段並切換過去；/fork worktree 會分到新 worktree。 |
| **/worktree** | 從設定的 base ref 建立新 git worktree 並切換，未提交變更留在原處。 |
| **/move** | 把未提交變更移到新 git worktree 並切換。 |
| **/context** | 查看上下文 token 用量分布。 |
| **/usage** | 查看工作階段用量與統計。 |
| **/limits** | 查看或編輯工作階段限制；AI Credit 上限為軟上限。 |
| **/session** | 查看與管理工作階段。 |
| **/compact** | 摘要對話以減少上下文用量；可附上重點指示。 |
| **/share** | 分享或匯出工作階段為 file、html、gist、research 或 link。 |
| **/copy** | 將最近一則回答以 Markdown 複製到剪貼簿。 |
| **/rewind** | 回到較早的回合，可選擇只還原對話或一併還原檔案；無法復原，必要時先 /fork。 |
| **/remote** | 查看遠端狀態或切換由 GitHub 網頁／行動裝置遠端操作。 |

### 規劃、研究與排程

| 命令 | 用途 |
| --- | --- |
| **/plan** | 在寫程式前先建立實作計畫。 |
| **/research** | 使用 GitHub 搜尋與網路來源進行深入研究。 |
| **/refine** | 將雜亂的提示改寫成清楚版本；也可用 Ctrl+X 再按 /。 |
| **/ask** | 提出不加入歷史的側邊問題。 |
| **/after** | 排程本工作階段的一次性提示，例如 /after 30m 跑測試。 |
| **/every** | 排程週期性提示，例如 /every 5m run tests；省略時間由模型自行調整。 |
| **/chronicle** | 工作階段歷史工具與洞察。 |
| **/search** | 搜尋對話時間軸（experimental）。 |

### 說明、設定與帳戶

| 命令 | 用途 |
| --- | --- |
| **/help** | 顯示互動命令說明。 |
| **/config** | 開啟設定畫面或指定區域，例如 /config mcp。 |
| **/settings** | 開啟設定 UI，或 show、set、unset 單一設定值。 |
| **/instructions** | 查看與切換自訂指引檔。 |
| **/memory** | 查看記憶狀態，或啟用／停用跨工作階段記憶。 |
| **/env** | 顯示已載入的指引、MCP、skills、agents、hooks、plugins 等。 |
| **/environments** | 管理進出連線的 Environments 畫面。 |
| **/theme** | 開啟色彩模式選擇器。 |
| **/statusline**、**/footer** | 設定狀態列項目。 |
| **/vim** | 切換輸入列 Vim 模式。 |
| **/voice** | 管理語音聽寫模式。 |
| **/experimental** | 查看可用的 experimental 功能。 |
| **/computer** | 查看或切換 Computer Use。 |
| **/keep-alive** | 執行期間防止系統休眠。 |
| **/login**、**/logout** | 登入或登出 Copilot 帳戶；/logout 不會登出 GH_TOKEN 或 gh 的登入。 |
| **/user** | 管理已登入的帳戶。 |
| **/version**、**/update** | 查看版本並檢查更新，或更新至最新版。 |
| **/changelog** | 查看版本變更記錄；加 summarize 取得 AI 摘要。 |
| **/diagnose** | 分析工作階段 log，包含權限請求為何需要核准。 |
| **/collect-debug-logs** | 收集除錯 log 為本機 .tgz。 |
| **/feedback** | 回報錯誤或功能需求。 |
| **/app** | 開啟 GitHub Copilot 桌面 App。 |
| **/restart** | 重新啟動 CLI 並恢復工作階段。 |
| **/exit** | 離開 CLI。 |

## 輸入前綴與快捷鍵

| 輸入 | 用途 |
| --- | --- |
| @檔案路徑 | 將檔案內容加入上下文。 |
| #NUMBER | 將 GitHub issue 或 PR 加入上下文（官方文件）。 |
| !指令 | 不經過 agent 直接執行 shell 指令；Windows 使用 PowerShell。 |
| ! | 空白提示列輸入 ! 進入 shell 模式；Esc 離開。 |
| $ | 單獨輸入 $ 將終端機交給真正的 shell，適合需要輸入密碼的 sudo、ssh、git。 |
| Shift+Tab | 循環切換 standard、plan、autopilot 模式（官方文件）。 |
| Enter（agent 執行中） | 將訊息插入目前回合，agent 會在下一次請求前讀取。 |
| Ctrl+Q | 將訊息排入佇列，在目前回合結束後執行。 |
| Esc Esc | 中斷目前回合；空白閒置提示列時開啟 /rewind。 |
| Ctrl+C | 立即停止回合或清除提示列；空白提示列連按兩次離開。 |
| Ctrl+D | 空白提示列時立即離開。 |
| Shift+Enter、Alt+Enter、Ctrl+J | 換行；Shift+Enter 無效時執行 /terminal-setup。 |
| Ctrl+G | 用外部編輯器編寫提示。 |
| Ctrl+R | 搜尋提示歷史。 |
| Ctrl+S | 暫存草稿並清空提示列，再按一次還原。 |

`!` 指令的輸出是否加入上下文，依官方命令參考說明為不加入（官方文件，未本機實測）。

## CLI 主命令

| 命令 | 用途 |
| --- | --- |
| **copilot login** | 登入 Copilot。 |
| **copilot init** | 初始化 Copilot 指引檔。 |
| **copilot config [key] [value]** | 查看或修改設定。 |
| **copilot update [channel]** | 下載最新版本。 |
| **copilot version** | 顯示版本資訊。 |
| **copilot app** | 開啟 GitHub Copilot App。 |
| **copilot sessions import** | 從 JSONL 匯入工作階段。 |
| **copilot memories import** | 匯入記憶。 |
| **copilot workflow run** | 執行已註冊的動態 workflow。 |
| **copilot mcp** | 管理 MCP；子命令包含 list、get、add、remove、enable、disable。 |
| **copilot plugin** | 管理 Plugin；子命令包含 install、uninstall、update、list、enable、disable、marketplace。 |
| **copilot skill** | 管理 Skill；子命令包含 list、add、remove、enable、disable。 |
| **copilot instruction list** | 列出偵測到的指引來源。 |
| **copilot lsp** | 檢視 language server 設定。 |
| **copilot sandbox ca** | 管理 credential proxy 憑證授權。 |
| **copilot completion** | 產生 shell 自動完成腳本。 |
| **copilot help [topic]** | 顯示說明；主題包含 commands、permissions、config、environment、input、sessions、skills、mcp、hooks、billing、providers 等。 |

## 常用啟動旗標

| 旗標 | 用途 |
| --- | --- |
| **-p**、**--prompt &lt;text&gt;** | 非互動模式執行後結束。 |
| **-i**、**--interactive &lt;prompt&gt;** | 開啟互動模式並自動送出提示。 |
| **-s**、**--silent** | 只輸出回答，搭配 -p 用於腳本。 |
| **--output-format &lt;text\|json&gt;** | 設定輸出格式；json 為每行一個物件的 JSONL。 |
| **--continue** | 繼續最近的工作階段。 |
| **-r**、**--resume [value]** | 依 ID、ID 前綴、task ID 或名稱恢復，或開啟選擇清單。 |
| **-n**、**--name &lt;name&gt;** | 為新工作階段命名。 |
| **-C &lt;directory&gt;** | 先切換工作目錄再啟動。 |
| **--model &lt;model&gt;** | 指定模型；auto 由 Copilot 自動選擇。 |
| **--reasoning-effort &lt;level&gt;** | 指定推理強度：none、minimal、low、medium、high、xhigh、max；依模型支援。 |
| **--mode &lt;mode&gt;** | 指定初始模式：interactive、plan、autopilot。 |
| **--plan** | 以 Plan 模式啟動；搭配 --mode autopilot 會自動核准計畫並實作。 |
| **--autopilot** | 以 Autopilot 模式啟動。 |
| **--max-autopilot-continues &lt;count&gt;** | Autopilot 最多自動續行次數，預設 5。 |
| **--max-ai-credits &lt;credits&gt;** | 設定本工作階段 AI credit 上限。 |
| **--fleet** | 以 fleet 模式平行執行 subagents。 |
| **--agent &lt;agent&gt;** | 指定自訂 agent。 |
| **--add-dir &lt;directory&gt;** | 允許存取額外目錄，可重複使用。 |
| **--allow-tool &lt;rules&gt;** | 允許指定工具不詢問，例如 'shell(npm:*)'、'write'。 |
| **--deny-tool &lt;rules&gt;** | 禁止指定工具，例如 'shell(git push)'；優先於所有 allow。 |
| **--allow-url**、**--deny-url** | 允許或禁止指定 URL／網域。 |
| **--available-tools**、**--excluded-tools** | 限定或排除模型可見的工具。 |
| **--allow-all-tools** | 所有工具自動執行不詢問。 |
| **--allow-all-paths** | 停用檔案路徑檢查。 |
| **--allow-all-urls** | 允許所有 URL。 |
| **--allow-all**、**--yolo** | 等同以上三者全開。 |
| **--assisted-approval** | 由 assisted-approval 安全判斷模型審核權限請求；非安全邊界。 |
| **--sandbox** | 本次執行的 shell 指令在 OS 層級 sandbox 內執行。 |
| **--trust-folder** | 僅本次 prompt 模式信任目前資料夾設定。 |
| **--additional-mcp-config &lt;json&gt;** | 加入額外 MCP 設定；@ 開頭表示檔案路徑。 |
| **--disable-mcp-server**、**--enable-mcp-server** | 本次停用或啟用指定 MCP 伺服器。 |
| **--plugin-dir &lt;directory&gt;** | 從本機目錄載入 Plugin。 |
| **--no-custom-instructions** | 不載入 AGENTS.md 等自訂指引。 |
| **--enable-memory** | 在 prompt 模式啟用記憶（預設停用）。 |
| **--share [path]**、**--share-gist** | 非互動模式結束後匯出為 Markdown 或私密 gist。 |
| **--usage-output-file &lt;file&gt;** | 結束時將用量統計寫成 JSON。 |
| **--secret-env-vars &lt;vars&gt;** | 從 shell 與 MCP 環境移除指定環境變數。 |
| **--acp** | 以 Agent Client Protocol 伺服器啟動。 |
| **--experimental**、**--no-experimental** | 啟用或停用 experimental 功能。 |
| **--no-auto-update** | 停用自動下載更新。 |
| **--log-level &lt;level&gt;**、**--log-dir &lt;dir&gt;** | 設定 log 等級與目錄。 |
| **-v**、**--version**、**-h**、**--help** | 顯示版本或說明。 |

### YOLO／allow-all 權限

本機 1.0.116 同時支援 --yolo 與 --allow-all，兩者都等同 --allow-all-tools --allow-all-paths --allow-all-urls。工作階段中可用 /allow-all 或 /permissions allow-all 開啟，/permissions manual 關閉。

即使在 allow-all 模式，以下情況仍會詢問或拒絕：

- --deny-tool 規則仍會拒絕。
- 要求在 sandbox 外執行的指令一律詢問。
- 組織政策的 permissions.deny、ask、allow 規則仍生效。
- 組織設定 permissions.disableBypassPermissionsMode 為 disable 時會關閉 allow-all。

只建議在隔離環境或可信任的專案使用。

## Plan、Autopilot 與權限模式切換

### 模式

| 模式 | 行為 |
| --- | --- |
| interactive（standard） | 預設模式；修改檔案、執行 shell 指令、存取外部路徑或 URL、呼叫 MCP 工具前會詢問，唯讀指令直接執行。 |
| plan | 先建立實作計畫再寫程式。 |
| autopilot | agent 自動續行完成目標；原本需要詢問的權限請求會被拒絕，問題由 agent 自行推測後繼續。 |

### 切換方式

| 方式 | 指令或操作 | 說明 |
| --- | --- | --- |
| 工作階段中循環切換 | Shift+Tab | 循環 standard、plan、autopilot（官方文件）。 |
| 工作階段中進入 Plan | /plan | 先建立實作計畫。 |
| 工作階段中切換 Autopilot | /autopilot [目標] | 可加 --max-ai-credits 限制用量。 |
| 啟動時指定模式 | copilot --mode plan | 也可指定 interactive 或 autopilot。 |
| 啟動時 Plan 後自動實作 | copilot --plan --mode autopilot | 自動核准計畫並實作。 |
| 切換權限模式 | /permissions | 例如 /permissions manual、/permissions allow-all。 |

### 權限核准選項

詢問權限時可選擇：只允許這次、在此 repo 或目錄不再詢問（存於 ~/.copilot/permissions-config.json）、本工作階段都允許，或拒絕並告訴 Copilot 改做什麼。Autopilot 與 -p 模式無法詢問，無人值守時需搭配 --allow-all 或 --allow-tool 規則。

## 預設模型設定

本機 1.0.116 實測（`copilot -p ... --usage-output-file` 讀取實際使用的模型）：

| 設定位置 | 寫法 | 作用範圍 |
| --- | --- | --- |
| 啟動旗標 | copilot --model claude-sonnet-5.5 | 單次啟動。 |
| 使用者設定 | copilot config model claude-haiku-5.5 | 寫入 ~/.copilot/settings.json，之後所有工作階段預設。 |
| 專案設定 | 在 repo 內寫入 .github/copilot/settings.json 的 "model" | 只在該 git repo 內生效（需 git repo 且受信任）。 |
| 互動介面 | /model（本次）、/config model（預設） | /model 只影響目前工作階段。 |

優先順序（實測）：啟動旗標 > 專案設定 > 使用者設定。

- 模型 ID 必須是帳戶可用的名稱，例如 `claude-haiku-5.5`；`claude-haiku-5-5` 會被拒絕。
- 未驗證：`/model --global` 在本機 help 找不到，不要使用。

## 自訂指令（Custom Instructions）

本機 1.0.116 的 `copilot help config` 說明，指令來源依序為：repository 根目錄與目前目錄中的 `CLAUDE.md`、`.claude/CLAUDE.md`、`.claude/rules/**/*.md`、`.github/instructions/**/*.instructions.md`、`.github/copilot-instructions.md`；個人層級的 `~/.copilot/copilot-instructions.md` 與 `~/.copilot/instructions/*.instructions.md`；以及 `COPILOT_CUSTOM_INSTRUCTIONS_DIRS` 指定的額外目錄。

| 指令或變數 | 用途 |
| --- | --- |
| copilot instruction list | 列出目前會載入的指令來源（本機實測）。 |
| COPILOT_CUSTOM_INSTRUCTIONS_DIRS | 逗號分隔的額外指令目錄，會與 git root、目前目錄一起搜尋（help 說明）。 |
| --no-custom-instructions | 本次不載入 AGENTS.md 等自訂指引。 |
| /instructions | 互動介面中查看與切換指令檔。 |

- 個人指令放在 `~/.copilot/copilot-instructions.md`，不是 `~/.copilot/AGENTS.md`。
- `COPILOT_CUSTOM_INSTRUCTIONS_DIRS` 是使用者層級環境變數，只影響新開的終端機或 Copilot 工作階段。
- 本機實測（1.0.116，測試時以單次指令設定環境變數）：未設定時 `copilot instruction list` 不列出 `~/.copilot/AGENTS.md`；設定 `COPILOT_CUSTOM_INSTRUCTIONS_DIRS=~/.copilot` 後，清單多出一筆 `Nested AGENTS.md`；指向空目錄或不存在的目錄時則沒有多出項目。
- 互動介面實測：`/instructions` 會列出 AGENTS.md，確認指令已載入。
- 永久設定：使用者層級環境變數 `COPILOT_CUSTOM_INSTRUCTIONS_DIRS=C:\Users\<user>\.copilot`；從 User 範圍載入後，`copilot instruction list` 會多出 `Nested AGENTS.md`。新開的終端機才會讀到永久值。

## 官方查核來源

- [GitHub Copilot CLI 文件](https://docs.github.com/en/copilot/how-tos/copilot-cli)
- [安裝 GitHub Copilot CLI](https://docs.github.com/en/copilot/how-tos/copilot-cli/set-up-copilot-cli/install-copilot-cli)
- [Copilot CLI Quickstart](https://docs.github.com/en/copilot/get-started/cli-quickstart)
- [Copilot CLI 命令參考](https://docs.github.com/en/copilot/reference/cli-command-reference)
- [github/copilot-cli Releases](https://github.com/github/copilot-cli/releases)
