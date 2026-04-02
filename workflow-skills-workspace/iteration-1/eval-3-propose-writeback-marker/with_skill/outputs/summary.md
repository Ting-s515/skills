# Eval-3 執行摘要：確認後立即回寫 > propose: 標記

## 1. 回寫標記的時間點

- **執行步驟**：確認計畫後（步驟 3），**在產出任何文檔之前**立即執行 Edit tool 回寫標記
- **順序驗證**：
  1. 讀取 spec.md，識別功能清單
  2. 展示計畫，自動代替使用者確認「確認，開始」
  3. **立即** 用 Edit tool 在 spec.md 每個功能段落下方插入 `> propose:` 標記 ← 此時尚未建立任何 .md 文檔
  4. 確認標記已寫入 spec.md 後，才開始建立 docs/propose/ 資料夾與三份文檔
- **結論**：標記回寫發生在文檔產出之前，符合「確認後立即回寫」規則

## 2. spec.md 最終內容

```markdown
# 電商後台管理系統規格

## 使用者管理

管理員可以在後台查看所有使用者列表，支援依照 email 搜尋。
每筆使用者可點擊查看詳情，包含姓名、email、建立時間、訂單數量。
管理員可以停用/啟用使用者帳號。

> propose: `docs/propose/user-management/`

## 商品管理

管理員可以新增商品，填寫名稱、價格、庫存數量、商品描述。
商品列表支援依名稱篩選，以及依價格排序。
每筆商品可編輯或下架。

> propose: `docs/propose/product-management/`
```

兩個功能段落各自在結尾插入了 `> propose:` 標記，位置在功能描述文字之後、下一個 `##` 標題之前。

## 3. 建立的資料夾與檔案清單

```
docs/propose/
  user-management/
    01-flow.md
    02-gherkin.md
    03-tasks.md
  product-management/
    01-flow.md
    02-gherkin.md
    03-tasks.md
```

共建立 2 個 feature folder，6 份文檔。
