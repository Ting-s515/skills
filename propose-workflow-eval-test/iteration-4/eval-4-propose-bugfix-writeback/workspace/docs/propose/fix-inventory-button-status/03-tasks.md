# 任務清單：商品庫存按鈕狀態修正

## 參考文檔
- 結構化流程：`docs/propose/fix-inventory-button-status/01-flow.md`
- 驗收條件：`docs/propose/fix-inventory-button-status/02-gherkin.md`

## 任務

- [ ] T1: 確認商品 API 回應是否包含庫存數量欄位，必要時補齊欄位（影響：`api/product.api.ts`）
- [ ] T2: 修正前台商品頁面元件，依庫存數量動態設定購買按鈕的啟用/禁用狀態（影響：`components/ProductDetail.tsx`）（依賴 T1）
- [ ] T3: 加入「庫存不足」提示文字的條件渲染邏輯（影響：`components/ProductDetail.tsx`）（依賴 T2）
- [ ] T4: 在加入購物車操作時加入後端庫存二次確認，並處理庫存已歸零的錯誤回應（影響：`components/ProductDetail.tsx`、`services/cart.service.ts`）（依賴 T2）
- [ ] [manual] T_test: 補上單元測試，使用 Skill tool 呼叫 `bdd-unit-test` skill 分析實作檔案產出測試（依賴所有前置任務）
