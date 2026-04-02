# 功能流程：商品庫存歸零時前台購買按鈕狀態更新

## 功能概述

商品庫存數量歸零時，前台商品頁的購買按鈕應即時反映庫存狀態，顯示為不可購買（停用或隱藏），防止買家對無庫存商品下單。

## 流程說明

### 比對條件

- 商品 ID（`product_id`）
- 商品庫存數量（`stock_quantity`）

### 處理流程

#### 後端：庫存更新時同步可購買狀態

1. 庫存數量因訂單成立、人工調整或盤點等原因發生變更

2. 更新 `products` 資料表的 `stock_quantity`

3. 承接第 2 點，計算新的可購買狀態：
   - **`stock_quantity > 0`：** 設定 `is_available = true`
   - **`stock_quantity <= 0`：** 設定 `is_available = false`

4. 更新 `products` 資料表的 `is_available` 欄位

5. 承接第 4 點，觸發快取失效（若商品資料有快取層）：
   - 清除或更新對應 `product_id` 的快取資料

#### 前端：商品頁取得商品資料並渲染按鈕狀態

6. 前台商品頁載入或刷新時，呼叫 API 取得商品資料（含 `is_available` 欄位）

7. 依照 `is_available` 決定按鈕呈現：
   - **`is_available = true`：** 顯示「加入購物車」或「立即購買」按鈕，按鈕可點擊
   - **`is_available = false`：** 顯示「已售完」或「補貨通知」，按鈕禁用（`disabled`）

8. 防止繞過前端限制：
   - 後端 API 在收到購買請求時，再次檢查 `stock_quantity`
   - **`stock_quantity <= 0`：** 拒絕下單，回傳庫存不足錯誤
   - **`stock_quantity > 0`：** 繼續處理下單流程

#### 邊界條件

- `stock_quantity` 為 `NULL`：視為庫存不明，`is_available = false`，按鈕禁用
- 多個訂單同時結帳造成超賣：以資料庫層樂觀鎖或交易（transaction）確保原子性，Out of Scope（超賣防護為獨立議題）
- 後台庫存更新後前台快取尚未失效期間：容忍短暫不一致（最終一致性），快取 TTL 以業務可接受時間為準
