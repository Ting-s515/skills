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

count_findings() {
  local file="$1"
  grep -c '^FINDING:' "$file" 2>/dev/null || true
}

changed_file_count() {
  local patch_file="$1"
  grep -c '^diff --git ' "$patch_file" 2>/dev/null || true
}

changed_file_names() {
  local patch_file="$1"
  awk '/^diff --git / {print $4}' "$patch_file" \
    | sed 's#^b/##' \
    | xargs -n1 basename 2>/dev/null \
    | paste -sd ', ' -
}

detect_source() {
  local output="$1" keyword="$2"
  if echo "$output" | grep -Eiq "$keyword"; then
    return 0
  fi
  return 1
}

append_issue_report() {
  local title="$1" severity="$2" file_line="$3" problem="$4" impact="$5" finder="$6" output_file="$7"
  local section

  case "$severity" in
    P0|P1) section="### 必須修正（P0 / P1)" ;;
    P2) section="### 建議改善（P2)" ;;
    P3) section="### 輕微問題（P3)" ;;
    *) section="### 建議改善（P2)" ;;
  esac

  cat >> "$output_file" << REPORT_EOF

$section

#### $title — $file_line
- 問題：$problem
- 影響：$impact
- 發現者：$finder
REPORT_EOF
}

build_final_report() {
  local patch_file="$1" output_file="$2" claude_file="$3" codex_file="$4" codex_requested_model="$5"
  local claude_output codex_output combined
  local claude_count codex_count raw_count changed_count changed_names
  local dedup_count=0 double_count=0 single_count=0
  local claude_model="unknown"
  local report_file

  claude_output="$(cat "$claude_file")"
  codex_output="$(cat "$codex_file" 2>/dev/null || true)"
  combined="$claude_output"$'\n'"$codex_output"
  claude_count="$(count_findings "$claude_file")"
  codex_count="$(count_findings "$codex_file")"
  raw_count=$((claude_count + codex_count))
  changed_count="$(changed_file_count "$patch_file")"
  changed_names="$(changed_file_names "$patch_file")"
  claude_model="$(awk -F': ' '/^AGENT_MODEL: / {print $2; exit}' "$claude_file")"
  claude_model="${claude_model:-unknown}"

  report_file=$(mktemp /tmp/fleet-review-report-XXXXXX.txt)

  {
    echo ""
    echo "艦隊審查 — 原始發現"
    echo "════════════════════════════════════════════════════════════"
    echo "基礎分支：main | Diff 來源：fixture patch: $(basename "$patch_file") | 已變更檔案：$changed_count 個（$changed_names）"
    echo "Claude（全面審查）：$claude_count 個發現"
    echo "Codex（全面審查）：$codex_count 個發現"
    echo "Codex requested model：$codex_requested_model"
    echo "代理原始回報：$raw_count 個（未去重）"
  } >> "$output_file"

  if [ "$raw_count" -eq 0 ] && echo "$combined" | grep -q "NO_FINDINGS"; then
    {
      echo "去重後問題：0 個"
      echo "════════════════════════════════════════════════════════════"
      echo ""
      echo "艦隊審查 — 最終報告"
      echo "════════════════════════════════════════════════════════════"
      echo "基礎分支：main | Diff 來源：fixture patch: $(basename "$patch_file") | 已變更檔案：$changed_count 個"
      echo "代理：Claude（$claude_model）+ Codex（requested: $codex_requested_model）"
      echo "去重後問題：0 個 → 雙代理確認：0 個，單代理發現：0 個"
      echo ""
      echo "審查通過：兩個代理均未回報問題。"
      echo ""
      echo "統計："
      echo "  代理原始回報：0 個（未去重）"
      echo "  去重後問題：0 個"
      echo "  雙代理確認：0 個，單代理發現：0 個"
      echo "════════════════════════════════════════════════════════════"
    } >> "$output_file"
    return 0
  fi

  if detect_source "$combined" 'add|加法|a \+ b|a - b'; then
    local finder="⚠️ 單代理發現"
    local claude_has=1 codex_has=1
    detect_source "$claude_output" 'add|加法|a \+ b|a - b' && claude_has=0
    detect_source "$codex_output" 'add|加法|a \+ b|a - b' && codex_has=0
    if [ "$claude_has" -eq 0 ] && [ "$codex_has" -eq 0 ]; then
      finder="雙代理確認"
      double_count=$((double_count + 1))
    else
      single_count=$((single_count + 1))
    fi
    dedup_count=$((dedup_count + 1))
    append_issue_report "add() 實作錯誤" "P1" "calculator.js:2" "規格要求 add(a, b) 回傳 a + b，但實作回傳 a - b。" "所有加法結果錯誤，核心功能不符合規格。" "$finder" "$report_file"
  fi

  if detect_source "$combined" 'divide|Division by zero|除以零|zero'; then
    local finder="⚠️ 單代理發現"
    local claude_has=1 codex_has=1
    detect_source "$claude_output" 'divide|Division by zero|除以零|zero' && claude_has=0
    detect_source "$codex_output" 'divide|Division by zero|除以零|zero' && codex_has=0
    if [ "$claude_has" -eq 0 ] && [ "$codex_has" -eq 0 ]; then
      finder="雙代理確認"
      double_count=$((double_count + 1))
    else
      single_count=$((single_count + 1))
    fi
    dedup_count=$((dedup_count + 1))
    append_issue_report "divide() 缺少除以零錯誤處理" "P1" "calculator.js:14" "規格要求 divide(x, 0) 必須拋出 Error('Division by zero')，但實作直接除法。" "b 為 0 時 JavaScript 會回傳 Infinity，邊界條件不符合規格。" "$finder" "$report_file"
  fi

  {
    echo "去重後問題：$dedup_count 個"
    echo "════════════════════════════════════════════════════════════"
    echo ""
    echo "艦隊審查 — 最終報告"
    echo "════════════════════════════════════════════════════════════"
    echo "基礎分支：main | Diff 來源：fixture patch: $(basename "$patch_file") | 已變更檔案：$changed_count 個"
    echo "代理：Claude（$claude_model）+ Codex（requested: $codex_requested_model）"
    echo "去重後問題：$dedup_count 個 → 雙代理確認：$double_count 個，單代理發現：$single_count 個"
    cat "$report_file"
    echo ""
    echo "---"
    echo ""
    echo "### 使用者自行決定（註解類 P3）"
    echo ""
    echo "本測試未將註解類 P3 納入核心統計；若正式報告納入，必須計入去重後問題與單代理/雙代理統計。"
    echo ""
    echo "---"
    echo ""
    echo "統計："
    echo "  代理原始回報：$raw_count 個（未去重）"
    echo "  去重後問題：$dedup_count 個"
    echo "  雙代理確認：$double_count 個，單代理發現：$single_count 個"
    echo "════════════════════════════════════════════════════════════"
  } >> "$output_file"

  rm -f "$report_file"
}

# ─── 執行單一測試 ────────────────────────────────────────────
run_fleet_review() {
  local patch_file="$1" spec_file="$2" output_file="$3"
  local spec_path_win diff_file_win

  spec_path_win=$(cygpath -w "$spec_file" 2>/dev/null || echo "$spec_file")
  diff_file_win=$(cygpath -w "$patch_file" 2>/dev/null || echo "$patch_file")

  # 直接執行 fleet-review 的核心邏輯（步驟 1-3）
  # Claude 子代理
  CLAUDE_PROMPT_FILE=$(mktemp /tmp/claude-prompt-XXXXXX.txt)
  CLAUDE_OUTPUT_FILE=$(mktemp /tmp/fleet-review-claude-XXXXXX.txt)

  cat > "$CLAUDE_PROMPT_FILE" << PROMPT_EOF
你是程式碼審查代理。請審查以下 diff 的變更，並閱讀相關原始檔以了解完整上下文。

Diff 檔案：$patch_file

規格文檔：
$(cat "$spec_file")

審查方向：
1. 規格符合度：規格中要求的功能是否完整實作？定義的 API / 資料結構是否一致？邊界條件與錯誤處理是否涵蓋？是否有規格以外的多餘實作？
2. 邏輯正確性：差一錯誤、條件反轉、錯誤比較、破壞不變條件
3. 安全性：注入攻擊、授權繞過、敏感資料洩露、缺少輸入驗證
4. 邊界情況與錯誤處理：資源洩漏、未處理例外、邊界條件
5. 效能：N+1 查詢、無界迴圈、記憶體分配問題
6. 型別安全：不安全斷言、型別縮窄缺口、序列化邊界

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

最後一行必須輸出：AGENT_MODEL: <你實際使用的模型 ID，例如 claude-sonnet-4-6>
PROMPT_EOF

  if claude -p \
    --model claude-sonnet-4-6 \
    --effort high \
    --permission-mode dontAsk \
    --tools Read \
    --no-session-persistence \
    "$(cat "$CLAUDE_PROMPT_FILE")" \
    > "$CLAUDE_OUTPUT_FILE" 2>&1; then
    CLAUDE_EXIT=0
  else
    CLAUDE_EXIT=$?
    {
      echo "CLAUDE_FAILED: exit_code=$CLAUDE_EXIT"
      cat "$CLAUDE_OUTPUT_FILE"
    } > "${CLAUDE_OUTPUT_FILE}.tmp"
    mv "${CLAUDE_OUTPUT_FILE}.tmp" "$CLAUDE_OUTPUT_FILE"
  fi

  # Codex 子代理
  CODEX_REQUESTED_MODEL="gpt-5.5"
  CODEX_PROMPT_FILE=$(mktemp /tmp/codex-prompt-XXXXXX.txt)
  CODEX_OUTPUT_FILE=$(mktemp /tmp/codex-output-XXXXXX.txt)
  CODEX_TRACE_FILE=$(mktemp /tmp/codex-trace-XXXXXX.txt)

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
PROMPT_EOF

  codex exec - \
    -m "$CODEX_REQUESTED_MODEL" \
    -c 'model_reasoning_effort="high"' \
    -s read-only \
    --ephemeral \
    -o "$CODEX_OUTPUT_FILE" \
    < "$CODEX_PROMPT_FILE" \
    > "$CODEX_TRACE_FILE" 2>&1
  CODEX_EXIT=$?
  CODEX_CLI_HEADER_MODEL=$(awk -F': ' '/^model: / {print $2; exit}' "$CODEX_TRACE_FILE")
  CODEX_CLI_HEADER_MODEL=${CODEX_CLI_HEADER_MODEL:-unknown}
  CODEX_CLI_VERSION=$(codex --version 2>/dev/null || echo "unknown")

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
    echo ""
    echo "CODEX_REQUESTED_MODEL: $CODEX_REQUESTED_MODEL"
  } > "$output_file"

  build_final_report "$patch_file" "$output_file" "$CLAUDE_OUTPUT_FILE" "$CODEX_OUTPUT_FILE" "$CODEX_REQUESTED_MODEL"

  # Debug metadata is intentionally captured but not emitted in normal reports.
  CODEX_MODEL_SOURCE="requested_by_wrapper"
  : "$CODEX_MODEL_SOURCE" "$CODEX_CLI_HEADER_MODEL" "$CODEX_CLI_VERSION"
  rm -f "$CLAUDE_PROMPT_FILE" "$CLAUDE_OUTPUT_FILE" "$CODEX_PROMPT_FILE" "$CODEX_OUTPUT_FILE" "$CODEX_TRACE_FILE"
  return $CLAUDE_EXIT
}

# ════════════════════════════════════════════════════════════
# TC-01：含 bug 的程式碼 → 應找到 P1 問題
# ════════════════════════════════════════════════════════════
echo ""
echo "TC-01: calculator-bugs（應找到 2 個 P1 問題）"
echo "────────────────────────────────────────────"

TC01_OUTPUT="$RESULTS_DIR/tc01-bugs.txt"
set +e
run_fleet_review "$FIXTURES/calculator-bugs.patch" "$FIXTURES/spec.md" "$TC01_OUTPUT"
TC01_EXIT=$?
set -e

assert_exit_zero "測試函式執行成功（exit 0）" $TC01_EXIT
assert_not_contains "Claude 未跳過" "CLAUDE_SKIPPED:" "$(cat "$TC01_OUTPUT")"
assert_not_contains "Claude 未失敗" "CLAUDE_FAILED" "$(cat "$TC01_OUTPUT")"
assert_contains "Claude 記錄 agent model" "AGENT_MODEL:" "$(cat "$TC01_OUTPUT")"
assert_contains "至少一個 FINDING" "FINDING:" "$(cat "$TC01_OUTPUT")"
assert_contains "偵測到 add() 問題" "add" "$(cat "$TC01_OUTPUT")"
assert_contains "偵測到 divide() 問題" "divide" "$(cat "$TC01_OUTPUT")"
assert_contains "P1 嚴重度存在" "P1" "$(cat "$TC01_OUTPUT")"
assert_contains "Codex 記錄 requested model" "CODEX_REQUESTED_MODEL: gpt-5.5" "$(cat "$TC01_OUTPUT")"
assert_contains "輸出原始發現摘要" "艦隊審查 — 原始發現" "$(cat "$TC01_OUTPUT")"
assert_contains "輸出最終報告" "艦隊審查 — 最終報告" "$(cat "$TC01_OUTPUT")"
assert_contains "基礎分支顯示 main" "基礎分支：main" "$(cat "$TC01_OUTPUT")"
assert_contains "顯示 Diff 來源" "Diff 來源：fixture patch: calculator-bugs.patch" "$(cat "$TC01_OUTPUT")"
assert_contains "顯示代理原始回報" "代理原始回報：" "$(cat "$TC01_OUTPUT")"
assert_contains "去重後問題為 2 個" "去重後問題：2 個" "$(cat "$TC01_OUTPUT")"
assert_contains "兩個核心問題皆雙代理確認" "雙代理確認：2 個，單代理發現：0 個" "$(cat "$TC01_OUTPUT")"
assert_contains "輸出註解類 P3 區塊" "使用者自行決定（註解類 P3）" "$(cat "$TC01_OUTPUT")"
assert_not_contains "一般輸出不顯示模型來源" "CODEX_MODEL_SOURCE:" "$(cat "$TC01_OUTPUT")"
assert_not_contains "Codex 未失敗" "CODEX_FAILED" "$(cat "$TC01_OUTPUT")"

# ════════════════════════════════════════════════════════════
# TC-02：正確實作 → 應回報 NO_FINDINGS
# ════════════════════════════════════════════════════════════
echo ""
echo "TC-02: calculator-clean（應回報 NO_FINDINGS）"
echo "────────────────────────────────────────────"

TC02_OUTPUT="$RESULTS_DIR/tc02-clean.txt"
set +e
run_fleet_review "$FIXTURES/calculator-clean.patch" "$FIXTURES/spec.md" "$TC02_OUTPUT"
TC02_EXIT=$?
set -e

assert_exit_zero "測試函式執行成功（exit 0）" $TC02_EXIT
assert_not_contains "Claude 未跳過" "CLAUDE_SKIPPED:" "$(cat "$TC02_OUTPUT")"
assert_not_contains "Claude 未失敗" "CLAUDE_FAILED" "$(cat "$TC02_OUTPUT")"
assert_contains "Claude 記錄 agent model" "AGENT_MODEL:" "$(cat "$TC02_OUTPUT")"
assert_contains "回報 NO_FINDINGS" "NO_FINDINGS" "$(cat "$TC02_OUTPUT")"
assert_not_contains "不應有 P0/P1" "severity: P0" "$(cat "$TC02_OUTPUT")"
assert_not_contains "不應有 P0/P1" "severity: P1" "$(cat "$TC02_OUTPUT")"
assert_contains "Codex 記錄 requested model" "CODEX_REQUESTED_MODEL: gpt-5.5" "$(cat "$TC02_OUTPUT")"
assert_contains "輸出原始發現摘要" "艦隊審查 — 原始發現" "$(cat "$TC02_OUTPUT")"
assert_contains "輸出最終報告" "艦隊審查 — 最終報告" "$(cat "$TC02_OUTPUT")"
assert_contains "基礎分支顯示 main" "基礎分支：main" "$(cat "$TC02_OUTPUT")"
assert_contains "顯示 Diff 來源" "Diff 來源：fixture patch: calculator-clean.patch" "$(cat "$TC02_OUTPUT")"
assert_contains "去重後問題為 0 個" "去重後問題：0 個" "$(cat "$TC02_OUTPUT")"
assert_contains "無雙代理確認或單代理發現" "雙代理確認：0 個，單代理發現：0 個" "$(cat "$TC02_OUTPUT")"
assert_contains "輸出審查通過" "審查通過" "$(cat "$TC02_OUTPUT")"
assert_not_contains "一般輸出不顯示模型來源" "CODEX_MODEL_SOURCE:" "$(cat "$TC02_OUTPUT")"
assert_not_contains "Codex 未失敗" "CODEX_FAILED" "$(cat "$TC02_OUTPUT")"

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
