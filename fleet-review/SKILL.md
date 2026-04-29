---
name: fleet-review
description: 並行啟動 Claude + Codex 子代理從不同角度審查程式碼，透過跨模型交叉驗證消除誤報。接受一個參數：規格文檔路徑（例如：/fleet-review path/to/spec.md）。
disable-model-invocation: true
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

從 `$ARGUMENTS` 取得規格文檔路徑並讀取內容：
- 若 `$ARGUMENTS` 有值（例如 `/fleet-review path/to/spec.md`）→ 讀取該路徑的文檔，並將路徑記為 `$SPEC_PATH`
- 若 `$ARGUMENTS` 為空 → 告知使用者需提供規格文檔路徑，例如：`/fleet-review path/to/spec.md`，並停止

### 取得 diff

```bash
BASE=$(gh pr view --json baseRefName -q .baseRefName 2>/dev/null || \
       gh repo view --json defaultBranchRef -q .defaultBranchRef.name 2>/dev/null || \
       echo "main")
DIFF_FILE=$(mktemp /tmp/fleet-review-XXXXXX.patch)
git diff origin/$BASE > "$DIFF_FILE"
git diff origin/$BASE --stat | tail -5
```

若 diff 為空，告知使用者並停止。

---

## 步驟 1：並行啟動審查代理（2 個 sub-agent，單一回應同時啟動）

> 1 個 Claude Agent + 1 個 Codex Bash，共 2 個並行。
> **重要**：以下 prompt 中的 `$DIFF_FILE`、`$SPEC_PATH`、`$BASE` 必須替換為步驟 0 取得的實際值再帶入，不可原樣傳入。

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
```

使用 `timeout: 300000`（5 分鐘）。

### Codex Agent — 全面審查（Bash，run_in_background: true）

> ⚠️ **絕對不可在 bash 腳本內部加 `&`**：`run_in_background: true` 已讓 Bash 工具本身非同步執行；若再於腳本內加 `&`，codex 會變成孤立子程序，輸出無法被捕捉，結果直接丟失。
>
> ⚠️ **只傳檔案路徑，不展開內容**：將 `$(cat file)` 嵌入 `codex exec "..."` 字串中，當檔案較大時 shell 解析含特殊字元的多行字串容易出錯，導致 codex 阻塞等待 stdin（"Reading additional input from stdin..."）。改為只傳路徑，讓 codex 用自身的 Read 工具讀取。
>
> ⚠️ **必須加 `< /dev/null`**：顯式關閉 stdin，防止 codex 在非互動環境中等待輸入而卡住。

```bash
codex exec "你是程式碼審查代理。請用你的 Read 工具依序讀取下列兩個檔案，再審查並輸出發現。

規格文檔路徑（請讀取）：$SPEC_PATH
Diff 檔案路徑（請讀取）：$DIFF_FILE

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
若無發現，輸出：NO_FINDINGS" \
  -s read-only \
  -m "gpt-5.5" \
  -c 'model_reasoning_effort="high"' \
  2>/dev/null < /dev/null
```

使用 `timeout: 300000`（5 分鐘）。

---

## 步驟 2：彙整原始發現（0 個 sub-agent）

> 主代理自行收集所有 FINDING 區塊並整理摘要，不啟動任何 sub-agent。

收集兩個代理的 FINDING 區塊，整理成一份清單，向使用者展示摘要：

```
艦隊審查 — 原始發現
════════════════════════════════════════════════════════════
基礎分支：$BASE | 已變更檔案：N 個
Claude（全面審查）：N 個發現
Codex（全面審查）：N 個發現
原始發現總計：N 個
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
基礎分支：$BASE | 已變更檔案：N 個
代理：Claude（sonnet-4.6）+ Codex（gpt-5.5）
原始發現：N 個 → 雙代理確認：N 個，單代理發現：N 個

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
  原始發現：N 個
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
