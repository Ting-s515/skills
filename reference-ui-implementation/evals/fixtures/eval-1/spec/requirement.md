# React 實作需求

- 建立 `ProfileForm.tsx`，以 `initialName` prop 初始化名稱。
- input 使用 React state 雙向更新，form submit 時呼叫 `onSave(name)`。
- 名稱去除空白後為空時，button 必須 disabled，opacity 為 `0.5`，cursor 為 `not-allowed`。
- 名稱有效時，button opacity 為 `1`，cursor 為 `pointer`。
- 這次沒有授權修改 global CSS，也不可新增任何 CSS 或 CSS-in-JS。
- 不要新增驗證訊息或其他 UI；只把指定行為綁定到參考 markup。
