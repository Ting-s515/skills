---
name: rewind
description: 還原上一次 AI（Codex）對檔案的所有變更。當使用者說「rewind」、「還原」、「undo」、「回退」、「把剛才改的還原」、「上一步」時必須載入此技能。這是 Codex 尚未原生支援 /rewind 前的暫時替代方案，專注於還原未提交的檔案變更。
---

## 執行步驟

### Step 1：找出上一輪 AI 修改的檔案

回顧對話歷史，找出最近一次 AI 執行的所有寫檔操作（write_file、edit_file、apply_patch 等），列出所有被修改的檔案路徑。

將清單列給使用者確認：
```
以下是上一輪 AI 修改的檔案，確認還原？
- src/foo.ts
- src/bar.ts
```

### Step 2：還原那些檔案

使用者確認後，執行：
```bash
git restore --staged <file1> <file2> ... && git restore <file1> <file2> ...
```

只還原上一輪 AI 修改的檔案，不動使用者自己的其他未提交修改。

### Step 3：回報結果

列出已還原的檔案，並提示：
> 若要同時回退對話 context，請按兩次 `Esc`

## 無未提交變更時

若 `git status` 顯示 working tree clean，告知使用者：
> 目前沒有未提交的變更，無法還原上一次 AI 的檔案修改。
> 若已提交，可考慮使用 `git reset --soft HEAD~1` 退回最近一次 commit。

## 非 git 專案時

若不在 git repo 中，告知使用者：
> 目前目錄非 git repository，無法自動還原。建議先執行 `git init` 並在每次實作前 commit，以便日後 rewind。
