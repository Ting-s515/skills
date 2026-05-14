# 功能流程：formatCurrency 工具函式

## 功能概述
提供一個純函式，將數字格式化為台幣貨幣字串。

## 流程說明

### formatCurrency(amount, options)

輸入：
- amount (number)：要格式化的金額
- options.symbol (string)：貨幣符號（預設 "NT$"）
- options.decimals (number)：小數位數（預設 0）

輸出：格式化後的字串

邏輯：
1. 若 amount 為 NaN 或 Infinity → 回傳 `${symbol}0`
2. 依 decimals 對 amount 四捨五入
3. 整數部分加上千分位逗號
4. 前綴貨幣符號

範例：
- formatCurrency(1234) → "NT$1,234"
- formatCurrency(1234.567, { decimals: 2 }) → "NT$1,234.57"
- formatCurrency(NaN) → "NT$0"
- formatCurrency(500, { symbol: "$" }) → "$500"
- formatCurrency(500) → "NT$500"
