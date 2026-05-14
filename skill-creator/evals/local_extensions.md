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
- Windows: `winget install jqlang.jq`

確認安裝是否成功：

```bash
jq --version
```

為什麼使用 `jq`：Bash 沒有內建 JSON parser；Codex/Claude CLI 支援非互動式執行 prompt，但沒有原生的 `evals.json` runner。避免用 `grep`/`sed` 解析 JSON；使用 `jq` 才能穩定處理跳脫字元、陣列與缺失欄位。
````

Fill in the actual skill name in the header comment:

```bash
#!/usr/bin/env bash
# Run <skill-name> behavior evals using codex or claude CLI
# Usage: ./run_evals.sh [eval-id]   — omit id to run all
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
EVALS_JSON="$SCRIPT_DIR/evals.json"

if ! command -v jq &>/dev/null; then
    echo "Error: jq is required"
    echo "Install: brew install jq | sudo apt-get install jq | sudo dnf install jq | winget install jqlang.jq"
    exit 1
fi

# Auto-detect AI tool: prefer codex if available, fall back to claude
if command -v codex &>/dev/null; then
    run_prompt() { codex exec --dangerously-bypass-approvals-and-sandbox "$1"; }
    echo "[tool] codex"
elif command -v claude &>/dev/null; then
    run_prompt() { claude -p "$1"; }
    echo "[tool] claude"
else
    echo "Error: neither codex nor claude CLI found"
    exit 1
fi

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

    echo ""
    echo "--- [$ID] $NAME ---"
    echo "Prompt: $PROMPT"
    echo ""
    run_prompt "$PROMPT"
    echo ""
    echo "--- end [$ID] ---"
done
```

Make the script executable: `chmod +x evals/run_evals.sh`.
