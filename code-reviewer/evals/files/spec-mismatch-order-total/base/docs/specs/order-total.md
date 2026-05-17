# 訂單總額規格

## 背景

結帳流程需要顯示使用者折扣後的實際應付總額。稅額必須依照折扣後金額計算，避免使用者被高估稅額。

## 規則

- `calculateOrderTotal(items, coupon)` 必須先計算商品小計。
- coupon 折扣不可讓折扣後小計低於 0。
- 必須先套用 coupon 折扣，再用折扣後小計計算 5% tax。
- 回傳資料必須包含 `subtotal`、`discount`、`tax`、`total`。
- `total` 必須等於折扣後小計加上 tax。
