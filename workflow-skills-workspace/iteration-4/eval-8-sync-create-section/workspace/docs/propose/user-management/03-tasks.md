# 任務清單：使用者管理

## 任務

- [x][cr] T1: 建立 UserList 頁面，串接 GET /api/admin/users API，支援 email 搜尋（影響：`src/pages/UserList.tsx`）
- [x][cr] T2: 建立 UserDetail 頁面，顯示姓名、email、建立時間、訂單數量（影響：`src/pages/UserDetail.tsx`）（依賴 T1）
- [x][cr] T3: 實作停用/啟用使用者功能，呼叫 PATCH /api/admin/users/:id/status（影響：`src/pages/UserDetail.tsx`）（依賴 T2）
- [ ] [manual] T_test: 補上單元測試，使用 Skill tool 呼叫 `bdd-unit-test` skill 分析實作檔案產出測試（依賴所有前置任務）
