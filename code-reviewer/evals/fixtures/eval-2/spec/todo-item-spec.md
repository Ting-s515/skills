# TodoItem 元件規格

## 功能說明

顯示單一待辦事項，包含標題與優先級狀態標籤。

## Props 介面

| Props | 型別 | 必填 | 說明 |
|-------|------|------|------|
| id | number | ✅ | 唯一識別碼 |
| title | string | ✅ | 待辦事項標題 |
| completed | boolean | ✅ | 是否已完成 |
| priority | `'low' \| 'medium' \| 'high'` | ✅ | 優先級 |

## 顯示規則

- `completed === true`：標題套用刪除線樣式，狀態標籤顯示「已完成」（綠色）
- `completed === false` 且 `priority === 'high'`：狀態標籤顯示「緊急」（紅色）
- 其他（`completed === false` 且 `priority !== 'high'`）：狀態標籤顯示「進行中」（藍色）

## 技術規範

- Props 必須使用明確的 TypeScript interface 定義，不可使用 `any`
- 狀態標籤邏輯必須易於閱讀與維護，避免巢狀三元運算子
