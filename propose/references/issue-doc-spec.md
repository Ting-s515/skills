# Issue Doc 標記格式規範

當使用者提供 issue 文檔（如 `docs/issue.md`）時，依照此規範判斷每個 bug 的處理方式。

## 標記語法

```
[<tag>] <描述>
```

## 標記類型

| 標記          | 說明                         | 觸發行為                |
| ------------- | ---------------------------- | ----------------------- |
| `[quick-fix]` | 明確的小改動，影響範圍可預期 | AI 直接實作             |
| `[propose]`   | 需要跨檔案協調或架構設計     | 走 `propose` skill 流程 |
| 無標記        | 由 AI 自動判斷               | 見下方判斷準則          |

## AI 自動判斷準則

判斷為 `quick-fix`：

- 改動單一參數、常數、設定值
- 修正明確的拼字錯誤或 typo
- 調整樣式、文字、顏色等純 UI 細節

判斷為 `propose`：

- 需跨 2 個以上檔案協調
- 涉及狀態管理或資料流設計
- 有 side effect 風險或行為不確定
- 影響 API 介面或 WebSocket 協定

## 文檔範例

```markdown
<!-- type: small → quick-fix | type: large → propose -->

## fix bug list

1. [quick-fix] debounce 改 200ms
2. [propose] WebSocket 切換容器時舊連線未關閉
3. 搜尋框清空後 filter 狀態沒有重置
```
