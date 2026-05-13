# 驗收條件：使用者管理

```gherkin
Feature: 使用者管理

  Scenario: 管理員查看使用者列表
    Given 管理員已登入後台
    When 管理員進入使用者管理頁面
    Then 系統顯示所有使用者列表，包含姓名、email、狀態、建立時間

  Scenario: 管理員依 email 搜尋使用者
    Given 管理員在使用者列表頁面
    When 管理員在搜尋框輸入 email 關鍵字
    Then 系統篩選並只顯示符合的使用者

  Scenario: 管理員查看使用者詳情
    Given 管理員在使用者列表頁面
    When 管理員點擊某使用者
    Then 系統顯示該使用者的姓名、email、建立時間、訂單數量

  Scenario: 管理員停用使用者帳號
    Given 管理員在使用者詳情頁，使用者狀態為啟用
    When 管理員點擊「停用」按鈕
    Then 系統更新使用者狀態為停用，頁面顯示最新狀態

  Scenario: 停用操作失敗
    Given 管理員點擊「停用」按鈕
    When API 回傳錯誤
    Then 系統顯示錯誤訊息，帳號狀態不變
```
