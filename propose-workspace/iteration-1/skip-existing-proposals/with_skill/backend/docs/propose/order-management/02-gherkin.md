# Gherkin：訂單管理

Feature: 訂單管理
  管理者可查看與管理所有訂單，支援依狀態篩選及更新訂單狀態

  Scenario: 查看全部訂單列表
    Given 管理者已登入
    And 系統存在 n 筆訂單
    When 管理者查詢訂單列表（不帶 status 篩選）
    Then 回傳全部 n 筆訂單與 200

  Scenario: 依有效狀態篩選訂單
    Given 管理者已登入
    And 系統存在多筆不同狀態訂單
    When 管理者以合法 status 值查詢訂單列表
    Then 回傳符合狀態的訂單列表與 200

  Scenario: 篩選結果為空
    Given 管理者已登入
    And 該狀態下無訂單
    When 管理者以合法 status 值查詢
    Then 回傳空陣列與 200

  Scenario: 傳入非法 status 值
    Given 管理者已登入
    When 管理者以非法 status 值查詢
    Then 回傳 400 驗證錯誤

  Scenario: 成功更新訂單狀態
    Given 管理者已登入
    And 訂單存在且目標狀態合法
    When 管理者送出狀態更新請求
    Then 訂單狀態更新成功，回傳 200 與更新後訂單資料

  Scenario: 更新不存在的訂單
    Given 管理者已登入
    When 管理者對不存在的訂單 ID 送出更新請求
    Then 回傳 404
