```gherkin
Feature: 訂單狀態更新通知信觸發
  訂單狀態發生變更時，系統應正確觸發並寄送對應通知信給買家

  Scenario: 訂單狀態更新為已確認，成功寄送通知信
    Given 訂單存在且買家 Email 有效
    And 訂單通知尚未發送
    When 訂單狀態更新為「已確認」
    Then 系統使用「訂單確認」模板寄送通知信給買家
    And 訂單通知記錄更新為已發送

  Scenario: 訂單狀態更新為已出貨，成功寄送通知信
    Given 訂單存在且買家 Email 有效
    And 訂單通知尚未發送
    When 訂單狀態更新為「已出貨」
    Then 系統使用「出貨通知」模板寄送通知信給買家
    And 訂單通知記錄更新為已發送

  Scenario: 訂單狀態更新為不需通知的狀態
    Given 訂單存在且買家 Email 有效
    When 訂單狀態更新為不在通知清單內的狀態
    Then 系統不觸發任何通知

  Scenario: 買家 Email 為空，跳過通知
    Given 訂單存在
    And 買家 Email 為空或 null
    When 訂單狀態更新為需通知的狀態
    Then 系統跳過通知發送
    And 記錄 warning log

  Scenario: Email 服務不可用，進入重試佇列
    Given 訂單存在且買家 Email 有效
    When 訂單狀態更新為需通知的狀態
    And Email 服務發送失敗
    Then 通知任務加入重試佇列
    And 最多重試 x 次

  Scenario: 重試 x 次均失敗，發出告警
    Given 通知任務已重試 x 次均失敗
    When 達到最大重試次數
    Then 通知標記為「發送失敗」
    And 系統發出告警通知給管理員

  Scenario: 相同狀態重複觸發，防止重複通知
    Given 訂單已發送過該狀態對應的通知信
    When 相同訂單狀態再次觸發更新事件
    Then 系統不重複發送通知信
```
