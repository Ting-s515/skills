# Code Review 紀錄 — 2026-05-18（第 1 輪）

## 📋 Code Review 摘要

**審查範圍：** `src/login.ts` 的 `POST /api/auth/login` 實作，對照 `docs/specs/login-spec.md`
**整體評估：** ❌ 不符合規格，需修正

---

### 📐 規格符合度

#### ✅ 符合規格的項目
- 必填欄位缺漏：`email` 或 `password` 缺少時回傳 `422`，符合請求體缺少必填欄位的規格方向。
- 成功回應格式：成功時回傳 `200`，並包含 `token` 與 `user.id`、`user.email`。
- JWT 過期時間：`jwt.sign(..., { expiresIn: '7d' })` 符合 7 天過期規格。
- JWT 密鑰來源：使用 `process.env.JWT_SECRET`，未硬編碼密鑰。

#### ❌ 不符合或缺漏的項目
- 登入失敗狀態碼：使用者不存在回傳 `404`，密碼錯誤回傳 `400`，但規格要求兩者都回傳 `401 Unauthorized`。
- 登入失敗錯誤訊息：使用者不存在回傳 `使用者不存在`，密碼錯誤回傳 `密碼錯誤`，違反規格要求兩種情況必須回傳相同訊息。
- 請求體型別驗證：規格定義 `email` 與 `password` 為 `string`，目前只檢查 truthy，未拒絕非字串輸入。

---

### 🔴 必須修正（Critical）

#### 問題 1：登入失敗未統一回傳 401
- **檔案：** `src/login.ts:16`
- **問題：** 使用者不存在時回傳 `404`，密碼錯誤時在 `src/login.ts:22` 回傳 `400`，與規格要求的 `401 Unauthorized` 不一致。
- **影響：** API consumer 會收到錯誤的狀態碼，且同一類登入失敗被拆成不同錯誤語意，破壞規格相容性。
- **建議修正：**
  ```typescript
  const invalidLoginResponse = { error: 'email 或密碼不正確' };

  if (!user) {
    return res.status(401).json(invalidLoginResponse);
  }

  // ...

  if (!isValid) {
    return res.status(401).json(invalidLoginResponse);
  }
  ```

#### 問題 2：錯誤訊息造成帳號枚舉風險
- **檔案：** `src/login.ts:16`
- **問題：** `使用者不存在` 直接揭露 email 是否存在；`src/login.ts:22` 的 `密碼錯誤` 也讓攻擊者可區分帳號存在但密碼錯誤。
- **影響：** 攻擊者可透過不同錯誤訊息與狀態碼判斷哪些 email 已註冊，違反規格的 Account Enumeration 防護要求。
- **建議修正：**
  ```typescript
  const invalidCredentials = { error: 'email 或密碼不正確' };

  // 使用者不存在與密碼錯誤必須走同一個狀態碼與訊息。
  return res.status(401).json(invalidCredentials);
  ```

---

### 🟠 建議改善（Warning）

#### 問題 1：未驗證 email 與 password 必須為字串
- **檔案：** `src/login.ts:7`
- **問題：** 目前 `if (!email || !password)` 只判斷缺值，若傳入非字串 truthy 值仍會繼續查詢或進入 `bcrypt.compare`。
- **影響：** 可能造成非預期查詢、執行期錯誤，或讓 `422` 的請求格式錯誤規格涵蓋不完整。
- **建議修正：**
  ```typescript
  if (typeof email !== 'string' || typeof password !== 'string' || !email || !password) {
    return res.status(422).json({ error: '缺少必填欄位' });
  }
  ```

#### 問題 2：JWT_SECRET 缺少啟動或執行前檢查
- **檔案：** `src/login.ts:27`
- **問題：** `process.env.JWT_SECRET as string` 只是型別斷言，沒有保證環境變數真的存在。
- **影響：** 若部署環境漏設密鑰，登入流程可能在簽發 token 時丟出 500，而不是明確的設定錯誤。
- **建議修正：**
  ```typescript
  const jwtSecret = process.env.JWT_SECRET;
  if (!jwtSecret) {
    throw new Error('JWT_SECRET is required');
  }

  const token = jwt.sign({ userId: user.id }, jwtSecret, { expiresIn: '7d' });
  ```

---

### ⚪ 使用者自行決定（註解類問題）

#### 問題 1：註解指出規格要求但程式碼刻意違反
- **檔案：** `src/login.ts:15`
- **問題：** 註解寫明「規格要求 401」但下一行回傳 `404`；`src/login.ts:21` 也有相同情況。
- **影響：** 在修正前會讓維護者誤以為這是暫時狀態或已知問題，進入正式實作前應避免留下與程式行為矛盾的註解。
- **建議：** 若目前是測試階段可短暫保留；正式修正後應刪除或改寫為說明統一錯誤回應的安全原因。
