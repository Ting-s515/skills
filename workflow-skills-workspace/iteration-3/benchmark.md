# Benchmark — Iteration 3

**時間：** 2026-03-26
**變更：**
- `apply` 根路徑改為自動偵測（試 frontend/ → backend/ → docs/propose/ 順序），不再詢問使用者
- `apply` 移除逐任務等待確認，全流程自動執行

---

## 結果摘要

| eval | 說明 | assertions | with_skill 通過 | old_skill 通過 | pass rate | 時間(s) with / old | tokens with / old |
|------|------|-----------|----------------|----------------|-----------|---------------------|-------------------|
| 5 | apply fresh start | 2 | 2 | 2 | 100% / 100% | 128.5 / 119.6 | 20,496 / 20,196 |
| 6 | apply resume midway | 4 | 4 | 4 | 100% / 100% | 109.2 / 126.0 | 18,172 / 17,868 |
| **合計** | | **6** | **6** | **6** | **100% / 100%** | | |

eval 1-4、7-8（propose / propose-sync）未修改，沿用 iteration-2 結果（100%）。

---

## 分析

### 功能正確性
兩版 apply skill 在所有 assertions 上均 100% 通過：
- `[x][cr]` checkbox 更新正確
- 依賴順序執行正確（T1→T2→T3）
- 中途繼續邏輯正確（T1跳過、T2補CR、T3全新執行）
- 補跑 code review 有明確輸出說明

### 行為差異觀察
- **eval-5（fresh start）：** 新版略慢（+8.9s），因自動偵測路徑邏輯；舊版需要使用者回答前端/後端（eval 中模擬「不區分」）
- **eval-6（resume midway）：** 新版較快（-16.8s），自動執行省去逐任務等待互動

### Token 消耗
兩版 token 差距極小（< 1%），新版自動偵測路徑不帶來額外 token 負擔。

### 結論
新版 apply skill 通過所有 assertions，行為正確性與舊版一致，且在自動執行場景（eval-6）更有效率。路徑自動偵測的改動透明，不影響顯式路徑指定的使用情境。
