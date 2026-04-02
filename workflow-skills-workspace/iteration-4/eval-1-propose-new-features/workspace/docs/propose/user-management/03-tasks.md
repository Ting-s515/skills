# 任務清單：使用者管理

## 參考文檔
- 結構化流程：`docs/propose/user-management/01-flow.md`
- 驗收條件：`docs/propose/user-management/02-gherkin.md`

## 任務

- [ ] T1: 建立使用者列表 API（GET /admin/users，支援 email 模糊搜尋 query param）（影響：`backend/routes/admin/users.ts`、`backend/controllers/userController.ts`）
- [ ] T2: 建立使用者詳情 API（GET /admin/users/:id，回傳姓名、email、建立時間、訂單數量）（影響：`backend/controllers/userController.ts`）（依賴 T1）
- [ ] T3: 建立停用帳號 API（PATCH /admin/users/:id/disable）（影響：`backend/controllers/userController.ts`、`backend/middlewares/auth.ts`）（依賴 T1）
- [ ] T4: 建立啟用帳號 API（PATCH /admin/users/:id/enable）（影響：`backend/controllers/userController.ts`）（依賴 T1）
- [ ] T5: 實作使用者列表頁面元件，含 email 搜尋框與列表渲染（影響：`frontend/pages/admin/users/index.tsx`、`frontend/components/UserTable.tsx`）（依賴 T1）
- [ ] T6: 實作使用者詳情頁面元件（影響：`frontend/pages/admin/users/[id].tsx`）（依賴 T2、T5）
- [ ] T7: 實作停用/啟用按鈕與確認對話框元件，含 API 呼叫與狀態即時更新（影響：`frontend/components/UserStatusToggle.tsx`）（依賴 T3、T4、T5）
- [ ] T8: 實作搜尋框清空還原列表邏輯（影響：`frontend/pages/admin/users/index.tsx`）（依賴 T5）
- [ ] T9: 實作權限不足與 API 失敗的錯誤提示處理（影響：`frontend/components/UserStatusToggle.tsx`、`frontend/utils/errorHandler.ts`）（依賴 T7）
- [ ] [manual] T_test: 補上單元測試，使用 Skill tool 呼叫 `bdd-unit-test` skill 分析實作檔案產出測試（依賴所有前置任務）
