# Git 入門課程：從零到推出第一個 PR

## 課程簡介

本課程專為公司新人設計，幫助你從完全不懂 Git 開始，一步步學會版本控制的核心概念，最終能夠獨立完成日常開發流程並推出第一個 Pull Request。

預計學習時間：4-6 小時

---

## 目錄

1. [為什麼需要 Git？](#1-為什麼需要-git)
2. [環境安裝與設定](#2-環境安裝與設定)
3. [Git 核心概念](#3-git-核心概念)
4. [基礎指令操作](#4-基礎指令操作)
5. [分支管理](#5-分支管理)
6. [遠端協作流程](#6-遠端協作流程)
7. [推出你的第一個 PR](#7-推出你的第一個-pr)
8. [常見問題與解法](#8-常見問題與解法)
9. [實作練習](#9-實作練習)

---

## 1. 為什麼需要 Git？

### 沒有版本控制的痛點

想像你在撰寫一份重要的報告：
- `報告_v1.docx`
- `報告_v2_修改.docx`
- `報告_v3_最終版.docx`
- `報告_v3_最終版_真的最終.docx`

程式碼的世界也會發生一樣的混亂，而且情況更複雜——多人同時修改同一個檔案時，誰的版本是對的？

### Git 解決的問題

- **歷史記錄**：每次變更都有記錄，隨時可以回到任何一個時間點
- **多人協作**：多人同時開發不同功能，不互相干擾
- **安全備份**：程式碼存放在遠端，本機壞掉也不會遺失
- **追責可查**：知道每一行程式碼是誰、在什麼時候、為了什麼原因修改的

---

## 2. 環境安裝與設定

### 安裝 Git

**Windows：**
1. 前往 https://git-scm.com/download/win
2. 下載並執行安裝程式
3. 安裝過程中保持預設選項即可

**macOS：**
```bash
# 方法一：安裝 Xcode Command Line Tools
xcode-select --install

# 方法二：使用 Homebrew
brew install git
```

**Linux（Ubuntu/Debian）：**
```bash
sudo apt update
sudo apt install git
```

### 確認安裝成功

```bash
git --version
# 預期輸出類似：git version 2.40.0
```

### 初次設定（必做）

Git 需要知道你是誰，這些資訊會顯示在每一次的提交記錄中：

```bash
# 設定你的名字（使用公司慣用的名稱）
git config --global user.name "你的名字"

# 設定你的 Email（使用公司 Email）
git config --global user.email "your.email@company.com"

# 確認設定是否正確
git config --list
```

---

## 3. Git 核心概念

在動手之前，先理解幾個關鍵概念：

### 倉庫（Repository / Repo）

存放專案所有程式碼與歷史記錄的地方，分為：
- **本地倉庫（Local）**：在你電腦上的副本
- **遠端倉庫（Remote）**：在 GitHub / GitLab 等平台上的副本

### 提交（Commit）

一個「提交」就是一個存檔點，記錄了：
- 這次修改了哪些內容
- 誰做的修改
- 什麼時候修改
- 為什麼修改（commit message）

### 工作區、暫存區、倉庫

理解 Git 的三個區域是掌握 Git 的關鍵：

```
工作區（Working Directory）
    ↓  git add
暫存區（Staging Area / Index）
    ↓  git commit
本地倉庫（Local Repository）
    ↓  git push
遠端倉庫（Remote Repository）
```

- **工作區**：你實際編輯檔案的地方
- **暫存區**：準備要提交的變更先放在這裡（讓你可以選擇性提交）
- **本地倉庫**：確認後的提交記錄存放在這裡
- **遠端倉庫**：推送到網路上與團隊共享

### 分支（Branch）

分支讓你可以在不影響主線的情況下開發新功能：

```
main branch:    A → B → C → D
                            ↓
feature branch:             E → F → G
```

---

## 4. 基礎指令操作

### 建立或複製倉庫

```bash
# 方法一：在現有目錄初始化新倉庫
mkdir my-project
cd my-project
git init

# 方法二：從遠端複製現有倉庫（最常用）
git clone https://github.com/company/project.git
cd project
```

### 查看狀態

```bash
# 查看目前工作區的狀態（最常用的指令之一）
git status
```

輸出說明：
- `Untracked files`：新增的檔案，Git 還不知道它的存在
- `Changes not staged for commit`：已追蹤的檔案被修改，但還沒加到暫存區
- `Changes to be committed`：在暫存區，等待提交

### 加入暫存區

```bash
# 加入單一檔案
git add filename.js

# 加入目錄下所有變更
git add .

# 互動式選擇要加入哪些變更（進階用法）
git add -p
```

### 提交變更

```bash
# 提交並附上說明訊息
git commit -m "feat: 新增使用者登入功能"

# 查看提交歷史
git log

# 精簡版歷史
git log --oneline
```

### Commit Message 撰寫規範

好的 commit message 讓團隊成員一眼看懂這次改了什麼：

```
格式：<type>: <簡短描述>

type 類型：
  feat     - 新增功能
  fix      - 修復 Bug
  docs     - 文件更新
  refactor - 重構（不影響功能）
  test     - 新增或修改測試
  chore    - 雜務（更新套件、設定等）

範例：
  feat: 新增使用者登入功能
  fix: 修正購物車金額計算錯誤
  docs: 更新 API 文件
```

---

## 5. 分支管理

### 建立與切換分支

```bash
# 查看所有分支
git branch

# 建立新分支
git branch feature/login

# 切換到分支
git checkout feature/login

# 建立並立即切換（常用簡寫）
git checkout -b feature/login

# Git 2.23+ 的新語法（更直覺）
git switch -c feature/login
```

### 合併分支

```bash
# 切換回主分支
git checkout main

# 將 feature 分支合併進來
git merge feature/login
```

### 刪除分支

```bash
# 刪除已合併的分支
git branch -d feature/login

# 強制刪除（未合併的分支）
git branch -D feature/login
```

---

## 6. 遠端協作流程

### 查看遠端設定

```bash
# 查看遠端倉庫資訊
git remote -v
```

### 拉取與推送

```bash
# 從遠端拉取最新變更（抓取 + 合併）
git pull origin main

# 推送到遠端
git push origin feature/login
```

### 日常開發流程

```
1. 拉取最新主線
   git checkout main
   git pull origin main

2. 建立功能分支
   git checkout -b feature/your-feature-name

3. 開發功能，多次提交
   git add .
   git commit -m "feat: 完成某功能"

4. 推送分支到遠端
   git push origin feature/your-feature-name

5. 在 GitHub/GitLab 建立 PR
```

---

## 7. 推出你的第一個 PR

### 什麼是 Pull Request（PR）？

PR 是一個「請求合併」的動作，讓你的程式碼在正式合入主線之前，由其他團隊成員進行審查（Code Review）。

### 推出 PR 的完整步驟

**步驟一：確保分支是最新的**

```bash
# 切回主分支拉取最新
git checkout main
git pull origin main

# 切回你的功能分支
git checkout feature/your-feature-name

# 將主分支的最新變更合入你的分支（避免衝突）
git merge main
# 或使用 rebase（保持更乾淨的歷史）
git rebase main
```

**步驟二：推送分支到遠端**

```bash
git push origin feature/your-feature-name
```

**步驟三：在 GitHub 建立 PR**

1. 前往 GitHub 專案頁面
2. 點擊 **"Compare & pull request"** 按鈕（通常會自動出現）
3. 填寫 PR 資訊：

```
標題：[簡短說明這個 PR 做了什麼]
例：feat: 新增使用者登入功能

內容（建議格式）：
## 變更說明
這個 PR 實作了使用者登入功能，包含：
- Email/密碼驗證
- JWT Token 產生
- 登入失敗錯誤處理

## 測試方式
1. 輸入正確帳號密碼，應成功登入
2. 輸入錯誤密碼，應顯示錯誤訊息

## 相關 Issue
Closes #123
```

4. 指定 Reviewers（需要審查你程式碼的同事）
5. 點擊 **"Create Pull Request"**

### PR 審查流程

```
你建立 PR
    ↓
Reviewer 審查程式碼，留下評論
    ↓
你根據評論修改程式碼
    ↓
git add . && git commit -m "fix: 根據 review 修正 ..."
git push origin feature/your-feature-name
    ↓
PR 自動更新，等待 Reviewer 重新確認
    ↓
Reviewer 核准（Approve）
    ↓
合併進主線（Merge）
```

---

## 8. 常見問題與解法

### 問題一：推送時被拒絕（rejected）

```
error: failed to push some refs
hint: Updates were rejected because the remote contains work that you do not have locally.
```

**原因**：遠端有別人推送的新 commit，你的本地版本落後了。

**解法**：
```bash
git pull origin main --rebase
git push origin feature/your-feature-name
```

### 問題二：合併衝突（Merge Conflict）

當兩個人修改了同一個檔案的同一個地方，Git 無法自動決定要保留哪個版本。

```
<<<<<<< HEAD（你的版本）
const name = "Alice";
=======
const name = "Bob";
>>>>>>> feature/other-branch（別人的版本）
```

**解法**：
1. 手動編輯檔案，決定要保留哪個版本（或兩者都保留）
2. 刪除衝突標記（`<<<<<<<`、`=======`、`>>>>>>>`）
3. `git add .`
4. `git commit -m "fix: 解決合併衝突"`

### 問題三：commit 了不該 commit 的檔案

```bash
# 從暫存區移除，但保留檔案（在推送前）
git reset HEAD filename.txt

# 撤銷最後一次 commit（保留修改，不影響檔案）
git reset --soft HEAD~1

# 查看哪些檔案不應該被追蹤 → 加入 .gitignore
```

### 問題四：.gitignore 怎麼設定

在專案根目錄建立 `.gitignore` 檔案，列出不需要 Git 追蹤的檔案：

```gitignore
# 環境變數（含機密資訊）
.env
.env.local

# 套件目錄
node_modules/

# 編譯輸出
dist/
build/

# 作業系統產生的檔案
.DS_Store
Thumbs.db

# IDE 設定
.vscode/
.idea/
```

### 問題五：想暫時儲存目前修改但不提交

```bash
# 暫存目前所有修改
git stash

# 做其他事情後，取回暫存的修改
git stash pop
```

---

## 9. 實作練習

### 練習 A：完成你的第一個 Commit

1. 在本機建立一個新目錄並初始化 Git
2. 建立一個 `README.md` 檔案，寫入你的自我介紹
3. 將檔案加入暫存區並提交

```bash
mkdir git-practice
cd git-practice
git init
echo "# 我的第一個 Git 練習\n\n我是 [你的名字]" > README.md
git add README.md
git commit -m "docs: 新增自我介紹"
```

### 練習 B：分支練習

1. 在現有倉庫建立分支 `feature/add-about`
2. 新增一個 `ABOUT.md` 檔案
3. 提交後合併回 `main`

```bash
git checkout -b feature/add-about
echo "# 關於本專案" > ABOUT.md
git add ABOUT.md
git commit -m "docs: 新增 ABOUT 頁面"
git checkout main
git merge feature/add-about
```

### 練習 C：推出你的第一個真實 PR

1. Clone 公司指定的練習倉庫
2. 建立分支並做一個小修改（如修正 typo 或新增文件）
3. 推送並建立 PR，指定你的 mentor 為 Reviewer

---

## 附錄：常用指令速查表

| 指令 | 說明 |
|------|------|
| `git init` | 初始化新倉庫 |
| `git clone <url>` | 複製遠端倉庫 |
| `git status` | 查看工作區狀態 |
| `git add <file>` | 加入暫存區 |
| `git add .` | 加入所有變更到暫存區 |
| `git commit -m "<msg>"` | 提交變更 |
| `git log --oneline` | 精簡提交歷史 |
| `git branch` | 列出所有分支 |
| `git checkout -b <branch>` | 建立並切換分支 |
| `git merge <branch>` | 合併分支 |
| `git pull origin <branch>` | 拉取遠端最新變更 |
| `git push origin <branch>` | 推送到遠端 |
| `git stash` | 暫存目前修改 |
| `git stash pop` | 取回暫存的修改 |
| `git diff` | 查看未暫存的變更 |
| `git reset --soft HEAD~1` | 撤銷最後一次提交（保留修改） |

---

## 下一步學習建議

完成本課程後，你可以進一步學習：

- **Git Flow**：一套適合團隊協作的分支管理策略
- **Rebase vs Merge**：兩種不同的合入策略與適用場景
- **Cherry-pick**：從其他分支挑選特定 commit
- **Git Bisect**：用二分搜尋法找出引入 Bug 的 commit
- **GitHub Actions**：自動化 CI/CD 流程

---

*如有任何問題，請向你的 mentor 或在公司 Slack 的 #git-help 頻道發問。*
