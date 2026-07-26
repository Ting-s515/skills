# 純靜態 Markdown 教材網站實作 Prompt

## 任務角色

你是一名負責教材閱讀體驗的資深前端工程師。請直接在目前 repository 中建立或維護 `docs-web/`，將 `docs/` 內全部 Markdown 教材產生為可在瀏覽器閱讀的純靜態網站。

這是一項實作任務，不要只提供範例、設計稿或操作說明。開始前先讀取 repository 內的 `AGENTS.md`、現有檔案與 Git 狀態；保留非本次任務的既有變更。

## 固定輸入與輸出

- Markdown 來源：repository 根目錄下的 `docs/*.md`。
- 網站專案：`docs-web/`。
- 靜態產物：`docs-web/dist/index.html`、`style.css`、`app.mjs`。
- 網站名稱與說明：優先使用本次需求；未指定時依 repository 文件或目錄名稱決定，不得從模板或其他專案沿用。
- 教材清單與數量：每次從目前 `docs/*.md` 動態取得，不設定固定名稱或份數。
- 本機網址：`http://127.0.0.1:18100`。
- Node.js：24 以上。
- 所有文字檔一律使用 UTF-8。

## 不可變更的技術方向

1. 使用原生 HTML、CSS 與 JavaScript ES Modules（`.mjs`）。
2. 不使用 React、Vue、Angular、Svelte、MDX、Next.js、Nuxt、Astro 或其他 UI framework。
3. 所有 Markdown 必須在 build 階段轉成 HTML，預先寫入同一份 `dist/index.html`。
4. 瀏覽器不得使用 `fetch()` 讀取 Markdown，也不得在切換文件時重新請求教材。
5. 不建立後端 API、SSR、database 或 runtime Markdown renderer。
6. `server.mjs` 只負責提供 build 完成的靜態檔案。
7. 不提交產生的 `dist/`，但必須以 `npm run build` 驗證它可以重新產生。

純靜態的定義是：網站可由任何 static file server 提供；client-side JavaScript 只負責文件切換、code block 複製、Mermaid SVG 渲染及圖表互動，不負責取得或轉換教材內容。

## 固定目錄結構

```text
docs-web/
├─ package.json
├─ package-lock.json
├─ prompt.md
├─ script/
│  ├─ build-site.mjs
│  └─ server.mjs
├─ src/
│  ├─ index.html
│  ├─ style.css
│  ├─ code-copy.mjs
│  ├─ dialog-keydown.mjs
│  └─ app.mjs
└─ test/
   └─ build-site.test.mjs
```

每個檔案只能承擔以下責任：

| 檔案 | 責任 |
| --- | --- |
| `script/build-site.mjs` | 掃描 Markdown、轉換 HTML、建立導覽、改寫連結及輸出靜態檔案 |
| `script/server.mjs` | 在固定 host 與 port 提供 `dist/` 內的四個公開路徑 |
| `src/index.html` | 頁面骨架、文件 placeholder 與 Mermaid 放大 dialog |
| `src/style.css` | 完整視覺、兩欄排版、Markdown、Mermaid、響應式與列印樣式 |
| `src/code-copy.mjs` | 提供可獨立測試的 Clipboard API 寫入行為 |
| `src/dialog-keydown.mjs` | 提供可獨立測試的 Mermaid dialog Escape 關閉行為 |
| `src/app.mjs` | hash 導覽、文件切換、code block 複製 UI、Mermaid render 與放大閱讀器 |
| `test/build-site.test.mjs` | 驗證靜態產物、連結、無 runtime fetch 與 Mermaid 閱讀器契約 |

## 套件與 scripts

`package.json` 必須使用 `"type": "module"`，並提供：

```json
{
  "scripts": {
    "build": "node ./script/build-site.mjs",
    "dev": "npm run build && node ./script/server.mjs",
    "preview": "node ./script/server.mjs",
    "test": "node --test ./test/*.test.mjs"
  }
}
```

使用並鎖定下列版本的 dev dependencies：

| 套件 | 版本 | 責任 |
| --- | --- | --- |
| `esbuild` | `0.28.1` | bundle 與 minify browser `app.mjs` |
| `mermaid` | `11.16.0` | browser 端產生 SVG |
| `unified` | `11.0.5` | Markdown 轉換 pipeline |
| `remark-parse` | `11.0.0` | 解析 Markdown |
| `remark-gfm` | `4.0.1` | 支援 GitHub Flavored Markdown |
| `remark-rehype` | `11.1.2` | mdast 轉成 hast |
| `rehype-slug` | `6.0.0` | 產生 heading ID |
| `rehype-stringify` | `10.0.1` | 輸出 HTML |

## Build 架構

`build-site.mjs` 必須完成以下流程：

1. 只讀取 `docs/` 第一層的 `.md` 檔案，依 `zh-Hant` locale 由檔名排序。
2. 以 Markdown 第一個 H1 作為導覽標題；沒有 H1 時才使用檔名。
3. 為每份文件建立穩定且唯一的 ID：保留 Unicode 字母與數字形成可讀 slug，並加入由原始完整檔名字串產生的短 hash，避免非 ASCII、相似檔名或 Unicode canonical-equivalent 檔名碰撞；前綴為 `doc-`。
4. 依目標 repository 的課程結構建立導覽群組。優先採用使用者要求或既有文件慣例；若沒有可靠的分類依據，全部文件放入單一中性群組。不得把特定專案的檔名前綴或分類名稱當成通用規則。
5. 將全部文件導覽寫入 `<!-- DOCUMENT_NAVIGATION -->`。
6. 將每份 HTML 放入獨立的 `<article class="document-panel markdown-body">`，再寫入 `<!-- DOCUMENT_CONTENT -->`。
7. 首份文件預設顯示，其餘 article 使用 `hidden`。
8. 將每份文件內 heading ID 加上所屬 document ID 前綴，避免多份 Markdown 的同名 heading 衝突。
9. 將 Markdown 文件連結改成同頁 hash；文件內 fragment 也必須指向加過前綴的 heading ID。
10. 外部連結使用 `target="_blank"`、`rel="noreferrer noopener"`。
11. Mermaid code fence 必須轉成 `<div class="mermaid">原始 Mermaid code</div>`，不可顯示成一般 code block。
12. GFM table、list、blockquote、inline code、code block、link 與 footnote 必須正常產生。
13. 每次 build 重新建立 `dist/`，輸出單一 HTML、CSS 與 bundle 後的 MJS。

文件切換一律使用 hash，例如 `#doc-00-course-introduction`；禁止使用 `?doc=` 或為每份 Markdown 產生不同 HTML 頁面。

## 固定頁面架構

Desktop 使用兩欄式閱讀頁面：

```text
┌──────────────────────┬──────────────────────────────────────┐
│ Sticky 文件目錄      │                                      │
│ 270px～320px         │      置中的 Markdown 內容卡片        │
│ 高度 100vh           │      最大寬度 980px                  │
│ 可獨立捲動           │                                      │
└──────────────────────┴──────────────────────────────────────┘
```

- 左欄使用 `<aside>` 與 `<nav>`，顯示目標專案名稱、動態文件總數、分類標題、教材標題及檔名。
- 右欄使用 `<main>`，一次只顯示一份 `<article>`。
- active 導覽項目同時具有 `.is-active` 與 `aria-current="page"`。
- hash 指向文件內 heading 時，先顯示所屬 article，再捲動至該 heading。
- 切換文件只操作現有 DOM，不重新載入頁面、不取得 Markdown。

## 固定暖色視覺

整體必須是低對比、偏暖、適合長時間閱讀的淺色設計，不得改成深黃色、純白高對比或冷灰藍色系。

使用以下固定 design tokens：

```css
:root {
  color: #332a1f;
  background: #faf7ef;
  --page-background: #faf7ef;
  --sidebar-background: #f4eddf;
  --content-background: #fffdf8;
  --code-background: #403b33;
  --border-color: #ded4c2;
  --muted-color: #6f675b;
  --link-color: #72531d;
  --active-background: #fff7df;
}
```

字型順序固定為：

```css
Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont,
"Segoe UI", "Microsoft JhengHei", sans-serif
```

主要視覺規格：

- `.document-shell`：CSS Grid，`grid-template-columns: minmax(270px, 320px) minmax(0, 1fr)`。
- `.document-sidebar`：sticky、`height: 100vh`、可垂直捲動、底色 `#f4eddf`。
- `.document-main`：暖白背景，desktop padding 使用 `3rem clamp(1.5rem, 5vw, 5rem) 6rem`。
- `.markdown-body`：`max-width: 980px`、置中、暖白卡片、1rem 圓角、淡邊框與低透明陰影。
- 正文：`line-height: 1.8`；paragraph 與 list item 最大 `78ch`。
- H1 使用響應式字級與較粗底線；H2、H3 保持清楚層級但不要過度裝飾。
- inline code 使用淺暖棕底；code block 使用 `#403b33` 深底及橫向捲動。
- table 必須能橫向捲動，偶數列使用極淡暖色背景。
- 所有 focus 狀態使用清楚可見的 `3px solid #8f681e` outline。

導覽與內容元件使用以下固定細節，不要自行替換成另一套設計語言：

| 元件 | 固定樣式 |
| --- | --- |
| Sidebar | `padding: 2rem 1.25rem`，右側 `1px solid #ded4c2` |
| Sidebar header | `padding: 0 0.5rem 1.5rem`，底部淡色分隔線 |
| Sidebar H1 | `font-size: 1.75rem`，margin `0.25rem 0` |
| 分類區塊 | `margin-top: 1.5rem` |
| 分類標題 | `0.78rem`、`#665b49`、字距 `0.08em` |
| 文件連結 | grid、gap `0.2rem`、padding `0.7rem 0.75rem`、圓角 `0.65rem` |
| Active 連結 | `#fff7df` 背景、`#d2bd8e` 邊框、極淡陰影 |
| 文件標題 | `0.9rem`、weight `700`、line-height `1.4` |
| 檔名 | `0.68rem` 等寬字、單行 ellipsis、muted color |
| Markdown 卡片 | `#e5dbc8` 邊框、`1rem` 圓角、`0 18px 45px rgb(84 70 45 / 8%)` 陰影 |
| H1 | `clamp(1.85rem, 4vw, 2.75rem)`，下方 `2px` 分隔線 |
| H2 | 上距 `2.75rem`、`1.55rem`，下方 `1px #e4d9c5` 分隔線 |
| H3 | 上距 `2rem`、`1.2rem` |
| Blockquote | `#f8f1e3` 背景與 `4px solid #b8924d` 左邊框 |
| Table cell | padding `0.65rem 0.8rem`，`1px solid #ddd0b8` |

## Code block 複製

每個 Markdown fenced code block 都要在右上角提供 icon-only 複製按鈕，讓教材中的 CLI 指令與程式碼可以直接貼到終端機或編輯器。Mermaid code fence 已轉為圖表，不得出現複製按鈕。

互動規格：

1. 使用 `.code-block-frame` 包住既有 `<pre><code>`，並建立 `minmax(0, 1fr) 3rem` 雙欄 Grid；指令只在左欄水平捲動，按鈕固定在右欄頂端，兩者不得重疊。
2. 按鈕固定為 `2rem × 2rem`，只顯示 `0.875rem` 的內嵌 SVG；預設使用兩張重疊方框的 Copy icon，不顯示可見文字或 emoji。
3. `<pre>` 使用 `min-width: 0` 並獨立處理水平捲動；按鈕不得使用 absolute positioning 或疊在 `<pre>` 上，也不得增加額外上方列。Hover 或 keyboard focus 時，tooltip 從按鈕左側展開。成功後 icon 暫時切換為 Check，tooltip 改為 `已複製`；失敗時保留 Copy icon、套用警示色並顯示 `複製失敗`。
4. 複製內容只取 `<code>` 的 `textContent`，不得包含按鈕內容，也不得改寫換行或空白；狀態約 1.8 秒後恢復。
5. 按鈕使用動態 `aria-label` 與 `aria-live="polite"`，並具有與網站一致的 keyboard focus outline。
6. 列印時隱藏複製按鈕，並將 frame 收回單欄，不保留右側控制欄位。

## Mermaid 固定呈現方式

Mermaid 初始化必須使用：

```js
{
  startOnLoad: false,
  securityLevel: "strict",
  theme: "base",
  themeVariables: {
    background: "#fffdf8",
    primaryColor: "#fff7df",
    primaryTextColor: "#342717",
    primaryBorderColor: "#b8924d",
    lineColor: "#72531d",
    secondaryColor: "#f4eddf",
    tertiaryColor: "#faf7ef"
  }
}
```

只有目前顯示文件中尚未處理的 `.mermaid` 才執行 `mermaid.run()`。Render 成功後再建立放大控制，避免重複初始化或重複增加按鈕。

一般閱讀狀態必須遵守：

- `.mermaid-frame` 固定 `width: 100%`，只能位於 Markdown 卡片的正文寬度內。
- 絕對禁止使用 viewport 計算、負 margin、translate 或其他方式讓圖表突破內容卡片。
- `.mermaid` 可橫向捲動，使用 `#faf4e7` 背景、淡棕邊框、圓角及內距。
- 每張圖右上角提供 `🔍 放大` 按鈕；直接點擊圖表也可以開啟。
- 圖表本身可取得 focus，按 `Enter` 或空白鍵也能開啟。

## Mermaid 全螢幕閱讀器

使用原生 `<dialog>`，不得引入 lightbox 或 zoom 套件。Dialog 固定包含：

- 標題：`Mermaid 圖表放大檢視`
- 縮小按鈕
- 即時縮放百分比
- 放大按鈕
- `重設` 按鈕
- `關閉` 按鈕
- 可拖曳的 viewport
- 操作提示：`使用滾輪縮放，按住圖表拖曳移動，按 Esc 關閉。`

互動規格：

1. Dialog desktop 尺寸為 `min(96vw, 1600px)` × `94vh`；背景維持暖色。
2. Backdrop 使用半透明深棕色並輕微 blur。
3. 開啟時依 SVG `viewBox` 與 viewport 自動計算 fit scale，置中顯示。
4. 縮放範圍固定為 20%～500%，按鈕倍率為 1.2。
5. 滑鼠滾輪可以縮放；pointer events 支援滑鼠與觸控拖曳。
6. `重設` 回到自動 fit、置中且清除位移。
7. 點擊 backdrop、關閉按鈕或按 `Esc` 均可關閉；`Esc` 必須由 dialog 的 `keydown` handler 明確處理，不可只依賴瀏覽器的原生預設行為。
8. 關閉後 focus 回到原本的放大按鈕或圖表。
9. 不要 clone Mermaid SVG。應暫時將原始 SVG 移入 dialog，使用 comment placeholder 記住位置，關閉時還原原本 style 與 DOM 位置，避免 duplicate SVG IDs。
10. 視窗尺寸改變且 dialog 開啟時，重新執行 fit。

## Responsive 與列印

Breakpoint 固定為 `820px`：

- 兩欄改成單欄。
- sidebar 改為一般區塊，寬度 100%，最大高度 `42vh`。
- main 與 Markdown 卡片縮小 padding。
- dialog 改成 `100vw × 100dvh`、無邊框、無圓角。
- dialog header 改為垂直排列，controls 可以換行。

列印時：

- 隱藏 sidebar、Mermaid 放大按鈕與 dialog。
- 隱藏 code block 複製按鈕。
- 移除 main 與 Markdown 卡片的 padding、背景、邊框及陰影。
- 不應因互動 UI 破壞紙本內容。

## Static server

`server.mjs` 使用 Node.js 內建 `node:http`，固定監聽 `127.0.0.1:18100`，只公開：

- `/` → `index.html`
- `/index.html` → `index.html`
- `/style.css` → `style.css`
- `/app.mjs` → `app.mjs`

所有回應需有正確 UTF-8 content type 與 `cache-control: no-cache`。未知路徑回傳 404 與 `找不到頁面`。Port 被占用時輸出清楚訊息，不得自動改用另一個 port。

## 測試要求

使用 Node.js 內建 `node:test`，在 `mkdtemp()` 建立不綁定特定專案的 Markdown fixture 與 build 輸出，測試後移除。Fixture 應包含非 ASCII 檔名、正規化後相似的檔名、Unicode composed／decomposed 檔名，以及至少一個跨文件 fragment 連結。至少驗證：

1. 產生的 article 數量等於 fixture 或目前 `docs/*.md` 的動態數量。
2. 全部教材內容已預先存在同一份 HTML，測試不得固定目標專案的教材名稱或份數。
3. 每份文件 ID 皆唯一，且只有第一個導覽項目具有 active 狀態。
4. Markdown 文件連結已正向改成目標文件與 heading 的同頁 hash，不再指向 `.md`。
5. `app.mjs` 與 `style.css` 均成功輸出且不是空檔。
6. 靜態 HTML 不引用 `/src/`。
7. 文件切換使用 `hashchange` 與 article `hidden`，client source 不得含 `fetch(`。
8. fixture 至少包含一個 fenced code block，client source 與 CSS 包含雙欄 Grid、獨立水平捲動的指令欄、固定右側控制欄、Copy SVG、左側 tooltip、Check 成功狀態與失敗警示色；不得退回可見文字按鈕、覆蓋式 absolute positioning 或額外上方預留列。
9. Clipboard helper 以 test double 驗證完整文字寫入，並測試 Clipboard API 不可用的失敗分支。
10. HTML 包含 Mermaid dialog 與 zoom controls。
11. client source 包含放大按鈕、`showModal()`、明確的 `Escape` keydown 關閉、wheel 與 pointer drag 行為；Escape helper 需以事件與 dialog test double 驗證關閉及非關閉分支。
12. CSS 包含 dialog backdrop。
13. `.mermaid-frame` 為 `width: 100%`，且不存在讓圖表突破正文的 viewport 寬度計算。

測試不可只檢查函式存在；也要驗證最終靜態 HTML 與輸出 assets 的契約。

## 執行與驗收

完成實作後依序執行：

```powershell
npm --prefix .\docs-web install
npm --prefix .\docs-web test
npm --prefix .\docs-web run build
npm --prefix .\docs-web run dev
```

開啟 <http://localhost:18100>，確認：

- 左側目錄與右側內容形成穩定兩欄。
- 背景為很淺的暖色，長時間閱讀不刺眼。
- 點擊目錄不重新下載 Markdown，URL hash 正確更新。
- heading deep link 可以開啟正確文件並捲動定位。
- table、code block 與長內容不撐破頁面。
- 每個 code block 右上角都有緊湊的 Copy icon，指令只在左欄水平捲動且不會被右側按鈕遮住，單行內容未被額外上方列撐高；hover tooltip、Check 成功狀態與失敗警示色正確，且複製文字不含按鈕內容。
- Mermaid 一般狀態不超出正文。
- 每張 Mermaid 都能透過按鈕、點圖與鍵盤開啟。
- 放大、縮小、重設、拖曳、滾輪、Esc 與 focus restore 正常。
- 手機寬度與列印模式沒有版面破壞。
- Browser console 沒有 Mermaid render error 或未捕捉例外。

若任何測試、build 或驗收失敗，請直接分析並修正，重跑直到通過。最終回覆列出實際修改檔案、測試與 build 結果；不要聲稱未實際驗證的瀏覽器行為已通過。
