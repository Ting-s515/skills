```gherkin
Feature: 使用者管理
  管理員在後台管理系統中查看、搜尋使用者列表，查看個別使用者詳情，以及停用或啟用使用者帳號

  Scenario: 查看完整使用者列表
    Given 管理員已登入後台
    And 系統中存在若干使用者資料
    When 管理員進入使用者管理頁面
    Then 顯示所有使用者列表

  Scenario: 依 email 搜尋使用者
    Given 管理員已進入使用者管理頁面
    When 管理員輸入 email 關鍵字進行搜尋
    Then 顯示 email 符合關鍵字的使用者列表

  Scenario: 搜尋結果為空
    Given 管理員已進入使用者管理頁面
    When 管理員輸入不存在的 email 關鍵字進行搜尋
    Then 顯示查無符合條件的使用者提示

  Scenario: 查看使用者詳情
    Given 管理員已在使用者列表頁面
    When 管理員點擊某筆使用者
    Then 顯示該使用者的姓名、email、建立時間與訂單數量

  Scenario: 查看不存在的使用者詳情
    Given 管理員已在使用者列表頁面
    When 管理員存取不存在的使用者 id
    Then 返回使用者列表頁面
    And 顯示錯誤提示

  Scenario: 停用啟用中的使用者帳號
    Given 管理員已查看某位狀態為「啟用」的使用者
    When 管理員執行停用操作
    Then 該使用者帳號狀態更新為「停用」

  Scenario: 啟用停用中的使用者帳號
    Given 管理員已查看某位狀態為「停用」的使用者
    When 管理員執行啟用操作
    Then 該使用者帳號狀態更新為「啟用」

  Scenario: 停用/啟用操作失敗
    Given 管理員嘗試對某位使用者執行停用或啟用操作
    When 資料庫操作失敗
    Then 使用者帳號狀態不變
    And 顯示錯誤提示

  Scenario: 未登入管理員嘗試存取後台
    Given 使用者未登入
    When 使用者嘗試進入使用者管理頁面
    Then 導向登入頁面

  Scenario: 無管理員權限的使用者嘗試存取後台
    Given 使用者已登入但身份非管理員
    When 使用者嘗試進入使用者管理頁面
    Then 返回 403 無權限錯誤
```
