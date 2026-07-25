# Code Review 紀錄 — 2026-07-25（第 2 輪）

## 📋 Code Review 摘要

**審查範圍：** `dialog-keydown.mjs` 的 Escape helper、`app.mjs` 的 dialog 接線、`build-site.test.mjs` 的行為測試、`design-spec.md` 的固定結構與測試契約，以及 `validate-static-docs-site.mjs` 的模板驗證規則。
**整體評估：** ✅ 符合規格可合併。第 1 輪 Warning 已解決；本輪未發現 correctness、regression、安全性或規格偏差 findings。

---

### Findings

無 findings。

---

### 📐 規格符合度

#### ✅ 符合規格的項目

- **第 1 輪 Warning 已解決：** `build-site.test.mjs:131-169` 直接呼叫 `closeDialogOnEscape()`，以 event 與 dialog test double 驗證 Escape 會取消預設行為、只關閉一次並回傳 `true`，以及 Enter 不會取消預設行為、不會關閉並回傳 `false`；不再依賴完整 handler 原始碼 regex。
- **Escape helper 行為正確：** `dialog-keydown.mjs:2-9` 只處理 `event.key === "Escape"`，先執行 `preventDefault()` 再呼叫 `dialog.close()`，非 Escape 分支沒有副作用。
- **整合接線保持明確：** `app.mjs:249` 將 dialog 的 `keydown` 事件直接交給 helper；`app.mjs:248` 的 `close` event 仍統一執行 `restoreDiagram()`，因此 Escape、關閉按鈕與 backdrop 都沿用 SVG/style/DOM/focus 還原流程。
- **固定結構沒有偏差：** `design-spec.md:45`、`design-spec.md:59` 已把 `src/dialog-keydown.mjs` 納入固定目錄與單一責任表；模組只承擔 Escape 判斷與關閉，未吸收其他 dialog 狀態或 UI 邏輯。
- **靜態輸出契約維持不變：** `build-site.mjs:274-282` 仍以 `app.mjs` 為唯一 browser entry 並開啟 esbuild bundle；新增 helper 會併入原本的 `dist/app.mjs`，不會新增公開檔案，也不影響 static server 的四個路徑。
- **Validator 降低實作綁定：** `validate-static-docs-site.mjs:93-102` 分別檢查 app 的 keydown/helper 接線與 helper export，不再要求匿名函式、判斷順序及完整呼叫排列；`validate-static-docs-site.mjs:141-150` 同時要求 Escape 與非 Escape 測試契約存在。
- **規格與測試同步：** `design-spec.md:286` 明確要求以事件與 dialog test double 覆蓋關閉及非關閉分支，與新增測試一致。
- **瀏覽器整合驗收通過：** 已提供的 in-app Browser 重測顯示 Esc 後 `dialogOpen=false`、dialog 內 SVG 為 0、來源 SVG 為 1、focus 回到放大按鈕，且 console 無 error/warning。

#### ❌ 不符合或缺漏的項目

無。

---

### 🔴 必須修正（Critical）

無。

---

### 🟠 建議改善（Warning）

無。

---

### ⚪ 使用者自行決定（註解類問題）

無。Helper 註解說明 WebView 相容性與抽離原因，屬於必要的 why 註解。

---

### 驗證與殘餘風險

- 已知驗證：提供的 `node --check` 全部通過、Node tests 8/8、build 成功、validator 成功、`git diff --check` 通過，且 in-app Browser 的 Escape／SVG／focus／console 驗收均通過。
- 本輪獨立重跑四個變更 JavaScript 檔案與新增 helper 的 `node --check`，全部通過；validator 與 `git diff --check` 亦通過。
- 本輪未重新執行完整 Node tests 與 build，因模板目錄目前沒有安裝 `esbuild` 等 dependencies，且審查範圍限制只允許更新報告；本輪依據已提供的 8/8 與 build 成功結果評估。
- 殘餘風險：validator 仍是原始碼靜態契約檢查，不能取代 test runner 或瀏覽器整合測試；目前由直接 helper 行為測試與已完成的 in-app Browser 驗收共同覆蓋，未構成本輪 finding。
