# 執行逐步說明：eval-6-apply-resume-midway

## 任務：繼續實作 notification-fix

---

## 步驟 1：讀取 Apply Skill 規則

讀取 `C:\Users\theon.lin\.claude\skills\apply\SKILL.md`，理解 apply skill 的執行流程：

- `[x][cr]`：實作與 code review 皆完成，完全跳過
- `[x]`：實作完成但 code review 未執行，直接補跑 code review，subagent 回傳後立即用 Edit tool 更新為 `[x][cr]`
- `[ ]`：從此任務開始實作

---

## 步驟 2：讀取三份文檔

讀取以下三份文檔載入 context：

- `eval-6-apply-resume-midway/docs/propose/notification-fix/01-flow.md`：了解業務邏輯（訂單狀態更新 → 觸發通知事件 → 發送 email → 重試機制）
- `eval-6-apply-resume-midway/docs/propose/notification-fix/02-gherkin.md`：驗收條件（訂單通知信發送、失敗重試、錯誤 log）
- `eval-6-apply-resume-midway/docs/propose/notification-fix/03-tasks.md`：任務清單狀態

---

## 步驟 3：識別各任務狀態

從 `03-tasks.md` 讀取到：

| 任務 | 狀態 | 說明 |
|------|------|------|
| T1 | `[x][cr]` | 實作 + code review 全部完成 |
| T2 | `[x]` | 實作完成，code review **未執行** |
| T3 | `[ ]` | 尚未開始 |

依照「中途繼續」規則，告知使用者：

> T1 已完成（含 code review），T2 實作完成但 code review 未執行，從補跑 T2 code review 開始，接著實作 T3。

---

## 步驟 4：T1 跳過

T1 為 `[x][cr]`，完全跳過。

---

## 步驟 5：T2 補跑 Code Review

T2 任務：實作 `NotificationService.sendOrderStatusEmail()`，處理各狀態的 email 模板（影響：`src/services/NotificationService.ts`）

**動作**：模擬開啟 subagent，使用 `code-reviewer` skill 審查。

- 規格文檔路徑：`docs/propose/notification-fix/`（含三份文檔）
- Code review 結果：實作符合規格，`sendOrderStatusEmail()` 正確依訂單狀態選擇對應 email 模板，無問題。

**動作**：使用 Edit tool 將 T2 的 `[x]` 更新為 `[x][cr]`。

```
- [x][cr] T2: 實作 NotificationService.sendOrderStatusEmail()...
```

**T2 完成（含 code review）。**

---

## 步驟 6：T3 實作

T3 任務：加入通知失敗時的重試機制與錯誤 log（影響：`src/services/NotificationService.ts`）（依賴 T2）

**依賴確認**：T2 為 `[x][cr]`，依賴條件滿足，可執行 T3。

**實作內容**（依 `01-flow.md` 與 `02-gherkin.md`）：

- 發送失敗時進入重試機制（最多 3 次，間隔 5 分鐘）
- 重試 3 次仍失敗 → 記錄錯誤 log，不再重試
- 成功 → 記錄成功 log

**動作**：使用 Edit tool 將 T3 的 `[ ]` 更新為 `[x]`。

**Commit message**：`fix: 加入通知信發送失敗重試機制與錯誤 log`

---

## 步驟 7：T3 Code Review

**動作**：模擬開啟 subagent，使用 `code-reviewer` skill 審查。

- 規格文檔路徑：`docs/propose/notification-fix/`（含三份文檔）
- Code review 結果：重試邏輯符合規格（最多 3 次、間隔 5 分鐘），錯誤 log 正確記錄，無問題。

**動作**：使用 Edit tool 將 T3 的 `[x]` 更新為 `[x][cr]`。

```
- [x][cr] T3: 加入通知失敗時的重試機制與錯誤 log...
```

**T3 完成（含 code review）。**

---

## 最終結果

所有任務皆完成：

```
- [x][cr] T1: 在 OrderService 訂單狀態更新後加入通知觸發點
- [x][cr] T2: 實作 NotificationService.sendOrderStatusEmail()
- [x][cr] T3: 加入通知失敗時的重試機制與錯誤 log
```

**所有 notification-fix 任務已全部完成（含 code review）。**

---

## 輸出檔案

- `outputs/03-tasks.md`：最終任務清單（所有任務皆為 `[x][cr]`）
- `outputs/transcript.md`：本執行說明文件
