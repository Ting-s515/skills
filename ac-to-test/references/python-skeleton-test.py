# test_{feature_name}.py
# 此測試骨架由 AC-{feature-name}.md 自動產出
# 實作完成後，將 TODO 替換為實際呼叫與斷言

import pytest


class Test{FeatureName}:

    # AC-001 Happy Path — 有效折價券正確折抵
    def test_AC001_GivenValidCoupon_WhenApply_ShouldReturnCorrectDiscount(self):
        # Given: 購物車小計為 1200 且折價券 SAVE100 有效
        # When: 使用者套用折價券
        # Then: 訂單應回傳折抵金額 100
        # And: 應付總額為 1100

        # TODO: import use case 並實作以下斷言
        # result = apply_coupon(cart_total=1200, coupon_code='SAVE100')
        # assert result.discount_amount == 100
        # assert result.final_total == 1100

        pytest.fail("紅燈佔位，實作完成後移除此行")

    # AC-002 邊界條件 — 未達最低門檻不可使用
    def test_AC002_GivenCartBelow1000_WhenApply_ShouldReturnThresholdError(self):
        # Given: 購物車小計為 999 且折價券規則為滿 1000 才可使用
        # When: 使用者套用折價券
        # Then: 系統應回傳 COUPON_THRESHOLD_NOT_MET
        # And: 訂單總額維持 999

        # TODO: import use case 並實作以下斷言
        # result = apply_coupon(cart_total=999, coupon_code='SAVE100')
        # assert result.error == 'COUPON_THRESHOLD_NOT_MET'
        # assert result.final_total == 999

        pytest.fail("紅燈佔位，實作完成後移除此行")

    # AC-003 錯誤條件 — 已過期折價券不得套用
    def test_AC003_GivenExpiredCoupon_WhenApply_ShouldReturnExpiredError(self):
        # Given: 折價券 SAVE100 已過期
        # When: 使用者套用折價券
        # Then: 系統應回傳 COUPON_EXPIRED
        # And: 不得更新訂單折扣欄位

        # TODO: import use case 並實作以下斷言
        # result = apply_coupon(cart_total=1200, coupon_code='EXPIRED_CODE')
        # assert result.error == 'COUPON_EXPIRED'
        # assert result.discount_amount is None

        pytest.fail("紅燈佔位，實作完成後移除此行")
