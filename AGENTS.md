## 維護原則

- 本檔只保留穩定、通用、長期有效的規則。
- 本檔是針對 Codex 的專案行為規則文檔，需使用 Codex 可執行的工具與流程描述。

## 語言與輸出

1. 所有回覆、說明、文件內容預設使用繁體中文。
2. 產出前先自我檢查語言；若非繁體中文，需先改寫後再輸出。
3. 英文僅保留在必要指令、路徑、程式碼與專有名詞。

## 程式規範

1. 禁止使用三元巢狀（三元運算子內再包含三元運算子）。
2. Mermaid 不支援 `\n`，若需換行僅用 `<br>`。
3. 註解只寫「為什麼（why）」。
   1. 必須加註解的區域：後端業務邏輯、前端邏輯判斷、hook 邏輯、工具函式邏輯。
   2. 不要加註解的區域：純 UI 樣式、簡單賦值、單純參數輸入/輸出。

## Workflow Gate（不可跳過）

每次透過工具新增、修改、刪除任何檔案後，最終回覆前必須完成：

1. 檢查本次變更檔案類型。
2. 產生完整多行 commit message。
3. 判斷是否需要 code review。
4. 除非符合下方 Code Review 跳過條件，否則必須執行 code review。
5. 若未執行 code review，必須在最終回覆明確寫出跳過原因。
6. 若本次變更包含測試檔案，測試完成後必須執行測試驗證；若未通過，需自動修正並重跑，直到測試通過為止。
7. 若本次變更包含應用程式實作、設定、建置流程或相依套件變更，必須執行對應 build 驗證；若建置失敗，需自動修正並重跑，直到建置成功為止。
8. 驗證與 review 完成後，必須自動 staging 本次對話由 AI agent 產生或修改的檔案。
9. 必須使用產生的完整多行 commit message 自動執行 `git commit`。
10. 若因 git hook、測試、build、review findings 或環境錯誤導致 commit 失敗，必須先自動修正可修正問題並重試；只有在無法自行修正時，才在最終回覆說明阻塞原因。

### Commit Message

- 自動產生一筆完整的多行 commit message。
- 第一行必須符合 Conventional Commits 格式：`<type>: <description>`
- 第二行開始必須輸出詳細的中文內容，供 PR code review 使用。
- 常用 type：`feat`、`fix`、`refactor`、`docs`、`style`、`other`、`test`
- 產生 message 後必須用於實際執行 `git commit`。
- commit message 必須描述本次實際提交內容，不可使用空泛描述。
- 詳細中文內容必須說明本次調整的背景、原本問題或風險，以及本次調整項目。
- 詳細中文內容建議格式：
  1. 第一段描述原本問題、觸發情境或調整原因。
  2. 第二段以「本次調整：」開頭。
  3. 後續逐行列出具體修改內容，每行一個重點。
- 若同一輪工作包含多個可獨立提交的完成單位，應依完成單位拆成多筆 commit；若變更彼此高度相關，可合併為單筆 commit。

### Build 驗證

- 新增或修改應用程式實作後，必須先判斷專案使用的建置指令，例如 `npm run build`、`pnpm build`、`dotnet build`、`mvn test` 或其他專案既有指令。
- 若專案提供明確 build 指令，必須在 commit 前執行。
- 若 build 失敗，AI agent 必須分析錯誤、修正可修正問題，並重新執行 build。
- build 修正流程需持續到建置成功；只有在缺少外部服務、缺少憑證、環境限制或相依工具不可用等無法自行排除的情況，才可停止並說明阻塞原因。
- 若本次只變更文檔、註解或不影響建置的純文字內容，可跳過 build，但需保留跳過原因。

### Code Review

- **以下情況跳過 Code Review：**
- 本次對話變更**僅有文檔檔案**（如 `.md`、`.txt` 等），不含程式碼變更
- 本次操作為**純 git 操作**（如 `git rebase`、`git merge`、`git cherry-pick`、`git reset`、`git stash` 等），不涉及程式碼撰寫或修改

- **若變更包含測試檔案：**
- 仍須照正常流程執行 Code Review，不可跳過
- 測試檔案本身的正確性與覆蓋率亦須由 Code Review 驗證

### 自動執行 Git Commit（無條件執行）

Build 驗證與 Code Review 完成後，必須使用 Commit Message 章節產生的完整多行 commit message 自動執行 `git commit`，不需要人工介入。

- AI agent 必須主動完成 `git status`、`git diff`、必要驗證、`git add` 與 `git commit`。
- 不得要求人類手動執行 staging、commit 或確認 commit message。
- staging 前必須確認只加入本次對話由 AI agent 產生或修改的檔案。
- 若工作區存在非本次對話產生的既有變更，必須保留並避免納入 commit。
- 不得使用 `git add .` 或 `git add -A`，除非已確認工作區沒有任何非本次對話產生的變更。
- 不得使用 `git reset --hard`、`git checkout --` 等會丟失變更的指令來處理非本次變更。
- 若 commit 前發現沒有實際檔案變更，應跳過 commit，並在最終回覆說明原因。
- 若因 git hook、測試、build、review findings 或環境錯誤導致 commit 失敗，必須先自動修正可修正問題並重試；只有在無法自行修正時，才可停止並說明阻塞原因。

## Review 執行原則

- 優先使用使用者在對話中明確提供的規格文件路徑。
- 若需要做規格對照審查，但對話中沒有明確規格路徑，直接以本次 `git diff` 內容作為依據執行 review，不得因此延遲或跳過。
- 若已知規格文件路徑，review prompt 必須填入實際路徑，不可使用佔位符。
- 若環境支援 sub-agent，優先使用 reviewer role 執行 review。
- review 前應優先查找名稱為 `code-reviewer` 的 skill，查找時必須對 skill 名稱與 `SKILL.md` 檔名使用大小寫不敏感比對，讀取其 `SKILL.md` 後依流程執行；不可只因本回合注入的 Available skills 清單未列出該 skill，就直接判定不可用。
- 查找 `code-reviewer` skill 時，不得因 `SKILL.md`、`SKILL.MD` 等檔名大小寫差異判定 skill 不存在；若使用 `rg` 比對路徑字串，必須使用大小寫不敏感搜尋。
- 若本回合技能清單未列出 `code-reviewer`，但本機可取得同名 skill 定義，仍應讀取並依其流程執行。
- 不可將 `code-reviewer` 寫成硬編碼的本機絕對路徑；應以 skill 名稱查找與載入。
- 只有在確認 `code-reviewer` skill 不存在、無法讀取，或 sub-agent 能力不可用時，才退回當前 agent 執行一般 code review 流程。

## 查證原則

- 只要問題涉及任何 **CLI 工具、AI 工具**（如 `Codex`、`Claude Code` 等）的能力、指令、feature、限制、版本行為、設定方式、URL，必須先查證再回答，不可只靠記憶作答。
- 查證順序：
  1. 該工具的**官方最新文件**（透過 WebSearch 或 WebFetch 取得）
  2. **本機指令實測**，例如 `<tool> --help`、`<tool> <subcommand> --help`
- 回答時必須明確區分：
  - 哪些是官方文件已確認事實
  - 哪些是本機實測結果
  - 哪些是根據文件與實測整理出的推論
- 若查不到或證據不足，必須直接說「目前無法確認」，不可猜測。

## 網路搜尋原則（強制）

以下類型的問題，**絕對禁止**使用模型內部舊資料或訓練資料推論回答，**必須先透過 WebSearch 或 WebFetch 搜尋最新資訊後才能回答**：

- 任何**時事、新聞、近期事件**（如股市、政策、人事、科技新聞）
- **套件、函式庫、框架、工具的版本、API、設定方式**（如 npm 套件版本、breaking change）
- **價格、匯率、指數、數值**等隨時間變動的資料
- **某功能是否存在、是否支援**等可能隨版本異動的事實
- 任何問題中出現「最新」、「現在」、「目前」、「今天」等時間敏感詞彙

**違反規則的情況**（必須避免）：

- 直接用模型記憶回答時事或版本資訊，即使有把握也不行
- 說「根據我的訓練資料」後直接給答案而不搜尋
- 搜尋失敗後改用舊資料推論，應改為明確告知「無法取得最新資訊」
