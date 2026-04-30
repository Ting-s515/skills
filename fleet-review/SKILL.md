---
name: fleet-review
description: 當使用者明確說出「fleet-review」關鍵字時，才觸發此技能。並行啟動 Claude + Codex 子代理從不同角度審查程式碼，透過跨模型交叉驗證消除誤報。接受一個參數：規格文檔路徑（例如：/fleet-review path/to/spec.md）。不得與 code-reviewer 技能混用，兩者功能不同：fleet-review 需明確呼叫，code-reviewer 則依業務邏輯文檔自動觸發。
---

# /fleet-review — 多代理程式碼審查

用法：`/fleet-review <規格文檔路徑>`

並行啟動 Claude + Codex 子代理從不同角度審查程式碼，再交叉比對找出高信心問題。

核心價值：不同代理以不同順序讀取程式碼，會建立不同的心智模型，因此發現不同的問題。
加入模型多樣性（Claude + Codex）可加乘這個效果，交叉驗證再過濾誤報。

---

## 步驟 0：前置檢查（0 個 sub-agent）

> 僅執行 Bash 指令，不啟動任何 sub-agent。

### 確認 Codex 可用

```bash
which codex 2>/dev/null || echo "NOT_FOUND"
```

若回傳 `NOT_FOUND`，告知安裝方式：`npm install -g @openai/codex`，並停止。

### 確認 Claude 可用

```bash
which claude 2>/dev/null || echo "NOT_FOUND"
```

若回傳 `NOT_FOUND`，告知使用者 `claude` CLI 未安裝，並停止。

### 取得規格文檔

從 `$ARGUMENTS` 解析參數：
- 必要：規格文檔路徑（第一個非旗標參數），記為 `$SPEC_PATH`
- 選用：`--diff path/to/file.patch`，直接使用指定的 patch 檔，跳過 git diff（供測試用）
- 若缺少規格文檔路徑 → 告知使用者，並停止

範例：
- 一般使用：`/fleet-review path/to/spec.md`
- 測試模式：`/fleet-review path/to/spec.md --diff path/to/fixture.patch`

### 取得 diff

```bash
# 解析 --diff 旗標
PRESET_DIFF=""
SPEC_PATH=""
ARGS=($ARGUMENTS)
i=0
while [ $i -lt ${#ARGS[@]} ]; do
  if [ "${ARGS[$i]}" = "--diff" ]; then
    i=$((i+1))
    PRESET_DIFF="${ARGS[$i]}"
  else
    SPEC_PATH="${ARGS[$i]}"
  fi
  i=$((i+1))
done

if [ -n "$PRESET_DIFF" ]; then
  # 測試模式：直接使用指定 patch，不執行 git diff
  DIFF_FILE="$PRESET_DIFF"
  BASE=$(gh repo view --json defaultBranchRef -q .defaultBranchRef.name 2>/dev/null || \
         git branch --show-current 2>/dev/null || \
         echo "main")
  DIFF_SOURCE="fixture patch: $PRESET_DIFF"
  wc -l "$DIFF_FILE"
else
  # 一般模式：從 git 取得 diff
  BASE=$(gh pr view --json baseRefName -q .baseRefName 2>/dev/null || \
         gh repo view --json defaultBranchRef -q .defaultBranchRef.name 2>/dev/null || \
         echo "main")
  DIFF_SOURCE="git diff origin/$BASE"
  DIFF_FILE=$(mktemp /tmp/fleet-review-XXXXXX.patch)
  git diff origin/$BASE > "$DIFF_FILE"
  git diff origin/$BASE --stat | tail -5
fi

# 將路徑轉換為 Windows 格式供 Codex 使用（cygpath 為 Git for Windows 內建）
# macOS/Linux 無 cygpath 時 fallback 回原始路徑，不影響行為
DIFF_FILE_WIN=$(cygpath -w "$DIFF_FILE" 2>/dev/null || echo "$DIFF_FILE")
SPEC_PATH_WIN=$(cygpath -w "$SPEC_PATH" 2>/dev/null || echo "$SPEC_PATH")
```

若 diff 為空，告知使用者並停止。

---

## 步驟 1：並行啟動審查代理（2 個 sub-agent，單一回應同時啟動）

> 1 個 Claude Agent + 1 個 Codex Bash，共 2 個並行。
> **重要**：以下 prompt 中的變數必須替換為步驟 0 取得的實際值再帶入，不可原樣傳入。
> - Claude Agent 使用 `$DIFF_FILE`、`$SPEC_PATH`（Unix 路徑，sub-agent 跑在 bash 環境）
> - Codex 使用 `$DIFF_FILE_WIN`、`$SPEC_PATH_WIN`（Windows 路徑，Codex 是 Windows process）

### Claude Agent — 全面審查（Agent 工具，run_in_background: true）

Prompt：

```
你是程式碼審查代理。請審查以下 diff 的變更，並閱讀相關原始檔以了解完整上下文。

Diff 檔案：$DIFF_FILE

規格文檔：
[貼上規格文檔內容]

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
```

使用 `timeout: 300000`（5 分鐘）。

### Codex Agent — 全面審查（Bash，run_in_background: true）

> ⚠️ **絕對不可在 bash 腳本內部加 `&`**：`run_in_background: true` 已讓 Bash 工具本身非同步執行；若再於腳本內加 `&`，codex 會變成孤立子程序，輸出無法被捕捉，結果直接丟失。
>
> ⚠️ **prompt 必須寫入暫存檔再以 stdin 傳入**：inline 字串（`codex exec "..."`）遇到中文、換行、引號時 shell 解析容易失敗。改用 heredoc 分段寫入暫存檔，再以 `< file` 傳入，可完全迴避這個問題。
>
> ⚠️ **輸出必須用 `-o` 寫入檔案**：background 執行時 stdout 不可靠，`-o` 保證輸出寫入指定路徑，最後再 `cat` 讀出。

```bash
CODEX_REQUESTED_MODEL="gpt-5.5"
CODEX_PROMPT_FILE=$(mktemp /tmp/codex-prompt-XXXXXX.txt)
CODEX_OUTPUT_FILE=$(mktemp /tmp/codex-output-XXXXXX.txt)
CODEX_TRACE_FILE=$(mktemp /tmp/codex-trace-XXXXXX.txt)

# 靜態 header（單引號 heredoc，完全不展開，避免特殊字元被 shell 解析）
cat > "$CODEX_PROMPT_FILE" << 'PROMPT_EOF'
你是程式碼審查代理。請用你的 Read 工具依序讀取下列兩個檔案，再審查並輸出發現。

PROMPT_EOF

# 動態路徑（雙引號 heredoc，展開 $SPEC_PATH_WIN 與 $DIFF_FILE_WIN）
cat >> "$CODEX_PROMPT_FILE" << PROMPT_EOF
規格文檔路徑（請讀取）：$SPEC_PATH_WIN
Diff 檔案路徑（請讀取）：$DIFF_FILE_WIN

PROMPT_EOF

# 靜態審查指示（單引號 heredoc）
cat >> "$CODEX_PROMPT_FILE" << 'PROMPT_EOF'
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

if [ $CODEX_EXIT -eq 0 ] && [ -s "$CODEX_OUTPUT_FILE" ]; then
  cat "$CODEX_OUTPUT_FILE"
  echo ""
  echo "CODEX_REQUESTED_MODEL: $CODEX_REQUESTED_MODEL"
else
  echo "CODEX_FAILED: exit_code=$CODEX_EXIT"
  echo "CODEX_REQUESTED_MODEL: $CODEX_REQUESTED_MODEL"
fi

# Debug metadata is intentionally captured but not emitted in normal reports.
CODEX_MODEL_SOURCE="requested_by_wrapper"
: "$CODEX_MODEL_SOURCE" "$CODEX_CLI_HEADER_MODEL" "$CODEX_CLI_VERSION"
rm -f "$CODEX_PROMPT_FILE" "$CODEX_OUTPUT_FILE" "$CODEX_TRACE_FILE"
```

使用 `timeout: 300000`（5 分鐘）。

---

## 步驟 2：彙整原始發現（0 個 sub-agent）

> 主代理自行收集所有 FINDING 區塊並整理摘要，不啟動任何 sub-agent。

從兩個代理的輸出中解析模型名稱：
- 從 Claude Agent 輸出的最後一行 `AGENT_MODEL: ...` 取得 `$CLAUDE_MODEL`（若缺失則顯示 `unknown`）
- 從 Codex wrapper 輸出的 `CODEX_REQUESTED_MODEL: ...` 取得 `$CODEX_REQUESTED_MODEL`（若缺失則顯示 `unknown`）
- 可選：內部可保留 `CODEX_MODEL_SOURCE`、`CODEX_CLI_HEADER_MODEL` 與 `CODEX_CLI_VERSION` 作為 debug metadata，不得宣稱為雲端實際模型 ID
- 一般報告僅輸出 `CODEX_REQUESTED_MODEL` 對應的精簡資訊；除非使用者要求 debug/raw metadata，否則不得輸出 `CODEX_MODEL_SOURCE`、`CODEX_CLI_HEADER_MODEL`、`CODEX_CLI_HEADER_MODEL_SOURCE`、`CODEX_CLI_VERSION`

收集兩個代理的 FINDING 區塊，整理成一份清單，向使用者展示摘要。

統計口徑必須分清楚：
- `代理原始回報`：Claude FINDING 數 + Codex FINDING 數，未去重，僅用於說明代理輸出量
- `去重後問題`：依 file + line + 問題語意交叉比對後的實際問題數，必須等於「雙代理確認 + 單代理發現」
- 最終報告不得把未去重的 `代理原始回報` 寫成 `原始發現：N 個 → 雙代理確認...`，避免左右數字口徑不一致
- 若使用 `--diff` 測試模式，`基礎分支` 仍顯示 `$BASE`，另以 `Diff 來源：$DIFF_SOURCE` 標示 fixture patch，不得把基礎分支顯示成 `(fixture)`

```
艦隊審查 — 原始發現
════════════════════════════════════════════════════════════
基礎分支：$BASE | Diff 來源：$DIFF_SOURCE | 已變更檔案：N 個
Claude（全面審查）：N 個發現
Codex（全面審查）：N 個發現
Codex requested model：$CODEX_REQUESTED_MODEL
代理原始回報：N 個（未去重）
去重後問題：N 個
════════════════════════════════════════════════════════════
```

若所有代理均回傳 NO_FINDINGS，跳過步驟 3，直接回報審查通過。

---

## 步驟 3：交叉比對，產出最終報告（0 個 sub-agent）

> 主代理根據兩個審查代理的發現進行交叉比對，直接輸出最終報告。

比對 Claude 與 Codex 對每條發現的重疊程度：

| 重疊狀態 | 信心等級 | 處理方式 |
| -------- | -------- | -------- |
| 兩者皆發現（相同 file/line/問題） | ✅ 高信心 | 直接納入，標注「雙代理確認」 |
| 僅一個代理發現 | ⚠️ 中信心 | 納入，標注發現來源 |

使用繁體中文輸出最終報告：

```
艦隊審查 — 最終報告
════════════════════════════════════════════════════════════
基礎分支：$BASE | Diff 來源：$DIFF_SOURCE | 已變更檔案：N 個
代理：Claude（$CLAUDE_MODEL）+ Codex（requested: $CODEX_REQUESTED_MODEL）
去重後問題：N 個 → 雙代理確認：N 個，單代理發現：N 個

### 📐 規格符合度

#### ✅ 符合規格的項目
- [規格項目]：[簡單說明實作如何對應]

#### ❌ 不符合或缺漏的項目
- [規格項目]：[說明缺漏或偏差之處]

---

### 🔴 必須修正（P0 / P1）

#### [標題] — file:line
- **問題：** [說明]
- **影響：** [後果]
- **發現者：** ✅ 雙代理確認 / ⚠️ 僅 Claude / ⚠️ 僅 Codex

---

### 🟠 建議改善（P2）

[同上格式]

---

### 🟡 輕微問題（P3）

[同上格式]

---

統計：
  代理原始回報：N 個（未去重）
  去重後問題：N 個
  雙代理確認：N 個，單代理發現：N 個
════════════════════════════════════════════════════════════
```

---

## 步驟 4：清理

```bash
rm -f "$DIFF_FILE"
```

---

## 重要規則

- **絕不修改程式碼**，所有代理以唯讀模式執行
- **審查代理全部在單一回應中並行啟動**，不得序列化
- **若某個代理結果缺失（非 NO_FINDINGS）**，繼續處理其他代理的結果，最終報告標注「[代理名稱] 結果缺失，已跳過」
