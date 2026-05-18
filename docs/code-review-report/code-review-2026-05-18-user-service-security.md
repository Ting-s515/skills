# Code Review 紀錄 — 2026-05-18（第 1 輪）

## 📋 Code Review 摘要

**審查範圍：** `src/user-service.ts` 中 `searchUsers` 與 `getUserById` 的資料庫查詢實作  
**整體評估：** ❌ 不符合可合併標準，需先修正 SQL Injection 風險

---

### 🔴 必須修正（Critical）

#### 問題 1：`searchUsers` 直接拼接 `term` 造成 SQL Injection
- **檔案：** `src/user-service.ts:5`
- **問題：** `term` 由外部輸入後直接嵌入 SQL 字串，攻擊者可透過特殊字元改寫查詢條件。
- **影響：** 可能造成任意資料查詢、資料外洩，甚至在資料庫權限過大時導致破壞性操作。
- **建議修正：**
  ```typescript
  export async function searchUsers(term: string) {
    const keyword = `%${term}%`;
    const result = await pool.query(
      'SELECT id, name, email FROM users WHERE name LIKE $1 OR email LIKE $1',
      [keyword],
    );
    return result.rows;
  }
  ```

#### 問題 2：`getUserById` 直接拼接 `id` 造成 SQL Injection
- **檔案：** `src/user-service.ts:11`
- **問題：** `id` 雖然型別標示為 `number`，但 TypeScript 型別不等於執行期驗證，直接嵌入 SQL 字串仍有注入風險。
- **影響：** 若呼叫邊界傳入未驗證資料，可能被注入額外 SQL 條件，造成越權查詢或資料外洩。
- **建議修正：**
  ```typescript
  export async function getUserById(id: number) {
    const result = await pool.query(
      'SELECT id, name, email FROM users WHERE id = $1',
      [id],
    );
    return result.rows[0] ?? null;
  }
  ```

---

### 🟠 建議改善（Warning）

#### 問題 1：`getUserById` 使用 `SELECT *` 擴大資料暴露面
- **檔案：** `src/user-service.ts:11`
- **問題：** 新增實作回傳 `SELECT *`，與 `searchUsers` 明確選取 `id, name, email` 的做法不一致。
- **影響：** 若 `users` 表包含密碼雜湊、權限旗標或內部欄位，可能讓上層呼叫者取得非預期資料。
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
- **問題：** `// TODO: 之後要加分頁功能` 沒有對應 issue、任務編號或實作時程。
- **影響：** 若進入正式實作，這類註解容易長期滯留，後續維護者難以判斷是否仍有效。
- **建議：** 若目前仍在開發階段可暫時保留；若準備合併，建議補上追蹤編號或移到需求管理工具。

#### 問題 2：保留被註解掉的舊版 `findUser` 實作
- **檔案：** `src/user-service.ts:15`
- **問題：** 被註解掉的函式屬於 dead code as comments，且查詢欄位與新版搜尋邏輯不同，容易造成維護混淆。
- **影響：** 若進入正式實作，後續讀者可能誤以為舊版邏輯仍是可參考或待恢復的設計。
- **建議：** 若只是備查，應依賴 git history；若仍有保留理由，建議改成明確任務或文件說明。
