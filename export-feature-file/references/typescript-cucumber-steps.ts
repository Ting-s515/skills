// JavaScript/TypeScript (Cucumber.js) Step Definitions 範例
//
// 框架：Cucumber.js（Cucumber Expression 原生支援）
// Scope：不支援，透過目錄結構區隔（features/login/step_definitions/）
// 命名：每個 Feature 的步驟放在獨立的 step_definitions 資料夾下

import { Given, When, Then } from '@cucumber/cucumber';

// Given：建立前置狀態 / 準備測試資料
Given('用戶已註冊帳號 {string}', function (email: string) {
    /* 準備測試資料 */
});

Given('帳號未被鎖定', function () {
    /* 確認帳號狀態 */
});

// When：執行觸發動作（一個 Scenario 理想只有一個 When）
When('用戶輸入正確的帳號密碼', function () {
    /* 執行登入 */
});

When('用戶輸入錯誤的密碼', function () {
    /* 執行登入（密碼錯誤） */
});

// Then：驗證預期結果
Then('系統導向至首頁', function () {
    /* 驗證頁面導向 */
});

Then('顯示錯誤訊息 {string}', function (message: string) {
    /* 驗證錯誤提示 */
});

Then('待發送清單應包含 {int} 筆資料', function (expectedCount: number) {
    /* 驗證筆數 */
});

// Scenario Outline 參數透過 Examples 傳入，型別對應 {string}/{int}/{float}
Then('帳號狀態為 {string}', function (status: string) {
    /* 驗證帳號狀態 */
});
