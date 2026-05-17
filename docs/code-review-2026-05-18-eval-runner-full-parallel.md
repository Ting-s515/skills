# Code Review 紀錄 — 2026-05-18（第 1 輪）

## 📋 Code Review 摘要

**審查範圍：** 本專案 8 個 `run_evals.py`，重點確認所有 eval/config run 是否統一以 `max_workers=len(tasks)` 全部同時啟動，並確認 prompt 是否已走 stdin 避免 Windows argv 長度限制。
**整體評估：** ✅ 核心行為符合要求，可達成所有 run 同時啟動；另有一項 CLI 文件/輸出一致性 Warning 建議後續清理。

---

### 📐 規格符合度

#### ✅ 符合規格的項目
- **所有 run 同時啟動：** 8 個 runner 都使用 `ThreadPoolExecutor(max_workers=len(tasks))`，不再以 `min(args.jobs, len(tasks))` 限制 worker 數。
- **task flatten 完整：** 通用 runner 先建立 `tasks = [(index, eval_case, config) ...]`，再對每個 task submit `run_eval_config`；`skill-creator` 與 `code-reviewer` 也把 `with_skill` / `without_skill` 各自作為獨立 task submit。
- **等待最慢回應完成：** 所有 runner 都透過 `as_completed(futures)` 收集結果，主流程會等所有 future 完成後才輸出 summary 與結束。
- **Windows argv 長度限制防護：** 8 個 runner 都使用 `stdin=subprocess.PIPE`，並透過 `communicate(input=prompt)` 或 `process.stdin.write(...)` 傳入 prompt；靜態掃描未發現 `[*command_prefix, prompt]`、`command_prefix + [prompt]`、`cmd.append(prompt)` 等 prompt-in-argv 舊寫法。

#### ❌ 不符合或缺漏的項目
- 未發現核心行為缺漏。

---

### 🔴 必須修正（Critical）

未發現會阻止合併的問題。

---

### 🟠 建議改善（Warning）

#### 問題 1：6 個通用 runner 仍保留已失效的 `--jobs` CLI 與輸出
- **檔案：** `apply/evals/run_evals.py:51`
- **檔案：** `propose/evals/run_evals.py:48`
- **檔案：** `propose-sync/evals/run_evals.py:48`
- **檔案：** `llm-repo/evals/run_evals.py:48`
- **檔案：** `fleet-review/evals/run_evals.py:48`
- **檔案：** `writing-training-doc/evals/run_evals.py:48`
- **問題：** 這 6 個 runner 已改為 `ThreadPoolExecutor(max_workers=len(tasks))`，但仍保留 `DEFAULT_JOBS`、`--jobs` 參數、help 文字 `Max parallel runs`，並在執行時輸出 `[jobs] {args.jobs}`。目前 `args.jobs` 不再影響實際 worker 數。
- **影響：** 使用者可能以為 `--jobs 1` 可以限制並行度，或誤判 log 中 `[jobs] 2` 代表實際只啟動 2 個 worker；這與「所有 run 同時啟動」的新行為不一致，容易造成操作與 debug 混淆。
- **建議修正：**
  ```python
  # 移除 DEFAULT_JOBS 與 --jobs 參數，或改名為相容性 no-op 並在 help 中明確標示 ignored。
  print(f"[parallel] launching {len(tasks)} runs  [timeout] {args.timeout}s  [configs] {', '.join(configurations)}")
  with ThreadPoolExecutor(max_workers=len(tasks)) as executor:
      # ...
  ```

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
- `rg -n "max_workers\\s*=|ThreadPoolExecutor\\(" -g run_evals.py` 確認 8 個 runner 都是 `ThreadPoolExecutor(max_workers=len(tasks))`。
- 靜態掃描確認未發現 prompt-in-argv 舊寫法。
- `python -m py_compile` 已對 8 個 `run_evals.py` 通過。

---

### 審查結論

Claude 這輪修改已把本專案所有 `run_evals.py` 的核心執行模型對齊為「所有 task 同時 submit，等待最慢的 future 完成後結束」。Windows 長 prompt 限制也仍由 stdin prompt 路徑防住。建議後續清理 6 個通用 runner 中已不生效的 `--jobs` CLI 與 `[jobs]` log，避免使用者誤判實際並行行為。
