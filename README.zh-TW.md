<p dir="auto">
  <a href="./README.md"><img src="https://img.shields.io/badge/docs-English-blue" alt="English" /></a>
  <a href="./README.zh-TW.md"><img src="https://img.shields.io/badge/docs-%E7%B9%81%E9%AB%94%E4%B8%AD%E6%96%87-yellow" alt="繁體中文" /></a>
</p>

Ting-s515 維護的個人 AI agent skills 與 workflow instructions。

這個 repository 是公開的 skill library，收錄可重用的 agent 行為，例如需求規劃、BDD 測試產生、code review、文件流程、本地知識庫查詢與網路搜尋結果保存。

## 相關 Workflow

這個 repository 是 skill library。每個 skill 都可以獨立使用，但穩定的 AI-assisted development process 通常不只是單一 prompt，而是需要一套可重複執行的流程。

如果你想參考更完整、可靠的 Specification-Driven Development（SDD）workflow，可以查看我的 [SDD Workflow](https://github.com/Ting-s515/SDD-workflow) repository。該 repo 說明 `propose`、`apply`、`propose-sync` 如何串接，並整理它們會直接呼叫的 dependency skills。

## Repository 結構

- `*/SKILL.md` - 每個 skill 的入口文件。
- `*/scripts/` - skill 可選用的輔助腳本。
- `*/references/`、`*/templates/`、`*/examples/` - 只有在 skill 要求時才載入的輔助資料。
- `AGENTS.md` - 給 Codex 使用的專案規則。
- `CLAUDE.md` - 給 Claude 使用的專案規則。

## Skill 索引

| Skill | 用途 | 使用時機 |
| --- | --- | --- |
| [`ac-to-test`](ac-to-test/) | 將驗收條件轉成預設紅燈的測試骨架。 | 已有 `AC.md` 或 Given/When/Then 驗收條件，且想先建立實作前的測試邊界。 |
| [`apply`](apply/) | 依 test-first 流程實作已規劃好的 proposal。 | 已有 `docs/propose/...` 功能資料夾，並要開始或繼續實作。 |
| [`bdd-unit-test`](bdd-unit-test/) | 為既有程式碼補上 BDD 風格單元測試。 | 需要針對指定檔案補 Happy Path、Edge Case 與 Error Case 測試。 |
| [`clarify-flow`](clarify-flow/) | 將混亂的業務流程整理成精確結構化步驟。 | 需求中分支、迴圈或判斷條件混在文字裡，不容易對齊。 |
| [`code-reviewer`](code-reviewer/) | 對照業務需求審查程式碼變更。 | 需要確認實作是否符合規格、User Story 或流程文件。 |
| [`explaining-code`](explaining-code/) | 用結構化說明與圖表解釋程式、工具或架構。 | 需要理解某段邏輯、技術概念或系統流程如何運作。 |
| [`export-ac`](export-ac/) | 產出 `AC.md` 驗收準則文件。 | 明確要在實作前建立 Acceptance Criteria。 |
| [`export-conversation`](export-conversation/) | 將目前對話匯出為 Markdown。 | 需要保留脈絡，交給其他模型或下一個對話接續。 |
| [`export-feature-file`](export-feature-file/) | 將行為規格轉成可執行的 `.feature` 檔。 | 需要給 Cucumber、Behave、Reqnroll 等測試框架使用的 Gherkin。 |
| [`export-gherkin`](export-gherkin/) | 將需求或邏輯轉成可讀的 Gherkin 規格。 | 需要用 Given/When/Then 與 PM、QA 或客戶對齊，而不是直接產生測試檔。 |
| [`fleet-review`](fleet-review/) | 啟動多代理審查並交叉驗證結果。 | 明確以 `fleet-review` 搭配規格路徑要求審查。 |
| [`llm-repo`](llm-repo/) | 從本地 LLM 知識庫載入相關 wiki 頁面。 | 需要根據本地 `wiki/` 內容回答問題。 |
| [`llm-repo-raw-capture`](llm-repo-raw-capture/) | 將深度搜尋結果保存為本地 raw knowledge snapshot。 | 完成網路搜尋後，需要留下可追蹤來源筆記供後續 ingest。 |
| [`plan-doc`](plan-doc/) | 從程式碼與需求產出實作規格文檔。 | 需要建立可交給下一個 agent 實作的 `*.plan.md`。 |
| [`propose`](propose/) | 將需求整理成澄清流程、Gherkin 與任務清單。 | 需要在實作前規劃功能，或先分流 bug fix。 |
| [`propose-sync`](propose-sync/) | 將已完成 proposal 狀態同步回需求文件。 | 需要把 `docs/propose/` 的完成狀態回寫到原始規格。 |
| [`react-design`](react-design/) | 提供 React component、hook、service 與狀態設計準則。 | 正在建立或重構 React 程式碼，需要架構邊界。 |
| [`remove-nul`](remove-nul/) | 移除 Windows 保留裝置名稱造成的異常檔案。 | `git status` 顯示 `nul`、`con`、`aux` 等一般工具刪不掉的檔案。 |
| [`req-interview`](req-interview/) | 進行互動式需求或架構訪談。 | 需要討論邊界案例、遺漏情境或技術決策，直到收斂。 |
| [`search-local-skill`](search-local-skill/) | 搜尋本機 skill 目錄與描述。 | 需要列出、尋找或瀏覽可用的 local skills。 |
| [`skill-creator-plus`](skill-creator-plus/) | 建立、改善與評測 skills。 | 需要建立新 skill、優化既有 skill，或 benchmark skill 行為。 |
| [`slim-doc`](slim-doc/) | 壓縮既有 Markdown 規格，移除過多實作細節。 | 需要縮短文件，但保留 API、圖表與核心資料結構。 |
| [`web-search`](web-search/) | 對時效性問題強制執行最新網路查證。 | 問題涉及目前版本、新聞、價格、政策或近期事實。 |
| [`writing-blog-post`](writing-blog-post/) | 撰寫結構化 Markdown blog 文章。 | 明確要求撰寫或整理成 blog 文章。 |
| [`writing-markdown`](writing-markdown/) | 產出結構化 Markdown 技術文件。 | 需要技術筆記、設計文件、流程說明或圖表化文件。 |
| [`writing-training-doc`](writing-training-doc/) | 建立做中學風格的技術訓練材料。 | 需要 Lab、SOP、新人訓練或實作型課程內容。 |

## 使用方式

每個 skill 都應從自己的目錄讀取。先閱讀目標 skill 的 `SKILL.md`，再依照 skill 指示載入 referenced files。

若要在其他 agent 環境使用這些 skills：

1. 複製需要的 skill 目錄。
2. 保留原本的目錄結構。
3. 保留 `SKILL.md` frontmatter。
4. 執行任何 script 前，先在你的環境中檢查內容。

## License

本 repository 使用 [MIT License](LICENSE) 授權。

你可以依 MIT 條款使用、複製、修改、散布與再授權這些內容。請保留 copyright notice 與 license text。
