# 驗收條件：使用者管理

## Feature: 使用者列表

```gherkin
Feature: 使用者列表查詢
  作為管理員
  我希望能查看所有使用者列表並依 email 搜尋
  以便管理系統使用者

  Scenario: 進入使用者管理頁面，顯示所有使用者
    Given 管理員已登入後台
    When 管理員點擊側邊欄「使用者管理」
    Then 系統顯示所有使用者列表
    And 列表包含 email、姓名、帳號狀態、建立時間、訂單數量欄位
    And 列表依建立時間降序排列

  Scenario: 依 email 關鍵字搜尋使用者 — 有結果
    Given 管理員在使用者管理頁面
    When 管理員在搜尋框輸入 email 關鍵字「test」
    Then 系統顯示所有 email 包含「test」的使用者（不區分大小寫）

  Scenario: 依 email 關鍵字搜尋使用者 — 無結果
    Given 管理員在使用者管理頁面
    When 管理員在搜尋框輸入不存在的 email 關鍵字
    Then 系統顯示「查無符合使用者」提示
    And 列表為空

  Scenario: 清空搜尋框還原列表
    Given 管理員已在搜尋框輸入關鍵字並看到篩選結果
    When 管理員清空搜尋框
    Then 系統還原顯示所有使用者列表
```

## Feature: 使用者詳情

```gherkin
Feature: 查看使用者詳情
  作為管理員
  我希望能查看使用者的詳細資訊
  以便了解使用者的帳號與訂單狀況

  Scenario: 點擊使用者查看詳情
    Given 管理員在使用者管理列表頁
    When 管理員點擊某一筆使用者
    Then 系統顯示該使用者的詳情頁
    And 詳情頁顯示姓名、email、建立時間、訂單數量

  Scenario: 使用者不存在時查看詳情
    Given 管理員嘗試開啟已刪除使用者的詳情頁
    When 系統嘗試載入該使用者資料
    Then 系統顯示錯誤提示
    And 提供返回使用者列表的入口
```

## Feature: 停用與啟用帳號

```gherkin
Feature: 停用使用者帳號
  作為管理員
  我希望能停用違規或異常的使用者帳號
  以便保護系統安全

  Scenario: 管理員成功停用使用者帳號
    Given 管理員在使用者列表或詳情頁
    And 目標使用者帳號狀態為「啟用中」
    When 管理員點擊「停用」按鈕
    Then 系統顯示確認對話框「確定要停用此帳號嗎？」
    When 管理員點擊確認
    Then 系統呼叫 API 執行停用
    And 帳號狀態更新為「已停用」
    And 列表即時反映最新狀態

  Scenario: 管理員取消停用操作
    Given 管理員點擊「停用」按鈕後系統顯示確認對話框
    When 管理員點擊取消
    Then 對話框關閉
    And 帳號狀態維持不變

  Scenario: 停用 API 呼叫失敗
    Given 管理員確認停用操作
    When API 回傳錯誤
    Then 系統顯示錯誤提示
    And 前端帳號狀態維持原狀

  Scenario: 管理員成功啟用已停用帳號
    Given 管理員在使用者列表或詳情頁
    And 目標使用者帳號狀態為「已停用」
    When 管理員點擊「啟用」按鈕
    Then 系統顯示確認對話框「確定要啟用此帳號嗎？」
    When 管理員點擊確認
    Then 系統呼叫 API 執行啟用
    And 帳號狀態更新為「啟用中」
    And 列表即時反映最新狀態

  Scenario: 管理員權限不足時嘗試停用帳號
    Given 當前管理員帳號無停用/啟用權限
    When 管理員點擊「停用」或「啟用」按鈕並確認
    Then 系統顯示「權限不足」錯誤提示
    And 帳號狀態維持不變
```
