# 任務清單：修正商品庫存歸零時購買按鈕狀態

## 參考文檔
- 結構化流程：`docs/propose/fix-product-stock-button-state/01-flow.md`
- 驗收條件：`docs/propose/fix-product-stock-button-state/02-gherkin.md`

## 任務

- [ ] T1: 確認後端商品 API 回應中包含 `stock_quantity` 欄位，若未回傳則調整 API 回應格式（影響：`controllers/product.controller.ts` 或 `serializers/product.serializer.ts`）
- [ ] T2: 在前台商品頁面元件中，依據 `stock_quantity` 判斷購買按鈕的啟用/停用狀態，`stock_quantity <= 0` 或 NULL 時顯示「已售完」並設為 disabled（影響：`components/ProductPage.vue` 或對應前台商品頁面元件）（依賴 T1）
- [ ] T3: 處理庫存即時更新事件（WebSocket 或輪詢），接收到庫存變更時動態更新按鈕狀態，不需整頁重整（影響：`store/product.store.ts` 或狀態管理模組、`components/ProductPage.vue`）（依賴 T2）
- [ ] T4: 在後端購買 API 中加入庫存驗證，庫存不足時回傳錯誤碼及訊息，作為前端的最後防線（影響：`services/order.service.ts` 或購買流程相關服務）（依賴 T1）
- [ ] T5: 前台處理後端庫存不足錯誤回應，顯示提示訊息「此商品已售完，無法購買」給使用者（影響：`components/ProductPage.vue`、`utils/error-handler.ts` 或錯誤處理模組）（依賴 T4）
