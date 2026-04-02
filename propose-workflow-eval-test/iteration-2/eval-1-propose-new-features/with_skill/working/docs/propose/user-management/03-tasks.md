# 任務清單：使用者管理

## 參考文檔
- 結構化流程：`docs/propose/user-management/01-flow.md`
- 驗收條件：`docs/propose/user-management/02-gherkin.md`

## 任務

- [ ] T1: 建立使用者列表 API（支援 email 模糊搜尋查詢參數）（影響：`backend/controllers/userController.ts`、`backend/routes/users.ts`）
- [ ] T2: 建立查看使用者詳情 API（含訂單數量計算）（影響：`backend/controllers/userController.ts`）（依賴 T1）
- [ ] T3: 建立停用/啟用使用者帳號 API（更新 `status` 欄位）（影響：`backend/controllers/userController.ts`）（依賴 T1）
- [ ] T4: 建立管理員權限驗證 middleware（驗證 role、未登入導向登入頁、無權限返回 403）（影響：`backend/middleware/adminAuth.ts`）
- [ ] T5: 串接 T4 middleware 至使用者管理相關路由（影響：`backend/routes/users.ts`）（依賴 T4）
- [ ] T6: 實作使用者列表頁前端元件（含 email 搜尋框、列表顯示）（影響：`frontend/pages/admin/users/index.tsx`）（依賴 T1）
- [ ] T7: 實作使用者詳情頁前端元件（顯示姓名、email、建立時間、訂單數量）（影響：`frontend/pages/admin/users/[id].tsx`）（依賴 T2）
- [ ] T8: 實作停用/啟用按鈕互動邏輯（含操作失敗錯誤提示）（影響：`frontend/pages/admin/users/[id].tsx`）（依賴 T3、T7）
- [ ] T9: 處理空列表與搜尋無結果的 UI 提示（影響：`frontend/pages/admin/users/index.tsx`）（依賴 T6）
