# Apply 執行摘要：user-management

## 1. 03-tasks.md 最終內容

```
# 任務清單：使用者管理

## 參考文檔
- 結構化流程：`docs/propose/user-management/01-flow.md`
- 驗收條件：`docs/propose/user-management/02-gherkin.md`

## 任務

- [x][cr] T1: 建立 UserList 頁面，串接 GET /api/admin/users API，支援 email 搜尋（影響：`src/pages/UserList.tsx`）
- [x][cr] T2: 建立 UserDetail 頁面，顯示姓名、email、建立時間、訂單數量（影響：`src/pages/UserDetail.tsx`）（依賴 T1）
- [x][cr] T3: 實作停用/啟用使用者功能，呼叫 PATCH /api/admin/users/:id/status（影響：`src/pages/UserDetail.tsx`）（依賴 T2）
```

所有任務均為 `[x][cr]`（實作完成 + code review 完成）。

## 2. 建立的程式碼檔案

| 檔案路徑 | 說明 |
|---|---|
| `src/pages/UserList.tsx` | 使用者列表頁面，串接 GET /api/admin/users，支援 email 關鍵字篩選 |
| `src/pages/UserDetail.tsx` | 使用者詳情頁面，顯示姓名/email/建立時間/訂單數量，含停用/啟用按鈕及錯誤處理 |

## 3. 執行順序與依賴關係

| 順序 | 任務 | 依賴 | 是否符合 |
|---|---|---|---|
| 1 | T1: UserList 頁面 | 無 | 符合 |
| 2 | T2: UserDetail 頁面 | 依賴 T1（T1 已完成才執行） | 符合 |
| 3 | T3: 停用/啟用功能 | 依賴 T2（T2 已完成才執行） | 符合 |

執行順序完全符合依賴關係。每個任務實作完成後立即更新 `[ ]` 為 `[x]`，code review 完成後立即更新為 `[x][cr]`，持久記錄無遺漏。
