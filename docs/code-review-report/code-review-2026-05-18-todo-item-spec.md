# Code Review 紀錄 — 2026-05-18（第 1 輪）

## 📋 Code Review 摘要

**審查範圍：** `src/components/TodoItem.tsx` 的 TodoItem 前端元件實作，對照 `docs/specs/todo-item-spec.md` 的 props、顯示規則與技術規範。
**整體評估：** ❌ 不符合規格，需修正

---

### ⚛️ React 最佳實踐

#### ✅ 符合最佳實踐
- [條件樣式集中於資料狀態]：標題刪除線依 `completed` 狀態切換，方向符合元件以 props 呈現 UI 狀態的設計。

#### ⚠️ 需改善
- [Props 型別邊界]：元件使用 `props: any`，導致 React 元件的輸入契約失去型別保護，也不符合規格要求的明確 TypeScript interface。
  ```tsx
  interface TodoItemProps {
    id: number;
    title: string;
    completed: boolean;
    priority: 'low' | 'medium' | 'high';
  }
  ```
- [可讀性與衍生狀態]：JSX 內直接塞入巢狀三元運算子，且上方已計算 `statusLabel` 卻沒有使用，造成重複邏輯與維護風險。
  ```tsx
  const getStatusMeta = (completed: boolean, priority: TodoItemProps['priority']) => {
    if (completed) {
      return { label: '已完成', className: 'status status--completed' };
    }

    if (priority === 'high') {
      return { label: '緊急', className: 'status status--urgent' };
    }

    return { label: '進行中', className: 'status status--active' };
  };
  ```

---

### 📐 規格符合度

#### ✅ 符合規格的項目
- [完成狀態文字]：`completed === true` 時，狀態標籤文字會顯示「已完成」。
- [高優先級文字]：`completed === false` 且 `priority === 'high'` 時，狀態標籤文字會顯示「緊急」。
- [一般進行中文字]：其他未完成且非 high 的情境，狀態標籤文字會顯示「進行中」。
- [標題刪除線]：`completed === true` 時，標題會套用 `line-through`。

#### ❌ 不符合或缺漏的項目
- [Props interface]：規格要求使用明確 TypeScript interface，但實作使用 `props: any`。
- [避免巢狀三元]：規格要求狀態標籤邏輯易讀且避免巢狀三元，但實作在 `statusLabel` 與 JSX 內都使用巢狀三元。
- [狀態標籤顏色]：規格要求「已完成」綠色、「緊急」紅色、「進行中」藍色，但目前 `<span>` 沒有 className 或 style 實作顏色。

---

### 🔴 必須修正（Critical）

#### 問題 1：Props 使用 any，違反型別規格
- **檔案：** `src/components/TodoItem.tsx:2`
- **問題：** `const TodoItem = (props: any)` 讓 `id`、`title`、`completed`、`priority` 的必填與 union 型別都無法在編譯期被驗證。
- **影響：** 呼叫端可傳入錯誤資料，例如 `priority: 'urgent'` 或缺少 `title`，元件仍可能編譯通過並在執行期出現錯誤顯示。
- **建議修正：**
  ```tsx
  interface TodoItemProps {
    id: number;
    title: string;
    completed: boolean;
    priority: 'low' | 'medium' | 'high';
  }

  export const TodoItem = ({ title, completed, priority }: TodoItemProps) => {
    // ...
  };
  ```

---

#### 問題 2：JSX 內使用巢狀三元運算子
- **檔案：** `src/components/TodoItem.tsx:17`
- **問題：** `{props.completed ? '已完成' : props.priority === 'high' ? '緊急' : '進行中'}` 是巢狀三元，違反規格與專案規範，也讓狀態邏輯分散在 JSX 中。
- **影響：** 後續若新增狀態或調整顏色，容易只改到其中一份邏輯，造成標籤文字與樣式不同步。
- **建議修正：**
  ```tsx
  const status = getStatusMeta(completed, priority);

  return (
    <span className={status.className}>
      {status.label}
    </span>
  );
  ```

---

#### 問題 3：狀態標籤缺少規格要求的顏色
- **檔案：** `src/components/TodoItem.tsx:16`
- **問題：** 狀態標籤只有文字，沒有依「已完成 / 緊急 / 進行中」套用綠色、紅色、藍色。
- **影響：** UI 顯示不符合規格，使用者無法透過顏色快速辨識狀態。
- **建議修正：**
  ```tsx
  const status = getStatusMeta(completed, priority);

  return (
    <span className={status.className}>
      {status.label}
    </span>
  );
  ```

---

### 🟠 建議改善（Warning）

#### 問題 1：`statusLabel` 計算後未使用
- **檔案：** `src/components/TodoItem.tsx:4`
- **問題：** `statusLabel` 變數已根據 props 計算狀態文字，但 return 內重新寫了一份巢狀三元，導致 `statusLabel` 成為 unused variable / dead code。
- **影響：** 若專案啟用 `noUnusedLocals` 或 ESLint unused 規則，會造成檢查失敗；即使未啟用，也會讓維護者誤判哪一份狀態邏輯才是有效來源。
- **建議修正：**
  ```tsx
  const status = getStatusMeta(completed, priority);

  return (
    <span className={status.className}>
      {status.label}
    </span>
  );
  ```

---

#### 問題 2：匯出形式從 named export 改成 default export
- **檔案：** `src/components/TodoItem.tsx:23`
- **問題：** 原本檔案是 `export const TodoItem`，這次改成 `export default TodoItem`。
- **影響：** 若既有呼叫端使用 `import { TodoItem } from ...`，會在整合時失敗。規格未要求變更匯出 API，建議保留 named export，必要時再額外提供 default export。
- **建議修正：**
  ```tsx
  export const TodoItem = ({ title, completed, priority }: TodoItemProps) => {
    // ...
  };
  ```

---

### ⚪ 使用者自行決定（註解類問題）

#### 問題 1：程式內保留描述缺陷的註解
- **檔案：** `src/components/TodoItem.tsx:1`
- **問題：** 註解直接描述 `props: any`、巢狀三元與 dead code 等缺陷，較像審查備註而非元件邏輯需要的 why 註解。
- **影響：** 若進入正式實作，這類註解會讓程式碼保留已知壞味道，也不符合專案「註解只寫 why」的規範。
- **建議：** 測試或教學階段可暫留；正式修正時應移除，並以清楚的 interface 與 helper 函式取代。
