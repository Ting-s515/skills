---
name: ac-to-test
description: >
  當使用者提供 AC.md（Acceptance Criteria 驗收準則文件），並要求產出測試骨架時，必須載入此技能。
  從 AC 文件的每一條 Given/When/Then 直接對應產出測試案例，測試名稱帶 AC 編號（AC001_Given..._When..._Should...），
  作為實作前的行為邊界確認，所有測試預設失敗（紅燈），等實作完成後補上真實斷言。
  支援 TypeScript、C#、Java、Python，依照使用者指定語言或詢問後產出對應語言的測試骨架。
  觸發情境包含但不限於：「依照 AC 產出測試」、「ac-to-test」、「根據 AC.md 寫測試」。
  即使使用者只說「先把 AC 轉成測試」，只要有提供 AC.md 路徑或貼上 AC 內容，也應載入此技能。
  注意：此技能用於實作前（無實作檔）；若實作已完成需補測試，請使用 bdd-unit-test 技能。
---

# AC to Test（從 AC 產出測試骨架）

## 目的

將 AC.md 的每一條驗收條件（AC-001, AC-002...）直接轉換為測試骨架：

- 測試名稱帶 AC 編號，1:1 對應 AC 條目
- Given/When/Then 保留為註解，清楚說明行為意圖
- 測試預設失敗（紅燈），強迫實作者回來補上真實斷言
- 不依賴實作檔案，實作前即可執行

## 輸入

- **AC.md 路徑**（或直接貼上 AC 文件內容）
- **目標語言**（TypeScript / C# / Java / Python）— 若未指定，詢問使用者

## 執行步驟

1. **判別目標語言**：若使用者未指定，詢問後再產出
2. **讀取對應語言的 reference 骨架**（見下表）
3. **讀取 AC.md**，識別功能名稱、每條 AC 的編號、分類、Given / When / Then / And
4. **對應測試案例**：每條 AC → 一個測試 block，依 reference 格式產出
5. **寫入測試檔案**，存放於對應語言的測試目錄

## 語言判別規則

| 語言 | 載入 Reference | 輸出位置 | 檔案命名 |
|------|--------------|---------|---------|
| TypeScript | `references/typescript-skeleton.test.ts` | 同目錄的 `__tests__/` | `{feature-name}.test.ts` |
| C# | `references/csharp-skeleton-test.cs` | 對應的 `.Tests` 專案資料夾 | `{FeatureName}Test.cs` |
| Java | `references/java-skeleton-test.java` | `src/test/java/` 對應套件路徑 | `{FeatureName}Test.java` |
| Python | `references/python-skeleton-test.py` | `tests/` 資料夾，保持與 src 相同結構 | `test_{feature_name}.py` |

**執行說明：**
- 判別語言後，**只讀取對應語言的 reference 檔**
- 依照 reference 的骨架格式，將 AC 條目逐一對應填入

## 檔案命名轉換

去掉 `AC-` 前綴，依語言慣例轉換：

| 輸入 AC 檔 | TypeScript | C# | Java | Python |
|-----------|-----------|-----|------|--------|
| `AC-coupon-apply.md` | `coupon-apply.test.ts` | `CouponApplyTest.cs` | `CouponApplyTest.java` | `test_coupon_apply.py` |

## 測試命名規則

格式：`AC{編號}_Given{前置條件}_When{動作}_Should{預期行為}`

- 編號補零對齊：AC-001 → `AC001`，AC-010 → `AC010`
- 從 Given/When/Then 萃取關鍵詞，保持簡潔（3-5 個英文單字）
- 使用業務語言，不使用技術術語
- Python 方法名加 `test_` 前綴

## 紅燈佔位原則

每個測試結尾必須有對應語言的紅燈佔位，確保沒有真實斷言前測試一定失敗。實作完成後移除佔位行並補上真實斷言。

## 輸出規範

1. 寫入對應語言的測試目錄
2. 告知使用者：
   - 測試檔案路徑
   - 共產出幾條測試
   - 下一步：「實作完成後，將各測試的 TODO 替換為實際呼叫，並移除紅燈佔位行」
