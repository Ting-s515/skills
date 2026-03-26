# 任務清單：商品管理

## 參考文檔
- 結構化流程：`docs/propose/product-management/01-flow.md`
- 驗收條件：`docs/propose/product-management/02-gherkin.md`

## 任務

- [ ] T1: 建立新增商品 API（含必填欄位、price/stock 格式驗證）（影響：`backend/controllers/productController.ts`、`backend/routes/products.ts`）
- [ ] T2: 建立商品列表 API（支援名稱模糊搜尋與價格排序查詢參數）（影響：`backend/controllers/productController.ts`）（依賴 T1）
- [ ] T3: 建立編輯商品 API（查詢商品是否存在、更新欄位，含相同驗證規則）（影響：`backend/controllers/productController.ts`）（依賴 T1）
- [ ] T4: 建立下架商品 API（更新 `status` 欄位，查詢商品是否存在）（影響：`backend/controllers/productController.ts`）（依賴 T1）
- [ ] T5: 串接管理員權限驗證 middleware 至商品管理路由（影響：`backend/routes/products.ts`）（依賴 T1，需使用者管理中已建立的 `backend/middleware/adminAuth.ts`）
- [ ] T6: 實作商品列表頁前端元件（含名稱搜尋框、價格排序選擇器、列表顯示）（影響：`frontend/pages/admin/products/index.tsx`）（依賴 T2）
- [ ] T7: 實作新增商品表單前端元件（含欄位驗證提示）（影響：`frontend/pages/admin/products/new.tsx`）（依賴 T1）
- [ ] T8: 實作編輯商品表單前端元件（帶入現有資料、含欄位驗證提示）（影響：`frontend/pages/admin/products/[id]/edit.tsx`）（依賴 T3）
- [ ] T9: 實作下架按鈕互動邏輯（含操作失敗錯誤提示）（影響：`frontend/pages/admin/products/index.tsx`）（依賴 T4、T6）
- [ ] T10: 處理空列表與篩選無結果的 UI 提示（影響：`frontend/pages/admin/products/index.tsx`）（依賴 T6）
