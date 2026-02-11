---
name: export-feature-file
description: 當我呼叫此技能時，依照我提供的 Gherkin 文檔或業務邏輯，轉換為可被測試框架執行的 Feature File 格式（.feature），支援各種 BDD 測試框架。
---

# Export Feature File

## 目的

產出可直接被 BDD 測試框架執行的 Feature File（`.feature`），實現「測試即文件」（Living Documentation）。

## 支援的測試框架

| 語言/平台 | 測試框架 |
|-----------|----------|
| .NET | SpecFlow, Reqnroll |
| Java | Cucumber-JVM |
| JavaScript/TypeScript | Cucumber.js |
| Python | Behave, pytest-bdd |
| Ruby | Cucumber |
| Go | Godog |
| PHP | Behat |

## 格式定義

```gherkin
Feature: 功能名稱
  功能描述（說明這個功能的目的）

  Scenario: 情境描述（單一固定案例）
    Given 前置條件
    When 觸發動作
    Then 預期結果

  Scenario Outline: 情境描述（多組測試資料）
    Given 前置條件 <參數A>
    When 觸發動作 <參數B>
    Then 預期結果 <參數C>

    Examples:
      | 參數A | 參數B | 參數C |
      | 值1   | 值2   | 值3   |
      | 值4   | 值5   | 值6   |
```

| 關鍵字 | 用途 | 範例 |
|--------|------|------|
| **Feature** | 功能名稱與描述 | `Feature: 用戶登入` |
| **Scenario** | 單一固定測試案例 | `Scenario: 用戶成功登入` |
| **Scenario Outline** | 參數化測試案例，搭配 Examples | `Scenario Outline: 登入驗證` |
| **Examples** | 測試資料表格，搭配 Scenario Outline | 見範例 |
| **Given** | 前置條件 / 初始狀態 | `Given 用戶已註冊帳號 "test@example.com"` |
| **When** | 觸發的動作或事件 | `When 用戶點擊登入按鈕` |
| **Then** | 預期的結果 | `Then 系統導向至首頁` |
| **And** | 延續上一個關鍵字（可選） | `And 顯示歡迎訊息` |

## 範例

### 範例 1：用戶登入

**輸入（程式碼邏輯）：**
```typescript
// 檢查帳號密碼，正確則導向首頁，錯誤則顯示錯誤訊息
// 連續錯誤 3 次則鎖定帳號
```

**輸出（Feature File）：**
```gherkin
Feature: 用戶登入
  用戶透過帳號密碼進行身份驗證，以存取系統功能

  Scenario: 用戶成功登入
    Given 用戶已註冊帳號 "test@example.com"
    And 帳號未被鎖定
    When 用戶輸入正確的帳號密碼
    Then 系統導向至首頁

  Scenario: 用戶登入失敗
    Given 用戶已註冊帳號 "test@example.com"
    When 用戶輸入錯誤的密碼
    Then 系統停留在登入頁面
    And 顯示錯誤訊息 "帳號或密碼錯誤"

  Scenario Outline: 連續登入失敗鎖定帳號
    Given 用戶已連續輸入錯誤密碼 <前次失敗> 次
    When 用戶第 <本次> 次輸入錯誤密碼
    Then 帳號狀態為 "<結果>"

    Examples:
      | 前次失敗 | 本次 | 結果   |
      | 1        | 2    | 正常   |
      | 2        | 3    | 鎖定   |
```

### 範例 2：購物車

**輸入（需求描述）：**
```
用戶可以將商品加入購物車，數量不可超過庫存，
結帳時計算總金額並套用折扣碼
```

**輸出（Feature File）：**
```gherkin
Feature: 購物車管理
  用戶可以管理購物車內的商品，並在結帳時套用優惠

  Scenario Outline: 加入商品至購物車
    Given 商品庫存為 <庫存> 件
    When 用戶將該商品加入購物車 <數量> 件
    Then 購物車商品數量為 <數量>
    And 庫存剩餘 <剩餘> 件

    Examples:
      | 庫存 | 數量 | 剩餘 |
      | 10   | 1    | 9    |
      | 10   | 5    | 5    |

  Scenario: 加入商品超過庫存數量
    Given 商品庫存為 5 件
    When 用戶嘗試將該商品加入購物車 10 件
    Then 系統拒絕此操作
    And 顯示錯誤訊息 "庫存不足"

  Scenario Outline: 套用折扣碼
    Given 購物車總金額為 <原價> 元
    And 折扣碼 "<折扣碼>" 可折抵 <折扣>%
    When 用戶輸入折扣碼 "<折扣碼>"
    Then 總金額更新為 <結果> 元

    Examples:
      | 原價 | 折扣碼  | 折扣 | 結果 |
      | 1000 | SAVE10  | 10   | 900  |
      | 1000 | SAVE20  | 20   | 800  |
```

## 輸出規範

1. **必須包含 Feature**：每個輸出都以 Feature 開頭，說明功能名稱與目的
2. **相關 Scenario 歸屬同一 Feature**：將相關的測試情境組織在同一個 Feature 下
3. 每個 Scenario 聚焦於**單一行為**
4. **專注在有價值的行為**：不求詳盡，只描述最關鍵的業務規則
5. 使用**業務語言**，但可提及 API、DB 等技術元素作為測試驗證點
6. Given/When/Then 各自獨立成行，保持可讀性
7. And 為可選，僅當條件或結果有多項時才使用
8.  **使用具體數值**：提供實際的測試資料，不使用抽象變數
9.  **參數化測試使用 Scenario Outline**：
    - 當同一行為需要多組測試資料時，使用 `Scenario Outline` + `Examples`
    - 參數使用 `<參數名稱>` 格式
    - Examples 表格提供具體測試資料
10. **字串參數用雙引號包覆**：如 `"test@example.com"`、`"SAVE10"`
11. **沙漏原則 - When 最小化**：
    - When 越小越好，理想情況只有一行
    - 將操作步驟移至 Given
    - When 只保留最關鍵的觸發點
12. **輸出後更新指定文檔**：將產出的內容寫入用戶指定的 `.feature` 檔案

## Step Definitions 對應提示

產出 Feature File 後，開發者需依據所使用的測試框架撰寫對應的 Step Definitions。

### .NET (SpecFlow / Reqnroll)

```csharp
[Binding]
public class LoginSteps
{
    [Given(@"用戶已註冊帳號 ""(.*)""")]
    public void Given用戶已註冊帳號(string email) { /* 準備測試資料 */ }

    [When(@"用戶輸入正確的帳號密碼")]
    public void When用戶輸入正確的帳號密碼() { /* 執行登入 */ }

    [Then(@"系統導向至首頁")]
    public void Then系統導向至首頁() { /* 驗證導向 */ }
}
```

### Java (Cucumber-JVM)

```java
public class LoginSteps {
    @Given("用戶已註冊帳號 {string}")
    public void 用戶已註冊帳號(String email) { /* 準備測試資料 */ }

    @When("用戶輸入正確的帳號密碼")
    public void 用戶輸入正確的帳號密碼() { /* 執行登入 */ }

    @Then("系統導向至首頁")
    public void 系統導向至首頁() { /* 驗證導向 */ }
}
```

### JavaScript/TypeScript (Cucumber.js)

```typescript
import { Given, When, Then } from '@cucumber/cucumber';

Given('用戶已註冊帳號 {string}', function (email: string) { /* 準備測試資料 */ });
When('用戶輸入正確的帳號密碼', function () { /* 執行登入 */ });
Then('系統導向至首頁', function () { /* 驗證導向 */ });
```

### Python (Behave)

```python
from behave import given, when, then

@given('用戶已註冊帳號 "{email}"')
def step_impl(context, email): pass  # 準備測試資料

@when('用戶輸入正確的帳號密碼')
def step_impl(context): pass  # 執行登入

@then('系統導向至首頁')
def step_impl(context): pass  # 驗證導向
```

## 檔案命名規範

- 使用 `.feature` 副檔名
- 檔名使用 PascalCase 或 kebab-case
- 範例：`UserLogin.feature`、`shopping-cart.feature`
