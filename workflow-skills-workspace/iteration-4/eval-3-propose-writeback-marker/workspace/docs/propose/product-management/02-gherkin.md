# 驗收條件：商品管理

## Feature: 商品列表

### Scenario: 管理員查看商品列表
```gherkin
Given 管理員已登入後台
When 管理員進入「商品管理」頁面
Then 系統顯示所有商品列表
And 列表包含欄位：名稱、價格、庫存數量、狀態
```

## Feature: 篩選與排序商品

### Scenario: 依名稱篩選商品（有結果）
```gherkin
Given 管理員在商品列表頁面
When 管理員在搜尋欄輸入商品名稱關鍵字 "手機"
Then 系統顯示名稱包含 "手機" 的商品列表
```

### Scenario: 依名稱篩選商品（無結果）
```gherkin
Given 管理員在商品列表頁面
When 管理員在搜尋欄輸入 "zzzzunknown"
Then 系統顯示「查無商品」提示
```

### Scenario: 依價格由低到高排序
```gherkin
Given 管理員在商品列表頁面
When 管理員第一次點擊「依價格排序」按鈕
Then 商品列表依價格由低到高排列
```

### Scenario: 依價格由高到低排序
```gherkin
Given 管理員已點擊一次「依價格排序」（目前為低到高）
When 管理員再次點擊「依價格排序」按鈕
Then 商品列表依價格由高到低排列
```

## Feature: 新增商品

### Scenario: 成功新增商品
```gherkin
Given 管理員點擊「新增商品」並看到表單
When 管理員填寫名稱 "藍牙耳機"、價格 "1200"、庫存數量 "50"
And 管理員送出表單
Then 系統新增商品成功
And 列表加入新商品「藍牙耳機」
And 顯示操作成功訊息
```

### Scenario: 必填欄位未填時無法送出
```gherkin
Given 管理員開啟新增商品表單
When 管理員未填名稱直接送出
Then 系統顯示欄位必填錯誤提示
And 表單不送出
```

### Scenario: API 失敗時表單維持開啟
```gherkin
Given 管理員填寫完整表單並送出
When API 回傳錯誤
Then 系統顯示錯誤訊息
And 表單不關閉
```

## Feature: 編輯商品

### Scenario: 成功編輯商品
```gherkin
Given 管理員點擊某筆商品的「編輯」按鈕
When 管理員修改價格為 "1500" 並送出
Then 系統更新商品資料
And 列表顯示更新後的價格
And 顯示操作成功訊息
```

## Feature: 下架商品

### Scenario: 成功下架商品
```gherkin
Given 管理員在商品列表頁面
When 管理員點擊某筆商品的「下架」按鈕
And 管理員在確認對話框中確認操作
Then 系統送出 API 請求將商品狀態改為下架
And 列表更新該商品狀態
And 顯示操作成功訊息
```

### Scenario: 取消下架操作
```gherkin
Given 管理員點擊「下架」按鈕後出現確認對話框
When 管理員點擊「取消」
Then 對話框關閉
And 商品狀態不變
```
