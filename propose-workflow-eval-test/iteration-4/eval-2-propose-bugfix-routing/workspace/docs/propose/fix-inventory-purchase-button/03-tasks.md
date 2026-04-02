# 任務清單：庫存歸零時停用購買按鈕修正

## 參考文檔

- 結構化流程：`docs/propose/fix-inventory-purchase-button/01-flow.md`
- 驗收條件：`docs/propose/fix-inventory-purchase-button/02-gherkin.md`

## 任務

- [ ] T1: 新增後端 API endpoint（或擴充現有商品詳情 API），回傳商品庫存狀態欄位（影響：`controllers/product.controller.ts`、`services/product.service.ts`）
- [ ] T2: 前台商品詳情頁根據 API 回傳的庫存狀態，初始渲染時正確顯示啟用或禁用的購買按鈕（影響：`components/ProductDetail.tsx` 或對應前端元件）（依賴 T1）
- [ ] T3: 實作前台庫存狀態動態更新機制（polling 或 WebSocket/SSE），使頁面在不重整的情況下反映最新庫存（影響：`hooks/useInventoryStatus.ts` 或對應前端邏輯）（依賴 T2）
- [ ] T4: 後端購買 API 加入庫存驗證防衛，庫存不足時回傳 HTTP 409 錯誤（影響：`services/order.service.ts`、`controllers/order.controller.ts`）
- [ ] T5: 後端使用樂觀鎖或資料庫原子操作防止多使用者同時購買超賣（影響：`services/order.service.ts`、資料庫 migration）（依賴 T4）
- [ ] T6: 前台接收後端 409 庫存不足錯誤時，顯示明確的提示訊息並更新按鈕狀態（影響：`components/ProductDetail.tsx`）（依賴 T2、T4）
- [ ] [manual] T_test: 補上單元測試，使用 Skill tool 呼叫 `bdd-unit-test` skill 分析實作檔案產出測試（依賴 T1、T2、T3、T4、T5、T6）
