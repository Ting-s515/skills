---
name: copilot-tdd-general
description: TDD 分工協作：Claude Code 只寫測試（紅燈），實作派給 GitHub Copilot CLI（--yolo）跑到綠燈，以節省 Claude Code token；Copilot 額度或速率用盡、執行失敗或多輪仍未綠燈時由 Claude Code 接手實作。使用者說「copilot-tdd-general」「copilot-tdd」「測試我寫、實作交給 copilot」「派給 copilot 實作」時使用。
---

# Copilot TDD 分工

Claude Code 負責「定義行為」（測試），Copilot CLI 負責「讓測試通過」（實作）。
Claude Code 不讀 Copilot 的完整輸出，只看腳本回傳的一行 JSON 與自己重跑的測試結果。
實作寫法由 Copilot 決定，驗收只看測試是否全綠。

## 前置條件

- 已安裝 PowerShell 7（`pwsh`）與 GitHub Copilot CLI；`--deny-tool` 行為以 Copilot CLI 1.0.116 實測。
- 預設模型為 `claude-opus-5.5`、推理強度 `medium`；除非使用者特別指定模型或推理強度，否則一律使用預設，
  不要自行改用 `auto` 或其他模型。
- 預設模型須在 Copilot 訂閱中可用（需先登入有該模型的方案，例如 Copilot Business；免費方案不可用），
  否則由使用者決定改用哪個模型，再以 `-Model` 指定。
- 派工單與 log 放在不進版控的暫存目錄（例如 `.scratch/copilot/`）；先確認該目錄已列入 `.gitignore`。

## 流程

1. **寫測試（紅燈）**
   - 專案有自己的 TDD skill 時先載入，依其接縫、命名、放置規則寫測試；沒有專案版時改載入 `tdd-general`。
   - 只跑本次相關的測試，確認是**因為功能未實作而失敗**（不是語法或設定錯誤）。
   - 記下：測試檔清單、單一可執行的測試指令。

2. **寫派工單**：寫到暫存目錄的 `task.md`（例如 `.scratch/copilot/task.md`），內容固定包含：
   - 目標：一句話說明要實作的功能，附規格文件路徑（讓 Copilot 自己讀，不要貼全文）。
   - 規格、測試規格、feature case 等有多份文件時，在 `task.md` 逐行列出每份的路徑即可，
     不需要 `--attachment`（只適用圖片與原生文件）；工作目錄外的文件用絕對路徑。
     實測（Copilot CLI 1.0.117、`--yolo`）：工作目錄內外共三份文件都能讀到。
   - 測試檔路徑與測試指令。指令要能在 Copilot 執行的 shell 直接執行：
     - Windows 上 Copilot 以 PowerShell 執行，含 `-D` 等會被 PowerShell 拆開的參數要整段加引號，
       例如 `mvn test "-Dtest=XxxTest"`；macOS／Linux 以 bash／zsh 執行，依該 shell 的引號規則。
     - 寫入前先在同一種 shell 實際跑一次，確認指令可直接執行。
     - 多模組專案先把依賴模組建置或安裝一次，派工單的指令只建置受測模組，避免 Copilot 每跑一次都重建依賴；
       本次實作需要修改依賴模組時，才一併建置。
   - 規則：不可修改測試檔；不可 commit/push；不可用 skip、`@Disabled`、刪斷言等方式繞過；
     遵守專案的 `AGENTS.md`（若有）；只跑指定測試，不跑全套。
   - 完成條件：指定測試指令全數通過，且 build/lint 無新錯誤。
   - 結尾要求：最後輸出「修改檔案清單 + 測試結果一行摘要」，不要長篇說明。

3. **派工**（`run_in_background: true`，等完成通知，不要輪詢 log）：

   ```powershell
   pwsh -NoProfile -File <skill 目錄>/scripts/invoke-copilot.ps1 -PromptFile .scratch/copilot/task.md -TestFiles "src/__tests__/a.test.ts","src/test/java/.../BTest.java" -Model claude-opus-5.5 -ReasoningEffort medium
   ```

   - `<skill 目錄>` 為本 skill 所在目錄（載入 skill 時提供）。
   - `-TestFiles` 必填本次寫的測試檔（相對 repo root），腳本會比對前後 hash 並回報 `modifiedTests`。
   - 在 repo 根目錄以外的位置派工（例如另一個 worktree）時，以 `-WorkDir` 指定 Copilot 的工作目錄。
   - 可選參數：`-Model`（預設 `claude-opus-5.5`）、`-ReasoningEffort`（預設 `medium`，可改 `high`）、`-MaxAiCredits 200`、
     `-ProtectedPaths`（覆寫受保護的測試路徑 glob）。
   - 派工時一律明確傳 `-Model claude-opus-5.5 -ReasoningEffort medium`（與腳本預設值相同，明確寫出避免誤判為 `auto`）；
     只有使用者明確指定其他模型或推理強度時才改值。
     使用者指定 `auto` 時要把 `-ReasoningEffort` 設為 `''`，因為 `auto` 不支援 `--reasoning-effort`。

4. **驗收**（不相信 Copilot 的自述）：
   - `git diff --stat` 確認測試檔沒被改；若被改，還原該檔的 Copilot 修改並視為失敗。
   - Claude Code 自己執行測試指令，看是否綠燈。
   - 只在需要時才讀 log 的特定段落（用 Grep 找錯誤），不要整份讀。

5. **分流**

   | 結果 | 處理 |
   | --- | --- |
   | `ok` 且測試綠燈 | 進入專案的 commit 流程 |
   | `ok` 但測試仍紅 | 把失敗摘要（只貼失敗測試名稱與錯誤前幾行）附加到 task.md，再派一次；含第一次派工總共最多派 2 次 |
   | `tests_modified` | 用 Claude 寫的版本還原測試檔，在 task.md 重申禁止改測試後重派；再犯就由 Claude Code 接手 |
   | `quota` / `rate_limit` | 告知使用者原因，Claude Code 直接接手實作 |
   | `failed`（非零結束碼） | 看 `tail` 判斷；環境問題先修再重派一次，否則 Claude Code 接手 |
   | 派滿 2 次（含第一次）仍紅 | Claude Code 接手，在既有修改上繼續，不要從頭重寫 |

6. **回報**：說明哪些由 Copilot 實作、哪些由 Claude Code 接手，以及 usage 檔路徑（`*.usage.json` 有 AI credits 用量）。

## 注意

- `--yolo` 下仍生效的保護只有 `--deny-tool`（腳本已擋 git commit/push/reset/checkout/restore/stash/clean 與測試路徑寫入）。
  實測（Copilot CLI 1.0.116）：被要求建立 `__tests__/x.test.ts` 時，Copilot 改用 shell 建檔，`write()` deny 擋不住；
  因此測試檔保護以 `-TestFiles` hash 比對與第 4 步 `git diff` 為準，deny 規則只是第一道防線。
- 腳本預設的受保護測試路徑涵蓋 JS／TS、Java、Python、Go、C# 的常見命名；專案慣例不同時以 `-ProtectedPaths` 覆寫。
- 派工前工作區若有非本次的變更，先提醒使用者，避免 Copilot 混改。
- Copilot 會自動讀專案的 `AGENTS.md`（若有）；不要在 task.md 重複貼專案規範。
