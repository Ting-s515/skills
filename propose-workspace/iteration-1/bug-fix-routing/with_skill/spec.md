# Bug Fix 清單

## bug fix list

1. [quick-fix] 商品列表每頁顯示筆數寫死 10，應改為可設定（預設 20）
2. [quick-fix] 新增商品成功後 toast 訊息顯示「刪除成功」，文字應為「新增成功」
3. [propose] 訂單狀態批次更新缺乏 transaction 保護，部分失敗時不會 rollback，其他已更新訂單無法回滾

> propose: `backend/docs/propose/fix-order-batch-update-transaction/`

4. 搜尋商品時輸入特殊字元（%、_、\）導致後端 SQL 查詢 500 錯誤

> propose: `backend/docs/propose/fix-product-search-special-chars/`
