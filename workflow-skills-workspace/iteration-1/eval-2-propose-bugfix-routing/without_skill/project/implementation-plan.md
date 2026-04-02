# 電商後台管理系統 Bug 修復實作方案

## 概覽

本文件針對 spec.md 中的 bug fix list 規劃修復方案。

---

## Bug 1：Safari 瀏覽器按鈕點擊無反應（quick-fix）

**標籤**：quick-fix
**優先級**：高

### 問題描述
登入頁面在 Safari 瀏覽器下，按鈕點擊事件無法觸發，可能與 Safari 對某些 event listener 的相容性處理方式不同有關。

### 修復方向
1. 確認 event listener 是否使用了 Safari 不支援的語法或 API（如 `passive` option 未正確設置）
2. 檢查是否有 CSS 屬性（如 `pointer-events: none` 或 `z-index` 問題）導致按鈕無法接收點擊
3. 確認是否使用了 `onclick` 屬性與 `addEventListener` 衝突
4. Safari 對 `form` 元素的 `submit` 事件有特殊行為，需確認是否需明確調用 `event.preventDefault()`

### 修復步驟
1. 在登入頁面按鈕加入 `type="button"` 或 `type="submit"` 明確指定類型
2. 將 event listener 改為標準寫法：`button.addEventListener('click', handler, false)`
3. 使用 Safari 開發者工具測試，確認點擊事件正常觸發
4. 在 iOS Safari 和 macOS Safari 分別驗證

---

## Bug 2：訂單通知信未正確寄送（propose）

**標籤**：propose
**優先級**：高

### 問題描述
訂單狀態更新後，系統未能正確觸發通知信件發送給買家。此問題涉及通知觸發流程的設計，需重新評估架構。

### 問題根因假設
- 通知觸發點（trigger）未與訂單狀態變更事件正確綁定
- 狀態更新與通知發送在同一個同步流程中，若有異常則通知被跳過
- 缺乏重試機制，導致暫時性錯誤造成通知永久遺失

### 設計方案

#### 方案 A：事件驅動架構（推薦）
將通知發送從訂單更新流程中解耦，改用事件觸發：

```
訂單狀態更新
    ↓
發送 OrderStatusChanged 事件
    ↓
通知服務監聽事件 → 發送信件
```

優點：
- 主流程不受通知失敗影響
- 可加入重試機制
- 擴展性佳（未來可加入 LINE、SMS 等通知管道）

實作重點：
- 建立 `OrderStatusChanged` 事件類別
- 建立 `NotificationService`，訂閱 `OrderStatusChanged` 事件
- 使用 queue（如 Redis Queue 或 DB-backed queue）確保通知不遺失
- 加入發送失敗重試（最多 3 次，指數退避）

#### 方案 B：同步補償機制（短期方案）
在現有流程中加入補償邏輯：

```
訂單狀態更新
    ↓
嘗試發送通知信
    ↓ 失敗
記錄到 notification_retry 表
    ↓
定時任務（每 5 分鐘）掃描並重試未發送通知
```

優點：不需大幅重構現有架構
缺點：即時性較差，延遲最多 5 分鐘

### 建議
短期先實作方案 B 解決問題，並同步規劃方案 A 作為長期改善目標。

---

## Bug 3：庫存歸零仍顯示可購買按鈕

**標籤**：無（依複雜度判斷為 quick-fix 等級）
**優先級**：中

### 問題描述
商品庫存歸零時，前台商品頁面仍顯示「可購買」按鈕，未根據庫存狀態動態更新。

### 修復方向
1. 確認前台顯示購買按鈕的邏輯是否有讀取庫存狀態
2. 確認 API 回傳的商品資料是否包含 `stock` 或 `available` 欄位
3. 加入前端渲染邏輯：若 `stock <= 0`，則按鈕顯示「已售完」並設為 `disabled`

### 修復步驟
1. 後端 API 確保回傳 `stock_quantity` 欄位
2. 前端根據 `stock_quantity` 判斷按鈕狀態：
   - `stock_quantity > 0`：顯示「加入購物車」，按鈕可點擊
   - `stock_quantity <= 0`：顯示「已售完」，按鈕禁用（`disabled`）
3. 若庫存資料有快取，需確認快取失效策略，庫存歸零時立即失效
4. 測試庫存剛好歸零的邊界情況

---

## 總結

| Bug | 標籤 | 複雜度 | 建議處理方式 |
|-----|------|--------|------------|
| Safari 按鈕點擊無反應 | quick-fix | 低 | 直接修復，1 天內完成 |
| 通知信未寄送 | propose | 高 | 需設計評估，建議分兩階段處理 |
| 庫存歸零顯示可購買 | 無 | 低-中 | 直接修復，1-2 天完成 |
