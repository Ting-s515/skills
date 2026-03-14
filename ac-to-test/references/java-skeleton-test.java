// {FeatureName}Test.java
// 此測試骨架由 AC-{feature-name}.md 自動產出
// 實作完成後，將 TODO 替換為實際呼叫與斷言

class {FeatureName}Test {

    // AC-001 Happy Path — 有效折價券正確折抵
    @Test
    @DisplayName("AC001_GivenValidCoupon_WhenApply_ShouldReturnCorrectDiscount")
    void AC001_GivenValidCoupon_WhenApply_ShouldReturnCorrectDiscount() {
        // Given: 購物車小計為 1200 且折價券 SAVE100 有效
        // When: 使用者套用折價券
        // Then: 訂單應回傳折抵金額 100
        // And: 應付總額為 1100

        // TODO: 建立 use case 並實作以下斷言
        // var result = couponService.apply(1200, "SAVE100");
        // assertThat(result.getDiscountAmount()).isEqualTo(100);
        // assertThat(result.getFinalTotal()).isEqualTo(1100);

        fail("紅燈佔位，實作完成後移除此行");
    }

    // AC-002 邊界條件 — 未達最低門檻不可使用
    @Test
    @DisplayName("AC002_GivenCartBelow1000_WhenApply_ShouldReturnThresholdError")
    void AC002_GivenCartBelow1000_WhenApply_ShouldReturnThresholdError() {
        // Given: 購物車小計為 999 且折價券規則為滿 1000 才可使用
        // When: 使用者套用折價券
        // Then: 系統應回傳 COUPON_THRESHOLD_NOT_MET
        // And: 訂單總額維持 999

        // TODO: 建立 use case 並實作以下斷言
        // var result = couponService.apply(999, "SAVE100");
        // assertThat(result.getError()).isEqualTo("COUPON_THRESHOLD_NOT_MET");
        // assertThat(result.getFinalTotal()).isEqualTo(999);

        fail("紅燈佔位，實作完成後移除此行");
    }

    // AC-003 錯誤條件 — 已過期折價券不得套用
    @Test
    @DisplayName("AC003_GivenExpiredCoupon_WhenApply_ShouldReturnExpiredError")
    void AC003_GivenExpiredCoupon_WhenApply_ShouldReturnExpiredError() {
        // Given: 折價券 SAVE100 已過期
        // When: 使用者套用折價券
        // Then: 系統應回傳 COUPON_EXPIRED
        // And: 不得更新訂單折扣欄位

        // TODO: 建立 use case 並實作以下斷言
        // var result = couponService.apply(1200, "EXPIRED_CODE");
        // assertThat(result.getError()).isEqualTo("COUPON_EXPIRED");
        // assertThat(result.getDiscountAmount()).isNull();

        fail("紅燈佔位，實作完成後移除此行");
    }
}
