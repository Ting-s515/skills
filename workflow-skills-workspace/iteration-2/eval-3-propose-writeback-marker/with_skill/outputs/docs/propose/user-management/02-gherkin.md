# Gherkin 驗收條件：使用者管理

```gherkin
Feature: 使用者管理
  管理員可在後台查看與管理所有使用者帳號，包含列表瀏覽、email 搜尋、詳情查看及帳號狀態控制

  Scenario: 管理員查看使用者列表
    Given 系統中存在若干使用者資料
    And 管理員已登入後台
    When 管理員進入使用者管理頁面
    Then 系統顯示所有使用者的列表

  Scenario: 管理員以 email 搜尋使用者
    Given 系統中存在若干使用者資料
    And 管理員已登入後台且在使用者管理頁面
    When 管理員輸入 email 關鍵字並搜尋
    Then 系統只顯示 email 符合關鍵字的使用者

  Scenario: 搜尋結果為空
    Given 系統中無符合搜尋條件的使用者
    And 管理員已登入後台且在使用者管理頁面
    When 管理員輸入 email 關鍵字並搜尋
    Then 系統顯示「目前無使用者資料」提示

  Scenario: 管理員查看使用者詳情
    Given 系統中存在某使用者
    And 管理員已登入後台且在使用者管理頁面
    When 管理員點擊該使用者
    Then 系統顯示該使用者的姓名、email、建立時間、訂單數量

  Scenario: 查看已不存在的使用者詳情
    Given 某使用者已從系統中刪除
    And 管理員已登入後台
    When 管理員嘗試存取該使用者的詳情頁
    Then 系統回傳錯誤提示
    And 導回使用者列表頁

  Scenario: 管理員停用使用者帳號
    Given 某使用者帳號狀態為啟用
    And 管理員已登入後台
    When 管理員對該使用者執行停用操作
    Then 該使用者帳號狀態更新為停用

  Scenario: 管理員啟用使用者帳號
    Given 某使用者帳號狀態為停用
    And 管理員已登入後台
    When 管理員對該使用者執行啟用操作
    Then 該使用者帳號狀態更新為啟用

  Scenario: 未登入者嘗試存取使用者管理
    Given 使用者未登入後台
    When 使用者嘗試存取使用者管理頁面
    Then 系統拒絕存取
    And 導向登入頁
```
