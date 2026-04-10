# Fleet Review 工作流程圖

```mermaid
flowchart TD
    Start([使用者觸發 fleet-review]) --> S0

    subgraph S0["步驟 0：前置檢查"]
        ChkCodex{Codex 可用?}
        GetDiff[取得 BASE 分支</br>產生 diff 檔案]
        NoDiff([無 diff，停止])
        Fallback[改用 3 Claude 子代理模式]

        ChkCodex -->|是| GetDiff
        ChkCodex -->|否| Fallback
        GetDiff --> ChkEmpty{diff 為空?}
        ChkEmpty -->|是| NoDiff
        ChkEmpty -->|否| S1
        Fallback --> S1
    end

    subgraph S1["步驟 1：並行審查代理（單一回應同時啟動）"]
        direction LR
        AgentA["Claude Agent A</br>邏輯 / 安全 / 型別 / API 合約"]
        AgentB["Claude Agent B</br>邊界情況 / 效能 / 並發 / 測試"]
        AgentC["Codex Agent</br>全面審查"]
    end

    S0 --> S1
    S1 --> S2

    subgraph S2["步驟 2：彙整原始發現"]
        Collect[收集所有 FINDING 區塊]
        ShowSummary[向使用者展示原始發現摘要]
        AllEmpty{所有代理皆</br>NO_FINDINGS?}
        Pass([審查通過，無問題])

        Collect --> ShowSummary --> AllEmpty
        AllEmpty -->|是| Pass
        AllEmpty -->|否| S3
    end

    subgraph S3["步驟 3：獨立驗證代理（並行啟動）"]
        direction LR
        ValClaude["Claude 驗證者</br>逐條讀原始碼</br>CONFIRMED / REFUTED / LIKELY"]
        ValCodex["Codex 驗證者</br>逐條讀原始碼</br>CONFIRMED / REFUTED / LIKELY"]
    end

    subgraph S4["步驟 4：交叉比對裁決"]
        Compare[比對兩驗證者裁決]
        High["✅ 高/中信心</br>CONFIRMED + CONFIRMED/LIKELY"]
        Low["⚠️ 低信心</br>LIKELY + LIKELY"]
        Dispute["❓ 有爭議</br>CONFIRMED + REFUTED"]
        Exclude["❌ 排除（誤報）</br>REFUTED + REFUTED/LIKELY"]

        Compare --> High
        Compare --> Low
        Compare --> Dispute
        Compare --> Exclude
    end

    S3 --> S4

    S4 --> Report["輸出最終報告</br>🔴 P0/P1 必須修正</br>🟠 P2 建議改善</br>🟡 低信心供參考</br>❓ 有爭議附雙方觀點</br>統計：原始 N → 確認 N，排除 N"]

    Report --> Cleanup[rm diff 暫存檔]
    Cleanup --> Done([完成])
```

## Sub-agent 數量總覽

| 步驟 | Sub-agent 數 | 說明 |
|------|-------------|------|
| 步驟 0 前置檢查 | **0** | 只跑 Bash 指令 |
| 步驟 1 審查代理 | **3** | Claude-A + Claude-B + Codex（並行） |
| 步驟 2 彙整發現 | **0** | 主代理自行整理 |
| 步驟 3 獨立驗證 | **2** | Claude 驗證者 + Codex 驗證者（並行） |
| 步驟 4 最終報告 | **0** | 主代理自行比對輸出 |
| **總計** | **5** | |

---

## 代理數量總覽

| 階段 | 正常模式 | Codex 不可用 |
|------|----------|--------------|
| 審查代理 | Claude-A + Claude-B + Codex | Claude-A + Claude-B + Claude-C |
| 驗證代理 | Claude 驗證者 + Codex 驗證者 | Claude（延伸思考）+ Claude（一般） |
| **合計** | **5 個代理** | **5 個代理** |

## 裁決交叉比對規則

| Claude 驗證者 | Codex 驗證者 | 結果 |
|---|---|---|
| CONFIRMED | CONFIRMED | ✅ 高信心，納入 |
| CONFIRMED | LIKELY | ✅ 中信心，納入 |
| LIKELY | CONFIRMED | ✅ 中信心，納入 |
| LIKELY | LIKELY | ⚠️ 低信心，標注後納入 |
| CONFIRMED | REFUTED | ❓ 有爭議，附雙方觀點 |
| REFUTED | CONFIRMED | ❓ 有爭議，附雙方觀點 |
| LIKELY | REFUTED | ❌ 排除 |
| REFUTED | LIKELY | ❌ 排除 |
| REFUTED | REFUTED | ❌ 排除（誤報） |
