# 功能流程：訂單狀態批次更新 Transaction 保護

## 功能概述
為訂單狀態批次更新操作加入 transaction 保護，確保部分失敗時所有已更新訂單能一併 rollback，維持資料一致性。

## 流程說明

### 比對條件
- 輸入：訂單 ID 清單（`order_ids[]`）與目標狀態（`target_status`）

### 處理流程

1. 接收批次更新請求，取得 `order_ids[]` 與 `target_status`
2. 驗證輸入
   - **`order_ids` 為空或 null 時：** 回傳 400，訊息「訂單清單不可為空」，結束流程
   - **`target_status` 為無效值時：** 回傳 400，訊息「無效的訂單狀態」，結束流程
3. 開啟資料庫 transaction
4. 遍歷 `order_ids[]` 中每一筆訂單 ID：
   - **訂單不存在：** rollback，回傳 404，訊息「訂單 {id} 不存在」，結束流程
   - **狀態不允許轉換：** rollback，回傳 422，訊息「訂單 {id} 狀態不可轉換」，結束流程
   - **更新失敗：** rollback，回傳 500，結束流程
5. 所有訂單更新成功後，commit transaction，回傳 200 與更新成功筆數

### 邊界條件
- **`order_ids` 包含重複 ID：** 自動去重，每筆只更新一次
- **Transaction timeout：** 自動 rollback，回傳 503
