```gherkin
Feature: 商品庫存歸零時前台購買按鈕狀態同步
  前台商品頁面應依據最新庫存狀態，正確顯示或禁用購買按鈕

  Scenario: 頁面載入時庫存充足，購買按鈕為可點擊
    Given 商品庫存數量大於 0
    When 使用者開啟商品頁面
    Then 購買按鈕為 enabled 狀態

  Scenario: 頁面載入時庫存為零，購買按鈕為禁用
    Given 商品庫存數量為 0
    When 使用者開啟商品頁面
    Then 購買按鈕為 disabled 狀態
    And 顯示已售完提示

  Scenario: 使用者停留頁面期間庫存歸零，按鈕即時更新
    Given 使用者已開啟商品頁面且庫存大於 0
    When 商品庫存被更新為 0
    Then 前台購買按鈕切換為 disabled

  Scenario: 使用者停留頁面期間庫存從零恢復，按鈕即時更新
    Given 使用者已開啟商品頁面且庫存為 0
    When 商品庫存被補充為大於 0
    Then 前台購買按鈕切換為 enabled

  Scenario: 庫存欄位為 null，按鈕保守顯示為禁用
    Given 商品庫存欄位為 null
    When 使用者開啟商品頁面
    Then 購買按鈕為 disabled 狀態

  Scenario: 即時推播失敗時，前台 polling 補償
    Given 即時推播服務不可用
    And 商品庫存已歸零
    When 前台 polling 機制觸發查詢
    Then 前台更新購買按鈕為 disabled

  Scenario: 使用者在庫存歸零後仍嘗試下單，後端阻擋
    Given 使用者停留頁面時庫存歸零，但 UI 尚未更新
    When 使用者送出購買請求
    Then 後端驗證庫存不足
    And 回傳庫存不足錯誤給前台
```
