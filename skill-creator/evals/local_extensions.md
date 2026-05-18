# 本地擴充 — skill-creator/SKILL.md

此檔案存放於 `evals/`，在 `update-skill-creator` 更新時受保護不被覆蓋。
更新腳本執行後，會自動將「插入內容」區塊插入 SKILL.md 的指定錨點之後。

## 運作流程

1. 先確認 Python 可用：`python --version`（Windows 若不可用，改用 `py --version`）
2. 執行 `python .\update-skill-creator.py`（Windows 可改用 `py .\update-skill-creator.py`；或執行 `.\update-skill-creator.ps1`）→ 官方最新 SKILL.md 覆蓋進來
3. `evals/local_extensions.md` 因 `evals/` 保護機制而存活
4. 腳本偵測錨點 `references/schemas.md` for the full schema，將「插入內容」插入其後
5. 結果：官方更新 + 本地擴充同時保留

## 新增擴充方式

在「插入內容」分隔線之後加入 Markdown 內容，下次執行更新腳本時會自動套用。

## 腳本類型說明（此區塊不會被插入 SKILL.md，僅供 AI 參考）

`skill-creator/scripts/` 下有多支 `.py` 腳本，類型各不相同，請勿混淆：

| 腳本 | 類型 | 說明 |
|---|---|---|
| `scripts/run_eval.py` | **Trigger Evaluation 工具** | 測試 skill description 是否讓 Claude 正確觸發，屬 skill-creator 內部基礎設施。**不適用 `eval-test/MAINTENANCE.md` eval runner 規範，不得套用或升級為 `run_evals_bdd.py` 格式。** |
| `scripts/run_loop.py` | skill-creator 內部工具 | 執行 improve 循環，非 eval runner |
| `scripts/quick_validate.py` | skill-creator 內部工具 | 快速驗證 skill 觸發率，非 eval runner |
| `scripts/aggregate_benchmark.py` | skill-creator 內部工具 | 彙整 benchmark 結果，非 eval runner |

> **注意**：`scripts/` 目錄在 `update-skill-creator.py` 執行時會被 GitHub 最新版覆蓋，  
> 任何直接寫在這些檔案頂部的標記都不會持久。類型說明須維護於此檔案（受 `evals/` 保護）。

---

## 插入內容

When creating eval tests, also create `evals/run_evals_bdd.py` alongside `evals.json`. This is the canonical eval runner — it computes the diff in Python, embeds diff + spec + expectations into a self-contained prompt, and the AI self-grades each expectation with `E1: PASS/FAIL — evidence`. Works cross-platform and cross-tool (Claude CLI and Codex CLI) without requiring filesystem access from the AI.

**Fixture structure** — create `evals/fixtures/eval-<id>/` for each eval:

```
evals/fixtures/eval-1/
├── base/          # file(s) before the change (empty dir = new file scenario)
├── staged/        # file(s) after the change (the code under review)
└── spec/          # optional spec/requirements docs fed to the AI
```

The `expectations` field in `evals.json` is what the BDD runner grades. Fill them in now or after the first few runs once you know what to look for.

See `skill-creator/SKILL.md` Test Cases section for the full `run_evals_bdd.py` template.
