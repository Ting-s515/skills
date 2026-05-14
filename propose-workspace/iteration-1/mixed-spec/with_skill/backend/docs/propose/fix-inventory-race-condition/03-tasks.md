# 任務清單：並發庫存扣減修正

## 參考文檔
- 結構化流程：`backend/docs/propose/fix-inventory-race-condition/01-flow.md`
- 驗收條件：`backend/docs/propose/fix-inventory-race-condition/02-gherkin.md`

## 任務

- [ ] T1: 在下單服務中引入資料庫交易，包裹庫存查詢與扣減操作（影響：`src/services/order.service.ts`）
- [ ] T2: 將庫存查詢改為 `SELECT ... FOR UPDATE`（row-level 排他鎖）（影響：`src/repositories/product.repository.ts`）（依賴 T1）
- [ ] T3: 將庫存扣減改為條件式更新 `UPDATE ... WHERE stock >= quantity`，並檢查影響列數（影響：`src/repositories/product.repository.ts`）（依賴 T2）
- [ ] T4: 當庫存扣減失敗（影響列數 = 0）時，rollback 並回傳 409（影響：`src/services/order.service.ts`）（依賴 T3）
- [ ] T5: 補充下單數量輸入驗證（拒絕 0 或負數），回傳 400（影響：`src/dto/create-order.dto.ts`）
- [ ] [manual] T_test: 補上單元測試，使用 Skill tool 呼叫 `bdd-unit-test` skill 分析實作檔案產出測試（依賴所有前置任務）
