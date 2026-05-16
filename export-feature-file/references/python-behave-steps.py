# Python (Behave) Step Definitions 範例
#
# 框架：Behave（不支援 Cucumber Expression，使用框架原生語法）
# Scope：不支援，透過 steps 目錄區隔（features/steps/login_steps.py）
# 命名：每個 Feature 的步驟放在獨立的 *_steps.py 檔案下
#
# Why: Behave 不原生支援 Cucumber Expression
# Syntax: 字串參數用 "{param}" 雙引號包覆，整數參數用 {param:d} 加型別後綴

from behave import given, when, then

# Given：建立前置狀態 / 準備測試資料
@given('用戶已註冊帳號 "{email}"')
def step_impl(context, email):
    pass  # 準備測試資料

@given('帳號未被鎖定')
def step_impl(context):
    pass  # 確認帳號狀態

# When：執行觸發動作（一個 Scenario 理想只有一個 When）
@when('用戶輸入正確的帳號密碼')
def step_impl(context):
    pass  # 執行登入

@when('用戶輸入錯誤的密碼')
def step_impl(context):
    pass  # 執行登入（密碼錯誤）

# Then：驗證預期結果
@then('系統導向至首頁')
def step_impl(context):
    pass  # 驗證頁面導向

@then('顯示錯誤訊息 "{message}"')
def step_impl(context, message):
    pass  # 驗證錯誤提示

@then('待發送清單應包含 {expected_count:d} 筆資料')
def step_impl(context, expected_count):
    pass  # 驗證筆數

# Scenario Outline 參數透過 Examples 傳入
@then('帳號狀態為 "{status}"')
def step_impl(context, status):
    pass  # 驗證帳號狀態
