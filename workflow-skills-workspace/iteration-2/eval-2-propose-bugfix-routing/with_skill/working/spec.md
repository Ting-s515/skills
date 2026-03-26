# 電商後台管理系統規格

## bug fix list

- [quick-fix] 登入頁面在 Safari 瀏覽器下按鈕點擊無反應，檢查 event listener 相容性
- [propose] 訂單狀態更新後，通知信未正確寄送給買家，需重新設計通知觸發流程
  > propose: `docs/propose/fix-order-notification/`
- 商品庫存歸零時，前台仍顯示「可購買」按鈕（應根據庫存狀態動態更新按鈕狀態）
  > propose: `docs/propose/fix-stock-button-state/`
