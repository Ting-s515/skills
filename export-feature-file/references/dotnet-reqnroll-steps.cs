// .NET (Reqnroll) Step Definitions 範例
//
// 框架：Reqnroll（Cucumber Expression 原生支援）
// Scope：[Scope(Feature = "...")] 綁定至指定 Feature，避免跨 Feature 步驟衝突
// 命名：Feature 名稱需與 .feature 檔案中的 Feature: 標題完全一致

using Reqnroll;

// Why: [Scope] 將 Step Definitions 綁定至指定 Feature，避免跨 Feature 的步驟定義衝突
[Scope(Feature = "用戶登入")]
[Binding]
public class LoginSteps
{
    // Given：建立前置狀態 / 準備測試資料
    [Given("用戶已註冊帳號 {string}")]
    public void Given用戶已註冊帳號(string email) { /* 準備測試資料 */ }

    [Given("帳號未被鎖定")]
    public void Given帳號未被鎖定() { /* 確認帳號狀態 */ }

    // When：執行觸發動作（一個 Scenario 理想只有一個 When）
    [When("用戶輸入正確的帳號密碼")]
    public void When用戶輸入正確的帳號密碼() { /* 執行登入 */ }

    [When("用戶輸入錯誤的密碼")]
    public void When用戶輸入錯誤的密碼() { /* 執行登入（密碼錯誤） */ }

    // Then：驗證預期結果
    [Then("系統導向至首頁")]
    public void Then系統導向至首頁() { /* 驗證頁面導向 */ }

    [Then("顯示錯誤訊息 {string}")]
    public void Then顯示錯誤訊息(string message) { /* 驗證錯誤提示 */ }

    [Then("待發送清單應包含 {int} 筆資料")]
    public void Then待發送清單應包含N筆資料(int expectedCount) { /* 驗證筆數 */ }

    // Scenario Outline 參數透過 Examples 傳入，型別對應 {string}/{int}/{float}
    [Then("帳號狀態為 {string}")]
    public void Then帳號狀態為(string status) { /* 驗證帳號狀態 */ }
}
