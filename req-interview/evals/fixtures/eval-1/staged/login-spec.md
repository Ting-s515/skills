# 登入功能規格

## 功能描述

使用者可透過 Email 與密碼登入系統，登入成功後發放 JWT Token。

## 主流程

1. 使用者在登入頁輸入 Email 與密碼
2. 點擊「登入」按鈕送出
3. 系統驗證帳號密碼
4. 驗證成功：發放 JWT Token（有效期 7 天），導向首頁
5. 驗證失敗：顯示錯誤訊息「帳號或密碼錯誤」

## API

```
POST /api/auth/login
Request:  { email: string, password: string }
Response: { token: string, user: { id, name, email } }
```

## UI 行為

- 登入按鈕在送出期間顯示 Loading 狀態
- 錯誤訊息顯示在表單下方
- 成功後跳轉至 `/dashboard`
