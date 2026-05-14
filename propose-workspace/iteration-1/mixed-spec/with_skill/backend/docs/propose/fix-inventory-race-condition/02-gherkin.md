# Gherkin：並發庫存扣減安全性

Feature: 並發庫存扣減安全性
  確保多個使用者同時下單時，庫存扣減為原子操作，不發生超賣

  Scenario: 單一使用者下單成功扣減庫存
    Given 商品庫存為 x 件
    When 使用者下單 y 件（y <= x）
    Then 庫存扣減為 x - y 件
    And 訂單建立成功

  Scenario: 庫存不足時拒絕下單
    Given 商品庫存為 x 件
    When 使用者下單 y 件（y > x）
    Then 系統回傳 409 庫存不足錯誤
    And 庫存維持 x 件不變

  Scenario: 並發下單時僅允許庫存充足的請求成功
    Given 商品庫存為 x 件
    And n 個使用者同時下單，每人下單 y 件（n * y > x）
    When 所有請求同時送出
    Then 最終庫存不低於 0（無超賣）

  Scenario: 商品不存在時拒絕下單
    Given 指定的 product_id 不存在
    When 使用者送出下單請求
    Then 系統回傳 404

  Scenario: 下單數量為 0 或負數
    When 使用者以數量 0 或負數送出下單請求
    Then 系統回傳 400 驗證錯誤
