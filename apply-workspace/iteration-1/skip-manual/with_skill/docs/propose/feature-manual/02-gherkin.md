# Gherkin：formatCurrency 工具函式

Feature: formatCurrency 貨幣格式化

  Scenario: 格式化整數金額（千分位）
    Given 輸入金額 1234
    When 呼叫 formatCurrency(1234)
    Then 回傳 "NT$1,234"

  Scenario: 格式化帶小數的金額
    Given 輸入金額 1234.567，設定 decimals: 2
    When 呼叫 formatCurrency(1234.567, { decimals: 2 })
    Then 回傳 "NT$1,234.57"

  Scenario: 輸入無效數字
    Given 輸入 NaN
    When 呼叫 formatCurrency(NaN)
    Then 回傳 "NT$0"

  Scenario: 自訂貨幣符號
    Given 輸入金額 500，symbol 設為 "$"
    When 呼叫 formatCurrency(500, { symbol: "$" })
    Then 回傳 "$500"

  Scenario: 小金額無千分位
    Given 輸入金額 500
    When 呼叫 formatCurrency(500)
    Then 回傳 "NT$500"
