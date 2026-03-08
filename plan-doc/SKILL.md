---
name: plan-doc
description: >
  從程式碼檔案與功能需求，產出完整的功能規格實作文檔（*.plan.md）。
  分析現有專案架構，識別需要新增或修改的檔案，以精簡程式碼（保留簽名、省略實作細節）、
  可視化架構圖（Mermaid / ASCII）、API endpoint 規格、request/response 資料結構、邊界情境等呈現，
  讓後續 AI 能夠依照文檔理解功能需求並按步驟實作。
  當使用者提出以下任何需求時必須載入此技能：「plan doc」、、「plan spec」、「分析需要改哪些檔案」、「依照這些檔案產出規格文檔」、「建立功能文檔」，或任何需要從現有程式碼分析並產出功能實作規格的情境。
  注意：此技能用於建立新規格文檔（輸入為程式碼 + 需求描述），精簡既有文檔請使用 slim-doc。
argument-hint: "[功能描述] [檔案路徑1] [檔案路徑2] ..."
---

# plan-doc 功能規格文檔產出

## 目標

分析使用者提供的程式碼檔案與功能需求，產出一份 `*.plan.md`，
讓後續 AI 能夠依照文檔按步驟實作，不需再重新探索程式碼架構。

---

## 工作流程

1. 確認使用者提供的**功能需求描述**與**相關程式碼檔案路徑**（若未提供，詢問）
2. 讀取所有提供的檔案，理解現有架構、設計模式、命名慣例
3. 主動探索延伸檔案：使用者提供的檔案不一定完整，需根據已讀內容判斷是否需要進一步讀取相關檔案
   - 若發現 import / 依賴未提供的模組，追蹤讀取
   - 若需要理解資料流向，讀取對應的 service / repository / model
   - 若涉及路由或設定，讀取相關設定檔
   - 探索到足以完整描述功能實作所需資訊為止
4. 分析實作該功能需要**新增**或**修改**哪些檔案
5. 依照下方文檔結構，產出 `<功能名稱>.plan.md`

---

## 文檔結構

產出的 `.plan.md` 依下方順序組織，主要章節加入 `Step N:` 編號，依實作相依關係排序：

```
> 依照此文檔按步驟實作功能，有相依關係的步驟須完成前置步驟後再進行。

# <功能名稱>

## 功能概述
## 架構概覽
## 異動檔案清單

---

### Backend

## Step 1: <資料模型 / Schema>
## Step 2: <Service / 業務邏輯>
## Step 3: <Controller / API>
...

---

### Frontend

## Step N: <UI 切版 / 靜態畫面>
## Step N+1: <基礎互動邏輯>
## Step N+2: <API 串接 / 詳細功能實作>
...

---

## 注意事項 / 邊界情境
```

若功能**僅涉及後端或前端**，省略不相關的區塊，不加分隔線。

---

## 各區塊撰寫規範

### 功能概述

一段簡短描述：這個功能做什麼、為什麼需要、影響哪些模組。

### 架構概覽

用圖表呈現功能在系統中的位置與資料流向：

- 涉及多個服務 / 模組間的互動 → 優先用 Mermaid sequence diagram
- 說明模組層級關係 → 用 ASCII 架構圖

### 異動檔案清單

列出所有需要新增或修改的檔案，依前後端分組：

```
**Backend**
| 檔案路徑 | 異動類型 | 說明 |
|---------|---------|------|
| src/models/user.model.ts | 新增 | ProfileUpdateDto 定義 |
| src/services/user.service.ts | 修改 | 新增 updateProfile 方法 |
| src/controllers/user.controller.ts | 修改 | 新增 PATCH /users/:id |

**Frontend**
| 檔案路徑 | 異動類型 | 說明 |
|---------|---------|------|
| src/api/user.api.ts | 修改 | 新增 updateProfile 呼叫 |
| src/components/ProfileForm.tsx | 新增 | 個人資料編輯表單 |
```

### Step N: 各實作區塊

每個 Step 對應一個實作層，依情況包含以下內容：

**精簡程式碼** — 保留函式簽名與關鍵型別，實作邏輯用 `// ...` 替代：

```typescript
// src/services/user.service.ts
class UserService {
  async updateProfile(userId: string, dto: ProfileUpdateDto): Promise<User> {
    // ...
  }
}
```

**API Endpoint 規格** — 涉及 API 時列出：

```
PATCH /api/users/:id

Request Body:
{
  "name": string,
  "avatar": string  // optional
}

Response 200:
{
  "id": string,
  "name": string,
  "updatedAt": string
}

Response 400: 資料驗證失敗
Response 404: 使用者不存在
```

**資料結構定義** — interface、type、schema、DTO 完整保留，不省略。

**邊界情境** — 針對此 Step 的潛在問題，用問句標註未定義行為：

```
> - userId 不存在時，回傳 404 還是靜默忽略？
> - name 傳入空字串的處理行為未定義
```

### 注意事項 / 邊界情境

彙整所有跨步驟的注意事項、架構限制、潛在副作用、與既有邏輯的衝突點。

---

## Step 排序原則

### Backend（由底層往上）

1. 資料模型 / Schema / DTO 定義
2. Repository / 資料存取層
3. Service / 業務邏輯層
4. Controller / API 層

### Frontend（UI 優先，畫面先行）

前端採用 UI 優先策略，先切出畫面，再逐步串接邏輯：

1. UI 切版（元件結構、靜態畫面、基本樣式）
2. 基礎互動邏輯（狀態管理、使用者操作、表單驗證）
3. API 串接 / 詳細功能實作（與後端整合、非同步資料）

若兩個 Step 無明確相依，依資料流方向排序（資料從哪裡來，往哪裡去）。

---

## 輸出規則

- 輸出路徑：使用者指定，或預設輸出至當前目錄 `<功能名稱>.plan.md`
- 功能名稱未指定時，從需求描述推斷，使用 kebab-case
- 精簡程式碼只保留：函式簽名、型別定義、關鍵常數；實作邏輯統一用 `// ...` 替代
- 資料結構（interface、type、schema）完整保留，不使用 `// ...` 省略欄位
- 架構圖優先使用 Mermaid，模組層級關係用 ASCII 補充
