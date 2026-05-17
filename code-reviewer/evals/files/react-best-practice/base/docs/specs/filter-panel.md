# Filter Panel 規格

## 背景

報表頁面需要一個搜尋欄位，使用者輸入後以 debounce 方式通知父層更新查詢條件。

## 規則

- `FilterPanel` 必須顯示一個受控文字輸入。
- 使用者輸入後，`onQueryChange` 必須在 300ms debounce 後才被呼叫。
- debounce timeout 必須在 effect cleanup 中取消。
- 不可在 render 期間呼叫 state setter。
- 若 `initialQuery` 變更，元件可以同步本地狀態，但同步邏輯必須放在 effect 中。
