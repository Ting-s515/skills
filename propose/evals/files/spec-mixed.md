# 後台管理系統規格

## 已完成

| 功能 | 資料夾 |
| --- | --- |
| 使用者認證 | `backend/docs/propose/user-auth/` |
| 權限管理 | `backend/docs/propose/permission/` |

---

## 商品管理

管理者可以新增和編輯商品資訊（名稱、售價、庫存）。

> propose: `backend/docs/propose/product-management/`

## 訂單管理

管理者可以查看訂單列表，依狀態篩選，更新訂單狀態。

> propose: `backend/docs/propose/order-management/`

## 報表匯出

管理者可以匯出銷售報表（Excel、CSV 格式），可選擇日期區間與商品類別篩選。

## bug fix list

1. [quick-fix] 登入頁面 Enter 鍵無法送出表單
2. [propose] 並發下單時庫存扣減可能出現 race condition 導致超賣
