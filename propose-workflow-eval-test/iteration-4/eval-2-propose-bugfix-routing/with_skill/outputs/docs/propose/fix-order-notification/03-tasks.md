# 任務清單：訂單狀態通知信修正

## 參考文檔

- 結構化流程：`docs/propose/fix-order-notification/01-flow.md`
- 驗收條件：`docs/propose/fix-order-notification/02-gherkin.md`

## 任務

- [ ] T1: 在訂單狀態更新 Service 中，狀態持久化成功後觸發通知事件（影響：`services/order.service.ts`）
- [ ] T2: 建立或修正 NotificationService，實作根據訂單狀態選擇對應 email 模板並組合內容（影響：`services/notification.service.ts`）（依賴 T1）
- [ ] T3: 實作通知冪等性檢查，防止同一訂單同一狀態重複寄送（影響：`services/notification.service.ts`、`repositories/notification-log.repository.ts`）（依賴 T2）
- [ ] T4: 實作 email 寄送失敗時的重試佇列機制，支援最多 3 次指數退避重試（影響：`queues/email-retry.queue.ts`、`services/notification.service.ts`）（依賴 T2）
- [ ] T5: 補上 email 缺失與格式錯誤的防衛性處理，確保不阻斷訂單狀態更新流程（影響：`services/notification.service.ts`）（依賴 T2）
- [ ] [manual] T_test: 補上單元測試，使用 Skill tool 呼叫 `bdd-unit-test` skill 分析實作檔案產出測試（依賴 T1、T2、T3、T4、T5）
