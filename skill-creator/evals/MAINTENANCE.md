# skill-creator 本地擴充維護指南

## 核心設計哲學

`local_extensions.md` 的存在目的：讓外部工具（Codex CLI）能在不依賴 Claude Code 子代理機制的情況下，執行與官方 skill-creator 等價的 eval 比對測試。

**Why:** Claude Code 的官方 eval 流程依賴子代理並行執行，Codex CLI 沒有這個機制。`run_evals.sh` 作為 shell 橋接層，讓 Codex 也能獨立跑完整的 with_skill vs without_skill 比對。

**修改原則：** 任何對 `run_evals.sh` 的修改都必須維持此對等性，不能讓兩種執行環境的行為產生語意差距。

---

## 官方行為 vs 本地擴充對照表

| 面向 | 官方 SKILL.md | run_evals.sh（本地擴充）|
|------|--------------|----------------------|
| 執行方式 | Claude Code 子代理（並行） | Codex/claude CLI（循序） |
| with_skill | 子代理載入 skill path | 注入完整 SKILL.md 到 prompt |
| without_skill | 子代理不帶 skill | 只傳 raw prompt |
| 結果存放 | `iteration-N/eval-ID/with_skill/` | `eval-results/eval-ID/with_skill/` |

---

## 維護原則

1. **兩種模式必須同時跑**：每個 eval 都需要 with_skill 和 without_skill，才能比較技能是否有效果，這是 eval 的核心意義。

2. **with_skill 的實作方式**：讀取 `../SKILL.md` 全文，注入到 prompt 前綴，格式固定為：
   ```
   [SKILL.md 完整內容]
   ---
   Apply the above skill instructions to this task:
   [eval prompt]
   ```

3. **without_skill 的實作方式**：只傳 raw prompt，不加任何 skill 上下文。

4. **AI 工具偵測順序**：優先 codex，fallback claude。Codex 固定使用 `--dangerously-bypass-approvals-and-sandbox`，不可改為 sandbox 模式。

5. **結果存檔**：每個 eval 的輸出分別存到 `eval-results/eval-<ID>/with_skill/output.txt` 和 `without_skill/output.txt`，方便後續 diff 比對。

6. **`evals/` 目錄受保護**：`update-skill-creator` 更新時不會覆蓋 `evals/` 目錄，`local_extensions.md` 的內容會在更新後自動注入到官方 SKILL.md 的指定錨點之後。

---

## 相關檔案

- `evals/local_extensions.md` — 本地擴充定義（受保護，update-skill-creator 不覆蓋）
- `evals/MAINTENANCE.md` — 本文件，維護指南
- `SKILL.md` — 官方技能主檔（update-skill-creator 會覆蓋，但插入點保留本地擴充）
- `update-skill-creator.ps1` / `.sh` — 更新腳本，負責合併官方更新與本地擴充
