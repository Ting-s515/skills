# 任務清單：訂單狀態更新通知修正

## 參考文檔
- 結構化流程：`docs/propose/fix-order-notification/01-flow.md`
- 驗收條件：`docs/propose/fix-order-notification/02-gherkin.md`

## 任務

- [ ] T1: 定義需觸發通知的訂單狀態清單（常數或設定檔）（影響：`config/order-status.ts` 或對應設定模組）
- [ ] T2: 在訂單狀態更新邏輯中加入通知觸發點，狀態寫入資料庫後呼叫通知服務（影響：`services/order.service.ts`）（依賴 T1）
- [ ] T3: 實作通知信組裝邏輯，包含訂單編號、新狀態、買家姓名等欄位（影響：`services/notification.service.ts`）
- [ ] T4: 整合郵件發送服務，處理發送失敗時的錯誤記錄與重試佇列邏輯（影響：`services/mail.service.ts`）（依賴 T3）
- [ ] T5: 加入發送結果日誌記錄（成功 / 失敗 / 無需通知）（影響：`services/notification.service.ts`）（依賴 T4）
