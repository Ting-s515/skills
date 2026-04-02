# 任務清單：訂單通知信修正

## 參考文檔
- 結構化流程：`docs/propose/fix-order-notification/01-flow.md`
- 驗收條件：`docs/propose/fix-order-notification/02-gherkin.md`

## 任務

- [ ] T1: 調查訂單狀態更新流程，找出通知信觸發點缺失原因（影響：`services/order.service.ts`）
- [ ] T2: 新增通知觸發條件判斷邏輯，依狀態類型決定是否觸發通知（影響：`services/order.service.ts`）（依賴 T1）
- [ ] T3: 實作郵件通知寄送，組裝通知信內容並呼叫郵件服務（影響：`services/notification.service.ts`）（依賴 T2）
- [ ] T4: 實作寄送失敗重試機制，記錄錯誤 log 並於重試間隔後自動重試最多 3 次（影響：`services/notification.service.ts`）（依賴 T3）
- [ ] T5: 新增通知寄送成功/失敗 log 記錄（影響：`utils/logger.ts`）（依賴 T3）
- [ ] [manual] T_test: 補上單元測試，使用 Skill tool 呼叫 `bdd-unit-test` skill 分析實作檔案產出測試（依賴所有前置任務）
