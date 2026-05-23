---
name: llm-repo-raw-capture
description: 將已完成的深度網路搜尋結果整理到本地 llm-repo 的 raw 資料層，供使用者之後手動 ingest 到 wiki。當任一 AI 工具已完成深度網路搜尋並需要保存可追蹤來源筆記時使用；也適用於 AGENTS.md 或 CLAUDE.md 的深度搜尋委派、「整理到 raw」、「寫入 llm-repo raw」、「保存搜尋結果」，或任何需要在最終回覆前保存已搜尋來源的流程。
---

# LLM Repo Raw Capture

## 目的

將深度搜尋後值得留存的事實、來源與判斷邊界整理成新的 raw Markdown snapshot。此 skill 只新增 raw 來源資料，不更新、不刪除既有 raw，不執行正式 wiki ingest。

## Workflow

1. 確認輸入包含搜尋脈絡：使用者原始問題、搜尋主題、搜尋日期、已查 URL、來源發布日期或版本日期、關鍵結論、資訊衝突點與仍無法確認的範圍。
2. 若目前對話或工具輸出已包含足夠資訊，直接整理；不要為了補格式重新搜尋。
3. 定位 raw 根目錄：以目前使用者 home 目錄作為前綴，組成 `<home>\.claude\llm-repo\raw`。在 PowerShell 優先用 `$HOME` 或 `$env:USERPROFILE` 解析；不得硬編碼 `C:\Users\<username>`。若路徑不存在或無法寫入，停止寫入並回報原因。
4. 決定輸出檔案：
   - 永遠新增 raw 檔案，不得修改、刪除、覆蓋或合併既有 raw 檔案。
   - 檔名使用 `kebab-case-YYYY-MM-DD.md`，日期使用執行當天日期；例如 `codex-search-behavior-2026-05-23.md`。
   - 若同一天同主題檔案已存在，在日期後加入遞增序號，例如 `codex-search-behavior-2026-05-23-2.md`。
   - 多主題只有在日後很可能拆成不同 wiki page 時才拆成多個新檔。
5. 寫入 raw：
   - 不處理既有 raw 的同步、去重、整併或維護；這些工作只能由使用者手動執行。
   - 新檔使用簡潔結構：標題、整理日期、來源、結論、細節、衝突與未確認範圍、待 ingest 備註。
   - 來源需列出 URL、發布日期或版本日期、查閱日期；無日期時標註「來源未標示日期」。
   - 區分官方文件、release note、issue tracker、社群回報與本機實測；推論必須標註為推論。
6. 嚴守邊界：
   - 不修改 `wiki/`、`wiki/index.md`、`wiki/log.md` 或 `docs/`。
   - 不寫入 API key、token、cookie、帳號密碼或私人識別資訊。
   - 不把單一來源的長段內容完整複製進 raw；以摘要與來源連結保存。

## 回報

完成後回報新增的 raw 檔案路徑。若未能寫入，回報阻塞原因與已整理但尚未落盤的主題名稱。
