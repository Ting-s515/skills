#!/usr/bin/env bash
# fleet-review 測試腳本
# 用法：bash fleet-review/test/run-test.sh
# 測試使用預製 patch fixture，不依賴 git 狀態

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FIXTURES="$SCRIPT_DIR/fixtures"
RESULTS_DIR="$SCRIPT_DIR/results"
PASS=0
FAIL=0
TOTAL=0

mkdir -p "$RESULTS_DIR"

# ─── 顏色輸出 ───────────────────────────────────────────────
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

pass() { echo -e "  ${GREEN}✓${NC} $1"; ((++PASS)); ((++TOTAL)); }
fail() { echo -e "  ${RED}✗${NC} $1"; ((++FAIL)); ((++TOTAL)); }
info() { echo -e "  ${YELLOW}→${NC} $1"; }

# ─── 斷言函式 ───────────────────────────────────────────────
assert_contains() {
  local desc="$1" pattern="$2" output="$3"
  if echo "$output" | grep -qF "$pattern"; then
    pass "$desc"
  else
    fail "$desc  (找不到: '$pattern')"
  fi
}

assert_not_contains() {
  local desc="$1" pattern="$2" output="$3"
  if ! echo "$output" | grep -qF "$pattern"; then
    pass "$desc"
  else
    fail "$desc  (不應出現: '$pattern')"
  fi
}

assert_exit_zero() {
  local desc="$1" exit_code="$2"
  if [ "$exit_code" -eq 0 ]; then
    pass "$desc"
  else
    fail "$desc  (exit code: $exit_code)"
  fi
}

# ─── 執行單一測試 ────────────────────────────────────────────
run_fleet_review() {
  local patch_file="$1" spec_file="$2" output_file="$3"
  local spec_path_win diff_file_win

  spec_path_win=$(cygpath -w "$spec_file" 2>/dev/null || echo "$spec_file")
  diff_file_win=$(cygpath -w "$patch_file" 2>/dev/null || echo "$patch_file")

  # 直接執行 fleet-review 的核心邏輯（步驟 1-3）
  # Claude 子代理
  CLAUDE_OUTPUT_FILE=$(mktemp /tmp/fleet-review-claude-XXXXXX.txt)
  claude --print "
你是程式碼審查代理。請審查以下 diff 的變更，並閱讀相關原始檔以了解完整上下文。

Diff 檔案：$patch_file

規格文檔：
$(cat "$spec_file")

審查方向：
1. 規格符合度：規格中要求的功能是否完整實作？
2. 邏輯正確性：差一錯誤、條件反轉、錯誤比較
3. 安全性：注入攻擊、授權繞過、敏感資料洩露
4. 邊界情況與錯誤處理：資源洩漏、未處理例外
5. 效能：N+1 查詢、無界迴圈
6. 型別安全：不安全斷言、型別縮窄缺口

絕不修改任何程式碼（唯讀）。

每個發現輸出以下精確格式：
FINDING:
  severity: P0|P1|P2|P3
  file: <路徑>
  line: <行號或範圍>
  title: <一行摘要>
  detail: <2-3 句話說明問題及其影響>

嚴重程度：P0=生產崩潰/安全漏洞 P1=功能錯誤 P2=條件性問題 P3=輕微問題
若無發現，輸出：NO_FINDINGS

最後一行必須輸出：AGENT_MODEL: <你實際使用的模型 ID>
" > "$CLAUDE_OUTPUT_FILE" 2>&1
  CLAUDE_EXIT=$?

  # Codex 子代理
  CODEX_PROMPT_FILE=$(mktemp /tmp/codex-prompt-XXXXXX.txt)
  CODEX_OUTPUT_FILE=$(mktemp /tmp/codex-output-XXXXXX.txt)

  cat > "$CODEX_PROMPT_FILE" << 'PROMPT_EOF'
你是程式碼審查代理。請用你的 Read 工具依序讀取下列兩個檔案，再審查並輸出發現。

PROMPT_EOF

  cat >> "$CODEX_PROMPT_FILE" << PROMPT_EOF
規格文檔路徑（請讀取）：$spec_path_win
Diff 檔案路徑（請讀取）：$diff_file_win

PROMPT_EOF

  cat >> "$CODEX_PROMPT_FILE" << 'PROMPT_EOF'
審查方向：
1. 規格符合度：規格中要求的功能是否完整實作？
2. 邏輯正確性：差一錯誤、條件反轉、錯誤比較
3. 安全性：注入攻擊、授權繞過、敏感資料洩露
4. 邊界情況與錯誤處理：資源洩漏、未處理例外
5. 效能：N+1 查詢、無界迴圈
6. 型別安全：不安全斷言、型別縮窄缺口

絕不修改任何程式碼（唯讀）。

每個發現輸出以下精確格式：
FINDING:
  severity: P0|P1|P2|P3
  file: <路徑>
  line: <行號或範圍>
  title: <一行摘要>
  detail: <2-3 句話說明問題及其影響>

嚴重程度：P0=生產崩潰/安全漏洞 P1=功能錯誤 P2=條件性問題 P3=輕微問題
若無發現，輸出：NO_FINDINGS

最後一行必須輸出：CODEX_MODEL: <你實際使用的模型 ID>
PROMPT_EOF

  codex exec - \
    -m "gpt-5.5" \
    -c 'model_reasoning_effort="high"' \
    -s read-only \
    --ephemeral \
    -o "$CODEX_OUTPUT_FILE" \
    < "$CODEX_PROMPT_FILE"
  CODEX_EXIT=$?

  # 合併輸出
  {
    echo "=== CLAUDE OUTPUT ==="
    cat "$CLAUDE_OUTPUT_FILE"
    echo ""
    echo "=== CODEX OUTPUT ==="
    if [ $CODEX_EXIT -eq 0 ] && [ -s "$CODEX_OUTPUT_FILE" ]; then
      cat "$CODEX_OUTPUT_FILE"
    else
      echo "CODEX_FAILED: exit_code=$CODEX_EXIT"
    fi
  } > "$output_file"

  rm -f "$CLAUDE_OUTPUT_FILE" "$CODEX_PROMPT_FILE" "$CODEX_OUTPUT_FILE"
  return $CLAUDE_EXIT
}

# ════════════════════════════════════════════════════════════
# TC-01：含 bug 的程式碼 → 應找到 P1 問題
# ════════════════════════════════════════════════════════════
echo ""
echo "TC-01: calculator-bugs（應找到 2 個 P1 問題）"
echo "────────────────────────────────────────────"

TC01_OUTPUT="$RESULTS_DIR/tc01-bugs.txt"
run_fleet_review "$FIXTURES/calculator-bugs.patch" "$FIXTURES/spec.md" "$TC01_OUTPUT"
TC01_EXIT=$?

assert_exit_zero "Claude 代理執行成功（exit 0）" $TC01_EXIT
assert_contains "至少一個 FINDING" "FINDING:" "$(cat "$TC01_OUTPUT")"
assert_contains "偵測到 add() 問題" "add" "$(cat "$TC01_OUTPUT")"
assert_contains "偵測到 divide() 問題" "divide" "$(cat "$TC01_OUTPUT")"
assert_contains "P1 嚴重度存在" "P1" "$(cat "$TC01_OUTPUT")"
assert_contains "Claude 回報模型名稱" "AGENT_MODEL:" "$(cat "$TC01_OUTPUT")"
assert_contains "Codex 回報模型名稱" "CODEX_MODEL:" "$(cat "$TC01_OUTPUT")"
assert_not_contains "Codex 未失敗" "CODEX_FAILED" "$(cat "$TC01_OUTPUT")"

# ════════════════════════════════════════════════════════════
# TC-02：正確實作 → 應回報 NO_FINDINGS
# ════════════════════════════════════════════════════════════
echo ""
echo "TC-02: calculator-clean（應回報 NO_FINDINGS）"
echo "────────────────────────────────────────────"

TC02_OUTPUT="$RESULTS_DIR/tc02-clean.txt"
run_fleet_review "$FIXTURES/calculator-clean.patch" "$FIXTURES/spec.md" "$TC02_OUTPUT"
TC02_EXIT=$?

assert_exit_zero "Claude 代理執行成功（exit 0）" $TC02_EXIT
assert_contains "回報 NO_FINDINGS" "NO_FINDINGS" "$(cat "$TC02_OUTPUT")"
assert_not_contains "不應有 P0/P1" "severity: P0" "$(cat "$TC02_OUTPUT")"
assert_not_contains "不應有 P0/P1" "severity: P1" "$(cat "$TC02_OUTPUT")"
assert_contains "Codex 回報模型名稱" "CODEX_MODEL:" "$(cat "$TC02_OUTPUT")"

# ════════════════════════════════════════════════════════════
# 結果
# ════════════════════════════════════════════════════════════
echo ""
echo "════════════════════════════════════════════"
echo "測試結果：$PASS/$TOTAL 通過，$FAIL 失敗"
echo "輸出目錄：$RESULTS_DIR"
echo "════════════════════════════════════════════"

[ $FAIL -eq 0 ] && echo -e "${GREEN}✅ ALL TESTS PASSED${NC}" || echo -e "${RED}❌ $FAIL TEST(S) FAILED${NC}"
[ $FAIL -eq 0 ] && exit 0 || exit 1
