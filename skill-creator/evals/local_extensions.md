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

Also create `evals/run_evals.sh` alongside `evals.json` so external tools (e.g. Codex CLI) can invoke the evals via shell. Fill in the actual skill name in the header comment:

```bash
#!/usr/bin/env bash
# Run <skill-name> behavior evals using claude CLI
# Usage: ./run_evals.sh [eval-id]   — omit id to run all
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
EVALS_JSON="$SCRIPT_DIR/evals.json"

if ! command -v jq &>/dev/null; then
    echo "Error: jq is required (brew install jq / apt install jq)"
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
    claude -p "$PROMPT"
    echo ""
    echo "--- end [$ID] ---"
done
```

Make the script executable: `chmod +x evals/run_evals.sh`.
