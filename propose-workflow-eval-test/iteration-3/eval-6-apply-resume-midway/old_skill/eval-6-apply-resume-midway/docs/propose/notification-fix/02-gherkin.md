# 驗收條件：通知信修復

```gherkin
Feature: 訂單狀態通知信

  Scenario: 訂單狀態更新後寄出通知信
    Given 買家有一筆訂單
    When 管理員將訂單狀態更新為「已出貨」
    Then 系統寄出「訂單已出貨」通知信給買家

  Scenario: 通知信發送失敗時進行重試
    Given 訂單狀態已更新
    When email 服務暫時不可用
    Then 系統在 5 分鐘後重試，最多重試 3 次

  Scenario: 重試 3 次仍失敗時記錄錯誤
    Given 通知信已重試 3 次
    When 第 3 次仍失敗
    Then 系統記錄錯誤 log，不再重試
```
