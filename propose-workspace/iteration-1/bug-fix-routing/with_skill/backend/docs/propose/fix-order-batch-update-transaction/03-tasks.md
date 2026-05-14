# 任務清單：訂單狀態批次更新 Transaction 保護

## 參考文檔
- 結構化流程：`backend/docs/propose/fix-order-batch-update-transaction/01-flow.md`
- 驗收條件：`backend/docs/propose/fix-order-batch-update-transaction/02-gherkin.md`

## 任務

- [ ] T1: 在 OrderService 的批次更新方法加入 transaction 包覆，確保全成功才 commit（影響：`src/services/order.service.ts`）
- [ ] T2: 新增訂單存在性驗證，查無訂單時拋出 NotFoundException 並觸發 rollback（影響：`src/services/order.service.ts`）（依賴 T1）
- [ ] T3: 新增狀態轉換合法性驗證，非法轉換時拋出 UnprocessableEntityException（影響：`src/services/order.service.ts`）（依賴 T1）
- [ ] T4: 在 Controller 層補上 400 輸入驗證（order_ids 不可為空、target_status 需為合法 enum）（影響：`src/controllers/order.controller.ts`、`src/dto/batch-update-order.dto.ts`）
- [ ] T5: 更新 Repository 層確保在 transaction context 下執行 SQL（影響：`src/repositories/order.repository.ts`）（依賴 T1）
- [ ] [manual] T_test: 補上單元測試，使用 Skill tool 呼叫 `bdd-unit-test` skill 分析實作檔案產出測試（依賴所有前置任務）
