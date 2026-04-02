# Eval 執行記錄：eval-5-apply-fresh-start（舊版 skill）

## Skill 版本
使用舊版 apply skill：`skill-snapshot-apply-old/SKILL.md`

---

## 前置確認

### 根路徑識別
- 使用者指定路徑：`eval-5-apply-fresh-start/docs/propose/user-management/`
- 路徑無 `frontend/` 或 `backend/` 前綴
- 舊版 skill 規則：未指定前綴時主動詢問「請問此功能為前端還是後端，或是不區分？」
- 本次 eval 選擇「不區分」，直接使用 `docs/propose/user-management/`

### 文檔確認
確認三份文檔存在：
- `eval-5-apply-fresh-start/docs/propose/user-management/01-flow.md` ✓
- `eval-5-apply-fresh-start/docs/propose/user-management/02-gherkin.md` ✓
- `eval-5-apply-fresh-start/docs/propose/user-management/03-tasks.md` ✓

---

## 步驟 1：載入 Context

### 01-flow.md 重點
- 使用者列表：GET /api/admin/users，支援 email 搜尋
- 使用者詳情：GET /api/admin/users/:id
- 停用/啟用：PATCH /api/admin/users/:id/status，成功更新畫面，失敗顯示錯誤訊息

### 02-gherkin.md 重點
- Scenario：管理員查看使用者列表（顯示姓名、email、狀態、建立時間）
- Scenario：管理員依 email 搜尋使用者
- Scenario：管理員查看使用者詳情（姓名、email、建立時間、訂單數量）
- Scenario：管理員停用使用者帳號（狀態更新，頁面顯示最新狀態）
- Scenario：停用操作失敗（顯示錯誤訊息，帳號狀態不變）

### 03-tasks.md 初始狀態
- [ ] T1：未開始
- [ ] T2：未開始（依賴 T1）
- [ ] T3：未開始（依賴 T2）

---

## 步驟 2：執行任務

### T1：建立 UserList 頁面

**宣告任務：** T1: 建立 UserList 頁面，串接 GET /api/admin/users API，支援 email 搜尋

**依賴確認：** T1 無依賴，直接執行。

**模擬實作：**
- 建立 `src/pages/UserList.tsx`
- 頁面載入時呼叫 GET /api/admin/users 取得列表
- 列表欄位：姓名、email、狀態、建立時間
- 搜尋框：有輸入時呼叫 GET /api/admin/users?email=<keyword>，無輸入顯示全部

**更新 checkbox：** `[ ]` → `[x]`

**Commit Message：**
```
feature: 建立 UserList 頁面並串接 GET /api/admin/users API，支援 email 搜尋篩選
```

**模擬 Code Review Subagent：**
- 規格文檔路徑：`docs/propose/user-management/`
- 使用 `code-reviewer` skill 審查
- 審查結果：通過（模擬）

**更新 checkbox：** `[x]` → `[x][cr]`（使用 Edit tool 立即更新）

**T1 完成。**

---

### T2：建立 UserDetail 頁面

**宣告任務：** T2: 建立 UserDetail 頁面，顯示姓名、email、建立時間、訂單數量

**依賴確認：** T2 依賴 T1，T1 狀態為 `[x][cr]`，已完成，可繼續。

**模擬實作：**
- 建立 `src/pages/UserDetail.tsx`
- 點擊列表使用者後呼叫 GET /api/admin/users/:id
- 顯示欄位：姓名、email、建立時間、訂單數量

**更新 checkbox：** `[ ]` → `[x]`

**Commit Message：**
```
feature: 建立 UserDetail 頁面，顯示使用者詳情（姓名、email、建立時間、訂單數量）
```

**模擬 Code Review Subagent：**
- 規格文檔路徑：`docs/propose/user-management/`
- 使用 `code-reviewer` skill 審查
- 審查結果：通過（模擬）

**更新 checkbox：** `[x]` → `[x][cr]`（使用 Edit tool 立即更新）

**T2 完成。**

---

### T3：實作停用/啟用使用者功能

**宣告任務：** T3: 實作停用/啟用使用者功能，呼叫 PATCH /api/admin/users/:id/status

**依賴確認：** T3 依賴 T2，T2 狀態為 `[x][cr]`，已完成，可繼續。

**模擬實作：**
- 在 `src/pages/UserDetail.tsx` 中新增停用/啟用按鈕
- 按鈕點擊時呼叫 PATCH /api/admin/users/:id/status
- 成功：更新畫面中的使用者狀態
- 失敗：顯示錯誤訊息，帳號狀態不變

**更新 checkbox：** `[ ]` → `[x]`

**Commit Message：**
```
feature: 實作停用/啟用使用者功能，串接 PATCH /api/admin/users/:id/status
```

**模擬 Code Review Subagent：**
- 規格文檔路徑：`docs/propose/user-management/`
- 使用 `code-reviewer` skill 審查
- 審查結果：通過（模擬）

**更新 checkbox：** `[x]` → `[x][cr]`（使用 Edit tool 立即更新）

**T3 完成。**

---

## 最終結果

所有任務已完成：

| 任務 | 狀態 |
|------|------|
| T1: 建立 UserList 頁面 | [x][cr] |
| T2: 建立 UserDetail 頁面 | [x][cr] |
| T3: 實作停用/啟用功能 | [x][cr] |

**最終 03-tasks.md 狀態：**
```
- [x][cr] T1: 建立 UserList 頁面，串接 GET /api/admin/users API，支援 email 搜尋（影響：`src/pages/UserList.tsx`）
- [x][cr] T2: 建立 UserDetail 頁面，顯示姓名、email、建立時間、訂單數量（影響：`src/pages/UserDetail.tsx`）（依賴 T1）
- [x][cr] T3: 實作停用/啟用使用者功能，呼叫 PATCH /api/admin/users/:id/status（影響：`src/pages/UserDetail.tsx`）（依賴 T2）
```

## 舊版 Skill 行為觀察

1. **詢問前端/後端：** 路徑無前綴時，舊版 skill 會主動詢問「前端還是後端，或是不區分？」。本次選擇「不區分」繼續。
2. **每任務完成後立即 code review：** 每個任務完成（更新為 `[x]`）後，立即開啟 subagent 執行 code review，再用 Edit tool 更新為 `[x][cr]`。
3. **依賴關係：** T2 等待 T1 完成後才執行，T3 等待 T2 完成後才執行。
4. **checkbox 更新順序：** `[ ]` → 實作完成 → `[x]` → code review 完成 → `[x][cr]`（兩步驟分開執行）。
