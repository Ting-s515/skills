# Git 入門課程：從零到推出第一個 PR

> 適合對象：完全沒有版本控制經驗的工程師新人
> 預計完成時間：2 天（含實作練習）

---

## 課程目標

完成本課程後，你將能夠：

- 理解 Git 版本控制的核心概念
- 在本地端建立與管理 Git 儲存庫
- 使用分支策略進行功能開發
- 透過 Pull Request 提交程式碼並參與 Code Review 流程

---

## 課程總覽

| 模組 | 主題 | 預估時間 |
|------|------|----------|
| 模組 1 | Git 是什麼？為什麼需要它？ | 30 分鐘 |
| 模組 2 | 環境設定與基本操作 | 45 分鐘 |
| 模組 3 | 分支管理與合作流程 | 60 分鐘 |
| 模組 4 | 遠端儲存庫與 GitHub 操作 | 45 分鐘 |
| 模組 5 | 實戰：推出你的第一個 PR | 60 分鐘 |

---

## 模組 1：Git 是什麼？為什麼需要它？

### 核心概念

**版本控制**是一種記錄檔案變更歷史的機制，讓你可以：

- 回溯到任意時間點的狀態
- 多人同時修改同一份程式碼而不互相干擾
- 追蹤「誰、在什麼時間、改了什麼、為什麼改」

### Git 的三個工作區域

```
工作目錄 (Working Directory)
    ↓  git add
暫存區 (Staging Area / Index)
    ↓  git commit
本地儲存庫 (Local Repository)
    ↓  git push
遠端儲存庫 (Remote Repository)
```

- **工作目錄**：你實際編輯檔案的地方
- **暫存區**：準備提交的變更集合，像是「購物車」
- **本地儲存庫**：儲存所有 commit 歷史的資料庫
- **遠端儲存庫**：存放在伺服器（如 GitHub）的共用儲存庫

### 重要術語

| 術語 | 說明 |
|------|------|
| Repository (Repo) | 儲存庫，包含所有版本歷史的資料夾 |
| Commit | 一次變更的快照，附有說明訊息 |
| Branch | 分支，獨立的開發線路 |
| Merge | 合併，將分支的變更合入另一個分支 |
| Pull Request (PR) | 請求將你的分支合入主分支的機制 |

---

## 模組 2：環境設定與基本操作

### 安裝 Git

**Windows：**
1. 前往 https://git-scm.com/download/win 下載安裝包
2. 安裝時建議勾選「Git Bash Here」與「Git GUI Here」
3. 開啟終端機驗證安裝：`git --version`

**macOS：**
```bash
# 透過 Homebrew 安裝
brew install git

# 驗證安裝
git --version
```

**Linux (Ubuntu/Debian)：**
```bash
sudo apt update && sudo apt install git
git --version
```

### 初始設定（必做）

```bash
# 設定你的名字（會出現在 commit 記錄中）
git config --global user.name "你的名字"

# 設定你的 Email（需與 GitHub 帳號一致）
git config --global user.email "your.email@company.com"

# 設定預設分支名稱為 main
git config --global init.defaultBranch main

# 確認設定
git config --list
```

### 基本操作指令

#### 建立儲存庫

```bash
# 在現有資料夾初始化 Git
git init my-first-repo
cd my-first-repo

# 或複製遠端儲存庫
git clone https://github.com/username/repo-name.git
```

#### 日常工作流程

```bash
# 查看目前狀態（最常用的指令）
git status

# 查看檔案變更內容
git diff

# 將特定檔案加入暫存區
git add filename.txt

# 將所有變更加入暫存區
git add .

# 提交變更
git commit -m "feat: 新增使用者登入功能"

# 查看 commit 歷史
git log --oneline
```

#### Commit 訊息規範（Conventional Commits）

好的 commit 訊息讓團隊成員快速了解變更目的：

```
<type>: <description>

常用 type：
  feat     - 新功能
  fix      - 錯誤修復
  refactor - 重構（不影響功能）
  docs     - 文件更新
  style    - 格式調整（不影響邏輯）
  test     - 測試相關
  chore    - 雜項維護
```

範例：
```
feat: 新增電子郵件驗證功能
fix: 修正登入頁面在 Safari 的顯示問題
docs: 更新 API 文件中的參數說明
```

### 實作練習 2-A

1. 建立一個新資料夾並初始化 Git
2. 建立一個 `hello.txt` 並寫入任意內容
3. 執行 `git status` 觀察輸出
4. 將檔案加入暫存區並提交
5. 執行 `git log --oneline` 確認 commit 記錄

---

## 模組 3：分支管理與合作流程

### 分支的概念

分支讓你在不影響主線程式碼的情況下，獨立開發新功能或修復 Bug。

```
main      ──────●──────────────────●── (穩定版本)
                 \                /
feature/login    ●──●──●──●──●──●    (功能開發中)
```

### 分支操作指令

```bash
# 查看所有分支
git branch

# 建立新分支
git branch feature/user-login

# 切換到分支
git checkout feature/user-login

# 建立並切換（推薦用法）
git checkout -b feature/user-login

# 刪除分支（合併後清理）
git branch -d feature/user-login
```

### 分支命名規範

```
功能開發：feature/<簡短說明>    例：feature/user-login
錯誤修復：fix/<簡短說明>        例：fix/login-safari-bug
緊急修復：hotfix/<簡短說明>     例：hotfix/payment-crash
```

### 合併分支

```bash
# 切換回主分支
git checkout main

# 合併功能分支
git merge feature/user-login

# 刪除已合併的分支
git branch -d feature/user-login
```

### 解決合併衝突

當兩個分支修改了同一段程式碼，Git 無法自動決定保留哪個版本，就會產生衝突：

```
<<<<<<< HEAD (你的分支)
const greeting = "Hello World";
=======
const greeting = "Hi Everyone";
>>>>>>> feature/greeting
```

**解決步驟：**

1. 開啟衝突檔案，找到所有 `<<<<<<`、`=======`、`>>>>>>>` 標記
2. 決定保留哪個版本（或合併兩者）
3. 刪除所有衝突標記
4. 執行 `git add <衝突檔案>`
5. 執行 `git commit` 完成合併

### 實作練習 3-A

1. 在 main 分支建立 `README.md`，寫入「# 我的專案」
2. 建立並切換到 `feature/about` 分支
3. 在分支中新增 `about.txt`，寫入個人介紹
4. 提交變更
5. 切換回 main 並合併 feature/about

---

## 模組 4：遠端儲存庫與 GitHub 操作

### 設定 SSH 金鑰（推薦）

SSH 金鑰讓你不需要每次輸入帳號密碼：

```bash
# 產生 SSH 金鑰
ssh-keygen -t ed25519 -C "your.email@company.com"

# 顯示公鑰內容（複製後貼到 GitHub）
cat ~/.ssh/id_ed25519.pub

# 測試連線
ssh -T git@github.com
```

將公鑰加入 GitHub：GitHub → Settings → SSH and GPG keys → New SSH key

### 遠端儲存庫操作

```bash
# 查看遠端設定
git remote -v

# 新增遠端（通常 clone 後已自動設定）
git remote add origin git@github.com:username/repo.git

# 推送到遠端（首次需加 -u 設定追蹤）
git push -u origin main

# 後續推送
git push

# 拉取最新變更
git pull

# 抓取但不合併（安全的方式）
git fetch origin
```

### GitHub 工作流程

```
1. Fork 或 Clone 儲存庫
        ↓
2. 建立功能分支
        ↓
3. 開發功能，提交 Commit
        ↓
4. Push 分支到遠端
        ↓
5. 建立 Pull Request
        ↓
6. 等待 Code Review
        ↓
7. 根據回饋修改
        ↓
8. Merge 到主分支
```

### 保持分支與主線同步

開發期間主線可能有新的 commit，需要同步：

```bash
# 切換到 main 並更新
git checkout main
git pull

# 切換回功能分支，將 main 的更新合入
git checkout feature/my-feature
git merge main

# 或使用 rebase（讓歷史更乾淨）
git rebase main
```

### 實作練習 4-A

1. 在 GitHub 建立一個新的公開儲存庫
2. 將本地練習用的儲存庫推送到 GitHub
3. 確認 GitHub 上能看到你的 commit 歷史

---

## 模組 5：實戰 - 推出你的第一個 PR

### Pull Request 是什麼？

Pull Request（簡稱 PR）是你向團隊提出「請將我的分支合入主分支」的請求。它同時也是：

- **Code Review 的入口**：讓其他工程師審查你的程式碼
- **討論的平台**：針對特定程式碼行留下評論
- **品質守門員**：可設定自動化測試必須通過才能 Merge

### 建立 PR 的步驟

**步驟一：確保分支是最新狀態**
```bash
git checkout main
git pull
git checkout feature/my-feature
git merge main
```

**步驟二：推送分支到遠端**
```bash
git push -u origin feature/my-feature
```

**步驟三：在 GitHub 建立 PR**

1. 前往 GitHub 儲存庫頁面
2. 點擊黃色提示橫幅的「Compare & pull request」按鈕
3. 填寫 PR 資訊：
   - **Title**：簡短描述這個 PR 做了什麼
   - **Description**：詳細說明（見下方範本）
4. 指定 Reviewer（請求 Code Review 的人）
5. 點擊「Create pull request」

### PR 描述範本

```markdown
## 變更說明
簡短說明這個 PR 做了什麼，以及為什麼要這樣做。

## 變更項目
- 新增 xxx 功能
- 修改 yyy 邏輯
- 移除舊有的 zzz

## 測試方式
1. 執行 `npm test` 確認所有測試通過
2. 手動測試步驟：...

## 相關 Issue
Closes #123
```

### Code Review 禮儀

**作為 PR 作者：**
- PR 越小越好，單一 PR 專注於一個功能或修復
- 自己先 review 一遍再請別人看
- 對評論保持開放態度，Code Review 是學習機會
- 及時回應評論，說明修改或解釋設計決策

**作為 Reviewer：**
- 在 24 小時內完成 review
- 評論要具體，說明問題所在與建議做法
- 區分「必須修改」與「建議考慮」
- 肯定好的設計，不只指出問題

### 處理 Review 意見

```bash
# 根據意見修改程式碼後
git add .
git commit -m "fix: 根據 review 意見調整驗證邏輯"
git push

# 你的新 commit 會自動出現在 PR 中
```

### 最終實作練習

1. Fork 公司的練習儲存庫（或使用你建立的練習 Repo）
2. 建立分支 `feature/onboarding-<你的名字>`
3. 新增一個檔案 `members/<你的名字>.md`，內容包含：
   - 你的名字
   - 你負責的職位
   - 一句自我介紹
4. Commit、Push，並建立 PR
5. 請隔壁的同事 Review 你的 PR
6. 根據意見調整後，完成 Merge

---

## 常見問題與錯誤處理

### Q: 不小心 commit 到 main 分支怎麼辦？

```bash
# 建立新分支儲存這些 commit
git branch feature/my-work

# 將 main 回退到正確位置（保留工作目錄的變更）
git reset HEAD~1

# 切換到正確分支繼續工作
git checkout feature/my-work
```

### Q: commit 訊息寫錯，但還沒 push，如何修改？

```bash
git commit --amend -m "feat: 正確的 commit 訊息"
```

**注意**：已經 push 的 commit 不要 amend，會造成歷史分歧。

### Q: 想撤銷某個 commit 的變更？

```bash
# 建立一個反向的新 commit（安全做法，保留歷史）
git revert <commit-hash>

# 查看 commit hash
git log --oneline
```

### Q: 暫時放下目前的工作，切換到別的分支處理緊急問題？

```bash
# 將未 commit 的變更暫存
git stash

# 切換分支，處理緊急問題...

# 切換回來，取回暫存的變更
git stash pop
```

### Q: 想查看某個檔案的修改歷史？

```bash
git log --follow -p filename.txt
```

---

## 快速參考卡

### 每日工作流程

```bash
# 開始工作前，同步最新程式碼
git checkout main && git pull

# 建立功能分支
git checkout -b feature/my-feature

# 開發過程中，定期提交
git add .
git commit -m "feat: 完成 xxx 部分"

# 完成後推送並建立 PR
git push -u origin feature/my-feature
```

### 常用指令速查

| 指令 | 說明 |
|------|------|
| `git status` | 查看工作目錄狀態 |
| `git add <file>` | 加入暫存區 |
| `git commit -m "msg"` | 提交變更 |
| `git push` | 推送到遠端 |
| `git pull` | 拉取遠端變更 |
| `git checkout -b <branch>` | 建立並切換分支 |
| `git merge <branch>` | 合併分支 |
| `git log --oneline` | 查看精簡歷史 |
| `git diff` | 查看未暫存的變更 |
| `git stash` | 暫存未提交的變更 |

---

## 延伸學習資源

- [Pro Git Book（免費，繁中版）](https://git-scm.com/book/zh-tw/v2)
- [Learn Git Branching（互動練習）](https://learngitbranching.js.org/?locale=zh_TW)
- [GitHub Skills（官方學習平台）](https://skills.github.com/)
- [Conventional Commits 規範](https://www.conventionalcommits.org/zh-hant/)

---

## 課程完成確認清單

完成本課程後，請確認自己能獨立完成以下操作：

- [ ] 初始化 Git 儲存庫並完成初始設定
- [ ] 執行 add → commit → push 標準工作流程
- [ ] 建立功能分支並在上面開發
- [ ] 解決基本的合併衝突
- [ ] 建立 Pull Request 並填寫清楚的描述
- [ ] 回應 Code Review 意見並更新 PR
- [ ] 使用 `git stash` 暫存未完成的工作

完成所有項目後，恭喜你已經具備在團隊中使用 Git 協作開發的基本能力！

---

*課程版本：1.0 | 最後更新：2026-05-09*
