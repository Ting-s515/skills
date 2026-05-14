# 本地擴充 — skill-creator/SKILL.md

此檔案存放於 `evals/`，在 `update-skill-creator` 更新時受保護不被覆蓋。
更新腳本執行後，會自動將「插入內容」區塊插入 SKILL.md 的指定錨點之後。

## 運作流程

1. 執行 `.\update-skill-creator.ps1`（或 `.sh`）→ 官方最新 SKILL.md 覆蓋進來
2. `evals/local_extensions.md` 因 `evals/` 保護機制而存活
3. 腳本偵測錨點 `references/schemas.md` for the full schema，將「插入內容」插入其後
4. 結果：官方更新 + 本地擴充同時保留

## 新增擴充方式

在「插入內容」分隔線之後加入 Markdown 內容，下次執行更新腳本時會自動套用。

---

## 插入內容

Also create `evals/run_evals.sh` alongside `evals.json` so external tools (e.g. Codex CLI) can invoke the evals via shell. Use `jq` as an explicit dependency for JSON parsing.

建立腳本前，先在腳本上方加入此前置需求說明：

````markdown
### Eval runner 前置需求

Eval runner 會使用 `jq` 讀取 `evals.json`。

執行 `evals/run_evals.sh` 前，請先安裝 `jq`：

- macOS: `brew install jq`
- Ubuntu/Debian: `sudo apt-get install jq`
- Fedora: `sudo dnf install jq`
- Windows/Git Bash: 交由 AI 統一設定，不要求使用者手動處理。

Windows/Git Bash 成功設定紀錄（通用化，不寫死使用者名稱）：

1. 確認 `winget` 已安裝 `jq`：
   ```powershell
   winget list jqlang.jq
   ```
2. 由 AI 在 PowerShell 找出 `jq.exe` 實際位置，不要假設 Windows 使用者名稱：
   ```powershell
   Get-ChildItem -Path "$env:LOCALAPPDATA\Microsoft\WinGet\Packages" -Recurse -Filter jq.exe -ErrorAction SilentlyContinue |
     Select-Object -First 1 -ExpandProperty FullName
   ```
3. 將找到的 Windows 目錄轉成 Git Bash 可解析路徑，例如：
   ```text
   C:\Users\<user>\AppData\Local\Microsoft\WinGet\Packages\<jq-package>\jq.exe
   → /c/Users/<user>/AppData/Local/Microsoft/WinGet/Packages/<jq-package>
   ```
4. 修正目前使用者的 `~/.bashrc`，加入轉換後的 Git Bash 目錄：
   ```bash
   export PATH="$PATH:<git-bash-jq-directory>"
   ```
5. 若 `.bashrc` 內有 Windows 路徑被斷行或重複追加，先整理成單行且去重。
6. 用新的 Git Bash shell 驗證：
   ```bash
   jq --version
   command -v jq
   ```

確認安裝是否成功：

```bash
jq --version
```

為什麼使用 `jq`：Bash 沒有內建 JSON parser；Codex/Claude CLI 支援非互動式執行 prompt，但沒有原生的 `evals.json` runner。避免用 `grep`/`sed` 解析 JSON；使用 `jq` 才能穩定處理跳脫字元、陣列與缺失欄位。

本地規則：Codex eval runner 必須固定使用 `--dangerously-bypass-approvals-and-sandbox`，不要改成 sandbox / approval 模式。這個 runner 預期只在一次性工作區或外部隔離環境中執行。
````

Fill in the actual skill name in the header comment:

```bash
#!/usr/bin/env bash
# Run <skill-name> behavior evals using codex or claude CLI
# Each eval runs twice: with_skill (SKILL.md injected) and without_skill (baseline)
# Usage: ./run_evals.sh [eval-id]   — omit id to run all
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
EVALS_JSON="$SCRIPT_DIR/evals.json"
SKILL_MD="$SCRIPT_DIR/../SKILL.md"
OUTPUT_DIR="$SCRIPT_DIR/../eval-results"

if ! command -v jq &>/dev/null; then
    echo "Error: jq is required"
    echo "Install jq first. On Windows/Git Bash, ask AI to configure ~/.bashrc with the WinGet jq.exe directory."
    exit 1
fi

if [ ! -f "$SKILL_MD" ]; then
    echo "Error: SKILL.md not found at $SKILL_MD"
    exit 1
fi

SKILL_INSTRUCTIONS="$(cat "$SKILL_MD")"

# Auto-detect AI tool: prefer codex if available, fall back to claude
if command -v codex &>/dev/null; then
    ai_run() { codex exec --dangerously-bypass-approvals-and-sandbox "$1"; }
    echo "[tool] codex"
elif command -v claude &>/dev/null; then
    ai_run() { claude -p "$1"; }
    echo "[tool] claude"
else
    echo "Error: neither codex nor claude CLI found"
    exit 1
fi

run_with_skill() {
    local full_prompt="$SKILL_INSTRUCTIONS

---

Apply the above skill instructions to this task:

$1"
    ai_run "$full_prompt"
}

run_without_skill() {
    ai_run "$1"
}

SKILL_NAME=$(jq -r '.skill_name' "$EVALS_JSON")
EVAL_COUNT=$(jq '.evals | length' "$EVALS_JSON")
TARGET_ID="${1:-}"

echo "=== $SKILL_NAME evals ($EVAL_COUNT total) ==="

for i in $(seq 0 $((EVAL_COUNT - 1))); do
    ID=$(jq -r ".evals[$i].id" "$EVALS_JSON")
    NAME=$(jq -r ".evals[$i].name // \"eval-$ID\"" "$EVALS_JSON")
    PROMPT=$(jq -r ".evals[$i].prompt" "$EVALS_JSON")

    if [ -n "$TARGET_ID" ] && [ "$ID" != "$TARGET_ID" ]; then
        continue
    fi

    EVAL_DIR="$OUTPUT_DIR/eval-$ID"
    mkdir -p "$EVAL_DIR/with_skill" "$EVAL_DIR/without_skill"

    echo ""
    echo "=== [$ID] $NAME ==="
    echo "Prompt: $PROMPT"

    echo ""
    echo "--- with_skill ---"
    run_with_skill "$PROMPT" | tee "$EVAL_DIR/with_skill/output.txt"
    echo "--- end with_skill ---"

    echo ""
    echo "--- without_skill (baseline) ---"
    run_without_skill "$PROMPT" | tee "$EVAL_DIR/without_skill/output.txt"
    echo "--- end without_skill ---"

    echo ""
    echo "[results saved] $EVAL_DIR"
done
```

Make the script executable: `chmod +x evals/run_evals.sh`.
