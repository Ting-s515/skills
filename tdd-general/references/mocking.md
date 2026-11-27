# 什麼時候用替身

只在系統邊界使用替身：

- 外部 API（第三方服務、其他團隊的系統、金鑰管理服務等）
- 資料庫（有時候；優先用測試專用資料庫，如 Testcontainers 或記憶體資料庫）
- 時間／亂數（注入時鐘或亂數來源，不要在程式內直接呼叫系統時間）
- 檔案系統（有時候）

不要對下列對象使用替身：

- 你自己的類別／模組
- 內部協作者
- 任何你能掌控的東西

常見的邊界替身做法：

- 後端整合測試：外部系統用替身伺服器（WireMock、MSW、nock 等）或測試框架提供的外部依賴模擬機制，不要替換自己的 service。
- 前端單元測試：替換 HTTP client 這個邊界模組（例如 `vi.mock('<api client 模組>')`），不要替換同一個功能內的 hook 或元件。

## 為可替換而設計

在系統邊界，設計容易替換的介面：

1. 使用依賴注入

把外部依賴從外面傳進來，而不是在內部建立：

```java
// 容易替換：以建構子注入介面
class PaymentService {
    private final PaymentGateway gateway;

    PaymentService(PaymentGateway gateway) {
        this.gateway = gateway;
    }

    String status(String orderId) {
        return gateway.fetchStatus(orderId);
    }
}

// 難以替換：在內部自行建立客戶端
class PaymentService {
    String status(String orderId) {
        var client = new HttpPaymentClient(System.getenv("PAYMENT_GATEWAY_URL"));
        return client.fetchStatus(orderId);
    }
}
```

2. 偏好 SDK 風格的介面，而不是通用的抓取函式

每個外部操作各寫一個函式，而不是寫一個帶條件邏輯的通用函式：

```ts
// 好：每個函式都能個別替換
export function listProducts(query: ProductListQuery) {
  return request<ProductListResponse>(`${apiBase()}/products?${toSearch(query)}`)
}

export function deleteProduct(id: string) {
  return request<void>(`${apiBase()}/products/${id}`, { method: 'DELETE' })
}

// 壞：替身裡必須寫條件邏輯
export function callApi<T>(endpoint: string, init?: RequestInit) {
  return request<T>(`${apiBase()}${endpoint}`, init)
}
```

SDK 風格的好處：

- 每個替身只回傳一種固定形狀
- 測試準備中沒有條件邏輯
- 容易看出一個測試動到哪些 endpoint
- 每個 endpoint 都有各自的型別安全
