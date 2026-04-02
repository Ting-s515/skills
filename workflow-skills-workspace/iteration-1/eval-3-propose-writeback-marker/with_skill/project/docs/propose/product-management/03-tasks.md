# 任務清單：商品管理

## 參考文檔
- 結構化流程：`docs/propose/product-management/01-flow.md`
- 驗收條件：`docs/propose/product-management/02-gherkin.md`

## 任務

- [ ] T1: 建立商品列表 API（取得全部商品，支援名稱篩選與價格排序參數）（影響：`api/products/index.ts`）
- [ ] T2: 建立商品列表頁面元件，含名稱篩選輸入框與價格排序功能（影響：`pages/admin/products/index.tsx`）（依賴 T1）
- [ ] T3: 建立新增商品 API（POST，含欄位驗證）（影響：`api/products/index.ts`）
- [ ] T4: 建立新增商品表單元件，含前端驗證邏輯（影響：`pages/admin/products/new.tsx`）（依賴 T3）
- [ ] T5: 建立取得單一商品 API（依 productId）（影響：`api/products/[id].ts`）
- [ ] T6: 建立編輯商品 API（PUT，含欄位驗證）（影響：`api/products/[id].ts`）
- [ ] T7: 建立編輯商品表單元件，預填現有資料（影響：`pages/admin/products/[id]/edit.tsx`）（依賴 T5、T6）
- [ ] T8: 建立下架商品 API（PATCH 更新上架狀態）（影響：`api/products/[id]/status.ts`）
- [ ] T9: 在商品列表頁實作「下架」按鈕與確認對話框，操作後重新整理列表（影響：`pages/admin/products/index.tsx`）（依賴 T2、T8）
