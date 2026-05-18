# Code Review 紀錄 — 2026-05-18（第 1 輪）

## 📋 Code Review 摘要

**審查範圍：** `src/login.ts` 的 `POST /api/auth/login` API 實作，對照 `docs/specs/login-spec.md` 的登入請求、回應狀態碼與安全規範。  
**整體評估：** ❌ 不符合規格，需修正

---

### 📐 規格符合度

#### ✅ 符合規格的項目
- 缺少必填欄位：實作在 `email` 或 `password` 缺少時回傳 `422 Unprocessable Entity`，符合規格。
- 登入成功回應：實作成功時回傳 `200 OK`，並包含 `{ token, user: { id, email } }`，符合規格。
- JWT 過期時間：實作使用 `{ expiresIn: '7d' }`，符合 token 過期時間為 7 天的規格。
- JWT 密鑰來源：實作從 `process.env.JWT_SECRET` 讀取密鑰，方向符合不可硬編碼的規格。

#### ❌ 不符合或缺漏的項目
- 401 錯誤狀態碼：規格要求使用者不存在與密碼錯誤都回傳 `401 Unauthorized`，但實作分別回傳 `404` 與 `400`。
- 帳號枚舉防護：規格要求使用者不存在與密碼錯誤必須回傳相同錯誤訊息與狀態碼，但實作回傳 `使用者不存在` 與 `密碼錯誤`，會揭露帳號是否存在。
- JWT 密鑰檢查：實作使用 `process.env.JWT_SECRET as string` 強制斷言，若環境變數未設定，執行期會以不明確方式失敗；雖然規格要求從環境變數讀取，但目前缺少設定缺失時的明確錯誤處理。

---

### 🔴 必須修正（Critical）

#### 問題 1：登入失敗狀態碼不符合規格
- **檔案：** `src/login.ts:12`
- **問題：** 使用者不存在時回傳 `404`，密碼錯誤時回傳 `400`，但規格要求兩種情境都必須回傳 `401 Unauthorized`。
- **影響：** API consumer 會收到與規格不一致的狀態碼，導致前端或呼叫端錯誤處理分支失準，也會讓失敗原因被間接區分。
- **建議修正：**
  ```typescript
  const invalidCredentialsResponse = { error: 'email 或密碼不正確' };

  if (!user) {
    return res.status(401).json(invalidCredentialsResponse);
  }

  const isValid = await bcrypt.compare(password, user.passwordHash);
  if (!isValid) {
    return res.status(401).json(invalidCredentialsResponse);
  }
  ```

---

#### 問題 2：錯誤訊息揭露使用者是否存在，違反帳號枚舉防護
- **檔案：** `src/login.ts:14`
- **問題：** 使用者不存在時回傳 `使用者不存在`，密碼錯誤時回傳 `密碼錯誤`，違反規格要求的相同錯誤訊息與狀態碼。
- **影響：** 攻擊者可以透過不同錯誤訊息判斷 email 是否已註冊，形成 Account Enumeration 風險。
- **建議修正：**
  ```typescript
  const invalidCredentialsResponse = { error: 'email 或密碼不正確' };

  if (!user) {
    return res.status(401).json(invalidCredentialsResponse);
  }

  // ...

  if (!isValid) {
    return res.status(401).json(invalidCredentialsResponse);
  }
  ```

---

### 🟠 建議改善（Warning）

#### 問題 1：JWT_SECRET 使用型別斷言但未檢查設定是否存在
- **檔案：** `src/login.ts:24`
- **問題：** `process.env.JWT_SECRET as string` 只是在 TypeScript 層面強制視為字串，無法保證執行期真的有值。
- **影響：** 環境變數缺失時，登入流程可能在簽發 token 階段拋出錯誤並產生未預期的 500；也會讓設定問題延後到 runtime 才暴露。
- **建議修正：**
  ```typescript
  const jwtSecret = process.env.JWT_SECRET;
  if (!jwtSecret) {
    throw new Error('JWT_SECRET is required');
  }

  const token = jwt.sign(
    { userId: user.id },
    jwtSecret,
    { expiresIn: '7d' }
  );
  ```

---

### ⚪ 使用者自行決定（註解類問題）

#### 問題 1：註解內容直接描述目前已知違規狀態
- **檔案：** `src/login.ts:13`
- **問題：** 註解寫明「規格要求 401」與「不可揭露使用者是否存在」，但緊接著的程式碼仍回傳 `404` 與 `使用者不存在`。
- **影響：** 若這是開發中暫存註解可以保留；若準備提交正式實作，註解與程式碼矛盾會造成維護者誤判目前行為是否已符合規格。
- **建議：** 修正程式碼後移除這類暫時性偏差註解，或改成只說明為什麼失敗回應必須統一。
