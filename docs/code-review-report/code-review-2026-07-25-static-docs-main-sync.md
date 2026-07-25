# Code Review 紀錄 — 2026-07-25（第 1 輪）

## 📋 Code Review 摘要

**審查範圍：** 將 `codex` 分支的 `build-static-docs-site/` 完整同步至
`main`，並檢查技能實作、build、測試、validator 與 eval runner。

**整體評估：** ⚠️ 同步內容一致且驗證通過，但來源技能仍有四項既有 Warning。

---

### 📐 規格符合度

#### ✅ 符合規格的項目

- `main` 自共同祖先起未修改或建立 `build-static-docs-site/`，沒有 Git 衝突。
- 來源與 `main` worktree 均為 39 個檔案，逐檔 SHA-256 完全一致。
- diff 未包含 `dist/`、`node_modules/`、`package-lock.json` 或
  `eval-results-bdd/` 等生成物。
- `npm test` 共 8 項測試全部通過。
- `npm run build` 成功產生 3 份 fixture 教材。
- `validate-static-docs-site.mjs` 驗證通過。
- 三組回覆層 eval 共 18 條 expectations 全部通過。

#### ❌ 不符合或缺漏的項目

- Unicode 文件切換後，active 導覽狀態可能遺失。
- Markdown 連結尚未拒絕危險 URI scheme。
- greenfield 固定結構缺少規格要求的 `prompt.md`。
- 404 回應缺少 `cache-control: no-cache`。

---

### 🔴 必須修正（Critical）

無。

---

### 🟠 建議改善（Warning）

#### 問題 1：Unicode 文件切換後不會保留 active 導覽狀態

- **檔案：** `build-static-docs-site/assets/docs-web/src/app.mjs:224`
- **問題：** `link.hash` 會百分比編碼 Unicode，但 `activePanel.id` 保留原始
  Unicode，兩者直接比較會失敗。
- **影響：** 切換非 ASCII 文件後，`.is-active` 與
  `aria-current="page"` 可能被移除。
- **建議：** 解碼 `link.hash.slice(1)` 後再比較，並新增 Unicode hash
  切換測試。

#### 問題 2：Markdown 連結允許危險 URI scheme

- **檔案：** `build-static-docs-site/assets/docs-web/script/build-site.mjs:84`
- **問題：** `isExternalLink()` 將所有 URI scheme 視為合法外部連結，
  `javascript:` 與 `data:` 可能原樣輸出。
- **影響：** 惡意或遭竄改的教材可能植入需點擊觸發的 XSS。
- **建議：** 採用 `http:`、`https:`、`mailto:`、`tel:` allowlist，拒絕
  其他 protocol，並加入危險 scheme 測試。

#### 問題 3：首次建立的固定目錄缺少 prompt.md

- **檔案：** `build-static-docs-site/SKILL.md:23`
- **問題：** skill 指示直接複製 `assets/docs-web/`，但 asset 沒有規格要求的
  `prompt.md`，validator 與測試也未檢查。
- **影響：** greenfield 執行可能產生不完整的固定結構。
- **建議：** 在來源 skill 的 asset 或建立流程補入 `prompt.md`，並讓
  validator 驗證。

#### 問題 4：404 回應缺少 no-cache header

- **檔案：** `build-static-docs-site/assets/docs-web/script/server.mjs:24`
- **問題：** 200 回應有 `cache-control: no-cache`，404 回應沒有。
- **影響：** 未符合規格對所有回應的 cache header 契約。
- **建議：** 在 404 header 加入 `cache-control: no-cache`，並增加 server
  response 測試。

---

### ⚪ 使用者自行決定（註解類問題）

無。
