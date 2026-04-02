# 任務清單：商品庫存歸零時前台購買按鈕狀態同步修正

## 參考文檔
- 結構化流程：`docs/propose/fix-stock-button-state/01-flow.md`
- 驗收條件：`docs/propose/fix-stock-button-state/02-gherkin.md`

## 任務

- [ ] T1: 確認現有商品詳情 API 是否回傳庫存數量欄位，若無則擴充回傳欄位（影響：`api/products/[id].ts` 或對應後端 endpoint）
- [ ] T2: 前台商品頁面初始載入時，依據庫存數量動態設定購買按鈕的 disabled 狀態（影響：`components/product/ProductDetail.tsx`）（依賴 T1）
- [ ] T3: 處理庫存為 null 的邊界情況，null 視為庫存不足，按鈕設為 disabled（影響：`components/product/ProductDetail.tsx`）（依賴 T2）
- [ ] T4: 後台庫存更新後觸發 `stock_updated` 事件（影響：`services/inventory/inventoryService.ts`）（依賴 T1）
- [ ] T5: 實作前台即時庫存狀態訂閱（WebSocket 或 polling），接收到事件後更新按鈕狀態（影響：`hooks/useStockStatus.ts`、`components/product/ProductDetail.tsx`）（依賴 T4）
- [ ] T6: 後端下單時加入最終庫存驗證，庫存不足時回傳錯誤（影響：`api/orders/create.ts` 或對應下單 API）（依賴 T1）
- [ ] T7: 撰寫單元測試，覆蓋各庫存狀態分支（依賴 T2、T3、T5、T6）
