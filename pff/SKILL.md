---
name: pff
description: Use only when the user's message explicitly contains the "pff" keyword. Scan the current project's docs directory to identify what Theon contributed to the project, then consolidate those contribution materials into a standalone Markdown file under the user's .claude/pff directory. Convert the collected evidence into performance review materials and draft narratives aligned with PFF evaluation criteria. Highlight measurable impact, professional growth, ownership, teamwork, and problem-solving contributions.
---

# PFF 評分表

## 使用流程

1. 只在使用者訊息明確包含 `pff` 時使用此技能。
2. 從目前工作區判斷專案根目錄，掃描該專案底下的 `docs` 目錄。
3. 掃描 `docs` 的目的，是統整 `Theon` 對此專案做過哪些事情，作為撰寫 PFF 的材料；不要把文件摘要本身當成最終目的。
4. 掃描 `docs` 內的 Markdown 與純文字文件，優先讀取與需求、規格、提案、任務、回顧、決策紀錄、測試策略、bug fix、review 結果相關的內容。
5. 將作者 `author` 固定指定為 `Theon`；若文件內已有作者欄位，只整理作者為 `Theon` 的內容；若文件沒有作者欄位，仍以 `Theon` 作為本次 PFF 整理對象。
6. 從文件內容回推並擷取可支撐 PFF 敘述的貢獻素材：完成事項、技術決策、問題分析、協作紀錄、風險處理、品質改善、測試或驗證結果、可量化影響。
7. 將資訊統整到目前執行者的 home 目錄下 `.claude/pff`，輸出為獨立 Markdown 檔案；路徑必須動態解析目前使用者，不可硬編碼特定帳號名稱。輸出檔名使用專案根目錄名稱並加上 `.md`，例如 Windows 使用 `%USERPROFILE%\.claude\pff\<project-root-name>.md` 或 `$env:USERPROFILE\.claude\pff\<project-root-name>.md`，macOS/Linux 使用 `$HOME/.claude/pff/<project-root-name>.md`。
8. 若專案根目錄名稱包含檔名不合法字元，先轉成安全檔名再輸出；若目標目錄不存在，先建立目錄；若同專案摘要檔已存在，更新內容而不是分散產出多個重複檔案。
9. 不要把缺少來源支撐的內容寫成既成事實；可推論內容需標示為推論或待確認。

## 輸出格式

輸出的 Markdown 必須包含：

- `author: Theon`
- 掃描來源範圍與產出時間
- 專案貢獻素材
- 對應 PFF 評分面向
- 可追溯來源
- 可直接用於績效回顧的敘述草稿
- 待補資料或需要 Theon 確認的項目

## 專業可信度 Profession

能夠展現相當深度與廣度的專業知識及技能
能夠信守對團隊成員所允諾的資源、時間、或處理事項等
能夠達到專案所要求的產出品質

## 組織能力 Organization

有多項被指派的工作時，能夠按照事情的輕重緩急排定其優先次序
能夠準確估計完成被指派的工作所需的時間與資源
能夠清楚定義工作中的瓶頸或關鍵步驟


## 發現、分析及解決問題的能力 Problem Solving

能夠快速地吸收與消化新資訊
能夠提出適當的問題以釐清複雜或不明確的狀況
能夠分析並明確指出各項問題背後的根本原因且提出適合的解決方案

## 溝通協調能力 Communication

在處理和專案相關的工作項目時，能夠主動清楚的說明在工作上造成的影響並整合意見
能夠傾聽及詢問不同立場的觀點，並且圓融地表達具爭議性的己見

## 對專案的投入程度及承諾 Commitment

被要求就所屬之工作項目提供協助時，能夠樂意配合
能夠視自己為專案工作項目的負責人並主動積極把專案工作完成

## 清楚的邏輯表達能力 Presentation

能夠表達意見言之有物，不前後矛盾
能夠簡潔、有系統、一致性的說明己見
能夠以讓人容易了解的方式，清楚解釋複雜的觀念和想法

## 對專案工作氣氛的影響 Morale Influence

能夠以積極的態度面對工作難題與挑戰
能夠正面影響專案士氣

## 自評能力之強項以及需加強之部份
1. 強項：
```
```
2. 需加強之部份：
```
```
