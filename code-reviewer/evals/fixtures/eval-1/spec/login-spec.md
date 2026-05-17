# Login API 規格

## POST /api/auth/login

### 請求體

| 欄位 | 型別 | 必填 | 說明 |
|------|------|------|------|
| email | string | ✅ | 使用者 email |
| password | string | ✅ | 使用者密碼 |

### 回應狀態碼

- `200 OK`：登入成功，回傳 `{ token: string, user: { id: number, email: string } }`
- `401 Unauthorized`：email 或密碼不正確（包含使用者不存在與密碼錯誤兩種情況，統一回傳相同訊息）
- `422 Unprocessable Entity`：請求體格式錯誤（缺少必填欄位）

### 安全規範

- 使用者不存在與密碼錯誤**必須回傳相同的錯誤訊息與狀態碼**，避免帳號枚舉攻擊（Account Enumeration）
- JWT token 過期時間為 7 天
- JWT 密鑰必須從環境變數讀取，不可硬編碼
