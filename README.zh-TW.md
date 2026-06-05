# Ting-s515 Skills

Ting-s515 維護的個人 AI agent skills 與 workflow instructions。

這個 repository 是公開的 skill library，收錄可重用的 agent 行為，例如需求規劃、BDD 測試產生、code review、文件流程、本地知識庫查詢與網路搜尋結果保存。

預設 GitHub 文件為英文版，請見 [README.md](README.md)。

## Repository 結構

- `*/SKILL.md` - 每個 skill 的入口文件。
- `*/scripts/` - skill 可選用的輔助腳本。
- `*/references/`、`*/templates/`、`*/examples/` - 只有在 skill 要求時才載入的輔助資料。
- `AGENTS.md` - 給 Codex 使用的專案規則。
- `CLAUDE.md` - 給 Claude 使用的專案規則。

## Skill 分類

- 規劃與實作流程：`propose`、`apply`、`propose-sync`、`plan-doc`、`req-interview`。
- BDD 與驗收條件：`export-ac`、`export-gherkin`、`export-feature-file`、`ac-to-test`、`bdd-unit-test`。
- Review 與分析：`code-reviewer`、`fleet-review`、`explaining-code`、`react-design`。
- 文件與寫作：`slim-doc`、`clarify-flow`、`writing-training-doc`、`writing-markdown`、`writing-blog-post`。
- 知識庫與搜尋支援：`llm-repo`、`llm-repo-raw-capture`、`web-search`。
- 工具與維護：`export-conversation`、`pff`、`skill-creator-plus`、`search-local-skill`、`remove-nul`。

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
