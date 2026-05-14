#!/usr/bin/env bash
# Run behavior evals using claude CLI
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
