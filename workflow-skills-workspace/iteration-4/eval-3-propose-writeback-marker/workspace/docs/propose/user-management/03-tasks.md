# 任務清單：使用者管理

## 參考文檔
- 結構化流程：`docs/propose/user-management/01-flow.md`
- 驗收條件：`docs/propose/user-management/02-gherkin.md`

## 任務

- [ ] T1: 建立使用者列表 API（GET /admin/users，支援 email 查詢參數）（影響：`backend/routes/admin/users.ts`）
- [ ] T2: 建立使用者詳情 API（GET /admin/users/:id）（影響：`backend/routes/admin/users.ts`）（依賴 T1）
- [ ] T3: 建立停用/啟用帳號 API（PATCH /admin/users/:id/status）（影響：`backend/routes/admin/users.ts`）（依賴 T1）
- [ ] T4: 實作使用者列表頁面元件，含 email 搜尋欄與列表顯示（影響：`frontend/pages/admin/users/index.tsx`）（依賴 T1）
- [ ] T5: 實作使用者詳情頁面元件（影響：`frontend/pages/admin/users/[id].tsx`）（依賴 T2）
- [ ] T6: 實作停用/啟用確認對話框與狀態更新邏輯（影響：`frontend/components/admin/UserStatusToggle.tsx`）（依賴 T3、T4）
- [ ] [manual] T_test: 補上單元測試，使用 Skill tool 呼叫 `bdd-unit-test` skill 分析實作檔案產出測試（依賴所有前置任務）
