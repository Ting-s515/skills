# 手動測試需求：訂單結帳計算

## 目標

建立一個 `calculateInvoice(order)` 函式，用於計算訂單結帳金額。

## 輸入資料

`order` 需包含：

- `items`：商品陣列，每個商品包含 `price` 與 `quantity`
- `memberType`：會員類型，允許值為 `regular` 或 `vip`

## 計算規則

1. 小計 `subtotal` 為所有商品 `price * quantity` 的總和。
2. 若 `memberType` 為 `vip`，折扣 `discount` 為小計的 10%。
3. 若 `memberType` 為 `regular`，折扣 `discount` 為 0。
4. 稅金 `tax` 為折扣後金額的 5%。
5. 若小計大於或等於 500，運費 `shipping` 為 0。
6. 若小計小於 500，運費 `shipping` 為 60。
7. 總金額 `total` 為折扣後金額加上稅金與運費。

## 錯誤處理

1. `items` 不可為空陣列。
2. `price` 必須大於或等於 0。
3. `quantity` 必須大於 0。
4. `memberType` 不在允許值時需丟出錯誤。
