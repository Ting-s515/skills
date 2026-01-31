---
name: react-design
description: 當我需要撰寫或設計react相關實作架構，請參考下方文件架構說明
---

## 資料夾路徑說明

> **注意**：`{ModuleName}` 為模組/單元名稱變數，請依實際功能替換（例如：DataExchanges、UserManagement、Dashboard 等）

```
src/app/{ModuleName}/
├── components/     # 組件層：UI 組件與容器組件
├── hooks/          # 自訂 Hook：狀態邏輯與業務邏輯封裝
├── services/       # API 服務層：後端 API 呼叫封裝
├── context/        # Context 層：跨組件共享狀態（謹慎使用）
├── utils/          # 工具函數：純函數、格式化、驗證等
├── types/          # TypeScript 型別定義（選用）
```

### 各層職責說明

| 資料夾 | 職責 | 範例 |
|--------|------|------|
| `components/` | 純 UI 渲染、事件綁定 | `UserList.tsx`, `FormDialog.tsx` |
| `hooks/` | 狀態管理、副作用處理、業務邏輯 | `useUserList.ts`, `useFormValidation.ts` |
| `services/` | API 請求封裝、資料轉換 | `userService.ts`, `authService.ts` |
| `context/` | 跨層級狀態共享（僅在必要時使用） | `UserContext.tsx` |
| `utils/` | 純函數、無副作用的工具 | `formatDate.ts`, `validators.ts` |

---

## 架構設計原則

### 1. Context 使用原則

- ❌ **避免**：僅用 Context 包裝單一 Hook（增加不必要的複雜度）
- ✅ **適用場景**：
  - 多個不相關組件需要共享相同狀態
  - 深層嵌套組件需要存取狀態（避免 prop drilling）
  - 全域性狀態（如：主題、語系、使用者認證）

```tsx
// ❌ 不推薦：Context 只是簡單包裝 Hook
const MyContext = createContext(null);
const MyProvider = ({ children }) => {
  const hookValue = useMyHook();  // 只是轉發 hook
  return <MyContext.Provider value={hookValue}>{children}</MyContext.Provider>;
};

// ✅ 推薦：直接使用 Hook
const MyComponent = () => {
  const { data, actions } = useMyHook();
  return <div>{/* 使用 data 和 actions */}</div>;
};
```

### 2. Hook 設計原則

#### 單一職責原則（SRP）
每個 Hook 只負責一個明確的功能領域：

```tsx
// ❌ 不推薦：一個 Hook 管理多個不相關狀態
const useEverything = () => {
  const [users, setUsers] = useState([]);
  const [theme, setTheme] = useState('light');
  const [notifications, setNotifications] = useState([]);
  // ... 混雜多種邏輯
};

// ✅ 推薦：拆分為獨立的 Hook
const useUsers = () => { /* 只管理使用者相關狀態 */ };
const useTheme = () => { /* 只管理主題相關狀態 */ };
const useNotifications = () => { /* 只管理通知相關狀態 */ };
```

#### 降低 Hook 間耦合
- 避免 Hook A 直接呼叫 Hook B
- 使用組合模式：在組件層組合多個 Hook
- 共用邏輯提取到 `utils/` 純函數

```tsx
// ❌ 不推薦：Hook 間強耦合
const useUserActions = () => {
  const { data } = useUserList();  // 直接依賴另一個 Hook
  // ...
};

// ✅ 推薦：組件層組合
const UserPage = () => {
  const { users } = useUserList();
  const { updateUser } = useUserActions();

  // 在組件層協調兩個 Hook
  const handleUpdate = (id, data) => updateUser(id, data);
};
```

### 3. 服務層設計原則

```tsx
// services/userService.ts
// 封裝 API 呼叫，統一錯誤處理與資料轉換
export const userService = {
  // 取得使用者列表
  getUsers: async (params?: QueryParams): Promise<User[]> => {
    const response = await api.get('/users', { params });
    return response.data;
  },

  // 更新使用者資料
  updateUser: async (id: string, data: UpdateUserDto): Promise<User> => {
    const response = await api.put(`/users/${id}`, data);
    return response.data;
  },
};
```

### 4. 組件設計原則

#### 容器組件 vs 展示組件

```tsx
// 容器組件：負責邏輯與狀態
const UserListContainer = () => {
  const { users, loading, error } = useUserList();

  if (loading) return <Spinner />;
  if (error) return <ErrorMessage error={error} />;

  return <UserList users={users} />;
};

// 展示組件：純 UI 渲染
const UserList = ({ users }: { users: User[] }) => (
  <ul>
    {users.map(user => <UserItem key={user.id} user={user} />)}
  </ul>
);
```

---

## 架構目標

1. **檢查 Context 必要性**：若只是單純包裝 Hook，應考慮移除
2. **評估 Hook 使用時機**：簡單狀態可用 `useState`，複雜邏輯再抽取 Hook
3. **Hook 單一職責**：避免單一 Hook 承擔過多責任
4. **降低 Hook 耦合**：Hook 間避免直接依賴，改由組件層組合
5. **簡化 Context 實作**：避免 Context 僅作為 Hook 的轉發層
6. **提升可維護性**：降低耦合性、簡化狀態管理、提高代碼可讀性
7. **狀態分離**：不相關的狀態不應放在同一個 Hook 管理
8. **避免 useEffect 內同步呼叫 setState**：確保狀態更新不會導致無限重渲染，非必要不要在 useEffect 內直接呼叫 setState（Calling setState synchronously within an effect can trigger cascading renders）

### 第 8 點補充說明

在 `useEffect` 內同步呼叫 `setState` 會觸發**連鎖渲染（cascading renders）**，可能導致：
- 效能問題（不必要的多次重渲染）
- 無限迴圈（當 state 作為 dependency 時）
- React 開發模式警告

```tsx
// ❌ 不推薦：useEffect 內直接呼叫 setState
useEffect(() => {
  setCount(count + 1);  // 觸發連鎖渲染
}, [someValue]);

// ❌ 危險：可能導致無限迴圈
useEffect(() => {
  setData(transformData(data));  // data 變更 → 觸發 effect → 又變更 data
}, [data]);

// ✅ 推薦：在事件處理函式中更新狀態
const handleClick = () => {
  setCount(prev => prev + 1);
};

// ✅ 推薦：使用 useMemo 計算衍生值，避免額外 state
const transformedData = useMemo(() => transformData(data), [data]);
```

**何時可以在 useEffect 內使用 setState**：
- 非同步操作完成後（如 API 回應）
- 訂閱外部資料源時
- 需要根據 props 初始化一次性狀態

---

## 重構注意事項

- ✅ 保證重構後原有功能不受影響
- ✅ 逐步重構，每次完成一個部分就進行測試
- ✅ 保持現有的 API 介面和用戶體驗不變
- ✅ 不需要更新單測檔

---

## 程式碼註解規範

### 需要註解的情況
- ✅ 邏輯互動的程式碼（說明 **為什麼** 這樣做）
- ✅ 複雜的業務邏輯
- ✅ 非顯而易見的實作決策

### 不需要註解的情況
- ❌ UI 樣式相關程式碼
- ❌ 資料結構/型別定義
- ❌ 未變更的程式碼
- ❌ 顯而易見的程式碼

```tsx
// ✅ 好的註解：說明why
// 使用 debounce 避免使用者快速輸入時頻繁觸發 API 請求
const debouncedSearch = useMemo(
  () => debounce(handleSearch, 300),
  [handleSearch]
);

// ❌ 不好的註解：只說明what（程式碼本身已經說明）
// 設定 loading 為 true
setLoading(true);
```