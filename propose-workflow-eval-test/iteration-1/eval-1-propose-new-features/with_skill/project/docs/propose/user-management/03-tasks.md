# 任務清單：使用者管理

## 參考文檔
- 結構化流程：`docs/propose/user-management/01-flow.md`
- 驗收條件：`docs/propose/user-management/02-gherkin.md`

## 任務

- [ ] T1: 建立使用者列表 API 串接（取得分頁使用者資料，支援 email 查詢參數）（影響：`src/api/users.ts`）
- [ ] T2: 建立使用者列表頁面元件（含分頁、email 搜尋欄）（影響：`src/pages/users/UserListPage.tsx`）（依賴 T1）
- [ ] T3: 實作 email 搜尋篩選邏輯（前端即時過濾或 debounce API 呼叫）（影響：`src/pages/users/UserListPage.tsx`）（依賴 T2）
- [ ] T4: 建立使用者詳情 API 串接（取得單一使用者姓名、email、建立時間、訂單數量）（影響：`src/api/users.ts`）
- [ ] T5: 建立使用者詳情元件（Modal 或獨立頁面）（影響：`src/pages/users/UserDetailModal.tsx`）（依賴 T4）
- [ ] T6: 建立停用/啟用帳號 API 串接（影響：`src/api/users.ts`）
- [ ] T7: 實作停用/啟用按鈕及確認對話框元件（影響：`src/pages/users/UserListPage.tsx`、`src/components/ConfirmDialog.tsx`）（依賴 T6）
- [ ] T8: 實作停用自身帳號的防護邏輯（比對當前登入者 ID，禁止操作並提示）（影響：`src/pages/users/UserListPage.tsx`）（依賴 T7）
- [ ] T9: 串接成功/失敗後的狀態即時更新與 Toast 通知（影響：`src/pages/users/UserListPage.tsx`）（依賴 T7）
