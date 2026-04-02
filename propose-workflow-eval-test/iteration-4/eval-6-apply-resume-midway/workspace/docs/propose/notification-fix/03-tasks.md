# 任務清單：通知信修復

## 參考文檔
- 結構化流程：`docs/propose/notification-fix/01-flow.md`
- 驗收條件：`docs/propose/notification-fix/02-gherkin.md`

## 任務

- [x][cr] T1: 在 OrderService 訂單狀態更新後加入通知觸發點（影響：`src/services/OrderService.ts`）
- [x][cr] T2: 實作 NotificationService.sendOrderStatusEmail()，處理各狀態的 email 模板（影響：`src/services/NotificationService.ts`）
- [x][cr] T3: 加入通知失敗時的重試機制與錯誤 log（影響：`src/services/NotificationService.ts`）（依賴 T2）
- [ ] [manual] T_test: 補上單元測試，使用 Skill tool 呼叫 `bdd-unit-test` skill 分析實作檔案產出測試（依賴所有前置任務）
