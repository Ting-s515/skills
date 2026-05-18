# Code Review 紀錄 — 2026-05-18（第 1 輪）

## 📋 Code Review 摘要

**審查範圍：** `src/user-service.ts` 的使用者搜尋與依 ID 查詢實作  
**整體評估：** ❌ 不符合規格，需修正

---

### 🔴 必須修正（Critical）

#### 問題 1：`searchUsers` 直接拼接搜尋字串造成 SQL Injection
- **檔案：** `src/user-service.ts:5`
- **問題：** `term` 參數直接插入 SQL 字串，使用者可透過輸入控制 `LIKE` 條件甚至注入額外 SQL。
- **影響：** 可能造成未授權資料讀取、查詢條件繞過，嚴重時可能破壞資料。
- **建議修正：**
  ```typescript
  const query = `
    SELECT id, name, email
    FROM users
    WHERE name LIKE $1 OR email LIKE $1
  `;
  const result = await pool.query(query, [`%${term}%`]);
  ```

#### 問題 2：`getUserById` 直接拼接 `id` 造成 SQL Injection 風險
- **檔案：** `src/user-service.ts:11`
- **問題：** 即使 `id` 型別宣告為 `number`，執行期輸入仍可能來自未驗證外部資料；直接嵌入 SQL 字串不應作為安全邊界。
- **影響：** 若呼叫端傳入未清理資料或型別被繞過，可能導致 SQL Injection 或查詢條件被竄改。
- **建議修正：**
  ```typescript
  const result = await pool.query(
    'SELECT id, name, email FROM users WHERE id = $1',
    [id],
  );
  ```

---

### 🟠 建議改善（Warning）

#### 問題 1：`getUserById` 使用 `SELECT *` 擴大資料外洩面
- **檔案：** `src/user-service.ts:11`
- **問題：** `SELECT *` 會回傳資料表所有欄位，與 `searchUsers` 明確選取 `id, name, email` 的做法不一致。
- **影響：** 若 `users` 表含有密碼雜湊、權限旗標或內部欄位，可能被上層流程意外暴露。
- **建議修正：**
  ```typescript
  const result = await pool.query(
    'SELECT id, name, email FROM users WHERE id = $1',
    [id],
  );
  ```

---

### ⚪ 使用者自行決定（註解類問題）

#### 問題 1：TODO 註解未追蹤
- **檔案：** `src/user-service.ts:3`
- **問題：** `// TODO: 之後要加分頁功能` 沒有對應 issue、任務編號或明確完成條件。
- **影響：** 目前若仍在開發階段可暫留；進入正式實作前，容易讓分頁需求失去追蹤。
- **建議：** 若分頁已列入需求，改連到正式任務；若只是想法，移到需求待辦文件或移除。

#### 問題 2：被註解掉的舊版 `findUser` 函式形成 dead code as comments
- **檔案：** `src/user-service.ts:15`
- **問題：** 舊版實作整段以註解保留，會讓維護者不確定目前是否仍有遷移或回復需求。
- **影響：** 測試或開發階段可短暫保留；正式化前應避免讓歷史程式碼留在主檔案中干擾判讀。
- **建議：** 若仍需追蹤舊行為，改由 git history 或正式遷移任務保存；否則移除註解區塊。
