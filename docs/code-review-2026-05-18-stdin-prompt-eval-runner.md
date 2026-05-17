# Code Review 紀錄 — 2026-05-18（第 1 輪）

## 📋 Code Review 摘要

**審查範圍：** 最新 commit `75a2fa3` 對所有 `run_evals.py` 與 `skill-creator/SKILL.md` runner 範本的 stdin prompt 修正
**整體評估：** ⚠️ 主要修正方向正確，建議補一個 timeout artifact 修正

---

### 🔴 必須修正（Critical）

未發現會阻止合併的問題。

---

### 🟠 建議改善（Warning）

#### 問題 1：timeout 時不會保留已輸出的 stdout artifact
- **檔案：** `skill-creator/evals/run_evals.py:99`
- **檔案：** `code-reviewer/evals/run_evals.py:157`
- **檔案：** `skill-creator/SKILL.md:268`
- **問題：** 這三處改成 `communicate(input=prompt, timeout=timeout)` 後，正常完成時會在 `output_file.write_text(stdout, ...)` 寫出完整輸出；但 timeout 分支只執行 `process.kill()` 與 `process.communicate()`，沒有把 timeout 前已收集到的輸出或 timeout 訊息寫入 `output.txt`。
- **影響：** 若 eval timeout，runner summary 仍會指向 `output.txt`，但該檔可能不存在或缺少 timeout 前輸出，會降低後續 debug 與 benchmark artifact 可用性。這不影響本次修正 WinError 206 的主要目的，但會讓 timeout 情境退化。
- **建議修正：**
  ```python
  try:
      stdout, _ = process.communicate(input=prompt, timeout=timeout)
      output_file.write_text(stdout, encoding="utf-8")
      return process.returncode, False
  except subprocess.TimeoutExpired as error:
      process.kill()
      stdout, _ = process.communicate()
      partial_output = error.output or stdout or ""
      output_file.write_text(f"{partial_output}\n[timeout] killed after {timeout}s\n", encoding="utf-8")
      return -1, True
  ```

---

### 🔵 型別安全

#### ✅ 符合項目
- `run_ai` 簽名維持 `tuple[int, bool]`，呼叫端不需要調整資料結構。
- `subprocess.Popen(..., text=True, encoding="utf-8", errors="replace")` 搭配 `communicate(input=prompt)` 的型別一致，`prompt` 以字串進 stdin，不再放入 argv。
- Pattern B runner 使用 binary stdin 時以 `prompt.encode("utf-8")` 寫入；`apply` 使用 `text=True` 時寫入字串，兩種型態與 Popen 設定相符。

---

### ⚪ 使用者自行決定（註解類問題）

未發現新增 TODO、FIXME、被註解掉的程式碼或暫時偵錯註解。

---

### 查證與驗證

- 本機 `codex exec --help` 已確認：未提供 `[PROMPT]` 參數或使用 `-` 時，instructions 會從 stdin 讀取；因此移除 argv prompt、改走 stdin 是正確修法。
- 全專案 `run_evals.py` 掃描結果顯示已沒有 `[*command_prefix, prompt]` 或等價 prompt-in-argv 寫法。
- `python -m py_compile` 已對 8 個 `run_evals.py` 通過。
- 既有 `skill-creator/eval-results/eval-1` 顯示 `with_skill` 與 `without_skill` 的 `exit_code` 都是 `0`，且未出現 `WinError 206` 或「檔名或副檔名太長」。

---

### 審查結論

本次修正能解決 Windows 命令列長度限制問題，且已同步更新所有 runner 與 `skill-creator` 範本。建議再補 timeout 分支的 artifact 寫檔，避免長時間 eval 被殺掉時失去 debug 輸出。
