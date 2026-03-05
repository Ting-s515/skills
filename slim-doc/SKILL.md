---
name: slim-doc
description: >
  精簡既有的需求規格 Markdown 文檔，移除詳細程式碼實作，只保留開發必要的結構性資訊，
  大幅降低文件 token 消耗，方便後續讀取需求文檔時節省 context。
  當使用者提出以下任何需求時必須載入此技能：「幫我精簡這個文件」、「slim doc」、「slim md」、「壓縮需求文檔」、「精簡 md」、「減少文件行數」，
  或任何需要將既有 Markdown 文件精簡、壓縮、去除冗餘程式碼的情境。
  注意：此技能專注於精簡既有文件（輸入已存在的 .md），不適用於撰寫新文件（請用 writing-markdown）。
argument-hint: "[輸入文件路徑]"
---

# slim-doc 精簡需求文檔

## 目標

將一份行數過多的需求規格 Markdown 文檔，精簡為開發友好的精簡版本，
輸出至 `xxx.slim.md`，同時確保開發所需的所有結構性資訊完整保留。

---

## 工作流程

1. 讀取使用者指定的 `.md` 文件（若未指定，詢問路徑）
2. 依照下方保留規則與刪除規則處理內容
3. 輸出至同目錄的 `<原檔名>.slim.md`
4. 告知使用者：原始行數、精簡後行數、節省比例

---

## 保留規則（絕對不可刪除）

以下內容對開發至關重要，必須完整保留：

- **Mermaid 流程圖 / 時序圖**（` ```mermaid ` 區塊完整保留）
- **File path**（程式碼中出現的路徑，如 `src/services/user.service.ts`）
- **API endpoint**（如 `POST /api/users`、`GET /api/orders/:id`）
- **資料結構定義**（interface、type、struct、schema 定義，即使在程式碼區塊中）
- **範例 payload**（JSON 範例、request/response body 範例）
- **SQL schema / 欄位定義**（CREATE TABLE、欄位清單）
- **設定檔範例**（config.yaml、.env 範例、nginx.conf 片段等）
- **章節標題**（`#`、`##`、`###` 開頭的標題，維持文件導覽結構）
- **說明文字段落**（非程式碼的純文字說明，描述「為什麼」或「是什麼」）
- **表格**（Markdown table，通常是比較表或欄位說明）
- **Skill 載入指令**（文件中指定在特定情境載入技能的指示，例如「遇到前端開發時載入 react-design skill」、「處理後端邏輯時使用 xxx skill」等描述，這些是 AI 工作流程的一部分，必須完整保留）

---

## 刪除 / 精簡規則

### 完整刪除
- 測試程式碼片段（describe、it、test、expect、assert 等測試框架語法）
- 重複出現的相似範例（保留第一個，其餘標註「（其他範例略）」）

### 精簡為省略符號
對於函式實作、class 實作，保留簽名，用 `// ...` 取代實作細節：

```
// 精簡前
function calculateDiscount(order: Order): number {
  const baseDiscount = order.total * 0.1;
  if (order.memberLevel === 'gold') {
    return baseDiscount * 1.5;
  }
  // ... 50 行邏輯
  return baseDiscount;
}

// 精簡後
function calculateDiscount(order: Order): number {
  // ...
}
```

```
// 精簡前
class UserService {
  private db: Database;
  constructor(db: Database) { this.db = db; }
  async findById(id: string): Promise<User> {
    const result = await this.db.query(...);
    // ... 實作細節
  }
  async updateProfile(...) { ... }
}

// 精簡後
class UserService {
  async findById(id: string): Promise<User> { // ... }
  async updateProfile(...): Promise<void> { // ... }
}
```

---

## 判斷原則

遇到邊界情況時，優先回答這個問題：
**「開發者在實作這個需求時，是否需要看這段內容？」**

- 需要 → 保留
- 不需要（只是示意、已有別處說明、純實作細節）→ 精簡或刪除

---

## 輸出格式

- 輸出路徑：`<原目錄>/<原檔名>.slim.md`

