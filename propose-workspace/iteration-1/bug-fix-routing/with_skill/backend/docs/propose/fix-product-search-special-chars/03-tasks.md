# 任務清單：商品搜尋特殊字元 SQL Escape 修正

## 參考文檔
- 結構化流程：`backend/docs/propose/fix-product-search-special-chars/01-flow.md`
- 驗收條件：`backend/docs/propose/fix-product-search-special-chars/02-gherkin.md`

## 任務

- [ ] T1: 新增 SQL LIKE escape 工具函式，依序 escape `\`、`%`、`_`（影響：`src/utils/sql-escape.util.ts`）
- [ ] T2: 在 ProductRepository 的搜尋方法中，於組裝 LIKE 查詢前呼叫 escape 工具函式，並加上 ESCAPE '\' 子句（影響：`src/repositories/product.repository.ts`）（依賴 T1）
- [ ] T3: 確認空字串/null keyword 時略過 LIKE 條件，回傳全部商品（影響：`src/services/product.service.ts`）
- [ ] [manual] T_test: 補上單元測試，使用 Skill tool 呼叫 `bdd-unit-test` skill 分析實作檔案產出測試（依賴所有前置任務）
