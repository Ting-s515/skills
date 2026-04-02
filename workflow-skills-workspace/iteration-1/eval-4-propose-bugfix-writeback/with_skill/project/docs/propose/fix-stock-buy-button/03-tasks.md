# 任務清單：庫存歸零時購買按鈕狀態修正

## 參考文檔
- 結構化流程：`docs/propose/fix-stock-buy-button/01-flow.md`
- 驗收條件：`docs/propose/fix-stock-buy-button/02-gherkin.md`

## 任務

- [ ] T1: 確認後端商品 API 回傳資料結構中包含庫存欄位（`stock` 或 `quantity`），必要時更新 API 回傳格式（影響：`controllers/product.controller.ts` 或對應 API 層）
- [ ] T2: 在前台商品頁面元件中，根據庫存數量動態計算購買按鈕的啟用 / 禁用狀態（影響：`components/ProductDetail.vue` 或對應頁面元件）（依賴 T1）
- [ ] T3: 庫存為 0 時，按鈕改為禁用並更新按鈕文字（如「已售完」），庫存 > 0 時恢復可購買狀態（影響：`components/ProductDetail.vue`）（依賴 T2）
- [ ] T4: 處理 API 回傳庫存欄位缺失的防禦邏輯，預設視為無庫存（影響：`components/ProductDetail.vue` 或資料轉換層）（依賴 T2）
