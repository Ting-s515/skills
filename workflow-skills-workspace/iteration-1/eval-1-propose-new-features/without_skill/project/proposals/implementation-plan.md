# 電商後台管理系統 — 功能實作規劃

## 概覽

根據 `spec.md`，本次需實作兩大模組：**使用者管理** 與 **商品管理**。

---

## 功能清單

### 模組 1：使用者管理

| 功能 | 描述 |
|------|------|
| 使用者列表 | 顯示所有使用者，支援依 email 搜尋 |
| 使用者詳情 | 顯示姓名、email、建立時間、訂單數量 |
| 停用 / 啟用帳號 | 管理員可切換使用者帳號狀態 |

### 模組 2：商品管理

| 功能 | 描述 |
|------|------|
| 新增商品 | 填寫名稱、價格、庫存數量、商品描述 |
| 商品列表 | 支援依名稱篩選 + 依價格排序 |
| 編輯商品 | 修改商品資料 |
| 下架商品 | 將商品標記為下架狀態 |

---

## 建議技術方案

### 資料結構

**使用者（User）**
```ts
interface User {
  id: string
  name: string
  email: string
  createdAt: Date
  orderCount: number
  status: 'active' | 'disabled'
}
```

**商品（Product）**
```ts
interface Product {
  id: string
  name: string
  price: number
  stock: number
  description: string
  status: 'active' | 'inactive'
}
```

---

## 建議實作順序

### Phase 1：使用者管理

1. **使用者列表頁**
   - API：`GET /api/users?search={email}`
   - 元件：`UserListPage`、`UserTable`、`UserSearchBar`
   - 功能：分頁、email 搜尋

2. **使用者詳情頁**
   - API：`GET /api/users/:id`
   - 元件：`UserDetailPage`、`UserDetailCard`
   - 顯示欄位：姓名、email、建立時間、訂單數量

3. **停用 / 啟用帳號**
   - API：`PATCH /api/users/:id/status`
   - 操作：在詳情頁或列表行內提供切換按鈕
   - 需有確認提示（避免誤操作）

### Phase 2：商品管理

4. **商品列表頁**
   - API：`GET /api/products?name={keyword}&sortBy=price&order=asc|desc`
   - 元件：`ProductListPage`、`ProductTable`、`ProductFilterBar`
   - 功能：名稱篩選、價格排序

5. **新增商品**
   - API：`POST /api/products`
   - 元件：`ProductFormModal` 或 `ProductCreatePage`
   - 欄位：名稱（必填）、價格（必填，正整數）、庫存數量（必填，非負整數）、商品描述

6. **編輯商品**
   - API：`PUT /api/products/:id`
   - 復用 `ProductFormModal`，預填現有資料

7. **下架商品**
   - API：`PATCH /api/products/:id/status`
   - 操作：在列表行內提供下架按鈕，需有確認提示

---

## API 端點彙整

| Method | Path | 描述 |
|--------|------|------|
| GET | `/api/users` | 取得使用者列表（支援 email 搜尋） |
| GET | `/api/users/:id` | 取得使用者詳情 |
| PATCH | `/api/users/:id/status` | 切換使用者帳號狀態 |
| GET | `/api/products` | 取得商品列表（支援篩選 + 排序） |
| POST | `/api/products` | 新增商品 |
| PUT | `/api/products/:id` | 編輯商品 |
| PATCH | `/api/products/:id/status` | 下架商品 |

---

## 注意事項

- 停用 / 下架操作需有確認對話框，防止誤操作
- 表單欄位需做前端驗證（必填、數字格式、正負值）
- 商品價格與庫存數量欄位需驗證為有效數字
- 列表頁建議實作分頁，避免資料量大時效能問題
