# 任務清單：商品管理

## 參考文檔
- 結構化流程：`backend/docs/propose/product-management/01-flow.md`
- 驗收條件：`backend/docs/propose/product-management/02-gherkin.md`

## 任務

- [ ] T1: 建立商品資料模型（Entity / Schema），定義 `name`、`price`、`stock` 欄位及資料庫對應（影響：`src/products/product.entity.ts`）
- [ ] T2: 建立新增商品 DTO，加入欄位驗證規則（name 必填、price > 0、stock ≥ 0）（影響：`src/products/dto/create-product.dto.ts`）（依賴 T1）
- [ ] T3: 建立編輯商品 DTO，欄位為 Partial，各欄位保有相同驗證規則（影響：`src/products/dto/update-product.dto.ts`）（依賴 T1）
- [ ] T4: 實作商品 Repository / Service 的新增方法，寫入資料庫並回傳建立後資料（影響：`src/products/products.service.ts`）（依賴 T1）
- [ ] T5: 實作商品 Repository / Service 的編輯方法，先查詢商品是否存在，不存在則拋出 NotFoundException，存在則更新並回傳（影響：`src/products/products.service.ts`）（依賴 T1）
- [ ] T6: 建立 ProductsController，實作 POST /products（新增）路由，呼叫 Service 並回傳 HTTP 201（影響：`src/products/products.controller.ts`）（依賴 T2、T4）
- [ ] T7: 在 ProductsController 實作 PATCH /products/:id（編輯）路由，呼叫 Service 並回傳 HTTP 200；商品不存在時回傳 HTTP 404（影響：`src/products/products.controller.ts`）（依賴 T3、T5）
- [ ] T8: 將 ProductsModule 注入應用程式，確認路由正確掛載（影響：`src/app.module.ts`、`src/products/products.module.ts`）（依賴 T6、T7）
- [ ] [manual] T_test: 補上單元測試，使用 Skill tool 呼叫 `bdd-unit-test` skill 分析 `products.service.ts`、`products.controller.ts` 產出測試（依賴所有前置任務）
