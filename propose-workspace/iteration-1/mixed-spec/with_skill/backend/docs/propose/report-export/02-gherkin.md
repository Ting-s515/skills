# Gherkin：報表匯出

Feature: 銷售報表匯出
  管理者可依日期區間與商品類別篩選，將銷售資料匯出為 Excel 或 CSV

  Scenario: 成功匯出 Excel 報表
    Given 管理者已登入且具備報表匯出權限
    And 系統存在符合條件的已完成訂單
    When 管理者以有效日期區間與 format=excel 送出匯出請求
    Then 系統回傳 .xlsx 格式的報表檔案供下載

  Scenario: 成功匯出 CSV 報表
    Given 管理者已登入且具備報表匯出權限
    And 系統存在符合條件的已完成訂單
    When 管理者以有效日期區間與 format=csv 送出匯出請求
    Then 系統回傳 UTF-8 with BOM 的 .csv 格式報表供下載

  Scenario: 查詢結果為空時回傳空報表
    Given 管理者已登入且具備報表匯出權限
    And 指定日期區間內無已完成訂單
    When 管理者送出匯出請求
    Then 系統回傳僅含欄位標題的空報表檔案

  Scenario: 日期起訖欄位未填
    When 管理者送出缺少 start_date 或 end_date 的匯出請求
    Then 系統回傳 400 驗證錯誤

  Scenario: 起始日期晚於結束日期
    When 管理者以 start_date 晚於 end_date 的條件送出請求
    Then 系統回傳 400 驗證錯誤

  Scenario: 日期區間超過 365 天
    When 管理者以超過 365 天的日期區間送出請求
    Then 系統回傳 400 驗證錯誤

  Scenario: 不支援的匯出格式
    When 管理者送出 format 不為 excel 或 csv 的匯出請求
    Then 系統回傳 400 驗證錯誤
