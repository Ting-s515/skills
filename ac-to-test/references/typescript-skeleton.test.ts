// {feature-name}.test.ts
// 此測試骨架由 AC-{feature-name}.md 自動產出
// 實作完成後，將 TODO 替換為實際呼叫與斷言

describe('{feature-name}', () => {

  // AC-001 Happy Path — 有效折價券正確折抵
  it('AC001_GivenValidCoupon_WhenApply_ShouldReturnCorrectDiscount', () => {
    // Given: 購物車小計為 1200 且折價券 SAVE100 有效
    // When: 使用者套用折價券
    // Then: 訂單應回傳折抵金額 100
    // And: 應付總額為 1100

    // TODO: import entry point（hook）並實作以下斷言
    // const result = applyCoupon({ cartTotal: 1200, couponCode: 'SAVE100' })
    // expect(result.discountAmount).toBe(100)
    // expect(result.finalTotal).toBe(1100)

    expect(true).toBe(false) // 紅燈佔位，實作完成後移除此行
  })

  // AC-002 邊界條件 — 未達最低門檻不可使用
  it('AC002_GivenCartBelow1000_WhenApply_ShouldReturnThresholdError', () => {
    // Given: 購物車小計為 999 且折價券規則為滿 1000 才可使用
    // When: 使用者套用折價券
    // Then: 系統應回傳 COUPON_THRESHOLD_NOT_MET
    // And: 訂單總額維持 999

    // TODO: import entry point 並實作以下斷言
    // const result = applyCoupon({ cartTotal: 999, couponCode: 'SAVE100' })
    // expect(result.error).toBe('COUPON_THRESHOLD_NOT_MET')
    // expect(result.finalTotal).toBe(999)

    expect(true).toBe(false) // 紅燈佔位，實作完成後移除此行
  })

  // AC-003 錯誤條件 — 已過期折價券不得套用
  it('AC003_GivenExpiredCoupon_WhenApply_ShouldReturnExpiredError', () => {
    // Given: 折價券 SAVE100 已過期
    // When: 使用者套用折價券
    // Then: 系統應回傳 COUPON_EXPIRED
    // And: 不得更新訂單折扣欄位

    // TODO: import entry point 並實作以下斷言
    // const result = applyCoupon({ cartTotal: 1200, couponCode: 'EXPIRED_CODE' })
    // expect(result.error).toBe('COUPON_EXPIRED')
    // expect(result.discountAmount).toBeUndefined()

    expect(true).toBe(false) // 紅燈佔位，實作完成後移除此行
  })

})
