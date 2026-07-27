---
name: build-static-docs-site
description: 建立或更新由 Markdown 教材產生的純靜態文件網站，固定使用 HTML、CSS、MJS、build-time Markdown render、淺暖色雙欄版面、可複製 code block 與可縮放 Mermaid 閱讀器。當使用者要求建立 docs-web、將 docs 轉成網站、重製相同教材閱讀介面、維護靜態文件網站架構、增加指令複製功能，或修正 Mermaid 閱讀體驗時使用；只修改教材文字或建立一般動態 Web 應用時不要使用。
---

# 建立純靜態教材網站

## 真相來源

依下列順序執行：

1. 使用者本次明確要求。
2. 目標 repository 的 `AGENTS.md` 與既有實作。
3. `references/design-spec.md` 的完整架構、視覺與驗收規格。
4. `assets/docs-web/` 的可執行基準模板。

主 agent 必須完整讀取 `references/design-spec.md` 後才可修改網站。不要把詳細規格重新摘要成另一份標準，以免多份規格漂移。

## 工作流程

1. 解析目標 repository root，讀取 `AGENTS.md`、Git status、README、`docs/` 與既有 `docs-web/`。
2. 判斷任務類型：
   - `docs-web/` 不存在：複製 `assets/docs-web/` 建立基準結構。
   - `docs-web/` 已存在：先讀現況，只修改需求涉及的檔案，不以模板覆蓋既有變更。
3. 首次建立時，依序從使用者要求、repository 文件與目錄名稱決定網站名稱及說明；不得沿用模板或其他專案的名稱。
4. 依目標 `docs/*.md` 的實際課程結構決定導覽分類；沒有明確分類時使用單一中性群組，不套用特定領域的檔名前綴規則。
5. 內容相依測試必須從目前 `docs/*.md` 或測試 fixture 動態取得教材清單與數量，不得固定目標專案的教材名稱或份數；fixture 應涵蓋非 ASCII、相似檔名與跨文件連結，設計契約測試則保留。
6. 維持 build-time Markdown render。所有教材預先寫入單一 HTML；client 不得在頁面切換時 `fetch()` Markdown。
7. 維持固定淺暖色 tokens、桌面雙欄導覽、行動版、同頁 hash、responsive 與 print styles。
8. 維持 Mermaid 正文 `width: 100%`，不得突破內容卡片；細節只透過原生 dialog 放大閱讀器查看。
9. 維持 code block 右上角緊湊的 icon-only 複製按鈕：使用雙欄 Grid，指令只在左欄捲動，按鈕位於固定 `3rem` 右欄且不得覆蓋指令或增加上方預留列；預設為重疊方框 Copy SVG，hover 或 focus 時 tooltip 從左側展開，成功切換 Check SVG，失敗套警示色；Mermaid 不得套用此按鈕。
10. 不主動改寫 `docs/*.md` 教材內容，除非使用者同時要求修改教材。
11. 依目標 repository 規則處理 tests、build、review、staging 與 commit，不得納入無關變更。

## 固定技術邊界

- 使用原生 HTML、CSS 與 ES modules；建置腳本使用 `.mjs`。
- Markdown 於 build-time 以 Unified/Remark/Rehype 轉換，並支援 GFM。
- Mermaid 由 npm 套件隨 `app.mjs` bundle，不使用 CDN。
- `dist/` 是完整靜態輸出；不得加入 runtime framework、SSR 或 API server。
- code block 使用 Clipboard API 複製完整文字；按鈕只顯示內嵌 SVG，不以可見文字或 emoji 取代 icon，並以獨立 helper 測試成功與不可用分支。
- 本機預覽只綁定 `127.0.0.1:18100`，避免占用常見的 8080/8100。
- Mermaid 使用 `securityLevel: "strict"`，dialog 支援按鈕、滾輪縮放、拖曳、重設、Esc 關閉與 focus restore。
- 網站名稱、導覽分類、課程標題與教材數量屬於目標專案內容，不是 skill 的固定設計契約。

## 驗證

在目標 repository 依序執行下列跨平台指令：

```shell
npm --prefix ./docs-web install
npm --prefix ./docs-web test
npm --prefix ./docs-web run build
```

validator 必須從 agent 已載入的 `build-static-docs-site/SKILL.md` 所在目錄定位，不可硬編碼使用者名稱或假設固定安裝根目錄。下列寫法的正斜線可同時用於 PowerShell 與 macOS/Linux shell：

```shell
node "<skill-directory>/scripts/validate-static-docs-site.mjs" .
```

`<skill-directory>` 必須替換成目前已解析的 skill 絕對目錄。

若 `node_modules/` 已符合 lockfile，可省略 `npm install`。測試或 build 失敗時先修正並重跑，直到通過或確認為不可自行排除的環境阻塞。

若環境允許控制瀏覽器，再驗證導覽切換、heading deep link、code block Copy icon、tooltip、Check 成功狀態、失敗警示色、Mermaid 開啟、縮放、拖曳、重設、Esc 關閉與 focus restore。若瀏覽器受政策或環境限制，不得繞過限制，也不得宣稱互動已實測通過。

## 資源

- `references/design-spec.md`：完整設計、架構、互動與驗收規格。
- `assets/docs-web/`：首次建立時使用的固定基準模板；不包含 `package-lock.json`、`node_modules/` 與 `dist/`。
- `scripts/validate-static-docs-site.mjs`：檢查結構、scripts、暖色 tokens、無 runtime fetch、code block Copy icon 與 Clipboard 狀態，以及 Mermaid 寬度與 dialog 互動契約。

修改基準設計時，需同步更新規格、asset template 與 validator，避免三者漂移。
