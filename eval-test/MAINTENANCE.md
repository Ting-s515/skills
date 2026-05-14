# eval test runner 維護指南

本文件記錄本專案各 skill 的 `evals/run_evals.py` 後續維護時應對齊的共用 eval 執行風格。目標是讓 Codex CLI runner 盡量接近 Claude Code skill-creator 的 eval flow，方便後續模型接手時不需要重新推導設計方向。

## 參考基準

以 `writing-training-doc-workspace/` 的 Claude Code eval 輸出為主要參考。該 workspace 的特徵：

- 每次測試以 `iteration-N/` 為一輪。
- 每個 eval case 有獨立資料夾，例如 `eval-kafka-lab/`。
- 每個 eval case 內分開保存 `with_skill/` 與 `without_skill/`。
- 每個 run 會保存可回放的輸出、`timing.json`、`grading.json`。
- 所有 run 完成後再彙整為 `benchmark.json` 與 reviewer HTML。

## 維護原則

1. **每個 eval case 必須彼此隔離**
   - 不要讓多個 eval 共用同一份輸出檔。
   - 若 eval 會修改檔案，優先使用每個 eval 自己的 workspace copy。

2. **with_skill 與 without_skill 必須分開**
   - `with_skill`：注入或指向目標 skill。
   - `without_skill`：只傳原始 prompt，作為 baseline。
   - 兩者輸出不可混在同一個 log，避免 benchmark 無法追蹤來源。

3. **並行執行以外層 runner 控制**
   - Claude Code 可在同一回合 spawn 多個 sub-agent。
   - Codex CLI runner 應以 Python 同時啟動多個 `codex exec` process 模擬 fan-out。
   - 不要期待單一 `codex exec` 自動替整批 eval 做外層並行。

4. **每個 run 必須留下可診斷資料**
   - `output.log`：完整 stdout/stderr。
   - `last-message.md`：最後 assistant message，建議搭配 `--output-last-message`。
   - `timing.json`：開始時間、結束時間、duration、exit code、timeout 狀態。
   - `metadata.json` 或 `eval_metadata.json`：eval id、name、prompt、configuration、workspace path。

5. **timeout 要落在單一 run 層級**
   - 不要只依賴外層工具 timeout。
   - 每個 `codex exec` process 都應有自己的 timeout。
   - timeout 後要終止該 process tree，並將該 run 標成 failed/timeout。

6. **summary 必須可讀**
   - 所有 run 結束後印出表格式摘要。
   - 摘要至少包含 eval name、configuration、exit code、duration、log path。
   - 任一 run 失敗時，整體 runner 應 exit non-zero。

## 建議輸出結構

```text
<skill-name>/evals/eval-runs/
  iteration-1/
    <eval-name>/
      eval_metadata.json
      with_skill/
        output.log
        last-message.md
        timing.json
      without_skill/
        output.log
        last-message.md
        timing.json
    <another-eval-name>/
      eval_metadata.json
      with_skill/
      without_skill/
    benchmark.json
    review.html
```

若短期只要驗證某個 skill 本身，也可以先只跑 `with_skill`。但 runner 的資料結構仍應保留 `configuration` 欄位，避免之後補 baseline 時需要重改格式。

## 實作路線

### 第一階段：低成本並行

- 保留現有 `evals.json`。
- 新增 `--jobs` 參數，預設 2 或 3。
- 使用 `subprocess.Popen` 同時啟動多個 `codex exec`。
- 每個 eval 寫入自己的 `output.log` 與 `timing.json`。
- 加入 per-run timeout。

這一階段可以先不複製 workspace，但要接受多個 Codex process 可能看到同一個 repo 的 git status。

### 第二階段：穩定隔離

- 每次執行建立新的 `eval-runs/iteration-N/`。
- 每個 eval 先複製 fixture 到獨立 workspace。
- 使用 `codex exec --cd <workspace>` 執行。
- 產出 `benchmark.json`。
- 後續可接 `skill-creator/eval-viewer/generate_review.py` 或相容的 static review HTML。

## 風險與取捨

- 並行能把總時間從「所有 eval 時間相加」壓到接近「最慢 eval 的時間」。
- 並行直接跑同一個 git repo 會有互相污染風險，尤其是 agent 內部執行 `git add -N`、`git diff`、code review 時。
- 對 `apply` 這類會改檔的 skill，長期應採用 workspace copy 隔離。
- 對純文字產出型 skill，可以先使用較簡單的並行 runner。

## 完成條件

後續修改 `run_evals.py` 時，應至少符合：

- 可並行執行多個 eval。
- 每個 eval 的 log 與 timing 分開。
- timeout 可定位到單一 eval。
- 最終 summary 能指出失敗的是哪個 eval 與哪個 configuration。
- 輸出結構可直接對照 Claude Code skill-creator 產生的 workspace。
