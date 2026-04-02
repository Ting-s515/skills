# 任務清單：商品管理

## 參考文檔
- 結構化流程：`docs/propose/product-management/01-flow.md`
- 驗收條件：`docs/propose/product-management/02-gherkin.md`

## 任務

- [ ] T1: 建立商品列表 API（GET /admin/products，支援 name 模糊搜尋與 price 排序 query param）（影響：`backend/routes/admin/products.ts`、`backend/controllers/productController.ts`）
- [ ] T2: 建立新增商品 API（POST /admin/products，含欄位驗證：名稱必填、價格 > 0、庫存 >= 0 整數）（影響：`backend/controllers/productController.ts`、`backend/validators/productValidator.ts`）（依賴 T1）
- [ ] T3: 建立編輯商品 API（PUT /admin/products/:id，含欄位驗證）（影響：`backend/controllers/productController.ts`）（依賴 T1）
- [ ] T4: 建立下架商品 API（PATCH /admin/products/:id/delist，含權限檢查）（影響：`backend/controllers/productController.ts`、`backend/middlewares/auth.ts`）（依賴 T1）
- [ ] T5: 實作商品列表頁面元件，含名稱篩選框與列表渲染（影響：`frontend/pages/admin/products/index.tsx`、`frontend/components/ProductTable.tsx`）（依賴 T1）
- [ ] T6: 實作依價格排序邏輯（升序/降序/還原，支援與篩選同時套用）（影響：`frontend/components/ProductTable.tsx`）（依賴 T5）
- [ ] T7: 實作新增商品表單元件，含欄位驗證與 API 呼叫（影響：`frontend/components/ProductFormModal.tsx`）（依賴 T2、T5）
- [ ] T8: 實作編輯商品表單元件，預填現有資料與 API 呼叫（影響：`frontend/components/ProductFormModal.tsx`）（依賴 T3、T5）
- [ ] T9: 實作下架按鈕與確認對話框元件，含 API 呼叫與狀態即時更新（影響：`frontend/components/ProductDelistButton.tsx`）（依賴 T4、T5）
- [ ] T10: 實作篩選框清空還原列表邏輯（影響：`frontend/pages/admin/products/index.tsx`）（依賴 T5）
- [ ] T11: 實作權限不足與 API 失敗的錯誤提示處理（影響：`frontend/components/ProductDelistButton.tsx`、`frontend/utils/errorHandler.ts`）（依賴 T9）
- [ ] [manual] T_test: 補上單元測試，使用 Skill tool 呼叫 `bdd-unit-test` skill 分析實作檔案產出測試（依賴所有前置任務）
