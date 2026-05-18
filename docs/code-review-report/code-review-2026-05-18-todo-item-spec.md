# Code Review 紀錄 — 2026-05-18（第 1 輪）

## 📋 Code Review 摘要

**審查範圍：** `src/components/TodoItem.tsx` 的 TodoItem 前端元件實作，對照 `docs/specs/todo-item-spec.md`
**整體評估：** ❌ 不符合規格，需修正

---

### ⚛️ React 最佳實踐

#### ✅ 符合最佳實踐
- 元件輸出結構：以單一 component 呈現待辦標題與狀態標籤，方向符合規格描述的單一待辦事項展示用途。

#### ⚠️ 需改善
- 型別安全：React component props 使用 `any`，會讓呼叫端傳入錯誤型別時無法在編譯期攔截，違反規格要求的明確 TypeScript interface。
  ```tsx
  interface TodoItemProps {
    id: number;
    title: string;
    completed: boolean;
    priority: 'low' | 'medium' | 'high';
  }

  const TodoItem = ({ title, completed, priority }: TodoItemProps) => {
    // ...
  };
  ```
- 狀態衍生邏輯：JSX 內直接放入巢狀三元運算子，閱讀與維護成本偏高，也違反規格要求避免巢狀三元運算子。應把 label 與樣式邏輯抽成清楚的 helper 或區塊變數。
  ```tsx
  const getStatusLabel = (completed: boolean, priority: TodoItemProps['priority']) => {
    if (completed) {
      return '已完成';
    }

    if (priority === 'high') {
      return '緊急';
    }

    return '進行中';
  };
  ```

---

### 📐 規格符合度

#### ✅ 符合規格的項目
- 標題顯示：`props.title` 有渲染在畫面中。
- 已完成標題樣式：`props.completed === true` 時，標題套用 `line-through`。
- 狀態文字規則：目前 JSX 文字可分別顯示「已完成」、「緊急」、「進行中」。

#### ❌ 不符合或缺漏的項目
- Props 型別：規格要求使用明確 TypeScript interface，實作使用 `props: any`，不符合技術規範。
- 狀態標籤顏色：規格要求「已完成」綠色、「緊急」紅色、「進行中」藍色；目前狀態 `<span>` 沒有任何顏色樣式或 class。
- 狀態標籤邏輯可維護性：規格要求避免巢狀三元運算子；目前 JSX 中使用 `props.completed ? '已完成' : props.priority === 'high' ? '緊急' : '進行中'`。
- `id` prop：規格定義 `id` 為必填唯一識別碼，但目前沒有 interface 保障，也沒有在元件簽名中明確呈現此 contract。

---

### 🔴 必須修正（Critical）

#### 問題 1：Props 使用 `any`，違反 TypeScript interface 規格
- **檔案：** `src/components/TodoItem.tsx:2`
- **問題：** `const TodoItem = (props: any)` 使 `id`、`title`、`completed`、`priority` 都失去型別保護。
- **影響：** 呼叫端可傳入不存在的 priority、非 boolean completed 或缺漏 title，編譯期不會報錯，與規格的 Props contract 不一致。
- **建議修正：**
  ```tsx
  interface TodoItemProps {
    id: number;
    title: string;
    completed: boolean;
    priority: 'low' | 'medium' | 'high';
  }

  const TodoItem = ({ title, completed, priority }: TodoItemProps) => {
    // ...
  };
  ```

---

#### 問題 2：JSX 中仍使用巢狀三元運算子
- **檔案：** `src/components/TodoItem.tsx:16`
- **問題：** 狀態標籤直接在 JSX 中使用巢狀三元運算子，違反規格「避免巢狀三元運算子」。
- **影響：** 後續若新增更多狀態或樣式，條件會更難閱讀，且容易造成 label 與樣式規則分岔。
- **建議修正：**
  ```tsx
  const statusLabel = getStatusLabel(completed, priority);

  return (
    // ...
    <span>{statusLabel}</span>
  );
  ```

---

#### 問題 3：狀態標籤缺少規格要求的顏色
- **檔案：** `src/components/TodoItem.tsx:15`
- **問題：** 狀態 `<span>` 只輸出文字，沒有依 completed / priority 套用綠色、紅色、藍色。
- **影響：** UI 顯示未完整符合規格，使用者無法透過顏色辨識狀態。
- **建議修正：**
  ```tsx
  const statusClassName = getStatusClassName(completed, priority);

  return (
    // ...
    <span className={statusClassName}>{statusLabel}</span>
  );
  ```

---

### 🟠 建議改善（Warning）

#### 問題 1：`statusLabel` 計算後未被使用
- **檔案：** `src/components/TodoItem.tsx:4`
- **問題：** `statusLabel` 已根據狀態算出文字，但 return 中又重新計算一次，造成 unused variable / dead code。
- **影響：** 邏輯重複會增加維護風險；未來若只改其中一處，可能導致顯示規則不一致。
- **建議修正：**
  ```tsx
  const statusLabel = getStatusLabel(completed, priority);

  return (
    // ...
    <span>{statusLabel}</span>
  );
  ```

---

### ⚪ 使用者自行決定（註解類問題）

#### 問題 1：程式內保留指出缺陷的暫時註解
- **檔案：** `src/components/TodoItem.tsx:1`
- **問題：** 註解直接描述 `props: any` 與巢狀三元問題，像是 review 備註而非元件實作必要說明。
- **影響：** 測試或示範階段可保留作為缺陷提示；正式實作前應移除，避免讓問題說明長期留在 production code。
- **建議：** 修正型別與狀態邏輯後移除此類註解；若需要保留設計理由，改寫成「為什麼」而不是描述目前程式做了什麼。
