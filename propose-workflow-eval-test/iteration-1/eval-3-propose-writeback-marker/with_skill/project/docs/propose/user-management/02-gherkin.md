# 驗收條件：使用者管理

```gherkin
Feature: 使用者管理

  Scenario: 管理員查看使用者列表
    Given 管理員已登入後台
    When 管理員進入使用者管理頁面
    Then 系統顯示所有使用者列表，包含姓名與 email 欄位

  Scenario: 管理員依 email 搜尋使用者
    Given 管理員在使用者管理頁面
    When 管理員輸入 email 關鍵字並送出搜尋
    Then 系統顯示 email 包含該關鍵字的使用者列表

  Scenario: 搜尋無結果
    Given 管理員在使用者管理頁面
    When 管理員輸入不存在的 email 關鍵字並送出搜尋
    Then 系統顯示「查無資料」提示

  Scenario: 管理員查看使用者詳情
    Given 管理員在使用者管理列表頁面
    When 管理員點擊某筆使用者
    Then 系統顯示該使用者的姓名、email、建立時間與訂單數量

  Scenario: 管理員停用使用者帳號
    Given 管理員在使用者詳情頁面，該帳號目前為啟用狀態
    When 管理員點擊「停用」按鈕並在確認對話框中確認
    Then 系統將帳號狀態更新為停用，並顯示成功訊息

  Scenario: 管理員啟用使用者帳號
    Given 管理員在使用者詳情頁面，該帳號目前為停用狀態
    When 管理員點擊「啟用」按鈕並在確認對話框中確認
    Then 系統將帳號狀態更新為啟用，並顯示成功訊息

  Scenario: 管理員取消停用操作
    Given 管理員點擊「停用」按鈕，確認對話框已開啟
    When 管理員點擊「取消」
    Then 系統關閉對話框，帳號狀態不變
```
