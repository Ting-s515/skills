# 驗收條件：使用者管理

## Feature: 使用者列表

### Scenario: 管理員查看使用者列表
```gherkin
Given 管理員已登入後台
When 管理員進入「使用者管理」頁面
Then 系統顯示所有使用者列表
And 列表包含欄位：姓名、email、建立時間、帳號狀態
And 列表依建立時間降序排列
```

## Feature: 搜尋使用者

### Scenario: 依 email 搜尋使用者（有結果）
```gherkin
Given 管理員在使用者列表頁面
When 管理員在搜尋欄輸入 email 關鍵字 "test"
Then 系統顯示 email 包含 "test" 的使用者列表
```

### Scenario: 依 email 搜尋使用者（無結果）
```gherkin
Given 管理員在使用者列表頁面
When 管理員在搜尋欄輸入 email 關鍵字 "nonexistent@xxx.com"
Then 系統顯示「查無使用者」提示
```

### Scenario: 清空搜尋欄恢復完整列表
```gherkin
Given 管理員已在搜尋欄輸入關鍵字並看到過濾結果
When 管理員清空搜尋欄
Then 系統恢復顯示全部使用者
```

## Feature: 使用者詳情

### Scenario: 查看使用者詳情
```gherkin
Given 管理員在使用者列表頁面
When 管理員點擊某筆使用者
Then 系統跳轉至詳情頁面
And 頁面顯示：姓名、email、建立時間、訂單數量、帳號狀態
```

## Feature: 停用 / 啟用帳號

### Scenario: 成功停用使用者帳號
```gherkin
Given 管理員查看一位狀態為「啟用」的使用者
When 管理員點擊「停用」按鈕
And 管理員在確認對話框中確認操作
Then 系統送出 API 請求更新帳號狀態為停用
And 頁面顯示帳號狀態已變更為「停用」
And 顯示操作成功訊息
```

### Scenario: 成功啟用使用者帳號
```gherkin
Given 管理員查看一位狀態為「停用」的使用者
When 管理員點擊「啟用」按鈕
And 管理員在確認對話框中確認操作
Then 系統送出 API 請求更新帳號狀態為啟用
And 頁面顯示帳號狀態已變更為「啟用」
And 顯示操作成功訊息
```

### Scenario: API 失敗時不改變狀態
```gherkin
Given 管理員確認停用某位使用者帳號
When API 回傳錯誤
Then 系統顯示錯誤訊息
And 帳號狀態維持不變
```

### Scenario: 管理員取消停用操作
```gherkin
Given 管理員點擊「停用」按鈕後出現確認對話框
When 管理員點擊「取消」
Then 對話框關閉
And 帳號狀態不變
```
