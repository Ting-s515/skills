# 電商後台管理系統規格

## 已完成

- [x] T1: 建立 UserList 頁面，串接 GET /api/admin/users API，支援 email 搜尋
- [x] T2: 建立 UserDetail 頁面，顯示姓名、email、建立時間、訂單數量
- [x] T3: 實作停用/啟用使用者功能，呼叫 PATCH /api/admin/users/:id/status

## 使用者管理

管理員可以在後台查看所有使用者列表，支援依照 email 搜尋。
每筆使用者可點擊查看詳情，包含姓名、email、建立時間、訂單數量。
管理員可以停用/啟用使用者帳號。

> propose: `docs/propose/user-management/`
