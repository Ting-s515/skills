# 功能流程：並發庫存扣減修正

## 功能概述
修正並發下單時因 race condition 導致庫存扣減不正確、出現超賣的問題，確保庫存扣減為原子操作。

## 流程說明（修正後的正確行為）

### 處理流程

1. 使用者送出下單請求，系統開始處理訂單
2. 對目標商品列取得資料庫層級的 row-level 排他鎖（`SELECT ... FOR UPDATE`）
3. 取得鎖定後讀取目前庫存值 `current_stock`
   - **`current_stock >= quantity`（庫存充足）：**
     - 執行條件式更新：`UPDATE products SET stock = stock - quantity WHERE id = product_id AND stock >= quantity`
     - **影響列數 = 1：** 扣減成功，繼續建立訂單，commit，結束
     - **影響列數 = 0：** rollback，回傳 409 庫存不足，結束
   - **`current_stock < quantity`（庫存不足）：** rollback，回傳 409，結束
4. 訂單建立成功，回傳訂單資訊

### 邊界條件
- 庫存恰等於下單數量：允許扣減，庫存歸零
- 多個並發請求：透過 row-level lock 序列化，後進者若庫存不足回傳 409
- 商品不存在：回傳 404
- 下單數量為 0 或負數：輸入驗證拒絕，回傳 400
