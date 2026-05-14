# 驗收條件：訂單管理

```gherkin
Feature: 訂單管理
  管理者可在後台查看所有訂單列表，並依訂單狀態進行篩選

  # ── 查看訂單列表 ──────────────────────────────────────

  Scenario: 查看所有訂單（不篩選）
    Given 資料庫中存在多筆不同狀態的訂單
    When 管理者請求訂單列表，不帶入 status 參數
    Then 回傳所有訂單，依建立時間由新到舊排序
    And 每筆訂單包含 orderId、createdAt、customerName、totalAmount、status 欄位
    And HTTP 200

  Scenario: 依狀態篩選訂單 - 待付款
    Given 資料庫中存在待付款與其他狀態的訂單
    When 管理者請求訂單列表，帶入 status=pending_payment
    Then 回傳所有待付款狀態的訂單
    And HTTP 200

  Scenario: 依狀態篩選訂單 - 已付款
    Given 資料庫中存在已付款與其他狀態的訂單
    When 管理者請求訂單列表，帶入 status=paid
    Then 回傳所有已付款狀態的訂單
    And HTTP 200

  Scenario: 依狀態篩選訂單 - 已出貨
    Given 資料庫中存在已出貨與其他狀態的訂單
    When 管理者請求訂單列表，帶入 status=shipped
    Then 回傳所有已出貨狀態的訂單
    And HTTP 200

  Scenario: 依狀態篩選訂單 - 已完成
    Given 資料庫中存在已完成與其他狀態的訂單
    When 管理者請求訂單列表，帶入 status=completed
    Then 回傳所有已完成狀態的訂單
    And HTTP 200

  Scenario: 篩選結果為空
    Given 資料庫中不存在任何已出貨狀態的訂單
    When 管理者請求訂單列表，帶入 status=shipped
    Then 回傳空陣列
    And HTTP 200

  Scenario: 帶入非法 status 值
    Given 管理者已登入後台
    When 管理者請求訂單列表，帶入非法的 status 參數值
    Then 回傳驗證錯誤，訊息為「status 參數不合法」
    And HTTP 400
```
