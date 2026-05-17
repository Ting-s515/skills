# Code Review 紀錄 — 2026-05-18（第 2 輪）

## 📋 Code Review 摘要

**審查範圍：** 重新審查本專案 8 個 `run_evals.py`，確認是否已統一改成 `max_workers=len(tasks)`、所有 eval/config run 是否同時 submit 並等待最慢的 future 完成，以及 prompt 是否已走 stdin 避免 Windows argv 長度限制。
**整體評估：** ✅ 所有問題已修正完畢（commit 見後續追蹤）

---

### 📐 規格符合度

#### ✅ 符合規格的項目
- **所有 run 同時啟動：** 8 個 runner 都使用 `ThreadPoolExecutor(max_workers=len(tasks))`，已符合「所有 run 同時啟動」的要求。
- **task flatten 完整：** 通用 runner 先建立 `tasks = [(index, eval_case, config) ...]`，再對每個 task submit `run_eval_config`；`skill-creator` 與 `code-reviewer` 也把 `with_skill` / `without_skill` 各自作為獨立 task submit。
- **等待最慢回應完成：** 所有 runner 都透過 `as_completed(futures)` 收集結果，主流程會等所有 future 完成後才輸出 summary 與結束。
- **Windows argv 長度限制防護：** 8 個 runner 都使用 `stdin=subprocess.PIPE`，並透過 `communicate(input=prompt)` 或 `process.stdin.write(...)` 傳入 prompt；靜態掃描未發現 `[*command_prefix, prompt]`、`command_prefix + [prompt]`、`cmd.append(prompt)` 等 prompt-in-argv 舊寫法。
- **失效 `--jobs` argparse 已移除：** 6 個通用 runner 已移除 `DEFAULT_JOBS`、`parser.add_argument("--jobs", ...)`、`args.jobs` 與 `[jobs]` log；本機實測 `python apply/evals/run_evals.py --jobs 1 --dry-run` 已回報 `unrecognized arguments: --jobs`。

#### ❌ 不符合或缺漏的項目
- 未發現核心執行行為缺漏。

---

### 🔴 必須修正（Critical）

未發現會阻止合併的問題。

---

### 🟠 建議改善（Warning）

#### ~~問題 1：6 個通用 runner 的檔頭 Usage docstring 仍殘留 `--jobs N`~~ ✅ 已修正
- **檔案：** apply、propose、propose-sync、llm-repo、fleet-review、writing-training-doc
- **問題：** argparse 已移除 `--jobs`，但檔頭 docstring Options 仍殘留 `--jobs N Parallel workers`，使用者閱讀檔案會誤以為該參數仍可使用。
- **修正內容：** 從 6 個檔案的 docstring 中移除 `--jobs N` 那一行。

---

### 🔵 型別安全

#### ✅ 符合項目
- `tasks` 結構在 submit 時直接傳入 `run_eval_config` / `run_eval_task`，沒有型別不一致或漏傳 config 的問題。
- prompt 透過 stdin 傳入，字串與 bytes 路徑分別符合各 runner 的 `Popen` 設定。
- timeout 分支仍保留 process cleanup 與 artifact 寫入，不會因並行數改為 `len(tasks)` 破壞原本的 timeout 結果結構。

---

### ⚪ 使用者自行決定（註解類問題）

未發現新增 TODO、FIXME、被註解掉的程式碼或暫時偵錯註解。

---

### 查證與驗證

- `rg --files -g run_evals.py` 確認本專案共有 8 個 `run_evals.py`。
- `rg -n "ThreadPoolExecutor\\(|max_workers\\s*=|tasks = \\[|as_completed\\(" -g run_evals.py` 確認 8 個 runner 都使用 `ThreadPoolExecutor(max_workers=len(tasks))`，並以 `as_completed` 等待全部 future。
- `rg -n "stdin=subprocess\\.PIPE|communicate\\(input=prompt|process\\.stdin\\.write" -g run_evals.py` 確認 8 個 runner 都透過 stdin 傳 prompt。
- prompt-in-argv 舊寫法掃描未命中。
- `rg -n -g run_evals.py -- "--jobs|args\\.jobs|DEFAULT_JOBS|Max parallel|\\[jobs\\]"` 只剩 6 個檔頭 docstring 的 `--jobs N`，沒有 argparse 或 runtime log 殘留。
- `python -m py_compile` 已對 8 個 `run_evals.py` 通過。
- `python apply/evals/run_evals.py --jobs 1 --dry-run` 已確認 `--jobs` 不再被 argparse 接受。

---

### 審查結論

所有 `run_evals.py` 核心執行模型已符合「`max_workers=len(tasks)`、所有 run 同時 submit、等待最慢回應完成」的要求；Windows 長 prompt 由 stdin prompt 路徑防住。

**後續追蹤：** 已從 6 個通用 runner 的 docstring 移除殘留的 `--jobs N` 說明，文件與 CLI 行為現已一致。所有問題已全數關閉。
