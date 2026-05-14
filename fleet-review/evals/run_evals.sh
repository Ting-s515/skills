#!/usr/bin/env bash
# Run fleet-review behavior evals using codex or claude CLI
# Usage: ./run_evals.sh [eval-id]   — omit id to run all
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
EVALS_JSON="$SCRIPT_DIR/evals.json"

if ! command -v jq &>/dev/null; then
    echo "Error: jq is required (brew install jq / apt install jq)"
    exit 1
fi

# Auto-detect AI tool: prefer codex if available, fall back to claude
if command -v codex &>/dev/null; then
    run_prompt() { codex --dangerously-bypass-approvals-and-sandbox "$1"; }
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
