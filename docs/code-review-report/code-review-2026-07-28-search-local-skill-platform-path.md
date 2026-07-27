# Code Review 紀錄 — 2026-07-28（第 2 輪）

## 📋 Code Review 摘要

**審查範圍：** `search-local-skill/SKILL.md`、`scripts/validate_skill_portability.py`、`scripts/test_validate_skill_portability.py`，並唯讀核對 `codex` branch 的 `search-local-skill/SKILL.md`
**整體評估：** ✅ 符合規格可合併

### Findings

- 無 findings。
- 前一輪「合成 fixture 未鎖定實際 branch 專屬內容」finding 已解除。

---

### 📐 規格符合度

#### ✅ 符合規格的項目

- **main branch 僅搜尋 Claude skills：** `search-local-skill/SKILL.md:3`、`:10`、`:18-20`、`:44-45` 均限定 `~/.claude/skills/`，且沒有改掃 `~/.codex/skills/` 或其他任意目錄。
- **codex branch 僅搜尋 Codex skills：** 唯讀檢查 `codex:search-local-skill/SKILL.md`，內容僅指向 `~/.codex/skills/`；平台分支與 main 版本一致。
- **環境明確直接使用、不明確才唯讀偵測：** `search-local-skill/SKILL.md:10-14` 明確先採用 agent context 的 OS/home；資訊不足時才唯讀偵測，無法解析時停止並要求提供路徑。
- **Windows/macOS 跨平台分支：** `search-local-skill/SKILL.md:16-22` 同時涵蓋 macOS/Linux、Windows PowerShell 與 Windows bash，且列舉操作維持唯讀。
- **validator 例外範圍：** `scripts/validate_skill_portability.py:46-53` 以實際相對檔案、finding 類型與完整 match 三個條件限定例外，沒有略過整個檔案或整類絕對路徑檢查。
- **Windows 路徑不會被例外遮蔽：** `scripts/test_validate_skill_portability.py:199-212` 在同一行同時放入允許的 Claude root 與 Windows drive-letter path，並精確要求只留下 Windows finding。
- **實際 main skill 契約已有回歸保護：** `scripts/test_validate_skill_portability.py:185-197` 直接讀取 repository 內的 `search-local-skill/SKILL.md`，斷言 Claude root 存在、Codex root 不存在、路徑策略文字及三個平台分支存在，已解除前一輪 finding。

#### ❌ 不符合或缺漏的項目

無。

---

### 🔴 必須修正（Critical）

無。

---

### 🟠 建議改善（Warning）

無。

---

### ⚪ 使用者自行決定（註解類問題）

無。

### Residual risks / Testing gaps

- main 的契約測試只驗證目前 checkout；`codex` branch 的 Codex-only 契約仍需由該 branch 自身的對應驗證持續保護。本輪已唯讀核對目前 `codex` 內容，未發現偏差。

### 驗證結果

- `python scripts/test_validate_skill_portability.py`：15 tests passed。
- `python scripts/validate_skill_portability.py`：28/28 skills passed。
- `python -m py_compile scripts/validate_skill_portability.py scripts/test_validate_skill_portability.py`：通過。
- `git diff --check`：未發現 whitespace error。
