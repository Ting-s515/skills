# Gherkin：訂單狀態批次更新 Transaction 保護

Feature: 訂單狀態批次更新 Transaction 保護
  批次更新訂單狀態時，任一訂單失敗應觸發全體 rollback，確保資料一致性

  Scenario: 所有訂單更新成功
    Given 系統中存在 n 筆有效訂單
    And 每筆訂單的狀態均允許轉換至目標狀態
    When 提交批次更新請求，包含 n 個訂單 ID 與目標狀態
    Then 所有訂單狀態更新成功
    And 回傳 200 與更新成功筆數

  Scenario: 批次中有一筆訂單不存在
    Given 批次訂單 ID 清單中有一個 ID 不存在於系統
    When 提交批次更新請求
    Then 所有已更新的訂單均被 rollback
    And 回傳 404，訊息說明哪個訂單不存在

  Scenario: 批次中有一筆訂單狀態不允許轉換
    Given 批次中某筆訂單目前狀態不允許轉換至目標狀態
    When 提交批次更新請求
    Then 所有已更新的訂單均被 rollback
    And 回傳 422

  Scenario: 訂單 ID 清單為空
    When 提交批次更新請求，`order_ids` 為空陣列
    Then 回傳 400，訊息「訂單清單不可為空」

  Scenario: 目標狀態為無效值
    When 提交批次更新請求，`target_status` 為系統不支援的值
    Then 回傳 400，訊息「無效的訂單狀態」
