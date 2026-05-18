# skill-creator 本地擴充維護指南

## 核心設計哲學

`run_evals_bdd.py` 現為 skill-creator 官方標準模板（定義於 `SKILL.md` 的 Test Cases 段落）。
與舊 `run_evals.py` 的根本差異在於：BDD runner 讓 AI 在單一 prompt 內完成任務並自評分，
不需要 with_skill / without_skill 兩組跑法，也不需要外部 grader，通過率直接從輸出取得。

**Why BDD：** `run_evals.py` 的 with_skill vs without_skill 架構只能判斷「有無 skill 的差異」，
但無法量化 skill eval test 通過率。`run_evals_bdd.py` 透過 `expectations` 欄位與自評分機制，
每次執行都能得到具體的 X/Y expectations passed 結果，支援迭代改善 skill 品質。

**修改原則：** 任何對 `run_evals_bdd.py` 模板的修改都必須同步更新 `skill-creator/SKILL.md`
與 `evals/local_extensions.md`（插入內容區塊），確保三者一致。

---

## 官方行為 vs BDD runner 對照表

| 面向 | 官方 SKILL.md（Claude Code 子代理） | `run_evals_bdd.py` |
|------|-------------------------------------|---------------------|
| 執行方式 | Claude Code 子代理（並行） | Codex/claude CLI（Python ThreadPoolExecutor 並行） |
| diff 取得 | AI 執行 shell 指令 | Python difflib 計算後 embed 進 prompt |
| 評分方式 | 外部 grader subagent | AI 在 prompt 內自評分（E1: PASS/FAIL） |
| 結果存放 | `iteration-N/eval-ID/with_skill/` | `eval-results-bdd/eval-ID/output.txt` |
| 通過率 | benchmark.json 彙整 | Summary 行直接輸出 |

---

## 維護原則

1. **fixture 結構必須齊備**：每個 eval 需要 `evals/fixtures/eval-<id>/staged/`，
   `base/` 與 `spec/` 可為空目錄，但 `staged/` 必須存在。

2. **`expectations` 欄位必填**：`evals.json` 每個 eval 都必須有 `expectations` 清單，
   這是 BDD runner 的評分依據，空陣列會導致 AI 無法評分。

3. **Windows UTF-8 re-exec**：`__main__` 的 re-exec 邏輯不可移除，
   這是在 Windows cp950 終端機正確輸出中文的唯一可靠方式。

4. **`evals/` 目錄受保護**：`update-skill-creator` 更新時不會覆蓋 `evals/` 目錄，
   `local_extensions.md` 的插入內容區塊會在更新後自動注入到官方 SKILL.md 的指定錨點之後。

---

## 相關檔案

- `evals/local_extensions.md` — 本地擴充定義（受保護，update-skill-creator 不覆蓋）
- `evals/MAINTENANCE.md` — 本文件，維護指南
- `SKILL.md` — 官方技能主檔，Test Cases 段落已含 run_evals_bdd.py 完整模板
- `update-skill-creator.py` / `.ps1` — 更新腳本，負責合併官方更新與本地擴充
