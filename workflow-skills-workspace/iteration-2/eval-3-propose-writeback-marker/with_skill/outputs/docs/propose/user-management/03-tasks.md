# 任務清單：使用者管理

## 參考文檔

- 結構化流程：`docs/propose/user-management/01-flow.md`
- 驗收條件：`docs/propose/user-management/02-gherkin.md`

## 任務

- [ ] T1: 建立使用者列表 API，支援 email 模糊搜尋查詢（影響：`backend/controllers/user.controller.ts`、`backend/services/user.service.ts`）
- [ ] T2: 建立查詢單筆使用者詳情 API，回傳姓名、email、建立時間、訂單數量（影響：`backend/controllers/user.controller.ts`、`backend/services/user.service.ts`）（依賴 T1）
- [ ] T3: 建立停用/啟用使用者帳號 API，更新 `status` 欄位（影響：`backend/controllers/user.controller.ts`、`backend/services/user.service.ts`）
- [ ] T4: 前端實作使用者列表頁，含 email 搜尋輸入框與列表渲染（影響：`frontend/pages/users/index.tsx`、`frontend/components/UserList.tsx`）（依賴 T1）
- [ ] T5: 前端實作使用者詳情頁，顯示姓名、email、建立時間、訂單數量（影響：`frontend/pages/users/[id].tsx`）（依賴 T2）
- [ ] T6: 前端實作停用/啟用按鈕，操作後更新列表/詳情頁狀態（影響：`frontend/components/UserStatusToggle.tsx`）（依賴 T3、T4）
- [ ] T7: 前端加入路由守衛，未登入者導向登入頁（影響：`frontend/middleware/auth.ts`）
