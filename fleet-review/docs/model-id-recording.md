# fleet-review 模型 ID 紀錄策略

## 背景

`fleet-review` 目前以本地 `codex exec` 啟動 Codex 審查代理，並透過 `-m "gpt-5.5"` 指定模型。先前測試中，Codex 審查代理最後輸出：

```text
CODEX_MODEL: gpt-5
```

但同一次 `codex exec` 的本地 transcript header 顯示：

```text
model: gpt-5.5
provider: openai
sandbox: read-only
reasoning effort: high
```

因此需要明確定義：`fleet-review` 應如何紀錄模型資訊，以及哪些資料不能當作雲端實際模型 ID 的可靠來源。

## 結論

在維持本地 `codex exec`、不直接接 OpenAI API key 的架構下，目前沒有穩定可靠的方法可取得「雲端實際使用的 API response model id」。

`fleet-review` 不應要求模型在 prompt 中自報模型 ID，因為該輸出只是模型生成文字，不是執行環境 metadata，也不是 API response metadata。

## 為何取不到雲端實際模型 ID

若直接呼叫 OpenAI Responses API，API 回應物件會包含 `model` 欄位，可作為該次 response 使用模型的權威 metadata。

但 `fleet-review` 的目標是跑本地 `codex exec`，不是直接呼叫 Responses API。`codex exec` 是一層本地 CLI agent runtime，會負責呼叫雲端模型並處理工具、sandbox、輸出檔等流程。以目前可觀察的 CLI 行為：

1. `-m, --model <MODEL>` 可指定本次 agent 應使用的模型。
2. `--json` 事件流會輸出 thread、turn、item、usage 等事件。
3. `-o, --output-last-message <FILE>` 只保存 agent 最後訊息。
4. 目前沒有公開穩定欄位可直接取得每次底層 API response 的 `model`。

因此，本地 `codex exec` 架構下能穩定取得的是「本地 wrapper 要求使用的模型」，不是「雲端 API 最終實際回傳的 response.model」。

## 不可靠方法

不要在 prompt 中要求：

```text
最後一行必須輸出：CODEX_MODEL: <你實際使用的模型 ID>
```

原因：

1. 這是模型生成內容，不是 CLI 或 API metadata。
2. 模型可能不知道實際部署 ID、alias 解析結果或 fallback 狀態。
3. 輸出可能與 `codex exec -m` 參數或 CLI transcript header 不一致。
4. 使用者容易誤解為雲端實際模型 ID。

## 建議的本地替代方法

在不接 OpenAI API key、不改成直接呼叫 Responses API 的前提下，`fleet-review` 應由 wrapper 自己紀錄可保證的本地資訊。

建議輸出：

```text
CODEX_REQUESTED_MODEL: gpt-5.5
CODEX_MODEL_SOURCE: requested_by_wrapper
CODEX_CLI_VERSION: codex-cli 0.125.0
```

可選 debug 輸出：

```text
CODEX_CLI_HEADER_MODEL: gpt-5.5
CODEX_CLI_HEADER_MODEL_SOURCE: cli_transcript_header
```

但 `CODEX_CLI_HEADER_MODEL` 只能作為輔助資訊，不應在正式報告中宣稱為雲端實際模型 ID，因為它依賴 Codex CLI 的輸出格式，不是公開穩定 API。

## 報告呈現建議

正式報告建議改為：

```text
代理：Claude（AGENT_MODEL: unknown）+ Codex（requested: gpt-5.5, source: wrapper）
```

若有紀錄 CLI header，可附在 debug 或 raw metadata 區塊：

```text
Codex CLI header model: gpt-5.5
```

但不要寫成：

```text
Codex actual cloud model: gpt-5.5
```

除非未來 `codex exec` 提供公開穩定欄位，或 `fleet-review` 改成直接呼叫 Responses API 並保存 `response.model`。

## 後續修改方向

`fleet-review/SKILL.md` 後續應做以下調整：

1. 移除 prompt 中的 `CODEX_MODEL: <你實際使用的模型 ID>` 要求。
2. 在執行 `codex exec` 前由 wrapper 設定 `CODEX_REQUESTED_MODEL="gpt-5.5"`。
3. 在 Codex 輸出後由 wrapper 追加 `CODEX_REQUESTED_MODEL` 與 `CODEX_MODEL_SOURCE`。
4. 若需要，從 CLI transcript header 解析 `model:` 作為 debug metadata，但不可視為權威雲端模型 ID。
5. 最終報告使用 `requested: gpt-5.5`，避免讓使用者誤以為已取得雲端實際 response metadata。
