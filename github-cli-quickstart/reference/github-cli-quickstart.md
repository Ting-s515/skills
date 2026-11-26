# GitHub CLI 指令速查表

> 查核日期：2026-11-26<br>
> 本機 CLI 版本：gh 2.106.0（2026-11-25），與官方 Releases 最新版一致。<br>
> 本機執行檔：C:\Program Files\GitHub CLI\gh.exe；已在 PATH 中。<br>
> 主命令、子命令與旗標以本機 gh --help 和各子命令 --help 為準；官方手冊與 release note 用於交叉確認。標示 preview 的命令可能未經通知即變更。

## 先分清命令種類

| 寫法 | 範例 | 用途 |
| --- | --- | --- |
| gh &lt;command&gt; | gh status | 執行主命令。 |
| gh &lt;command&gt; &lt;subcommand&gt; | gh pr create | 對指定資源執行動作，大多數操作屬於此類。 |
| --option、-x | gh pr list --state merged | 調整子命令行為。 |
| -R、--repo [HOST/]OWNER/REPO | gh issue list -R cli/cli | 不切換目錄，直接指定其他 repository。 |

在 Git repository 目錄中執行時，gh 會從 remote 推斷目標 repository；多個 remote 時可用 gh repo set-default 指定預設。

## 快速啟動

| 指令 | 用途 |
| --- | --- |
| gh auth login | 互動式登入 GitHub，選擇 HTTPS 或 SSH 與驗證方式。 |
| gh auth status | 查看各 host 的登入帳戶與 token 狀態。 |
| gh repo clone OWNER/REPO | 複製 repository。 |
| gh repo view --web | 在瀏覽器開啟目前 repository。 |
| gh pr create --fill | 以 commit 資訊建立 PR。 |
| gh pr checkout 123 | 在本機切換到 PR #123 的分支；簡寫 gh co 123。 |
| gh pr status | 查看與自己相關的 PR 狀態。 |
| gh issue list | 列出目前 repository 的 issue。 |
| gh run watch | 監看 workflow run 直到完成。 |
| gh status | 跨 repository 查看指派給自己的 issue、PR、review 請求與通知。 |
| gh --help、gh &lt;command&gt; --help | 顯示命令說明。 |
| gh --version | 顯示本機 CLI 版本。 |

## 主命令總覽

### Core Commands

| 命令 | 子命令 | 用途 |
| --- | --- | --- |
| **gh auth** | login、logout、refresh、setup-git、status、switch、token | 登入、登出、切換帳戶、設定 git 憑證。 |
| **gh browse** | — | 在瀏覽器開啟 repo、issue、PR、檔案或 commit。 |
| **gh codespace**、**gh cs** | code、cp、create、delete、edit、jupyter、list、logs、ports、rebuild、ssh、stop、view | 管理 Codespaces。 |
| **gh discussion** | create、list、comment、edit、view | 操作 GitHub Discussions（preview）。 |
| **gh gist** | clone、create、delete、edit、list、rename、view | 管理 gist。 |
| **gh issue** | create、list、status、artifact、close、comment、delete、develop、edit、lock、pin、reopen、transfer、unlock、unpin、view | 管理 issue。 |
| **gh org** | list | 列出所屬組織。 |
| **gh pr** | create、list、status、checkout、checks、close、comment、diff、edit、lock、merge、ready、reopen、revert、review、unlock、update-branch、view | 管理 pull request。 |
| **gh project** | create、list、view、edit、close、copy、delete、field-*、item-*、link、unlink、mark-template | 管理 GitHub Projects。 |
| **gh release** | create、list、delete、delete-asset、download、edit、upload、verify、verify-asset、view | 管理 release 與附件。 |
| **gh repo** | create、list、archive、autolink、clone、delete、deploy-key、edit、fork、gitignore、license、read-dir、read-file、rename、set-default、sync、unarchive、view | 管理 repository；read-dir、read-file 為 preview。 |
| **gh skill**、**gh skills** | install、list、preview、publish、search、update | 安裝與管理 agent skills（preview）。 |

### GitHub Actions Commands

| 命令 | 子命令 | 用途 |
| --- | --- | --- |
| **gh run** | cancel、delete、download、list、rerun、view、watch | 查看、重跑、取消 workflow run 與下載 artifact。 |
| **gh workflow** | disable、enable、list、run、view | 查看、啟停或以 workflow_dispatch 觸發 workflow。 |
| **gh cache** | delete、list | 管理 Actions cache。 |
| **gh secret** | delete、list、set | 管理 repo、環境或組織 secret。 |
| **gh variable** | delete、get、list、set | 管理 Actions 變數。 |

### Additional Commands

| 命令 | 子命令 | 用途 |
| --- | --- | --- |
| **gh agent-task**、**gh agent** | create、list、view | 操作 Copilot agent task（preview）。 |
| **gh alias** | delete、import、list、set | 建立自訂命令捷徑。 |
| **gh api** | — | 以登入身分呼叫 REST 或 GraphQL API。 |
| **gh attestation**、**gh at** | download、trusted-root、verify | 驗證 artifact attestation。 |
| **gh completion** | — | 產生 shell 自動完成腳本，例如 gh completion -s powershell。 |
| **gh config** | clear-cache、get、list、set | 管理 gh 設定，例如 editor、git_protocol。 |
| **gh copilot** | — | 執行 GitHub Copilot CLI（preview）；--remove 移除已下載的 Copilot CLI。 |
| **gh event** | listen、subscription | 監聽 GitHub 事件（preview）。 |
| **gh extension**、**gh ext** | browse、create、exec、install、list、remove、search、upgrade | 管理 gh extension。 |
| **gh gpg-key**、**gh ssh-key** | add、delete、list | 管理帳戶 GPG／SSH 金鑰。 |
| **gh label** | clone、create、delete、edit、list | 管理 label。 |
| **gh licenses** | — | 查看第三方授權資訊。 |
| **gh preview** | prompter | 預覽 gh 實驗功能。 |
| **gh ruleset**、**gh rs** | check、list、view | 查看 repository／組織 ruleset。 |
| **gh search** | code、commits、issues、prs、repos | 跨 GitHub 搜尋。 |
| **gh status** | — | 跨 repo 彙整相關 issue、PR 與通知。 |

### Help Topics

gh help &lt;topic&gt; 可查看：accessibility、actions、environment、exit-codes、formatting、mintty、reference、telemetry。其中 gh help reference 會輸出所有命令的完整參考。

## 常用情境指令

### 登入與帳戶

| 指令 | 用途 |
| --- | --- |
| gh auth login --web | 以瀏覽器裝置碼登入。 |
| gh auth login -p ssh | 登入並設定 git 使用 SSH。 |
| gh auth login --with-token | 從 stdin 讀取 token 登入，適合腳本。 |
| gh auth login -h github.example.com | 登入 GitHub Enterprise Server。 |
| gh auth refresh -s project | 補申請額外 scope，例如 Projects 需要 project scope。 |
| gh auth switch | 在同一 host 的多個帳戶間切換。 |
| gh auth setup-git | 讓 git 透過 gh 取得 HTTPS 憑證。 |
| gh auth logout | 2.106.0 起會先撤銷 OAuth token 再移除本機憑證；加 --no-revoke 保留舊行為（只刪本機）。 |
| gh auth token | 印出目前 token；內容等同密碼，勿貼到公開位置。 |

### Repository

| 指令 | 用途 |
| --- | --- |
| gh repo create my-app --private --clone | 建立私有 repo 並複製到本機。 |
| gh repo create --source . --private --push | 將現有本機專案建立成 GitHub repo 並推送。 |
| gh repo fork OWNER/REPO --clone | Fork 並複製，自動設定 upstream remote。 |
| gh repo sync | 將 fork 與上游同步。 |
| gh repo list OWNER --limit 50 | 列出使用者或組織的 repo。 |
| gh repo set-default | 為目前目錄指定預設 repository。 |
| gh repo edit --visibility public --accept-visibility-change-consequences | 變更 repo 可見性。 |

### Pull Request

| 指令 | 用途 |
| --- | --- |
| gh pr create -t "標題" -b "內容" -B main | 指定標題、內容與 base 分支建立 PR。 |
| gh pr create --draft --fill | 以 commit 資訊建立草稿 PR。 |
| gh pr create -r USER -a @me -l bug | 指定 reviewer、assignee 與 label。 |
| gh pr create --web | 在瀏覽器建立 PR。 |
| gh pr list --state merged --author @me | 列出自己已合併的 PR。 |
| gh pr view 123 --comments | 查看 PR 內容與留言。 |
| gh pr diff 123 | 查看 PR 差異。 |
| gh pr checks 123 --watch | 監看 PR 的 CI 狀態。 |
| gh pr review 123 --approve | 核准 PR；--request-changes 要求修改，--comment 留言。 |
| gh pr comment 123 -b "內容" | 在 PR 留言。 |
| gh pr ready 123 | 將草稿 PR 標記為可審查。 |
| gh pr merge 123 --squash --delete-branch | Squash 合併並刪除分支；也可用 --merge、--rebase。 |
| gh pr merge 123 --auto --squash | 條件滿足後自動合併。 |
| gh pr update-branch 123 | 以 base 分支更新 PR 分支。 |
| gh pr checkout 123 --worktree ../pr-123 | 將 PR 簽出到獨立 worktree。 |
| gh pr revert 123 | 建立還原該 PR 的新 PR。 |

### Issue

| 指令 | 用途 |
| --- | --- |
| gh issue create -t "標題" -b "內容" -l bug | 建立 issue。 |
| gh issue create --parent 10 | 建立為 #10 的 sub-issue。 |
| gh issue list -a @me -s open | 列出指派給自己的未關閉 issue。 |
| gh issue view 45 --comments | 查看 issue 與留言。 |
| gh issue comment 45 -b "內容" | 在 issue 留言。 |
| gh issue edit 45 --add-label bug | 修改 issue 欄位。 |
| gh issue close 45 | 關閉 issue；gh issue reopen 重新開啟。 |
| gh issue develop 45 --checkout | 為 issue 建立連結分支並切換過去。 |

### GitHub Actions

| 指令 | 用途 |
| --- | --- |
| gh run list --limit 10 | 列出最近 workflow run。 |
| gh run view &lt;run-id&gt; --log-failed | 只看失敗步驟的 log。 |
| gh run view &lt;run-id&gt; --verbose | 顯示 job 步驟。 |
| gh run watch &lt;run-id&gt; --exit-status | 監看 run，失敗時回傳非零 exit code。 |
| gh run rerun &lt;run-id&gt; --failed | 只重跑失敗的 job。 |
| gh run download &lt;run-id&gt; | 下載 run 產生的 artifact。 |
| gh workflow list | 列出 workflow。 |
| gh workflow run deploy.yml -r main -f env=prod | 以 workflow_dispatch 觸發 workflow 並傳入 input。 |
| gh secret set API_KEY | 互動輸入並設定 secret；也可用 --body 或 stdin。 |
| gh variable set NODE_VERSION --body 22 | 設定 Actions 變數。 |

### Release

| 指令 | 用途 |
| --- | --- |
| gh release create v1.0.0 --generate-notes | 建立 release 並自動產生 release note。 |
| gh release create v1.0.0 ./dist/*.zip -t "v1.0.0" | 建立 release 並上傳附件。 |
| gh release create v1.1.0-rc1 --prerelease --draft | 建立 prerelease 草稿。 |
| gh release list | 列出 release。 |
| gh release download v1.0.0 -p "*.zip" | 依 pattern 下載附件。 |
| gh release upload v1.0.0 ./file.zip --clobber | 上傳或覆蓋附件。 |

### 搜尋與 API

| 指令 | 用途 |
| --- | --- |
| gh search repos "topic:cli" --language go | 搜尋 repository。 |
| gh search prs --review-requested @me --state open | 搜尋等待自己 review 的 PR。 |
| gh search code "func main" --repo OWNER/REPO | 搜尋程式碼。 |
| gh api repos/{owner}/{repo} | 呼叫 REST API；{owner}、{repo} 會依目前目錄自動帶入。 |
| gh api repos/{owner}/{repo}/issues -f title="標題" | -f 傳字串參數，有參數時預設改用 POST。 |
| gh api -X PATCH repos/{owner}/{repo} -F has_wiki=false | -X 指定 method，-F 傳型別化參數。 |
| gh api --paginate repos/{owner}/{repo}/pulls --jq ".[].title" | 取回全部頁面並以 jq 篩選。 |
| gh api graphql -f query='query { viewer { login } }' | 呼叫 GraphQL API。 |

## 常用通用旗標

| 旗標 | 用途 |
| --- | --- |
| **-R**、**--repo [HOST/]OWNER/REPO** | 指定其他 repository。 |
| **-w**、**--web** | 在瀏覽器開啟或建立對應資源。 |
| **--json &lt;fields&gt;** | 輸出 JSON；不帶欄位值可列出可用欄位。 |
| **-q**、**--jq &lt;expr&gt;** | 搭配 --json 以 jq 篩選，不需另外安裝 jq。 |
| **-t**、**--template &lt;tmpl&gt;** | 以 Go template 格式化 JSON；見 gh help formatting。 |
| **-L**、**--limit &lt;n&gt;** | list 類命令的最大筆數，預設多為 30。 |
| **-s**、**--state** | 依狀態篩選，例如 open、closed、merged、all。 |
| **@me** | 在 assignee、author 等欄位代表目前登入帳戶。 |
| **--help**、**--version** | 顯示說明或版本。 |

## 常用環境變數

| 變數 | 用途 |
| --- | --- |
| GH_TOKEN、GITHUB_TOKEN | 指定 github.com 的驗證 token，優先於已儲存的憑證；CI 常用。 |
| GH_ENTERPRISE_TOKEN | 指定 GitHub Enterprise Server 的 token。 |
| GH_HOST | 未能從 repo 推斷時使用的預設 host。 |
| GH_REPO | 以 [HOST/]OWNER/REPO 指定目標 repository。 |
| GH_EDITOR | 指定編寫內容時開啟的編輯器。 |
| GH_PAGER、PAGER | 指定輸出用的分頁程式，例如 less。 |
| GH_DEBUG | 設為真值輸出除錯訊息；設為 api 額外記錄 HTTP 流量。 |
| GH_NO_UPDATE_NOTIFIER | 停用更新提示。 |
| NO_COLOR | 停用 ANSI 色彩輸出。 |

完整清單見 gh help environment。

## Windows PowerShell 注意事項

- --jq 與 GraphQL query 含雙引號或大括號時，建議以單引號包住整段，例如 gh api graphql -f query='query { viewer { login } }'。
- 臨時設定環境變數：$env:GH_REPO = "OWNER/REPO"；macOS／Linux 等效寫法為 export GH_REPO=OWNER/REPO。
- 啟用 PowerShell 自動完成：gh completion -s powershell | Out-String | Invoke-Expression，可加入 $PROFILE 長期生效。

## 官方查核來源

- [GitHub CLI Manual](https://cli.github.com/manual/)
- [GitHub CLI Releases](https://github.com/cli/cli/releases)
- [gh agent-task](https://cli.github.com/manual/gh_agent-task)
- [gh skill preview](https://cli.github.com/manual/gh_skill_preview)
