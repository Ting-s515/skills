# 任務清單：商品管理

## 參考文檔
- 結構化流程：`docs/propose/product-management/01-flow.md`
- 驗收條件：`docs/propose/product-management/02-gherkin.md`

## 任務

- [ ] T1: 建立商品列表 API（GET /admin/products，支援 name 查詢參數與 sort 排序參數）（影響：`backend/routes/admin/products.ts`）
- [ ] T2: 建立新增商品 API（POST /admin/products，欄位驗證：name 必填、price 正整數、stock 非負整數）（影響：`backend/routes/admin/products.ts`）（依賴 T1）
- [ ] T3: 建立編輯商品 API（PUT /admin/products/:id）（影響：`backend/routes/admin/products.ts`）（依賴 T1）
- [ ] T4: 建立下架商品 API（PATCH /admin/products/:id/status）（影響：`backend/routes/admin/products.ts`）（依賴 T1）
- [ ] T5: 實作商品列表頁面元件，含名稱搜尋欄與價格排序按鈕（影響：`frontend/pages/admin/products/index.tsx`）（依賴 T1）
- [ ] T6: 實作新增商品表單元件，含欄位驗證邏輯（影響：`frontend/components/admin/ProductForm.tsx`）（依賴 T2）
- [ ] T7: 實作編輯商品表單元件，預填現有資料（影響：`frontend/components/admin/ProductForm.tsx`）（依賴 T3、T6）
- [ ] T8: 實作下架確認對話框元件（影響：`frontend/components/admin/ProductStatusToggle.tsx`）（依賴 T4、T5）
- [ ] [manual] T_test: 補上單元測試，使用 Skill tool 呼叫 `bdd-unit-test` skill 分析實作檔案產出測試（依賴所有前置任務）
