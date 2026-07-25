---
name: build-static-docs-site
description: 建立或更新由 Markdown 教材產生的純靜態文件網站，固定使用 HTML、CSS、MJS、build-time Markdown render、淺暖色雙欄版面與可縮放 Mermaid 閱讀器。當使用者要求建立 docs-web、將 docs 轉成網站、重製相同教材閱讀介面、維護靜態文件網站架構，或修正 Mermaid 閱讀體驗時使用；只修改教材文字或建立一般動態 Web 應用時不要使用。
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

1. 解析目標 repository root，讀取 `AGENTS.md`、Git status、`docs/` 與既有 `docs-web/`。
2. 判斷任務類型：
   - `docs-web/` 不存在：複製 `assets/docs-web/` 建立基準結構。
   - `docs-web/` 已存在：先讀現況，只修改需求涉及的檔案，不以模板覆蓋既有變更。
3. 首次建立時，只調整專案識別內容、教材分類規則與內容相依測試；保留設計契約測試。
4. 維持 build-time Markdown render。所有教材預先寫入單一 HTML；client 不得在頁面切換時 `fetch()` Markdown。
5. 維持固定淺暖色 tokens、桌面雙欄導覽、行動版、同頁 hash、responsive 與 print styles。
6. 維持 Mermaid 正文 `width: 100%`，不得突破內容卡片；細節只透過原生 dialog 放大閱讀器查看。
7. 不主動改寫 `docs/*.md` 教材內容，除非使用者同時要求修改教材。
8. 依目標 repository 規則處理 tests、build、review、staging 與 commit，不得納入無關變更。

## 固定技術邊界

- 使用原生 HTML、CSS 與 ES modules；建置腳本使用 `.mjs`。
- Markdown 於 build-time 以 Unified/Remark/Rehype 轉換，並支援 GFM。
- Mermaid 由 npm 套件隨 `app.mjs` bundle，不使用 CDN。
- `dist/` 是完整靜態輸出；不得加入 runtime framework、SSR 或 API server。
- 本機預覽只綁定 `127.0.0.1:18100`，避免占用常見的 8080/8100。
- Mermaid 使用 `securityLevel: "strict"`，dialog 支援按鈕、滾輪縮放、拖曳、重設、Esc 關閉與 focus restore。

## 驗證

在目標 repository 依序執行：

```powershell
npm --prefix .\docs-web install
npm --prefix .\docs-web test
npm --prefix .\docs-web run build
node "$env:USERPROFILE\.codex\skills\build-static-docs-site\scripts\validate-static-docs-site.mjs" .
```

若 `node_modules/` 已符合 lockfile，可省略 `npm install`。測試或 build 失敗時先修正並重跑，直到通過或確認為不可自行排除的環境阻塞。

若環境允許控制瀏覽器，再驗證導覽切換、heading deep link、Mermaid 開啟、縮放、拖曳、重設、Esc 關閉與 focus restore。若瀏覽器受政策或環境限制，不得繞過限制，也不得宣稱互動已實測通過。

## 資源

- `references/design-spec.md`：完整設計、架構、互動與驗收規格。
- `assets/docs-web/`：首次建立時使用的固定基準模板；不包含 `package-lock.json`、`node_modules/` 與 `dist/`。
- `scripts/validate-static-docs-site.mjs`：檢查結構、scripts、暖色 tokens、無 runtime fetch、Mermaid 寬度與 dialog 互動契約。

修改基準設計時，需同步更新規格、asset template 與 validator，避免三者漂移。
