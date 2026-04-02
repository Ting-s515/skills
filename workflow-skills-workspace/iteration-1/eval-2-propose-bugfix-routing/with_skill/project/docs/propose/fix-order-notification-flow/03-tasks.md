# 任務清單：修正訂單狀態通知信觸發流程

## 參考文檔
- 結構化流程：`docs/propose/fix-order-notification-flow/01-flow.md`
- 驗收條件：`docs/propose/fix-order-notification-flow/02-gherkin.md`

## 任務

- [ ] T1: 定義需觸發通知的訂單狀態清單（如：已確認、已出貨、已完成、已取消），以常數或設定檔管理（影響：`config/order-notification-statuses.ts` 或對應設定模組）
- [ ] T2: 建立或修正訂單狀態更新後的通知事件觸發點，確保狀態更新完成後正確發出通知事件（影響：`services/order.service.ts` 或訂單狀態更新相關模組）（依賴 T1）
- [ ] T3: 實作買家 email 有效性驗證邏輯（空值檢查、格式驗證），驗證失敗時記錄警告並中止通知流程（影響：`services/notification.service.ts` 或通知模組）
- [ ] T4: 建立各訂單狀態對應的通知信模板選取邏輯，依 new_status 組合信件內容（影響：`templates/order-notification/` 或 email 模板模組）（依賴 T1）
- [ ] T5: 實作郵件服務呼叫邏輯，發送成功後更新訂單 `notification_sent_at` 欄位（影響：`services/mail.service.ts`、`repositories/order.repository.ts`）（依賴 T3、T4）
- [ ] T6: 實作重試佇列機制，發送失敗時加入佇列，支援最多 3 次重試、間隔遞增（1/5/15 分鐘）（影響：`queues/notification-retry.queue.ts` 或任務佇列模組）（依賴 T5）
- [ ] T7: 超過最大重試次數後，標記通知永久失敗並發送警示給管理員（影響：`services/notification.service.ts`、`services/admin-alert.service.ts`）（依賴 T6）
- [ ] T8: 加入冪等保護，避免同一訂單狀態重複寄送通知信（可透過 `notification_sent_at` 或專屬冪等鍵實作）（影響：`services/notification.service.ts`）（依賴 T5）
