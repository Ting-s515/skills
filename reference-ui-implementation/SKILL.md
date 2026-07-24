---
name: reference-ui-implementation
description: >
  當使用者提供或指定既有 HTML、JSX、TSX、React、Vue、Angular、Svelte 等範例切版檔案，並要求依照範例實作、
  React 化、替換為動態資料、沿用既有樣式、不要腦補畫面或維持相同 DOM 層級時，必須載入此技能。
  嚴格保留範例實際 render 的元素順序、父子層級、class 與 style，只允許必要的框架語法轉換、
  動態資料綁定、事件與需求明定的條件顯示。用於避免額外 wrapper 破壞 global CSS selectors、
  Flex/Grid item 與既有版型契約。
---

# 範例切版實作

將範例切版視為 DOM 與 CSS 契約。除非使用者事前同意，禁止重新設計結構、增加實體 wrapper，
或為了套用共用元件而改變範例 markup。

## 執行流程

### 1. 讀取參考來源

- 完整讀取使用者指定的範例切版檔案，不可只看局部片段。
- 讀取範例引用的必要樣式；對大型全域樣式檔，以範例 class 搜尋相關 selectors。
- global CSS 預設為唯讀；讀取目的只限理解 selectors 與版型契約，不代表取得修改授權。
- 若範例檔案不存在、無法讀取或來源不明，停止實作並回報，不自行重建版型。
- 截圖只作輔助；使用者提供切版原始檔時，以原始檔的 DOM 結構為準。

### 2. 建立內部對照

實作前逐層確認下列契約；除非使用者要求，不另外產生對照文件：

- 元素標籤、出現順序、父元素與直接子元素。
- class、inline style、重要 attributes 與表單結構。
- 靜態文字、固定值及固定清單中哪些位置要替換成動態資料。
- 哪些區塊依需求進行條件顯示、驗證或事件綁定。
- 哪些 selectors 使用 `>`、`+`、`~`、`:first-child`、`:nth-child()`，或依賴 Flex/Grid item 身分。

### 3. 評估共用元件

- 讀取候選共用元件實作，確認其實際 render 的 DOM，不可從名稱或外觀推定相容。
- 只有當元素順序、父子層級、class 與 style 均符合範例時，才可直接使用共用元件。
- 共用元件若增加任何範例不存在的實體 wrapper，不可直接使用。
- 可共用 hook、service、事件處理或資料轉換等行為，再由目前畫面自行維護範例 markup。
- `Fragment` 不會產生實體 DOM，可用於 React 組織程式碼。

### 4. 確認 CSS 與 DOM 授權

- 只有使用者明確指名「可以修改 global CSS」時，才能在該次需求範圍內修改；「調整樣式」、
  「讓畫面一致」等模糊描述不構成授權。
- 未取得 global CSS 修改授權時，需要新增或調整的樣式只能寫在元素的 inline style：
  React 使用 `style`、Vue 使用 `:style`，Angular 使用 `[style]`、`[style.*]` 或 `[ngStyle]`。
- 未取得授權時，不可新增或修改 CSS、SCSS、Sass、Less、CSS Module、CSS-in-JS、元件 style block
  或其他會產生樣式規則的檔案與程式結構。
- global CSS 授權與 DOM 授權彼此獨立；允許修改 CSS 不代表允許新增 wrapper、調整元素順序或改變父子層級。
- 若完成需求需要尚未取得的 CSS 或 DOM 授權，先說明衝突、影響與可行替代方案，等待使用者決定後再實作。

### 5. 實作動態行為

只允許下列變更：

- HTML 到目標框架的必要語法轉換，例如 `class` 改為 `className`、`for` 改為 `htmlFor`。
- 將靜態內容替換成動態資料、迴圈或必要條件渲染。
- 加入需求指定的事件、狀態、資料綁定與驗證訊息。
- 在未授權修改 global CSS 時，以目標框架的元素 inline style 實作需求指定的新樣式。
- 加入不產生實體 DOM 的程式結構。

禁止下列行為：

- 增加、刪除、合併、拆分或重新排序範例元素。
- 增加宣稱不影響視覺的 wrapper。
- 為套用共用元件、設計模式、響應式建議或個人偏好而改寫版型。
- 未經明確授權修改 global CSS，或將 CSS 修改授權擴張解讀為 DOM 修改授權。
- 自行新增範例與需求未定義的空狀態文案、標題、按鈕或提示。

若框架限制、無效 HTML、第三方元件或存取性要求造成結構衝突，先說明衝突、影響與最小偏差方案，
取得使用者同意後才能繼續。

### 6. 驗證與交付

- 比對範例與實際 render DOM 的元素順序、直接父子關係、class 與 style。
- 執行既有 focused component tests；測試重要直接子層與禁止出現的額外 wrapper。
- 確認範例依賴的 CSS selectors 仍能命中，不以肉眼視覺相似取代結構驗證。
- 依專案規則執行 build 與 code review；review 明確檢查 DOM/CSS 契約。
- 最終回報是否完全相符；若存在已核准偏差，逐項列出。

## 優先順序

- 使用者當前明確指示最高。
- global CSS 與 DOM 必須分別取得明確授權，不可由其中一項推定另一項。
- 範例切版 DOM/CSS 契約高於一般元件共用與前端架構偏好。
- React 或其他框架技能仍負責資料流與狀態設計，但不得藉此改變範例 render 結構。
