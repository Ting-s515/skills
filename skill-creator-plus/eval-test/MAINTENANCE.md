# eval test runner 維護指南

本文件記錄本專案各 skill 的 `evals/run_evals_bdd.py` 後續維護時應對齊的共用 BDD eval 執行風格。目標是讓 Codex CLI runner 盡量接近 Claude Code skill-creator 的 eval flow，方便後續模型接手時不需要重新推導設計方向。

## 設計哲學

`run_evals_bdd.py` 是跨工具（Claude CLI 與 Codex CLI）的 BDD 自評分 eval runner。
Python 端計算 diff，將 diff + spec + expectations embed 進單一 prompt，AI 在 prompt 內完成任務並自評分（`E1: PASS/FAIL — 證據`），不需要任何 filesystem 存取。

| 面向 | 舊 `run_evals.py` | `run_evals_bdd.py` |
|------|-------------------|--------------------|
| diff 取得 | AI 執行 `git diff` | Python 計算後 embed 進 prompt |
| 需要 filesystem | 是（建立 temp git repo） | 否 |
| 評分方式 | 外部 grader | AI 在 prompt 內自評分 |
| baseline 對照 | with_skill vs without_skill | 僅 with_skill（by design） |
| 通過率輸出 | 無 | `X/Y expectations passed` |

## 命名規範

| 項目 | 規定命名 | 說明 |
|---|---|---|
| eval runner 腳本 | `evals/run_evals_bdd.py` | 固定此檔名，`validate_structure.py` 依賴此路徑進行結構驗證 |
| eval 定義檔 | `evals/evals.json` | runner 讀取的 eval case 清單，必須含 `expectations` 欄位 |
| fixture 根目錄 | `evals/fixtures/` | 各 eval 的 base/staged/spec 放在此目錄下 |
| eval fixture 目錄 | `fixtures/eval-<id>/` | 依 evals.json 的 `id` 欄位命名 |
| 輸出根目錄 | `eval-results-bdd/` | 所有 eval 輸出放在此目錄下 |
| 單一 eval 輸出 | `eval-results-bdd/eval-<id>/output.txt` | AI 完整輸出含 Grading 區塊 |

> 新增 skill 時，eval runner 腳本必須命名為 `run_evals_bdd.py`，否則 `validate_structure.py` 將靜默跳過（SKIP）而不驗證。

## fixture 結構

```text
evals/fixtures/eval-1/
├── base/     # 變更前的檔案（空目錄 = 新增檔案情境）
├── staged/   # 變更後的檔案（被審查的程式碼）—— 必要
└── spec/     # 規格文檔（選填，有則自動注入 prompt）
```

`staged/` 是必要目錄；`base/` 與 `spec/` 可為空目錄。

## 維護原則

1. **並行執行**
   - 所有 eval 以 `ThreadPoolExecutor(max_workers=len(evals))` 同時啟動
   - 總執行時間 ≈ 最慢的單一 eval，而非全部加總
   - 執行 runner 時預設不得指定或新增 `--jobs` 限流，避免讓獨立 eval 排隊等待
   - 只有在使用者明確要求限流，或實際遇到資源限制、CLI 併發錯誤、timeout 問題時，才可引入或使用 `--jobs`，且需說明原因
   - 不要改成序列 for 迴圈

2. **自評分格式**
   - AI 輸出結束後須接 `## Grading` 區塊
   - 每條 expectation 獨立一行：`E1: PASS — 證據` 或 `E1: FAIL — 說明`
   - `parse_grading()` 以 regex 解析，找不到對應行視為 FAIL

3. **Windows UTF-8 相容**
   - `__main__` 必須包含 re-exec 邏輯：Windows 環境偵測到非 UTF-8 模式時，以 `-X utf8` 重新執行自身
   - 不要改回 `sys.stdout.reconfigure()` 補丁寫法

4. **timeout 落在單一 eval 層級**
   - 每個 `run_bdd_eval()` 呼叫都有獨立的 `DEFAULT_TIMEOUT`（預設 300 秒）
   - timeout 後殺掉 process，輸出 `[timeout] killed after Ns`

5. **通過率輸出**
   - Summary 行格式：`=== Summary: X/Y expectations passed ===`
   - exit code 0 = 全部通過，1 = 有任何 FAIL 或未評分

## 建議輸出結構

```text
<skill-name>/eval-results-bdd/
  eval-1/
    output.txt       ← AI 完整輸出（Code Review + Grading 區塊）
  eval-2/
    output.txt
  eval-3/
    output.txt
```

## 完成條件

後續修改 `run_evals_bdd.py` 時，應至少符合：

- 可並行執行多個 eval（`ThreadPoolExecutor`）
- 預設執行不需要也不應傳入 `--jobs`
- 每個 eval 的輸出存至 `eval-results-bdd/eval-{id}/output.txt`
- 通過率可從 Summary 行讀取（`X/Y expectations passed`）
- Windows UTF-8 re-exec 機制完整（`sys.platform == "win32" and not sys.flags.utf8_mode`）
- 任一 eval 有 FAIL 或 timeout 時 exit code 為 1
