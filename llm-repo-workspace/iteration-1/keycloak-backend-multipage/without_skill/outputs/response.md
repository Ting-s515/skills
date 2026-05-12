# Keycloak 在 .NET 後端驗證 JWT 的 Middleware 設定

## 概述

在 .NET 後端整合 Keycloak 進行 JWT 驗證，主要透過 ASP.NET Core 內建的 **JWT Bearer Authentication Middleware** 搭配 Keycloak 的 OpenID Connect 端點完成。

---

## 1. 安裝必要套件

```bash
dotnet add package Microsoft.AspNetCore.Authentication.JwtBearer
```

---

## 2. appsettings.json 設定

```json
{
  "Keycloak": {
    "Authority": "https://<keycloak-host>/realms/<your-realm>",
    "Audience": "your-client-id",
    "RequireHttpsMetadata": true
  }
}
```

- `Authority`：Keycloak Realm 的基礎 URL，ASP.NET Core 會自動從 `{Authority}/.well-known/openid-configuration` 取得公鑰與驗證設定。
- `Audience`：對應 Keycloak 中的 Client ID（或 resource server 的 audience claim）。

---

## 3. Program.cs / Startup.cs Middleware 設定

### .NET 6+ (Program.cs)

```csharp
var builder = WebApplication.CreateBuilder(args);

// 設定 JWT Bearer 驗證
builder.Services.AddAuthentication(options =>
{
    options.DefaultAuthenticateScheme = JwtBearerDefaults.AuthenticationScheme;
    options.DefaultChallengeScheme    = JwtBearerDefaults.AuthenticationScheme;
})
.AddJwtBearer(options =>
{
    // Keycloak Realm URL，自動取得 JWKS（公鑰）
    options.Authority = builder.Configuration["Keycloak:Authority"];

    // 對應 Keycloak client id 或 audience
    options.Audience = builder.Configuration["Keycloak:Audience"];

    options.RequireHttpsMetadata = true; // 正式環境務必開啟

    options.TokenValidationParameters = new TokenValidationParameters
    {
        ValidateIssuer           = true,
        ValidIssuer              = builder.Configuration["Keycloak:Authority"],
        ValidateAudience         = true,
        ValidAudience            = builder.Configuration["Keycloak:Audience"],
        ValidateLifetime         = true,
        ValidateIssuerSigningKey = true,
        // 簽名公鑰由 Authority JWKS 端點自動載入，無需手動設定
    };

    // （可選）自訂事件，例如 token 解析失敗時記錄 log
    options.Events = new JwtBearerEvents
    {
        OnAuthenticationFailed = context =>
        {
            // 可在此加入 logging
            return Task.CompletedTask;
        },
        OnTokenValidated = context =>
        {
            // token 驗證成功後可額外處理 claims
            return Task.CompletedTask;
        }
    };
});

builder.Services.AddAuthorization();

var app = builder.Build();

// 必須在 UseRouting 之後、UseEndpoints 之前
app.UseAuthentication(); // 驗證 JWT
app.UseAuthorization();  // 授權（檢查 roles / policies）

app.MapControllers();
app.Run();
```

---

## 4. Keycloak 特有注意事項

### 4.1 Audience 驗證問題

Keycloak 預設發出的 JWT 中，`aud` claim 可能是 `account` 而非你的 client id。有兩種解決方式：

**方式 A：在 Keycloak 設定 Audience Mapper**
- 進入 Keycloak Admin Console → Client → 你的 client → Client scopes
- 新增 `Audience` mapper，將 client id 加入 `aud` claim

**方式 B：停用 Audience 驗證（不建議正式環境）**
```csharp
options.TokenValidationParameters = new TokenValidationParameters
{
    ValidateAudience = false
};
```

### 4.2 Roles 驗證（Realm Roles vs Client Roles）

Keycloak JWT 中 roles 結構與一般不同：

```json
{
  "realm_access": {
    "roles": ["offline_access", "uma_authorization", "my-role"]
  },
  "resource_access": {
    "your-client-id": {
      "roles": ["client-role"]
    }
  }
}
```

若要用 `[Authorize(Roles = "my-role")]`，需自訂 Claims 對應：

```csharp
options.TokenValidationParameters = new TokenValidationParameters
{
    RoleClaimType = "realm_access.roles" // 預設不支援巢狀，需自訂 transformer
};
```

更完整的做法是實作 `IClaimsTransformation`：

```csharp
public class KeycloakRolesClaimsTransformer : IClaimsTransformation
{
    public Task<ClaimsPrincipal> TransformAsync(ClaimsPrincipal principal)
    {
        var identity = (ClaimsIdentity)principal.Identity!;
        var realmAccess = principal.FindFirst("realm_access")?.Value;

        if (realmAccess != null)
        {
            var roles = JsonDocument.Parse(realmAccess)
                .RootElement.GetProperty("roles")
                .EnumerateArray();

            foreach (var role in roles)
            {
                identity.AddClaim(new Claim(ClaimTypes.Role, role.GetString()!));
            }
        }

        return Task.FromResult(principal);
    }
}
```

註冊：
```csharp
builder.Services.AddTransient<IClaimsTransformation, KeycloakRolesClaimsTransformer>();
```

---

## 5. Controller 使用授權

```csharp
[ApiController]
[Route("api/[controller]")]
[Authorize] // 要求任何有效 JWT
public class ProductController : ControllerBase
{
    [HttpGet]
    [Authorize(Roles = "admin")] // 要求特定 role
    public IActionResult GetAll() => Ok("OK");
}
```

---

## 6. 驗證流程摘要

```
Client Request (Bearer Token)
        |
        v
UseAuthentication Middleware
        |
        v
JwtBearerHandler
  ├─ 從 Authorization header 取出 token
  ├─ 向 Keycloak JWKS 端點取得公鑰（自動快取）
  ├─ 驗證簽名、過期時間、issuer、audience
  └─ 建立 ClaimsPrincipal 注入到 HttpContext
        |
        v
UseAuthorization Middleware
  └─ 依 [Authorize] 屬性檢查 roles / policies
```

---

## 7. 使用第三方套件（可選）

若需要更完整的 Keycloak 整合（如 token refresh、logout），可考慮：

- **Keycloak.AuthServices.Authentication**（NuGet）：封裝常見 Keycloak 設定，簡化 appsettings 結構
  ```bash
  dotnet add package Keycloak.AuthServices.Authentication
  ```
  ```csharp
  builder.Services.AddKeycloakAuthentication(builder.Configuration);
  ```

---

## 小結

| 步驟 | 說明 |
|------|------|
| 安裝 `Microsoft.AspNetCore.Authentication.JwtBearer` | 核心 JWT 驗證套件 |
| 設定 `Authority` 指向 Keycloak Realm | 自動取得 JWKS 公鑰 |
| 設定 `Audience` 對應 Client ID | 確保 token 是給本服務的 |
| `app.UseAuthentication()` + `app.UseAuthorization()` | Middleware 順序不可顛倒 |
| 自訂 `IClaimsTransformation` | 解析 Keycloak 巢狀 roles 結構 |
