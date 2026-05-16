// Flutter/Dart (flutter_gherkin) Step Definitions 範例
//
// 框架：flutter_gherkin（Cucumber Expression 原生支援）
// Scope：不支援，在 FlutterTestConfiguration.stepDefinitions 集中註冊所有步驟
// 命名：數字後綴代表參數數量（given1 = 1 個參數、when0 = 0 個參數）
//
// Why: flutter_gherkin 使用函式式 API，每個步驟是獨立的 StepDefinitionGeneric 函式

import 'package:flutter_gherkin/flutter_gherkin.dart';

// Given：建立前置狀態 / 準備測試資料
StepDefinitionGeneric givenUserIsRegistered() =>
    given1<String>('用戶已註冊帳號 {string}',
        (email, context) async { /* 準備測試資料 */ });

StepDefinitionGeneric givenAccountIsNotLocked() =>
    given0('帳號未被鎖定',
        (context) async { /* 確認帳號狀態 */ });

// When：執行觸發動作（一個 Scenario 理想只有一個 When）
StepDefinitionGeneric whenUserEntersCorrectCredentials() =>
    when0('用戶輸入正確的帳號密碼',
        (context) async { /* 執行登入 */ });

StepDefinitionGeneric whenUserEntersWrongPassword() =>
    when0('用戶輸入錯誤的密碼',
        (context) async { /* 執行登入（密碼錯誤） */ });

// Then：驗證預期結果
StepDefinitionGeneric thenNavigateToHomePage() =>
    then0('系統導向至首頁',
        (context) async { /* 驗證頁面導向 */ });

StepDefinitionGeneric thenShowErrorMessage() =>
    then1<String>('顯示錯誤訊息 {string}',
        (message, context) async { /* 驗證錯誤提示 */ });

StepDefinitionGeneric thenPendingListContains() =>
    then1<int>('待發送清單應包含 {int} 筆資料',
        (expectedCount, context) async { /* 驗證筆數 */ });

// Scenario Outline 參數透過 Examples 傳入
StepDefinitionGeneric thenAccountStatusIs() =>
    then1<String>('帳號狀態為 {string}',
        (status, context) async { /* 驗證帳號狀態 */ });

// 在 FlutterTestConfiguration 中集中註冊：
// stepDefinitions: [
//   givenUserIsRegistered,
//   givenAccountIsNotLocked,
//   whenUserEntersCorrectCredentials,
//   whenUserEntersWrongPassword,
//   thenNavigateToHomePage,
//   thenShowErrorMessage,
//   thenPendingListContains,
//   thenAccountStatusIs,
// ]
