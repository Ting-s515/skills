# 功能流程：商品搜尋特殊字元 SQL Escape 修正

## 功能概述
修正後端商品搜尋功能，在 SQL LIKE 查詢前對輸入字串做特殊字元 escape（%、_、\），防止查詢 500 錯誤與 SQL injection 風險。

## 流程說明

### 處理流程

1. 接收搜尋請求，取得 `keyword`
2. **`keyword` 為 null 或空字串時：** 回傳全部商品列表，跳至步驟 5
3. 對 `keyword` 執行特殊字元 escape 處理：
   - 先將 `\` 替換為 `\\`
   - 再將 `%` 替換為 `\%`
   - 再將 `_` 替換為 `\_`
4. 使用 escaped keyword 組裝 SQL LIKE 查詢：`LIKE '%{escaped_keyword}%' ESCAPE '\'`
5. 執行查詢，回傳符合條件的商品列表（結果為空時回傳 [] 與 200）

### 邊界條件
- `keyword` 僅包含特殊字元：escape 後正常查詢，結果可能為空陣列
- 資料庫查詢失敗：回傳 500
