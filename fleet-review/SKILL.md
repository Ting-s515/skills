---
name: fleet-review
description: |
  並行啟動 Claude + Codex 子代理從不同角度審查程式碼，
  透過跨模型交叉驗證消除誤報，找出單次審查遺漏的問題。
  當使用者說「fleet review」、「multi-agent review」、「用多個代理審查我的程式碼」、
  「fleet-review」、「深度審查」或「完整審查流程」時觸發。
---

# /fleet-review — 多代理程式碼審查

並行啟動多個 Claude + Codex 子代理從不同角度審查程式碼，再交叉比對找出高信心問題。

核心價值：不同代理以不同順序讀取程式碼，會建立不同的心智模型，因此發現不同的問題。
加入模型多樣性（Claude + Codex）可加乘這個效果，交叉驗證再過濾誤報。

---

## 步驟 0：前置檢查（0 個 sub-agent）

> 僅執行 Bash 指令，不啟動任何 sub-agent。

### 確認 Codex 可用

```bash
which codex 2>/dev/null || echo "NOT_FOUND"
```

若回傳 `NOT_FOUND`，告知安裝方式：`npm install -g @openai/codex`，
並詢問是否改以 3 個 Claude 子代理執行（見文末備用方案）。

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

## 步驟 1：並行啟動審查代理（3 個 sub-agent，單一回應同時啟動）

> 2 個 Claude Agent + 1 個 Codex Bash，共 3 個並行。

### Claude Agent A — 邏輯與安全（Agent 工具，run_in_background: true）

Prompt：

```
你是程式碼審查代理。請審查以下 diff 的變更，並閱讀相關原始檔以了解完整上下文。

Diff 檔案：$DIFF_FILE

關注方向（僅聚焦這些面向，不評論其他）：
- 邏輯正確性：差一錯誤、條件反轉、錯誤比較、破壞不變條件
- 安全性：注入攻擊、授權繞過、敏感資料洩露、缺少輸入驗證
- 型別安全：不安全斷言、型別縮窄缺口、序列化邊界
- API 合約：破壞性變更、回應結構改變、缺少版本控制

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

### Claude Agent B — 穩健性與品質（Agent 工具，run_in_background: true）

Prompt：

```
你是程式碼審查代理。請審查以下 diff 的變更，並閱讀相關原始檔以了解完整上下文。

Diff 檔案：$DIFF_FILE

關注方向（僅聚焦這些面向，不評論其他）：
- 邊界情況與錯誤處理：缺少錯誤處理、資源洩漏、未處理例外、邊界條件
- 效能：N+1 查詢、無界迴圈、記憶體分配、缺少快取
- 並發：競態條件、缺少鎖、async/await 陷阱
- 測試覆蓋：新程式碼路徑是否有測試、現有測試是否需要更新

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

### Codex 代理（Bash，run_in_background: true）

```bash
codex exec "你是程式碼審查代理。審查以下 diff 的所有變更，閱讀實際原始檔了解上下文。
找出邏輯錯誤、安全問題、邊界情況、效能問題與程式碼品質問題。
絕不修改任何程式碼（唯讀）。

Diff 檔案：$DIFF_FILE

每個發現輸出：
FINDING:
  severity: P0|P1|P2|P3
  file: <路徑>
  line: <行號>
  title: <一行摘要>
  detail: <2-3 句話說明問題及其影響>

嚴重程度：P0=生產崩潰/安全漏洞 P1=功能錯誤 P2=條件性問題 P3=輕微問題
若無發現，輸出：NO_FINDINGS" \
  -s read-only \
  -c 'model_reasoning_effort="xhigh"' \
  --enable web_search_cached \
  2>/dev/null
```

使用 `timeout: 900000`（15 分鐘）。

---

## 步驟 2：彙整原始發現（0 個 sub-agent）

> 主代理自行收集所有 FINDING 區塊並整理摘要，不啟動任何 sub-agent。

收集所有代理的 FINDING 區塊，整理成一份清單，向使用者展示摘要後進行驗證：

```
艦隊審查 — 原始發現
════════════════════════════════════════════════════════════
基礎分支：$BASE | 已變更檔案：N 個
Claude-A（邏輯/安全）：N 個發現
Claude-B（穩健性/品質）：N 個發現
Codex（全面）：N 個發現
原始發現總計：N 個
════════════════════════════════════════════════════════════
```

若所有代理均回傳 NO_FINDINGS，跳過步驟 3，直接回報審查通過。

---

## 步驟 3：獨立驗證（2 個 sub-agent，單一回應同時啟動）

> 1 個 Claude Agent + 1 個 Codex Bash，共 2 個並行。

驗證代理不知道哪個審查代理提出哪條發現——它們是「冷眼旁觀者」，
回去讀原始程式碼，獨立確認每條發現是否真的存在，過濾審查代理的誤判。

### Claude 驗證者（Agent 工具，run_in_background: true）

Prompt：

```
你是驗證代理。以下是程式碼審查者回報的發現清單。
你的任務是透過閱讀實際原始碼，獨立驗證每一條發現。

對每條發現：
1. 讀取被參照的檔案和行號
2. 追蹤程式碼邏輯，確認或反駁該主張
3. 給出裁決

待驗證的發現：
[貼上所有 FINDING 區塊]

每條發現輸出以下精確格式：
VERDICT:
  original_title: <來自發現的 title>
  status: CONFIRMED|REFUTED|LIKELY
  confidence: HIGH|MEDIUM|LOW
  reasoning: <1-2 句說明確認或反駁的理由>

裁決說明：
  CONFIRMED = 確認問題存在
  REFUTED   = 問題不存在，是誤報
  LIKELY    = 無法完全確認，但邏輯合理
```

### Codex 驗證者（Bash，run_in_background: true）

```bash
codex exec "你是驗證代理。以下發現由程式碼審查者回報。
閱讀實際原始檔案並驗證每一條。

對每條：讀取 file/line，追蹤邏輯，給出裁決。

待驗證的發現：
[貼上所有 FINDING 區塊]

每條發現輸出：
VERDICT:
  original_title: <來自發現的 title>
  status: CONFIRMED|REFUTED|LIKELY
  confidence: HIGH|MEDIUM|LOW
  reasoning: <1-2 句說明理由>" \
  -s read-only \
  -c 'model_reasoning_effort="xhigh"' \
  --enable web_search_cached \
  2>/dev/null
```

使用 `timeout: 900000`（15 分鐘）。

---

## 步驟 4：交叉比對裁決，產出最終報告（0 個 sub-agent）

> 主代理根據兩個驗證者的 VERDICT 裁決表進行比對，直接輸出最終報告。

比對兩個驗證者對每條發現的裁決：

| Claude 驗證者 | Codex 驗證者 | 結果                      |
| ------------- | ------------ | ------------------------- |
| CONFIRMED     | CONFIRMED    | ✅ 高信心，納入           |
| CONFIRMED     | LIKELY       | ✅ 中信心，納入           |
| LIKELY        | CONFIRMED    | ✅ 中信心，納入           |
| LIKELY        | LIKELY       | ⚠️ 低信心，納入並標注     |
| CONFIRMED     | REFUTED      | ❓ 有爭議，附雙方觀點納入 |
| REFUTED       | CONFIRMED    | ❓ 有爭議，附雙方觀點納入 |
| LIKELY        | REFUTED      | ❌ 排除（可能誤報）       |
| REFUTED       | LIKELY       | ❌ 排除（可能誤報）       |
| REFUTED       | REFUTED      | ❌ 排除（誤報）           |

使用繁體中文輸出最終報告：

```
艦隊審查 — 最終報告
════════════════════════════════════════════════════════════
基礎分支：$BASE | 已變更檔案：N 個
代理：Claude-A + Claude-B + Codex | 驗證：Claude 驗證者 + Codex 驗證者
原始發現：N 個 → 確認：N 個，有爭議：N 個，排除（誤報）：N 個

### 🔴 必須修正（P0 / P1）

#### [標題] — file:line
- **問題：** [說明]
- **影響：** [後果]
- **發現者：** [Claude-A / Claude-B / Codex]
- **驗證：** [兩者均確認 / Claude 確認 + Codex 可能]

---

### 🟠 建議改善（P2）

[同上格式]

---

### 🟡 低信心（兩者 LIKELY）

[同上格式，標注「兩個驗證者均為 LIKELY，供參考」]

---

### ❓ 有爭議

#### [標題] — file:line
- **Claude 驗證者：** CONFIRMED — [理由]
- **Codex 驗證者：** REFUTED — [理由]

---

統計：
  原始發現：N 個
  驗證後：N 個確認，N 個低信心，N 個有爭議，N 個排除
  誤報率：X%
════════════════════════════════════════════════════════════
```

---

## 步驟 5：清理

```bash
rm -f "$DIFF_FILE"
```

---

## 備用方案：Codex 不可用

以 3 個 Claude 子代理取代審查層：

- Agent A：邏輯與安全（同上）
- Agent B：穩健性與品質（同上）
- Agent C：全面審查（不限關注方向，找任何問題）

驗證層改為 2 個 Claude 驗證者——一個使用延伸思考，一個不使用——以獲得觀點多樣性。
裁決規則與原版相同。

---

## 重要規則

- **絕不修改程式碼**，所有代理以唯讀模式執行
- **審查代理全部在單一回應中並行啟動**，不得序列化
- **驗證代理在審查代理全部完成後，同一回應中並行啟動**
- **若某個代理逾時**，繼續處理其他代理的結果，最終報告標注「N 個代理完成」
