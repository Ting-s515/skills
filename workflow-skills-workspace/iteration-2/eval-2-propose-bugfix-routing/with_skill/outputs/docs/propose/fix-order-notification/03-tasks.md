# 任務清單：訂單狀態更新通知信觸發修正

## 參考文檔
- 結構化流程：`docs/propose/fix-order-notification/01-flow.md`
- 驗收條件：`docs/propose/fix-order-notification/02-gherkin.md`

## 任務

- [ ] T1: 調查現有通知觸發點，確認 bug 根因（事件未觸發 / 模板錯誤 / Email Service 呼叫失敗）（影響：`services/order/orderStatusService.ts` 或對應後端服務）
- [ ] T2: 設計通知觸發介面，定義狀態與模板的對應關係（影響：`services/notification/notificationTemplateMap.ts`）（依賴 T1）
- [ ] T3: 實作通知觸發邏輯，於訂單狀態更新後呼叫 Email Service（影響：`services/order/orderStatusService.ts`）（依賴 T2）
- [ ] T4: 新增 `notification_sent` 欄位防止重複發送（影響：`models/order.ts`、DB migration）（依賴 T3）
- [ ] T5: 實作重試佇列邏輯（最多 3 次），失敗後發出告警（影響：`services/notification/notificationRetryQueue.ts`）（依賴 T3）
- [ ] T6: 補充買家 Email 空值檢查與 warning log（影響：`services/notification/notificationService.ts`）（依賴 T3）
- [ ] T7: 撰寫單元測試，覆蓋各狀態分支與邊界情境（依賴 T3、T4、T5、T6）
