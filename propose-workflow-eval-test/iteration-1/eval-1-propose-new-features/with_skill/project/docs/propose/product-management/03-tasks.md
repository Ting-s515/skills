# 任務清單：商品管理

## 參考文檔
- 結構化流程：`docs/propose/product-management/01-flow.md`
- 驗收條件：`docs/propose/product-management/02-gherkin.md`

## 任務

- [ ] T1: 建立商品列表 API 串接（取得分頁商品資料，支援名稱查詢參數與價格排序參數）（影響：`src/api/products.ts`）
- [ ] T2: 建立商品列表頁面元件（含分頁、名稱搜尋欄、價格排序選單）（影響：`src/pages/products/ProductListPage.tsx`）（依賴 T1）
- [ ] T3: 實作名稱篩選邏輯（debounce API 呼叫或前端即時過濾）（影響：`src/pages/products/ProductListPage.tsx`）（依賴 T2）
- [ ] T4: 實作價格排序邏輯（切換排序參數重新呼叫 API）（影響：`src/pages/products/ProductListPage.tsx`）（依賴 T2）
- [ ] T5: 建立新增/編輯商品 API 串接（POST 建立、PUT 更新）（影響：`src/api/products.ts`）
- [ ] T6: 建立商品表單元件（含名稱、價格、庫存數量、商品描述欄位及表單驗證）（影響：`src/pages/products/ProductFormModal.tsx`）（依賴 T5）
- [ ] T7: 實作新增商品流程（開啟表單、填寫、送出後列表新增該商品）（影響：`src/pages/products/ProductListPage.tsx`）（依賴 T6）
- [ ] T8: 實作編輯商品流程（預填現有資料、修改後送出、列表即時更新）（影響：`src/pages/products/ProductListPage.tsx`）（依賴 T6）
- [ ] T9: 建立下架商品 API 串接（PATCH 或 DELETE 更新商品狀態）（影響：`src/api/products.ts`）
- [ ] T10: 實作下架按鈕及確認對話框元件（影響：`src/pages/products/ProductListPage.tsx`、`src/components/ConfirmDialog.tsx`）（依賴 T9）
- [ ] T11: 串接成功/失敗後的狀態即時更新與 Toast 通知（影響：`src/pages/products/ProductListPage.tsx`）（依賴 T10）
