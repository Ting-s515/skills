# 任務清單：商品庫存歸零時前台購買按鈕狀態更新

## 參考文檔

- 結構化流程：`docs/propose/fix-product-availability-status/01-flow.md`
- 驗收條件：`docs/propose/fix-product-availability-status/02-gherkin.md`

## 任務

- [ ] T1: 在 `products` 資料表新增 `is_available` 欄位，並建立對應 migration（影響：`migrations/`、`models/product.model.ts`）
- [ ] T2: 實作庫存更新邏輯：每次 `stock_quantity` 變更後，自動同步計算並更新 `is_available`（`stock_quantity > 0` → true，否則 false，NULL 視為 false）（影響：`services/product.service.ts`）（依賴 T1）
- [ ] T3: 庫存更新後觸發快取失效，清除對應 `product_id` 的快取（影響：`services/product.service.ts`、`cache/product.cache.ts`）（依賴 T2）
- [ ] T4: 更新商品查詢 API，在回應資料中包含 `is_available` 欄位（影響：`controllers/product.controller.ts`、`dto/product-response.dto.ts`）（依賴 T1）
- [ ] T5: 前台商品頁依照 `is_available` 欄位動態控制購買按鈕啟用/禁用狀態（影響：`components/ProductPage/BuyButton.tsx`）（依賴 T4）
- [ ] T6: 後端下單 API 加入二次庫存檢查，`stock_quantity <= 0` 時拒絕下單並回傳庫存不足錯誤（影響：`services/order.service.ts`、`controllers/order.controller.ts`）（依賴 T2）
