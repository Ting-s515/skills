# 功能流程：訂單管理

## 功能概述

管理者可在後台查看所有訂單列表，並依訂單狀態篩選，每筆訂單顯示關鍵資訊欄位。

## 流程說明

### 比對條件

| 欄位 | 說明 |
|------|------|
| `status`（可選） | 篩選條件，允許值：`pending_payment`、`paid`、`shipped`、`completed` |

---

### 查看訂單列表（含篩選）

1. 管理者發送查看訂單列表請求，請求參數可選帶入 `status` query string。

2. **未帶入 `status` 參數時（查看全部訂單）：**
   查詢資料庫中所有訂單，不套用狀態篩選條件。

3. **帶入 `status` 參數時：**

   - **`status` 為合法值（`pending_payment` / `paid` / `shipped` / `completed`）：**
     查詢資料庫，篩選出該狀態的訂單。

   - **`status` 為非法值（不在允許值清單內）：**
     回傳驗證錯誤，HTTP 400，訊息：「status 參數不合法」，結束流程。

4. 查詢結果依建立時間（`createdAt`）由新到舊排序。

5. 每筆訂單回傳以下欄位：
   - `orderId`：訂單編號
   - `createdAt`：建立時間
   - `customerName`：客戶名稱
   - `totalAmount`：總金額
   - `status`：目前狀態

6. **查詢結果為空時（無符合條件訂單）：**
   回傳空陣列 `[]`，HTTP 200，不視為錯誤。

7. **查詢成功：**
   回傳訂單陣列，HTTP 200。

8. **資料庫查詢異常：**
   回傳系統錯誤，HTTP 500，結束流程。

---

### 邊界條件（Out of Scope 說明）

| 情境 | 處理方式 |
|------|----------|
| 管理者未登入 / 無權限 | Out of Scope，由 Auth middleware 處理，不在本功能流程內 |
| 分頁（pagination） | Out of Scope，目前規格未要求分頁，回傳全部符合訂單 |
| 多重 status 篩選 | Out of Scope，目前僅支援單一 status 篩選 |
| 依其他欄位排序 | Out of Scope，固定依 `createdAt` 由新到舊 |
