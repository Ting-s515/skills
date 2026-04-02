```gherkin
Feature: 訂單狀態更新通知信寄送
  訂單狀態發生變更時，系統自動觸發並寄送通知信給買家，確保買家即時收到訂單進度更新

  Scenario: 訂單狀態變更為需通知狀態，成功寄送通知信
    Given 訂單存在且買家 Email 有效
    And 訂單目前狀態為舊狀態
    When 訂單狀態更新為需通知的新狀態
    Then 通知任務推送至佇列
    And 買家收到對應狀態的通知信

  Scenario: 訂單狀態未實際改變，不觸發通知
    Given 訂單目前狀態為 x
    When 訂單狀態被更新為相同的 x
    Then 不觸發任何通知

  Scenario: 訂單狀態變更為非通知清單內的狀態，不觸發通知
    Given 訂單存在且買家 Email 有效
    When 訂單狀態更新為不在通知清單內的狀態
    Then 不觸發任何通知

  Scenario: 買家 Email 為空，跳過通知
    Given 訂單存在
    And 訂單對應買家的 Email 為空
    When 訂單狀態更新為需通知的新狀態
    Then 系統記錄警告日誌
    And 不觸發通知信

  Scenario: 郵件服務暫時失敗，重試後成功
    Given 通知任務已進入佇列
    When 郵件服務第一次呼叫失敗
    Then 系統進行重試
    And 重試成功後通知發送狀態更新為「已發送」

  Scenario: 郵件服務連續失敗超過重試上限
    Given 通知任務已進入佇列
    When 郵件服務連續失敗達 x 次（超過重試上限）
    Then 通知發送狀態更新為「發送失敗」
    And 系統記錄錯誤日誌

  Scenario: 重複觸發相同狀態通知，跳過重複發送
    Given 同一訂單的相同狀態通知已成功發送
    When 再次觸發相同訂單相同狀態的通知
    Then 系統跳過發送
    And 不重複寄出通知信
```
