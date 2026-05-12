# Keycloak 在 .NET 後端的 JWT 驗證與 Middleware 設定

根據 `[[keycloak-backend]]` 與 `[[keycloak-integration]]`：

---

## 整體認證架構

後端收到 API Request 後，依序經過以下驗證流程：

```
收到 API Request
    ↓
健康檢查路徑（/_hc）→ 直接放行
    ↓
標記 [SkipCurrentUser] → 放行
    ↓
Header 含 apiKey → 測試模式（僅 Development）
    ↓
JWT Bearer 驗證（JWKS 簽章 + Claims 解析）
```

---

## JWT Token 驗證參數

| 參數 | 值 |
|------|----|
| `ValidateIssuer` | true |
| `ValidateAudience` | true |
| `ValidateLifetime` | true |
| `ClockSkew` | `TimeSpan.Zero`（嚴格過期驗證，不容許時鐘偏移）|

簽章驗證方式為 **JWKS**（JSON Web Key Set），由 Keycloak 提供公鑰端點，.NET 自動下載並驗證 Token 簽章。

---

## Middleware 執行順序

```csharp
app.UseAuthentication();          // 1. 驗證 JWT Bearer Token
app.UseAuthorization();           // 2. 授權檢查
// RequestBodyCaptureMiddleware   // 3. 擷取 Request Body（日誌用）
// TrackIdMiddleware              // 4. 追蹤 ID 注入
// CurrentUserMiddleware          // 5. 解析 JWT Claims，建立使用者資訊
```

**關鍵點：** `UseAuthentication` 必須在 `UseAuthorization` 之前呼叫，`CurrentUserMiddleware` 放在最後，確保前面已完成 Token 驗證，才能安全地解析 Claims。

---

## JWT Claim 對照表

Keycloak 核發的 JWT 中，各 Claim 欄位對照如下：

| Claim | Keycloak 欄位 |
|-------|--------------|
| `sub` | User ID（GUID）|
| `preferred_username` | 登入帳號 |
| `email` | 電子郵件 |
| `realm_access.roles` | 角色清單 |
| `unit` / `phone` | 自訂屬性（需在 Keycloak Mapper 設定）|

---

## MultiScheme 雙認證支援

本後端支援 **JWT + ApiKey** 雙認證模式：

- **正式環境：** 使用 JWT Bearer Token（由 Keycloak 核發）
- **開發/測試環境（Development only）：** 可在 Header 帶入 `apiKey`，產生具有所有權限的固定測試用戶

```http
GET /api/dashboard
apiKey: testUser
```

---

## 整合流程補充（來自 `[[keycloak-integration]]`）

後端 API 驗證在整體三方流程中的位置：

```
Frontend middleware 確認/刷新 access_token（向 Keycloak）
    ↓
Backend API 收到 Bearer access_token
    ↓ JWKS 驗證簽章 + 解析 Claims
回傳 API 結果
```

前端每次 API 請求都會帶上 `Authorization: Bearer <access_token>`，後端透過 Keycloak 的 JWKS 端點驗證簽章後，再由 `CurrentUserMiddleware` 將 Claims 轉換為應用層的使用者物件。

---

## 相關頁面

- `[[keycloak-integration]]` — 前後端三方互動整體流程
- `[[keycloak-frontend]]` — 前端 Token 管理與路由保護
- `[[jwt-auth-token]]` — JWT Access Token + Refresh Token 機制原理
