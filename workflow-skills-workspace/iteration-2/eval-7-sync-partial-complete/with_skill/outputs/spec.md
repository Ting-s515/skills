# 電商後台管理系統規格

## 已完成

| 功能       | 資料夾                               |
| ---------- | ------------------------------------ |
| 使用者管理 | `docs/propose/user-management/` |
| Bug Fix：通知信修復 | `docs/propose/notification-fix/` |

---

## 使用者管理

管理員可以在後台查看所有使用者列表，支援依照 email 搜尋。
每筆使用者可點擊查看詳情，包含姓名、email、建立時間、訂單數量。
管理員可以停用/啟用使用者帳號。

> propose: `docs/propose/user-management/`

## 商品管理

管理員可以新增商品，填寫名稱、價格、庫存數量、商品描述。
商品列表支援依名稱篩選，以及依價格排序。
每筆商品可編輯或下架。

> propose: `docs/propose/product-management/`

## Bug Fix：通知信修復

訂單狀態更新後，通知信未正確寄送給買家，需重新設計通知觸發流程。

> propose: `docs/propose/notification-fix/`
