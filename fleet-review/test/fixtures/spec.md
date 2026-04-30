# Calculator 規格文檔

## 功能需求

實作一個簡單的計算機模組，支援四則運算。

### API

```js
add(a, b)       // 回傳 a + b
subtract(a, b)  // 回傳 a - b
multiply(a, b)  // 回傳 a * b
divide(a, b)    // 回傳 a / b；b 為 0 時拋出 Error('Division by zero')
```

### 邊界條件

- `divide(x, 0)` 必須拋出 `Error('Division by zero')`
- 所有輸入皆為 number 型別，無需驗證非數字輸入
- 回傳值為 number

### 不在範圍內

- 浮點精度處理
- 型別轉換
