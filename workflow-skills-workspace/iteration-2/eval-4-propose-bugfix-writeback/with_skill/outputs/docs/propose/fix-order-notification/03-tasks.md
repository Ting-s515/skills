# 任務清單：訂單狀態更新通知信寄送

## 參考文檔

- 結構化流程：`docs/propose/fix-order-notification/01-flow.md`
- 驗收條件：`docs/propose/fix-order-notification/02-gherkin.md`

## 任務

- [ ] T1: 新增通知狀態白名單設定，定義哪些訂單狀態需觸發通知（影響：`config/order-notification.config.ts`）
- [ ] T2: 在訂單狀態更新邏輯中加入狀態差異比對，防止相同狀態重複觸發（影響：`services/order.service.ts`）（依賴 T1）
- [ ] T3: 建立通知佇列任務推送邏輯，將通知任務（order_id、buyer_email、new_status、template_id）推入非同步佇列（影響：`services/notification-queue.service.ts`）（依賴 T2）
- [ ] T4: 實作佇列消費端，從佇列取出任務並呼叫郵件服務發送通知信（影響：`workers/notification.worker.ts`）（依賴 T3）
- [ ] T5: 實作重試機制（最多 3 次，指數退避），並在失敗超過上限時更新發送狀態為「發送失敗」（影響：`workers/notification.worker.ts`）（依賴 T4）
- [ ] T6: 新增冪等保護機制，檢查同一 order_id 與 new_status 組合是否已有「已發送」紀錄，若有則跳過（影響：`services/notification-queue.service.ts`、`repositories/notification-log.repository.ts`）（依賴 T3）
- [ ] T7: 建立通知發送日誌資料表或紀錄模型，儲存發送狀態與錯誤訊息（影響：`migrations/`、`models/notification-log.model.ts`）（依賴 T4、T6）
