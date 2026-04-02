# 執行摘要

## 03-tasks.md 最終內容（checkbox 狀態）

```
# 任務清單：使用者管理

## 參考文檔
- 結構化流程：`docs/propose/user-management/01-flow.md`
- 驗收條件：`docs/propose/user-management/02-gherkin.md`

## 任務

- [x] T1: 建立 UserList 頁面，串接 GET /api/admin/users API，支援 email 搜尋（影響：`src/pages/UserList.tsx`）
- [x] T2: 建立 UserDetail 頁面，顯示姓名、email、建立時間、訂單數量（影響：`src/pages/UserDetail.tsx`）（依賴 T1）
- [x] T3: 實作停用/啟用使用者功能，呼叫 PATCH /api/admin/users/:id/status（影響：`src/pages/UserDetail.tsx`）（依賴 T2）
```

## 建立的檔案

- `src/pages/UserList.tsx` — 使用者列表頁面，串接 GET /api/admin/users，支援 email 關鍵字搜尋篩選
- `src/pages/UserDetail.tsx` — 使用者詳情頁面，顯示姓名/email/建立時間/訂單數量，包含停用/啟用帳號功能（PATCH /api/admin/users/:id/status）
