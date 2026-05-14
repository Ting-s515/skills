# 任務清單：訂單管理

## 參考文檔
- 結構化流程：`backend/docs/propose/order-management/01-flow.md`
- 驗收條件：`backend/docs/propose/order-management/02-gherkin.md`

## 任務

- [ ] T1: 建立訂單狀態枚舉（OrderStatus enum），定義 `pending_payment`、`paid`、`shipped`、`completed` 四個合法值（影響：`src/orders/order-status.enum.ts`）
- [ ] T2: 建立訂單資料模型（Entity / Schema），定義 `orderId`、`createdAt`、`customerName`、`totalAmount`、`status` 欄位（影響：`src/orders/order.entity.ts`）（依賴 T1）
- [ ] T3: 建立查詢訂單列表 DTO / Query 驗證，`status` 為可選欄位並限制為合法枚舉值（影響：`src/orders/dto/list-orders.dto.ts`）（依賴 T1）
- [ ] T4: 實作 OrdersService 的查詢方法，支援可選 `status` 篩選，查詢結果依 `createdAt` 由新到舊排序（影響：`src/orders/orders.service.ts`）（依賴 T2）
- [ ] T5: 建立 OrdersController，實作 GET /orders 路由，接收可選 `status` query param，呼叫 Service 並回傳 HTTP 200（影響：`src/orders/orders.controller.ts`）（依賴 T3、T4）
- [ ] T6: 將 OrdersModule 注入應用程式，確認路由正確掛載（影響：`src/app.module.ts`、`src/orders/orders.module.ts`）（依賴 T5）
- [ ] [manual] T_test: 補上單元測試，使用 Skill tool 呼叫 `bdd-unit-test` skill 分析 `orders.service.ts`、`orders.controller.ts` 產出測試（依賴所有前置任務）
