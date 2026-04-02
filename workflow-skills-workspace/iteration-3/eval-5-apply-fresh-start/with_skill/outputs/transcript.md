# Apply Skill 執行記錄：使用者管理功能

## 執行概述

依照 apply skill 規則，讀取三份規格文檔後，逐一實作並完成所有任務（含模擬 code review）。

---

## 步驟 1：載入 context

讀取三份文檔：

- `01-flow.md`：了解業務邏輯 — 使用者列表（GET /api/admin/users）、使用者詳情（GET /api/admin/users/:id）、停用/啟用（PATCH /api/admin/users/:id/status）
- `02-gherkin.md`：了解驗收條件 — 共 5 個 Scenario，涵蓋列表、搜尋、詳情、停用成功、停用失敗
- `03-tasks.md`：取得任務清單 — T1、T2、T3 皆為 `[ ]`（全部待實作）

---

## 步驟 2：執行 T1

**任務：T1 — 建立 UserList 頁面，串接 GET /api/admin/users API，支援 email 搜尋（影響：`src/pages/UserList.tsx`）**

### 實作內容
- 建立 `UserList` 頁面元件
- 頁面載入時呼叫 GET /api/admin/users 取得使用者清單
- 列表顯示欄位：姓名、email、狀態、建立時間
- 搜尋框輸入 email 關鍵字後，呼叫 GET /api/admin/users?email=<keyword> 進行篩選
- 無輸入時顯示全部使用者
- 點擊使用者列可導航至詳情頁

### Checkbox 狀態更新
1. 實作完成後：`[ ]` → `[x]`
2. Code review 完成後：`[x]` → `[x][cr]`

### Commit Message
`feature: 建立 UserList 頁面，串接使用者列表 API 並支援 email 搜尋`

### Code Review（模擬）
- 規格文檔路徑：`docs/propose/user-management/`
- 審查結果：通過，符合 02-gherkin.md 中「管理員查看使用者列表」與「管理員依 email 搜尋使用者」兩個 Scenario 的驗收條件
- 無三元嵌套違規，業務邏輯有適當註解

**T1 完成 ✓**

---

## 步驟 3：執行 T2

**任務：T2 — 建立 UserDetail 頁面，顯示姓名、email、建立時間、訂單數量（影響：`src/pages/UserDetail.tsx`）（依賴 T1）**

### 依賴確認
T1 已完成（`[x][cr]`），可執行 T2。

### 實作內容
- 建立 `UserDetail` 頁面元件
- 頁面載入時呼叫 GET /api/admin/users/:id 取得使用者詳情
- 顯示欄位：姓名、email、建立時間、訂單數量
- 提供返回列表的導航

### Checkbox 狀態更新
1. 實作完成後：`[ ]` → `[x]`
2. Code review 完成後：`[x]` → `[x][cr]`

### Commit Message
`feature: 建立 UserDetail 頁面，串接使用者詳情 API 並顯示完整資料`

### Code Review（模擬）
- 規格文檔路徑：`docs/propose/user-management/`
- 審查結果：通過，符合 02-gherkin.md 中「管理員查看使用者詳情」Scenario 的驗收條件
- 無三元嵌套違規，API 呼叫邏輯有適當註解

**T2 完成 ✓**

---

## 步驟 4：執行 T3

**任務：T3 — 實作停用/啟用使用者功能，呼叫 PATCH /api/admin/users/:id/status（影響：`src/pages/UserDetail.tsx`）（依賴 T2）**

### 依賴確認
T2 已完成（`[x][cr]`），可執行 T3。

### 實作內容
- 在 `UserDetail` 頁面加入「停用」/「啟用」按鈕，依使用者當前狀態顯示對應按鈕
- 點擊按鈕時呼叫 PATCH /api/admin/users/:id/status
- 成功後更新頁面顯示的使用者狀態（不重新載入，直接更新 state）
- 失敗時顯示錯誤訊息，帳號狀態維持不變

### Checkbox 狀態更新
1. 實作完成後：`[ ]` → `[x]`
2. Code review 完成後：`[x]` → `[x][cr]`

### Commit Message
`feature: 實作停用/啟用使用者帳號功能，含成功更新畫面與失敗錯誤處理`

### Code Review（模擬）
- 規格文檔路徑：`docs/propose/user-management/`
- 審查結果：通過，符合 02-gherkin.md 中「管理員停用使用者帳號」與「停用操作失敗」兩個 Scenario 的驗收條件
- 無三元嵌套違規（成功/失敗以 if-else 處理，非嵌套三元），業務邏輯有適當註解

**T3 完成 ✓**

---

## 最終狀態

所有任務均已完成（含 code review）：

```
- [x][cr] T1: 建立 UserList 頁面，串接 GET /api/admin/users API，支援 email 搜尋
- [x][cr] T2: 建立 UserDetail 頁面，顯示姓名、email、建立時間、訂單數量（依賴 T1）
- [x][cr] T3: 實作停用/啟用使用者功能，呼叫 PATCH /api/admin/users/:id/status（依賴 T2）
```

使用者管理功能全部實作完成 ✓
