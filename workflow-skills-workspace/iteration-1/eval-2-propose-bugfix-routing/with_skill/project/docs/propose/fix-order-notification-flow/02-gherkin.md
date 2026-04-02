# 驗收條件：修正訂單狀態通知信觸發流程

```gherkin
Feature: 訂單狀態更新通知信寄送

  Scenario: 訂單狀態更新為「已出貨」時，正確寄送通知信給買家
    Given 系統中存在一筆訂單，狀態為「已確認」
    And 買家具備有效的 email 地址
    When 後台操作人員將訂單狀態更新為「已出貨」
    Then 系統應觸發通知事件
    And 自動發送「已出貨」通知信至買家 email
    And 訂單的 notification_sent_at 應記錄為發送時間

  Scenario: 訂單狀態更新為不需通知的內部狀態時，不寄送通知信
    Given 系統中存在一筆訂單
    When 系統將訂單狀態更新為內部處理狀態（不在通知清單內）
    Then 系統應跳過通知信寄送
    And 不呼叫郵件服務 API

  Scenario: 買家 email 為空時，通知信寄送失敗並記錄警告
    Given 系統中存在一筆訂單
    And 買家的 email 欄位為空字串或 NULL
    When 訂單狀態更新為「已完成」
    Then 系統應記錄警告日誌
    And 標記本次通知為失敗
    And 不呼叫郵件服務 API

  Scenario: 郵件服務暫時失敗時，通知任務加入重試佇列
    Given 系統中存在一筆訂單，買家具備有效 email
    And 郵件服務 API 暫時回傳錯誤
    When 訂單狀態更新為「已取消」
    Then 系統應嘗試發送通知信
    And 發送失敗後將任務加入重試佇列
    And 重試次數上限為 3 次，間隔遞增

  Scenario: 重試成功後正確更新通知時間戳
    Given 通知任務已在重試佇列中等待
    And 郵件服務已恢復正常
    When 重試發送成功
    Then 訂單的 notification_sent_at 應更新為本次成功發送時間
    And 任務從重試佇列中移除

  Scenario: 超過最大重試次數後標記永久失敗並通知管理員
    Given 通知任務已重試 3 次均失敗
    When 第 3 次重試仍失敗
    Then 系統應標記本次通知為永久失敗
    And 記錄警告日誌
    And 發送警示通知給管理員

  Scenario: 同一訂單狀態短時間重複觸發，不重複寄送通知信
    Given 買家已收到訂單「已出貨」通知信
    When 同一訂單狀態在短時間內再次觸發通知事件
    Then 系統應透過冪等保護跳過重複發送
    And 不重複呼叫郵件服務 API
```
