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
| 程式碼輸入 | 子代理有 filesystem 存取，可自行讀取檔案 | Python difflib 計算 diff，embed 進 prompt |
| 評分方式 | 外部 grader subagent | AI 在 prompt 內自評分（E1: PASS/FAIL） |
| 結果存放 | `iteration-N/eval-ID/with_skill/` | `eval-results-bdd/eval-ID/output.txt` |
| 通過率 | benchmark.json 彙整 | Summary 行直接輸出 |

---

## 9 個本地 Patch 說明

`update-skill-creator.py` 拉取官方最新 SKILL.md 後，套用以下 9 個 patch 對齊本地行為。
每次官方更新後若 patch 失效（target 字串找不到），腳本會 crash 並提示需要重新確認。

### 核心背景

官方 skill-creator 使用 **with_skill vs without_skill（baseline）對照跑法**：
每個 eval 同時跑兩個 subagent，比較有無 skill 的差異，再用外部 grader 評分。

本地改為 **BDD 自評分 runner**：只跑 with_skill，AI 在單一 prompt 內完成任務並自評分
（`E1: PASS/FAIL`），直接輸出 `X/Y expectations passed`，不需要 baseline 也不需要 grader。

**9 個 patch 的統一目的：移除官方 baseline 流程，補入本地 BDD runner 指令。**

| # | 名稱 | 做什麼 | 為什麼需要 |
|---|------|--------|-----------|
| 1 | evals.json 範例欄位 | 移除 `expected_output`、`files`；補 `name`、`expectations` | 官方範例有 BDD runner 不使用的欄位；`name` 讓 eval 有描述性命名，`expectations` 是 BDD 評分依據 |
| 2 | schema 備註術語 | `assertions` → `expectations` | 本地統一使用 `expectations` 欄位名，與 run_evals_bdd.py 的讀取邏輯一致 |
| 3 | Step 1 移除 Baseline run | 移除 without_skill / old_skill subagent 說明與 prompt 範例 | 本地不跑 baseline；保留說明會誤導 AI 多開不必要的 subagent |
| 4 | Step 2 加 BDD runner 指令 | `assertions` → `expectations`；補 `python evals/run_evals_bdd.py` 執行區塊 | Step 2 需明確說明在 runs 進行中執行 BDD runner 取得量化通過率 |
| 5 | benchmark delta | 移除 with_skill vs baseline 的 delta 統計說明 | 無 baseline 就無 delta，保留會造成混淆 |
| 6 | 迭代迴圈 baseline | 移除「including baseline runs」 | 迭代迴圈只重跑 with_skill，措辭需與主流程一致 |
| 7 | Claude.ai baseline | 移除「Skip the baseline runs」指令 | 主流程已無 baseline，Claude.ai 專屬說明不需再提 |
| 8 | Claude.ai benchmarking | 改為「requires subagents to run run_evals_bdd.py」 | 跳過 benchmarking 的原因是「需要 subagent 跑 BDD runner」，而非「baseline 無意義」 |
| 9 | Cowork baseline | 移除「run baselines」 | Cowork 說明與主流程保持一致，不提 baseline |

### Patch 失效時的處理方式

若 `update-skill-creator.py` 執行時 crash 並顯示 `Patch [name] 失敗`：
1. 查此表找到對應 patch 的目的
2. 確認官方 SKILL.md 是否更動了該段落
3. 更新 `update-skill-creator.py` 裡的 `old` 字串以對齊新版官方內容
4. 重新執行，確認 `validate_structure.py skill-creator-patches` 通過

---

## Eval 測試範圍設計原則

**只測本地擴充行為，官方行為不測。**

skill-creator 的流程分為兩類：

| 類別 | 涵蓋階段 | 是否納入 eval |
|------|---------|:---:|
| 官方行為 | 階段一（理解意圖）、二（訪談研究）、六（迭代改善）、七（描述最佳化） | 不測 |
| 本地擴充行為 | 階段三（SKILL.md 結構）、四（Eval 基礎設施自動產出）、五（BDD runner 機制） | 測試 |

**官方行為不測的原因：**
- 由 Anthropic 維護，官方更新時自動同步，不屬於本地責任範圍
- 測試官方行為等於在測 Claude 本身，而不是測本地擴充

**本地擴充行為必測的原因：**
- 本地對 SKILL.md 有額外擴充定義（`local_extensions.md`）
- `run_evals_bdd.py` 本身是本地產物，需確認被正確產出
- 每次 `update-skill-creator.py` 更新官方內容後，跑一次 eval 可確認本地擴充沒有被覆蓋破壞

**這 3 個 eval 的定位是回歸保護，不是全功能驗證。**

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
