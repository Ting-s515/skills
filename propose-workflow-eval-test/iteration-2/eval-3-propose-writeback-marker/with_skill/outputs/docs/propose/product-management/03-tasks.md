# 任務清單：商品管理

## 參考文檔

- 結構化流程：`docs/propose/product-management/01-flow.md`
- 驗收條件：`docs/propose/product-management/02-gherkin.md`

## 任務

- [ ] T1: 建立新增商品 API，包含必填驗證（name）及格式驗證（price、stock）（影響：`backend/controllers/product.controller.ts`、`backend/services/product.service.ts`）
- [ ] T2: 建立商品列表查詢 API，支援名稱模糊篩選及價格排序（影響：`backend/controllers/product.controller.ts`、`backend/services/product.service.ts`）
- [ ] T3: 建立查詢單筆商品詳情 API（影響：`backend/controllers/product.controller.ts`、`backend/services/product.service.ts`）（依賴 T2）
- [ ] T4: 建立編輯商品 API，執行相同輸入驗證後更新記錄（影響：`backend/controllers/product.controller.ts`、`backend/services/product.service.ts`）（依賴 T1）
- [ ] T5: 建立下架商品 API，更新 `status` 欄位（影響：`backend/controllers/product.controller.ts`、`backend/services/product.service.ts`）
- [ ] T6: 前端實作商品列表頁，含名稱篩選輸入框、價格排序控制項與列表渲染（影響：`frontend/pages/products/index.tsx`、`frontend/components/ProductList.tsx`）（依賴 T2）
- [ ] T7: 前端實作新增商品表單頁，含欄位驗證與錯誤提示（影響：`frontend/pages/products/new.tsx`、`frontend/components/ProductForm.tsx`）（依賴 T1）
- [ ] T8: 前端實作編輯商品表單頁，預填既有資料（影響：`frontend/pages/products/[id]/edit.tsx`）（依賴 T3、T4、T7）
- [ ] T9: 前端實作下架按鈕，操作後更新列表狀態（影響：`frontend/components/ProductStatusToggle.tsx`）（依賴 T5、T6）
- [ ] T10: 前端加入路由守衛，未登入者導向登入頁（影響：`frontend/middleware/auth.ts`）（若已由 user-management 實作則跳過）
