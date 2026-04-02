# 驗收條件：使用者管理

```gherkin
Feature: 使用者管理

  Scenario: 管理員查看使用者列表
    Given 管理員已登入後台
    When 管理員進入「使用者管理」頁面
    Then 系統顯示所有使用者的分頁列表

  Scenario: 管理員依 email 搜尋使用者
    Given 管理員在使用者列表頁面
    When 管理員在搜尋欄輸入 email 關鍵字
    Then 系統顯示 email 符合關鍵字的使用者列表

  Scenario: 搜尋結果為空
    Given 管理員在使用者列表頁面
    When 管理員輸入不存在的 email 關鍵字
    Then 系統顯示「無符合條件的使用者」提示

  Scenario: 管理員查看使用者詳情
    Given 管理員在使用者列表頁面
    When 管理員點擊某筆使用者
    Then 系統顯示該使用者的姓名、email、建立時間、訂單數量

  Scenario: 管理員停用使用者帳號
    Given 管理員在使用者列表頁面，且目標帳號狀態為「啟用」
    When 管理員點擊「停用」按鈕並確認操作
    Then 系統將帳號狀態更新為「停用」並顯示成功訊息
    And 列表中該使用者的狀態標籤即時更新為「停用」

  Scenario: 管理員啟用使用者帳號
    Given 管理員在使用者列表頁面，且目標帳號狀態為「停用」
    When 管理員點擊「啟用」按鈕並確認操作
    Then 系統將帳號狀態更新為「啟用」並顯示成功訊息
    And 列表中該使用者的狀態標籤即時更新為「啟用」

  Scenario: 管理員取消停用確認對話框
    Given 管理員點擊「停用」按鈕後系統顯示確認對話框
    When 管理員點擊「取消」
    Then 對話框關閉，帳號狀態維持不變

  Scenario: 停用/啟用 API 呼叫失敗
    Given 管理員確認停用或啟用操作
    When API 回傳錯誤
    Then 系統顯示錯誤訊息，帳號狀態維持不變

  Scenario: 管理員嘗試停用自身帳號
    Given 管理員查看自身帳號
    When 管理員嘗試點擊「停用」
    Then 系統禁止操作並顯示「無法停用自身帳號」提示
```
