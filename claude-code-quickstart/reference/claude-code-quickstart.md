# Claude Code CLI 指令速查表

> 查核日期：2026-11-23<br>
> 本機 CLI 版本：Claude Code 2.1.330<br>
> 本機執行檔：%USERPROFILE%\.local\bin\claude.exe；目前 PowerShell 的 PATH 未包含此路徑。<br>
> CLI 主命令與旗標以本機 --help 和巢狀命令的 --help 為準；Slash Commands 依官方命令參考整理。命令實際可用性可能依版本、平台、方案、帳戶與設定而異。

## 先分清命令種類

| 寫法 | 輸入位置 | 用途 |
| --- | --- | --- |
| claude &lt;command&gt; | 終端機 | 執行 CLI 主命令，例如 claude auth status。 |
| claude --option | 終端機 | 啟動 Claude Code 時設定旗標，例如 --model。 |
| /command | Claude Code 互動介面 | 控制目前工作階段，例如 /plan、/model。 |

在互動介面輸入 / 可查看目前可用命令，再輸入字母篩選。部分命令只在指定平台、方案或功能啟用時出現；少數命令需輸入完整名稱才會顯示。

## 快速啟動

以下範例適用於已將 claude 加入 PATH 的終端機：

| 指令 | 用途 |
| --- | --- |
| claude | 開啟互動工作階段。 |
| claude "分析目前專案" | 開啟互動工作階段並送出初始提示。 |
| claude -p "說明這段函式" | 非互動模式輸出結果後結束。 |
| Get-Content log.txt \| claude -p "解釋這些錯誤" | 在 Windows PowerShell 將文字透過 stdin 傳給 Claude。 |
| claude --continue | 繼續目前目錄最近的對話。 |
| claude --resume "&lt;session&gt;" | 依工作階段 ID 或名稱恢復對話。 |
| claude --help | 顯示 CLI 旗標與主命令。 |
| claude &lt;command&gt; --help | 顯示指定主命令的用法，例如 claude mcp --help。 |
| claude --version | 顯示本機 CLI 版本。 |

### 本機 Windows 安裝查詢

本機實測版本為 2.1.330。若 PowerShell 找不到 claude，可用已確認的安裝位置查詢：

    & "$env:USERPROFILE\.local\bin\claude.exe" --version
    & "$env:USERPROFILE\.local\bin\claude.exe" --help

不同電腦的安裝路徑可能不同；一般安裝並設定好 PATH 後可直接使用 claude。

## Slash Commands

以下依官方命令參考按用途分組；名稱中的 &lt;arg&gt; 表示必要參數，[arg] 表示選用參數。標記為 Skill 或 Workflow 的項目是隨附的提示或工作流程，不代表另一個 CLI 子命令。

### 專案、模式與設定

| 命令 | 用途 |
| --- | --- |
| **/add-dir &lt;path&gt;** | 將目錄加入本工作階段可讀寫的工作範圍。 |
| **/cd &lt;path&gt;** | 切換本工作階段的工作目錄並保留對話。 |
| **/init** | 在專案建立 CLAUDE.md 起始指南。 |
| **/memory** | 編輯 CLAUDE.md、管理自動記憶或查看記憶項目。 |
| **/plan [description]** | 進入 Plan Mode；可附上要規劃的工作。 |
| **/permissions**、**/allowed-tools** | 管理工具的允許、詢問與拒絕規則。 |
| **/config**、**/settings** | 查看與調整設定。 |
| **/update-config [request]** | 依描述修改對應的設定檔。 |
| **/sandbox** | 切換 sandbox 模式；僅限支援的平台。 |
| **/model [model]** | 切換模型。 |
| **/effort [level]** | 調整推理強度。 |
| **/output-style [style]** | 列出或切換輸出風格。 |
| **/advisor [model\|off]** | 設定輔助模型；依帳戶功能而異。 |
| **/auto-mode-setup** | 草擬 Auto Mode 環境規則；依方案與版本而異。 |
| **/autocompact [auto\|tokens]** | 設定自動摘要上下文的門檻。 |
| **/fast [on\|off]** | 切換 Fast Mode；供應情況依帳戶而異。 |
| **/hooks** | 查看 hook 設定。 |
| **/mcp** | 管理 MCP 伺服器連線與驗證。 |
| **/status** | 查看版本、模型、帳戶與連線狀態。 |
| **/statusline** | 設定終端機狀態列。 |
| **/doctor**、**/checkup** | 診斷安裝、設定與專案指引問題。 |

### 對話與上下文

| 命令 | 用途 |
| --- | --- |
| **/clear**、**/reset**、**/new** | 清空目前上下文並開始新對話。 |
| **/compact [instructions]** | 摘要對話以釋放上下文空間。 |
| **/context [all]** | 查看上下文使用量與容量提醒。 |
| **/copy [N]** | 複製最近一則回答或選取其中的區塊。 |
| **/export [filename]** | 將目前對話匯出為純文字。 |
| **/btw [question]** | 提出不加入主對話歷史的側邊問題。 |
| **/goal [condition\|clear]** | 設定、查看或清除工作目標。 |
| **/recap** | 產生目前工作階段的一行摘要。 |
| **/rename [name]** | 重新命名目前工作階段。 |
| **/resume [session]**、**/continue** | 從 ID、名稱或清單恢復對話。 |
| **/rewind**、**/checkpoint**、**/undo** | 回到對話或程式碼檢查點。 |
| **/exit**、**/quit** | 離開 CLI；附加的背景工作階段會繼續執行。 |
| **/help** | 顯示說明與可用命令。 |
| **/login**、**/logout** | 登入或登出 Anthropic 帳戶。 |

### 程式碼檢視、診斷與驗證

| 命令 | 用途 |
| --- | --- |
| **/diff** | 查看目前工作樹中的變更。 |
| **/code-review [target]**、**/review [target]** | 檢查目前差異或指定 PR、分支、路徑；支援修正選項。 |
| **/security-review** | 檢查目前分支的安全風險。 |
| **/simplify [target]** | 檢查變更並套用簡化建議。 |
| **/ultrareview [PR or branch]** | 在雲端執行深入多代理審查；也可用 /code-review ultra。 |
| **/run** | 啟動應用程式並觀察變更是否實際生效。 |
| **/verify** | 建置、啟動並觀察應用程式以驗證變更。 |
| **/run-skill-generator** | 為專案產生供 /run 和 /verify 使用的技能。 |
| **/debug [description]** | 開啟工作階段除錯記錄並協助診斷。 |
| **/autofix-pr [prompt]** | 監看 PR CI 與審查留言並建立修正；需 gh 與 Cloud Sessions。 |
| **/heapdump** | 產生記憶體診斷檔；不會出現在一般命令選單，heap snapshot 含對話與憑證，勿分享。 |

### Agent、背景工作與雲端工作

| 命令 | 用途 |
| --- | --- |
| **/agents** | 管理或查看 subagents。 |
| **/background [prompt]**、**/bg** | 將目前工作階段轉為背景工作並釋出終端機。 |
| **/batch &lt;instruction&gt;** | 將大型工作拆分至多個隔離 worktree 平行執行。 |
| **/branch [name]** | 從目前對話建立分支並切換至新分支。 |
| **/fork [prompt]** | 複製目前對話為背景工作階段。 |
| **/list-agents**、**/peers** | 查看可互相傳訊的 agent、隊友與工作階段。 |
| **/subtask &lt;task&gt;** | 啟動會將結果帶回目前對話的背景 subagent。 |
| **/stop** | 停止目前附加的背景工作階段。 |
| **/tasks**、**/bashes** | 查看目前工作階段的背景工作。 |
| **/team-onboarding** | 依近期使用紀錄產生團隊上手指南。 |
| **/loop [interval] [prompt]**、**/proactive** | 在工作階段保持開啟時重複執行提示。 |
| **/schedule [description]**、**/routines** | 建立、管理或執行雲端排程工作。 |
| **/workflows** | 查看、暫停、恢復或儲存工作流程。 |
| **/workflow-authoring** | 載入動態 Workflow 腳本撰寫指引。 |
| **/remote-control**、**/rc** | 讓目前工作階段可由 Claude 網頁或 App 遠端操作。 |
| **/remote-env** | 選擇新雲端工作階段使用的環境。 |
| **/teleport**、**/tp** | 將雲端工作階段接回目前終端機。 |

### Skills、Plugins 與外部整合

| 命令 | 用途 |
| --- | --- |
| **/skills** | 瀏覽可用 Skills。 |
| **/skill-doctor** | 查看各 Skill 的上下文用量與使用情形。 |
| **/reload-skills** | 重新掃描 Skill 與命令目錄。 |
| **/plugin [subcommand]** | 瀏覽或管理 Plugins。 |
| **/plugin-authoring** | 載入 Mod 撰寫指引；需支援版本與功能。 |
| **/reload-plugins [--force]** | 重新載入已啟用的 Plugins。 |
| **/fewer-permission-prompts** | 依常見唯讀操作建議權限允許清單。 |
| **/chrome** | 設定 Claude in Chrome。 |
| **/claude-in-chrome [task]** | 透過 Chrome 執行瀏覽器任務；需啟用整合。 |
| **/claude-api [subcommand]** | 載入 Claude API 或 Managed Agents 專案指引。 |
| **/ide** | 管理 IDE 整合與查看狀態。 |
| **/desktop**、**/app** | 將工作階段切換至 Claude Desktop；平台與帳戶需符合條件。 |
| **/mobile**、**/ios**、**/android** | 顯示 Claude 行動 App 下載 QR code。 |
| **/import [codex\|gemini\|cursor]** | 匯入其他 coding agent 的設定；支援 dry-run。 |
| **/install-github-app** | 安裝 Claude GitHub App 與選用的 GitHub Actions 設定。 |
| **/install-slack-app** | 安裝 Claude Slack App。 |
| **/setup-bedrock** | 設定 Amazon Bedrock 驗證與模型；需設定 CLAUDE_CODE_USE_BEDROCK=1。 |
| **/setup-vertex** | 設定 Google Cloud Agent Platform 驗證與模型；需設定 CLAUDE_CODE_USE_VERTEX=1。 |
| **/web-setup** | 使用本機 gh 憑證連結 GitHub Cloud Sessions。 |

### Artifacts、設計與資料工作

| 命令 | 用途 |
| --- | --- |
| **/artifact-capabilities** | 載入已發布 Artifact 可使用的執行能力。 |
| **/artifact-diagramming** | 載入 Artifact 圖表設計指引。 |
| **/artifacts** | 列出並開啟可用的 Artifacts。 |
| **/dataviz [request]** | 載入圖表與儀表板設計指引。 |
| **/deep-research &lt;question&gt;** | 平行搜尋、交叉比對來源並產生引用報告。 |
| **/design [brief]** | 產生 Claude Design 畫板；依帳戶、平台與功能開放情況而異。 |
| **/design consent**、**/design revoke** | 授權或撤銷 Claude Design 存取權。 |
| **/design-login** | 為設計系統同步授權 Claude Design。 |
| **/design-sync [hint]** | 將專案 React 設計系統同步至 Claude Design。 |
| **/slides [brief]** | 產生 Claude Slides 簡報 Artifact；依帳戶與功能開放情況而異。 |
| **/powerup** | 透過互動短課程探索 Claude Code 功能。 |

### 外觀、帳戶與使用量

| 命令 | 用途 |
| --- | --- |
| **/color [color\|default]** | 設定提示列顏色。 |
| **/focus** | 切換精簡焦點檢視；僅在 Fullscreen renderer 可用。 |
| **/keybindings** | 開啟鍵盤快捷鍵設定檔。 |
| **/scroll-speed** | 調整滑鼠滾輪速度；僅在支援的 Fullscreen 終端機可用。 |
| **/stickers** | 查看 Claude Code 貼紙功能。 |
| **/terminal-setup** | 設定終端機按鍵或剪貼簿整合。 |
| **/theme** | 切換終端機色彩主題。 |
| **/tui [classic\|fullscreen]** | 切換終端機 UI renderer。 |
| **/voice [hold\|tap\|off]** | 切換語音輸入；需 Claude.ai 帳戶。 |
| **/usage**、**/cost**、**/stats** | 查看工作階段成本、方案用量與活動統計。 |
| **/usage-credits** | 管理額外用量點數；舊名稱為 /extra-usage。 |
| **/rate-limit-options** | 查看遇到用量限制時可用的選項。 |
| **/privacy-settings** | 查看或更新隱私設定；限符合資格的方案。 |
| **/passes** | 分享 Claude Code 試用週；限符合資格的帳戶。 |
| **/upgrade** | 開啟方案升級頁面。 |
| **/insights** | 依本機近期工作階段產生使用分析報告。 |
| **/release-notes** | 依版本查看變更記錄。 |
| **/bug [report]**、**/share** | 提交錯誤回報或分享工作階段；送出前會要求同意。 |
| **/feedback [report]** | 提交產品意見。 |
| **/radio** | 在瀏覽器開啟 Claude FM。 |
| **/restart**、**/update** | 重新啟動 CLI 並接續工作階段以套用更新；依平台、方案與版本而異。 |

舊版命令備註：官方文件標示 /pr-comments 與 /ultraplan 已移除；前者可直接請 Claude 查看 PR 留言，後者改用 /plan。命令清單也可能因平台、方案、設定與功能旗標而不同，實際執行前可在互動介面輸入 / 查看。

## CLI 主命令

以下主命令與巢狀子命令依本機 Claude Code 2.1.330 的 help 實測整理。巢狀子命令用法可執行 claude &lt;command&gt; --help。

| 命令 | 用途 |
| --- | --- |
| **claude agents** | 管理背景 agent。 |
| **claude attach &lt;id\|name&gt;** | 在目前終端機附加背景工作階段。 |
| **claude auth login**、**logout**、**status** | 登入、登出或查詢登入狀態。 |
| **claude auto-mode config**、**critique**、**defaults**、**reset** | 檢視、檢查或重設 Auto Mode 規則。 |
| **claude doctor** | 檢查 Claude Code 安裝健康狀態。 |
| **claude gateway** | 啟動企業驗證與遙測 Gateway。 |
| **claude import [source]** | 從 Codex、Gemini CLI 或 Cursor 匯入設定。 |
| **claude install [target]** | 安裝指定版本或 stable/latest 版本。 |
| **claude logs &lt;id\|name&gt;** | 顯示背景工作階段近期輸出。 |
| **claude mcp** | 管理 MCP；子命令包含 add、add-json、add-from-claude-desktop、get、list、login、logout、remove、reset-project-choices、serve。 |
| **claude plugin**、**claude plugins** | 管理 Plugin；子命令包含 configure、details、disable、enable、eval、init/new、install、list、marketplace、prune/autoremove、restore-set-aside、tag、test、uninstall/remove、update、validate。 |
| **claude purge [path]** | 刪除本機專案工作階段資料；先用 --dry-run 預覽。 |
| **claude respawn [id]** | 以目前 CLI 版本重新啟動背景工作階段。 |
| **claude rm &lt;id&gt;** | 移除背景工作階段清單項目及可安全刪除的 worktree。 |
| **claude setup-token** | 建立長期驗證 token；需 Claude 訂閱。 |
| **claude stop &lt;id&gt;**、**claude kill &lt;id&gt;** | 停止背景工作階段。 |
| **claude ultrareview [target]** | 在雲端執行多代理程式碼審查。 |
| **claude update**、**claude upgrade** | 檢查並安裝 CLI 更新。套件管理器安裝需透過原套件管理器更新。 |

claude --help 的本機清單未包含官方 CLI 文件中其他版本出現的所有命令。若命令不在本機 --help 中，不要假設此版本已支援。

## 常用啟動旗標

| 旗標 | 用途 |
| --- | --- |
| **-p**、**--print** | 非互動模式輸出後結束，常用於腳本與 pipe。 |
| **-c**、**--continue** | 繼續目前目錄最近的工作階段。 |
| **-r**、**--resume [session]** | 依工作階段 ID 或名稱恢復，或開啟選擇清單。 |
| **--fork-session** | 恢復工作階段時建立新的 session ID。 |
| **-w**、**--worktree [name]** | 在新的 Git worktree 執行工作階段。 |
| **--add-dir &lt;directories...&gt;** | 加入可讀寫的額外工作目錄。 |
| **--model &lt;model&gt;** | 指定模型別名或完整模型 ID。 |
| **--effort &lt;level&gt;** | 指定 low、medium、high、xhigh 或 max 推理強度。 |
| **--permission-mode &lt;mode&gt;** | 指定啟動權限模式，見下方模式表。 |
| **--allow-dangerously-skip-permissions** | 將 bypass 模式加入互動介面的 Shift+Tab 循環，不會直接啟用。 |
| **--dangerously-skip-permissions** | 直接以 bypassPermissions 啟動，跳過權限提示；只在隔離環境使用。 |
| **--allowedTools**、**--allowed-tools** | 指定不用逐次詢問即可使用的工具。 |
| **--disallowedTools**、**--disallowed-tools** | 指定禁止使用的工具。 |
| **--tools &lt;tools...&gt;** | 限定可用的內建工具。 |
| **--agent &lt;agent&gt;**、**--agents &lt;json-or-file&gt;** | 指定 agent 或定義自訂 agents。 |
| **--mcp-config &lt;configs...&gt;** | 載入指定 MCP 設定。 |
| **--plugin-dir &lt;path&gt;** | 從指定目錄或 zip 載入 Plugin。 |
| **--settings &lt;file-or-json&gt;** | 載入額外設定檔或 JSON 設定。 |
| **--setting-sources &lt;sources&gt;** | 指定載入 user、project、local 設定來源。 |
| **--output-format &lt;format&gt;** | 搭配 -p 設定 text、json 或 stream-json 輸出。 |
| **--input-format &lt;format&gt;** | 搭配 -p 使用 text 或 stream-json 輸入。 |
| **--max-budget-usd &lt;amount&gt;** | 限定 -p API 呼叫的最高金額。 |
| **--no-session-persistence** | 不儲存非互動工作階段；無法稍後恢復。 |
| **--background**、**--bg** | 啟動背景工作階段並立即返回。 |
| **--cloud [description\|session_id\|url]** | 建立雲端工作階段或傳送後續訊息。 |
| **--remote-control [name]** | 啟動互動工作階段並開啟 Remote Control。 |
| **--ide** | 啟動時連接唯一可用的 IDE。 |
| **--chrome**、**--no-chrome** | 啟用或停用 Chrome 整合。 |
| **--bare** | 以精簡模式略過多數自動探索與載入設定。 |
| **--safe-mode** | 停用自訂設定、Plugin、Hooks 等，以協助診斷設定問題。 |
| **--debug [filter]**、**--verbose** | 啟用除錯記錄或較詳細的輸出。 |
| **--version**、**--help** | 顯示版本或命令說明。 |

### YOLO／bypass 權限

Claude Code 的 bypass 啟動旗標是 --dangerously-skip-permissions，沒有把 --yolo 列為本機 2.1.330 的旗標。bypass 會跳過權限提示；官方文件建議僅在隔離的容器或虛擬機等環境使用。--allow-dangerously-skip-permissions 只讓你能從互動模式循環選到 bypass，啟動時仍保留目前權限模式。

## Plan Mode 與權限模式切換

### 權限模式

| --permission-mode 值 | 互動介面標籤 | 行為 |
| --- | --- | --- |
| manual | Manual | 大部分檔案修改、Shell 命令與網路操作先詢問。本機 help 列出 manual；官方文件稱此模式為 default，並說 CLI 接受 manual 作為別名。 |
| acceptEdits | Accept Edits | 自動接受工作目錄與額外目錄中的檔案編輯及部分常見檔案操作。 |
| plan | Plan | 可讀取檔案及探索；不修改來源檔案。 |
| auto | Auto | 由背景 classifier 檢查動作是否符合要求，減少逐次詢問。 |
| dontAsk | — | 自動拒絕原本需要詢問的操作。 |
| bypassPermissions | Bypass Permissions | 略過權限提示；僅在隔離環境使用。 |

### 切換方式

| 方式 | 指令或操作 | 說明 |
| --- | --- | --- |
| 工作階段中進入 Plan Mode | /plan | 可加上工作描述，例如 /plan 修正登入錯誤。 |
| 工作階段中循環切換 | Shift+Tab | 循環 Manual、Accept Edits、Plan，以及可用時的 Bypass 與 Auto；不包含 dontAsk。 |
| Windows 按鍵替代方式 | Alt+M | 若 Node 或 Bun runtime 未啟用 VT input mode，可用此快捷鍵循環模式。 |
| 啟動時選擇模式 | claude --permission-mode plan | 也可指定 manual、acceptEdits、auto、dontAsk 或 bypassPermissions。 |
| 預設新工作階段模式 | 設定 defaultMode | 在 Claude Code settings 檔設定預設權限模式。 |

/plan 專門進入 Plan Mode；使用 Shift+Tab 可在目前工作階段中切換回其他模式。auto 依賴 classifier，bypassPermissions 則略過權限提示，兩者行為不同。

## 官方查核來源

- [Claude Code CLI Reference](https://code.claude.com/docs/en/cli-reference)
- [Claude Code Commands](https://code.claude.com/docs/en/commands)
- [Claude Code Permissions](https://code.claude.com/docs/en/permissions)
- [Claude Code Interactive Mode](https://code.claude.com/docs/en/interactive-mode)
