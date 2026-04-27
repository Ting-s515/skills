# 此為 fleet-review 更改需求文檔
- 此技能適用於claude or codex 
- 類似code-reviewer，使用者會提供業務邏輯文檔（需求規格、User Story、API 文件、流程說明等），並要求審查程式碼實作時，必須載入此技能。使用 git diff 比對業務邏輯與程式碼變更，確認功能是否正確實作、找出邏輯衝突、潛在問題與副作用，並檢視是否符合最佳實踐。
- 為手動呼叫，不給模型自動呼叫，避免與 code-reviewer skill 混亂

1. 統一只保留混合模式 claude+ codex
2. ## 步驟 0：前置檢查（0 個 sub-agent）
   1. 指令確認 Codex 可用
   2. 指令確認 Claude 可用
3. ## 步驟 1：並行啟動審查代理（2 個 sub-agent，單一回應同時啟動）
   1. 1 個 claude sub agent ，model= sonnet-4.6 、 effort = high
   2. 1 個 codex sub agent  ，model= gpt-5.5 、 effort = high
4. ## 步驟 2：彙整原始發現（0 個 sub-agent）
5. ## 步驟 3：交叉比對裁決，產出最終報告（0 個 sub-agent）

## 保留
1. 原有的 timeout 機制
2. agent review審查風格

## 最終目的
1. 減少步驟、agent 數量，以減少token usage