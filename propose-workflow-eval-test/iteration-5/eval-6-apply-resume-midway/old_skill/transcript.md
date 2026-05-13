# Eval-6 Apply Resume Midway — Old Skill Transcript

## Eval 設定

- **Eval**: eval-6-apply-resume-midway
- **Skill 版本**: old_skill（舊版 apply）
- **Eval Prompt**: `繼續實作 docs/propose/notification-fix/`
- **執行日期**: 2026-05-13

---

## 初始狀態（03-tasks.md）

```
- [x][cr] T1: 在 OrderService 訂單狀態更新後加入通知觸發點
- [x]     T2: 實作 NotificationService.sendOrderStatusEmail()
- [ ]     T3: 加入通知失敗時的重試機制與錯誤 log（依賴 T2）
```

---

## 執行流程

### 步驟一：載入 context

讀取三份文檔：
- `01-flow.md`：了解業務邏輯（通知觸發 → 模板選擇 → 發送 → 重試機制）
- `02-gherkin.md`：驗收條件（3 個 Scenario）
- `03-tasks.md`：任務清單（T1=[x][cr]、T2=[x]、T3=[ ]）

### 步驟二：進度分析

| 任務 | 狀態 | 行動 |
|------|------|------|
| T1 | [x][cr] | 完全跳過 |
| T2 | [x] | code review 未執行，補跑後更新為 [x][cr] |
| T3 | [ ] | 待實作 |

告知使用者：「T1 已完成（含 code review），T2 實作完成但 code review 未執行，從補跑 T2 code review 開始」

---

### 步驟三：補跑 T2 Code Review

**審查對象**：`src/services/NotificationService.ts`（sendOrderStatusEmail + getEmailTemplate + sendEmail）

**規格對照**：
- 01-flow.md：「依訂單狀態選擇對應 email 模板，發送 email 給買家」
- Gherkin Scenario 1：「管理員將訂單狀態更新為「已出貨」→ 系統寄出通知信」

**Code Review 結果**：

```markdown
## 📋 Code Review 摘要

**審查範圍：** NotificationService.sendOrderStatusEmail() 與 email 模板選擇邏輯
**整體評估：** ✅ 符合規格可合併

### 📐 規格符合度

#### ✅ 符合規格的項目
- 依訂單狀態選擇 email 模板：templates map 覆蓋 shipped/delivered/cancelled
- 找不到模板時記錄 error log 並提前返回
- 不含 T3 的重試邏輯（範疇正確）

#### 無缺漏項目
```

**動作**：用 Edit tool 將 T2 從 `[x]` 更新為 `[x][cr]`

```
- [x][cr] T2: 實作 NotificationService.sendOrderStatusEmail()...
```

---

### 步驟四：實作 T3

**任務描述**：加入通知失敗時的重試機制與錯誤 log（依賴 T2）

**依賴確認**：T2 已為 [x][cr]，可以繼續

**實作內容**（`src/services/NotificationService.ts`）：

1. 新增常數：`MAX_RETRY_COUNT = 3`、`RETRY_INTERVAL_MS = 5 * 60 * 1000`
2. 重構 `sendOrderStatusEmail` 改呼叫 `sendWithRetry`
3. 新增 `sendWithRetry(to, subject, body, orderId, attempt = 1)` 私有方法：
   - try/catch 包覆 `sendEmail`
   - 成功：`console.log` 記錄成功
   - 失敗且 `attempt >= MAX_RETRY_COUNT`：`console.error` 記錄錯誤 log，return
   - 失敗且未達上限：`console.warn`，`await this.delay(RETRY_INTERVAL_MS)`，遞迴呼叫 `attempt + 1`
4. 新增 `delay(ms)` 私有方法

**規格驗證**：
- Scenario 2：「5 分鐘後重試，最多 3 次」→ `RETRY_INTERVAL_MS = 5 * 60 * 1000`，`MAX_RETRY_COUNT = 3`
- Scenario 3：「第 3 次仍失敗 → 記錄錯誤 log，不再重試」→ `attempt >= MAX_RETRY_COUNT` 分支

**動作**：將 T3 從 `[ ]` 更新為 `[x]`

```
- [x] T3: 加入通知失敗時的重試機制與錯誤 log...
```

**Commit Message**：`fix: 加入通知發送失敗時的重試機制與錯誤 log`

---

### 步驟五：T3 Code Review

**Code Review 結果**：

```markdown
## 📋 Code Review 摘要

**審查範圍：** NotificationService 重試機制與錯誤 log（sendWithRetry、delay）
**整體評估：** ✅ 符合規格可合併

### 📐 規格符合度

#### ✅ 符合規格的項目
- 最多重試 3 次：MAX_RETRY_COUNT = 3
- 間隔 5 分鐘：RETRY_INTERVAL_MS = 5 * 60 * 1000
- 仍失敗則記錄錯誤 log：console.error + return（不再重試）
- 成功時記錄 log：console.log

#### ✅ 程式碼品質
- 無三元嵌套
- 業務邏輯均有中文註解說明
- attempt 從 1 開始，MAX_RETRY_COUNT 為 3，邊界正確（attempt >= 3 時停止）
```

**動作**：用 Edit tool 將 T3 從 `[x]` 更新為 `[x][cr]`

```
- [x][cr] T3: 加入通知失敗時的重試機制與錯誤 log...
```

---

## 最終狀態（03-tasks.md）

```
- [x][cr] T1: 在 OrderService 訂單狀態更新後加入通知觸發點
- [x][cr] T2: 實作 NotificationService.sendOrderStatusEmail()
- [x][cr] T3: 加入通知失敗時的重試機制與錯誤 log（依賴 T2）
```

所有任務已完成。

---

## Eval 評分重點

| 檢查項目 | 結果 |
|----------|------|
| T1=[x][cr] 正確跳過 | PASS |
| T2=[x] 補跑 code review → [x][cr] | PASS |
| T3 實作完成 → [x] | PASS |
| T3 code review 執行 → [x][cr] | PASS |
| 未呼叫 bdd-unit-test（舊版無此步驟） | PASS |
| 不呼叫 bdd-unit-test | PASS |

---

## 產出檔案

- `outputs/03-tasks.md`：最終任務清單（全部 [x][cr]）
- `outputs/NotificationService.ts`：T2+T3 實作
- `outputs/02-gherkin.md`：驗收條件文檔
