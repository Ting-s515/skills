# 任務清單：使用者管理

## 參考文檔
- 結構化流程：`docs/propose/user-management/01-flow.md`
- 驗收條件：`docs/propose/user-management/02-gherkin.md`

## 任務

- [ ] T1: 建立使用者列表 API（取得全部使用者，支援 email 篩選參數）（影響：`api/users/index.ts`）
- [ ] T2: 建立使用者列表頁面元件，含分頁與 email 搜尋輸入框（影響：`pages/admin/users/index.tsx`）（依賴 T1）
- [ ] T3: 建立使用者詳情 API（依 userId 取得姓名、email、建立時間、訂單數量）（影響：`api/users/[id].ts`）
- [ ] T4: 建立使用者詳情頁面元件（影響：`pages/admin/users/[id].tsx`）（依賴 T3）
- [ ] T5: 建立帳號停用/啟用 API（PATCH 更新帳號狀態）（影響：`api/users/[id]/status.ts`）
- [ ] T6: 在詳情頁實作停用/啟用按鈕與確認對話框，操作後重新取得帳號狀態（影響：`pages/admin/users/[id].tsx`）（依賴 T4、T5）
