# 任務清單：訂單管理

## 參考文檔
- 結構化流程：`backend/docs/propose/order-management/01-flow.md`
- 驗收條件：`backend/docs/propose/order-management/02-gherkin.md`

## 任務

- [ ] T1: 定義訂單狀態枚舉（OrderStatus: PENDING / PAID / SHIPPED / COMPLETED）（影響：`src/orders/order-status.enum.ts`）
- [ ] T2: 建立 Order Entity，含 id、status、createdAt、customerId、totalAmount 欄位（影響：`src/orders/order.entity.ts`）（依賴 T1）
- [ ] T3: 建立訂單查詢 DTO，status 為可選的 OrderStatus enum 值，加入驗證（影響：`src/orders/dto/query-order.dto.ts`）（依賴 T1）
- [ ] T4: 實作 OrdersService.findAll(status?)，依 status 過濾訂單（影響：`src/orders/orders.service.ts`）（依賴 T2）
- [ ] T5: 實作 OrdersService.updateStatus(id, status)，先查詢存在性（404），再更新（影響：`src/orders/orders.service.ts`）（依賴 T2）
- [ ] T6: 建立 OrdersController，實作 GET /orders（含可選 status 查詢參數）與 PATCH /orders/:id/status 路由（影響：`src/orders/orders.controller.ts`）（依賴 T3, T4, T5）
- [ ] [manual] T_test: 補上單元測試，使用 Skill tool 呼叫 `bdd-unit-test` skill 分析 `orders.service.ts` 和 `orders.controller.ts` 產出測試（依賴所有前置任務）
