# BDD Eval 架構說明

## 檔案關係

```
evals/
├── evals.json          ← 定義「測什麼」
├── run_evals_bdd.py    ← 定義「怎麼跑」
└── fixtures/
    └── eval-<id>/
        ├── base/       ← 變更前的檔案
        ├── staged/     ← 變更後的檔案
        └── spec/       ← 規格文檔（選填）
```

## 各檔案職責

**`evals.json`** — 純資料，描述每個測試案例：
- 要發給 AI 的 prompt
- 評分標準（expectations）

**`run_evals_bdd.py`** — 執行引擎，負責：
1. 讀 `evals.json` 取得所有 eval cases
2. 讀 `fixtures/eval-<id>/` 計算 diff
3. 把 SKILL.md + diff + expectations 組成完整 prompt
4. 呼叫 claude CLI 執行
5. 解析 AI 輸出的 `E1: PASS/FAIL` 評分
6. 輸出 `X/Y expectations passed`

## 資料流

```
evals.json (prompt + expectations)
    +
fixtures/eval-<id>/ (base → staged diff)
    +
SKILL.md (技能指令)
    ↓
run_evals_bdd.py 組裝成單一 prompt
    ↓
claude -p
    ↓
AI 輸出結果 + ## Grading 自評分
    ↓
run_evals_bdd.py 解析 → X/Y passed
```

## 核心設計原則

**`evals.json` 是測試規格，`run_evals_bdd.py` 是測試執行器。**
兩者分離讓你可以只修改測試內容（evals.json）而不動執行邏輯，反之亦然。
