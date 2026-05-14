# Gherkin：商品搜尋特殊字元處理

Feature: 商品搜尋特殊字元處理
  商品搜尋 API 應正確處理含特殊字元的關鍵字，避免 SQL 錯誤並返回正確結果

  Scenario: 搜尋關鍵字包含 % 字元
    Given 資料庫中存在商品名稱包含「50%」的商品
    When 以關鍵字「50%」呼叫商品搜尋 API
    Then 回傳 200
    And 結果包含商品名稱含「50%」的商品

  Scenario: 搜尋關鍵字包含 _ 字元
    Given 資料庫中存在商品名稱包含「product_v2」的商品
    When 以關鍵字「product_v2」呼叫商品搜尋 API
    Then 回傳 200

  Scenario: 搜尋關鍵字包含反斜線
    Given 資料庫中存在商品名稱包含反斜線的商品
    When 以含反斜線的關鍵字呼叫商品搜尋 API
    Then 回傳 200

  Scenario: 搜尋關鍵字為空字串
    Given 資料庫中存在 n 筆商品
    When 以空字串關鍵字呼叫商品搜尋 API
    Then 回傳 200
    And 回傳全部 n 筆商品

  Scenario: 搜尋結果為空
    Given 資料庫中不存在符合關鍵字的商品
    When 呼叫商品搜尋 API
    Then 回傳 200
    And 回傳空陣列
