// Java (Cucumber-JVM) Step Definitions 範例
//
// 框架：Cucumber-JVM（Cucumber Expression 原生支援）
// Scope：不支援，透過 @CucumberOptions(glue = "steps.featureName") 路徑區隔
// 命名：每個 Feature 的步驟放在獨立的 package 下（如 steps.login）

import io.cucumber.java.en.Given;
import io.cucumber.java.en.When;
import io.cucumber.java.en.Then;

// @CucumberOptions(glue = "steps.login") — 在 runner 設定，限制只載入此 package 的步驟
public class LoginSteps {

    // Given：建立前置狀態 / 準備測試資料
    @Given("用戶已註冊帳號 {string}")
    public void 用戶已註冊帳號(String email) { /* 準備測試資料 */ }

    @Given("帳號未被鎖定")
    public void 帳號未被鎖定() { /* 確認帳號狀態 */ }

    // When：執行觸發動作（一個 Scenario 理想只有一個 When）
    @When("用戶輸入正確的帳號密碼")
    public void 用戶輸入正確的帳號密碼() { /* 執行登入 */ }

    @When("用戶輸入錯誤的密碼")
    public void 用戶輸入錯誤的密碼() { /* 執行登入（密碼錯誤） */ }

    // Then：驗證預期結果
    @Then("系統導向至首頁")
    public void 系統導向至首頁() { /* 驗證頁面導向 */ }

    @Then("顯示錯誤訊息 {string}")
    public void 顯示錯誤訊息(String message) { /* 驗證錯誤提示 */ }

    @Then("待發送清單應包含 {int} 筆資料")
    public void 待發送清單應包含N筆資料(int expectedCount) { /* 驗證筆數 */ }

    // Scenario Outline 參數透過 Examples 傳入，型別對應 {string}/{int}/{float}
    @Then("帳號狀態為 {string}")
    public void 帳號狀態為(String status) { /* 驗證帳號狀態 */ }
}
