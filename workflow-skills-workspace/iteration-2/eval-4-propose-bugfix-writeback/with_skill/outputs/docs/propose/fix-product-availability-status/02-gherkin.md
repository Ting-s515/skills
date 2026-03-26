```gherkin
Feature: 商品庫存狀態與購買按鈕同步
  商品庫存歸零時，前台購買按鈕應即時反映為不可購買，防止買家對無庫存商品下單

  Scenario: 庫存充足時，購買按鈕可點擊
    Given 商品庫存數量大於 0
    When 買家瀏覽商品頁
    Then 購買按鈕為啟用狀態

  Scenario: 庫存歸零時，購買按鈕禁用
    Given 商品庫存原為 x 件
    When 庫存更新後數量歸零
    Then 前台商品頁的購買按鈕更新為禁用狀態

  Scenario: 庫存為 NULL 時，購買按鈕禁用
    Given 商品的庫存數量為 NULL
    When 買家瀏覽商品頁
    Then 購買按鈕為禁用狀態

  Scenario: 買家繞過前端限制對無庫存商品下單，後端拒絕
    Given 商品庫存為 0
    And 前台按鈕顯示禁用
    When 買家透過非正常途徑送出購買請求
    Then 後端拒絕此下單請求
    And 回傳庫存不足錯誤

  Scenario: 庫存從零恢復補貨，購買按鈕重新啟用
    Given 商品庫存為 0，購買按鈕禁用
    When 後台補貨後庫存更新為大於 0
    Then 前台商品頁的購買按鈕恢復為啟用狀態
```
