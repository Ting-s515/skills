# 驗收條件：formatCurrency 工具函式

## Feature: formatCurrency

Scenario: 格式化正整數金額
  Given 金額為 1234
  When 呼叫 formatCurrency
  Then 應回傳 "$1,234"

Scenario: 使用自訂幣別符號
  Given 金額為 500
  And 幣別符號為 "NT$"
  When 呼叫 formatCurrency
  Then 應回傳 "NT$500"
