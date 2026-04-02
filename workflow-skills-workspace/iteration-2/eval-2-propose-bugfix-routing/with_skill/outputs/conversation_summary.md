# Propose 技能執行紀錄 — Bug Fix 分流處理說明

## 規格文檔

`working/spec.md`（電商後台管理系統規格）

---

## Bug Fix 分流結果

### [quick-fix] 直接實作清單

| # | 描述 | 判斷依據 |
|---|------|----------|
| 1 | 登入頁面在 Safari 瀏覽器下按鈕點擊無反應，檢查 event listener 相容性 | 明確標記 `[quick-fix]`，改動範圍可預期（單一 event listener 相容性修正，不涉及架構變動） |

### [propose] 走完整流程清單

| # | Folder | 描述 | 判斷依據 |
|---|--------|------|----------|
| 1 | `docs/propose/fix-order-notification/` | 訂單狀態更新後，通知信未正確寄送給買家，需重新設計通知觸發流程 | 明確標記 `[propose]`，且問題描述涉及「重新設計通知觸發流程」，屬架構層級改動，需跨多個服務協調（訂單服務、通知服務、Email Service、重試佇列） |
| 2 | `docs/propose/fix-stock-button-state/` | 商品庫存歸零時，前台仍顯示「可購買」按鈕（應根據庫存狀態動態更新按鈕狀態） | **無標記，AI 自動判斷為 propose**。理由：需跨前後台多個檔案協調（商品 API、前台元件、庫存事件觸發、下單驗證），涉及狀態管理與即時資料流設計（WebSocket 或 polling），有 side effect 風險（按鈕 UI 與下單後端驗證必須一致），符合 issue-doc-spec 的 propose 判斷準則 |

---

## 產出文檔清單

```
outputs/
  spec.md                                               ← 含回寫 propose 標記
  docs/propose/
    fix-order-notification/
      01-flow.md                                        ← 修正後的正確通知觸發流程
      02-gherkin.md                                     ← 各狀態通知情境驗收條件
      03-tasks.md                                       ← 7 項實作任務
    fix-stock-button-state/
      01-flow.md                                        ← 庫存狀態同步的正確行為流程
      02-gherkin.md                                     ← 庫存狀態與按鈕互動驗收條件
      03-tasks.md                                       ← 7 項實作任務
  conversation_summary.md                               ← 本文檔
```

---

## 執行過程說明

1. **讀取規格文檔**：識別 `## bug fix list` 區塊，共 3 筆 bug item
2. **套用 issue-doc-spec 分流規則**：
   - 第 1 筆：明確 `[quick-fix]` → 列入直接實作清單
   - 第 2 筆：明確 `[propose]` → 建立 `fix-order-notification/` folder
   - 第 3 筆：無標記 → AI 判斷涉及跨檔案狀態管理與資料流，歸類為 `propose`，建立 `fix-stock-button-state/` folder
3. **執行 clarify-flow**：對每個 propose bug 整理結構化流程，補全邊界條件（依 Bug Fix 特別規則：只描述修正後的正確行為）
4. **執行 export-gherkin**：依 01-flow.md 產出 Gherkin 驗收條件
5. **產出 03-tasks.md**：拆解具體實作任務，標示影響檔案與依賴關係
6. **回寫 spec.md**：在各 propose 項目下方插入 `> propose: ...` 標記
