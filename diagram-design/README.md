# Diagram Design Skill（繁體中文版）

此資料夾是可獨立複製使用的 Agent Skill，包含 `SKILL.md`、參考文件、範本與執行所需的輔助腳本；範例 HTML 不包含在內。

## 複製與使用

將整個技能資料夾複製到你使用的 AI agent 所設定的 skills 目錄，並可在目的位置命名為 `diagram-design`。安裝位置依 agent 而異，本 skill 不要求固定路徑。例如：

```text
<agent-skills-directory>/diagram-design/
```

請遵循該 agent 的技能發現慣例，並確認 `SKILL.md` 位於技能資料夾根目錄，且 `references/`、`assets/`、`scripts/` 子目錄完整保留。此技能使用標準 `SKILL.md` 格式；支援 Agent Skills 格式的 agent 可讀取此技能指示與附帶資源。

## 必要環境

- Agent 執行環境需支援 `SKILL.md` 技能格式，並能讀寫本機檔案及使用 shell 執行 Python 輔助腳本。
- Python 3.9 或更新版本，用於 Mermaid、draw.io、Excalidraw 匯入資料擷取、自我檢查及 SVG 匯出。這些腳本主要使用 Python 標準函式庫。
- 若要匯出 PNG，需在執行腳本的同一個 Python 環境安裝 Playwright，並安裝 Chromium 瀏覽器：

  ```bash
  python -m pip install playwright
  python -m playwright install chromium
  ```

  PNG 匯出為選用功能；未安裝 Playwright 時，HTML、匯入工具、自我檢查與 SVG 匯出仍可使用。

## 網路需求

圖表建立、HTML／SVG 輸出和本機範本使用不需要 MCP、Node.js、npm、API key 或網路連線。以網址進行品牌樣式引導或載入 Google Fonts 時才需要網路；離線時可使用本機檔案／自訂 token，並依風格指南選擇系統字型。

## 檔案用途

- `SKILL.md`：技能入口與工作規則。
- `references/`：各類型、匯入格式、樣式、輸出與驗證說明；文件連結均相對於此資料夾。
- `assets/`：HTML 範本與必要圖示片段，不含範例畫廊。
- `scripts/`：資料擷取、輸出及自我檢查工具。
- `LICENSE`、`THIRD_PARTY_LICENSES.md`：授權資訊。

此資料夾由上游儲存庫的建置工具產生。修改翻譯時請更新技能來源目錄中的 `SKILL.zh-TW.md` 或 `README.zh-TW.md`，再重新產生副本，以免建置時覆寫翻譯。
