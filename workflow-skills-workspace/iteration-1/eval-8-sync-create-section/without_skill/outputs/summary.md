# 摘要：spec.md 最終內容

## spec.md 最終內容

```markdown
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
```

## 確認結果

- `## 已完成` 區塊：**已建立** (第 3 行)
- 位置：**在頂部**（緊接在 H1 標題之後，位於其他 section 之前）
- 完成項目數量：3 項（T1、T2、T3），均來自 `docs/propose/user-management/03-tasks.md` 中標記為 `[x][cr]` 的任務
