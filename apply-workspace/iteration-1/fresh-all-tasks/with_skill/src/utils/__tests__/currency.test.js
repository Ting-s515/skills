import { formatCurrency } from '../currency.js';

describe('formatCurrency', () => {
  describe('Happy Path', () => {
    it('GivenInteger1234_WhenFormatCurrency_ShouldReturnNT$1,234', () => {
      // Given
      const amount = 1234;
      // When
      const result = formatCurrency(amount);
      // Then
      expect(result).toBe('NT$1,234');
    });

    it('GivenDecimal1234567WithDecimals2_WhenFormatCurrency_ShouldReturnNT$1,234.57', () => {
      // Given
      const amount = 1234.567;
      // When
      const result = formatCurrency(amount, { decimals: 2 });
      // Then
      expect(result).toBe('NT$1,234.57');
    });

    it('GivenSmallAmount500_WhenFormatCurrency_ShouldReturnNT$500', () => {
      // Given
      const amount = 500;
      // When
      const result = formatCurrency(amount);
      // Then
      expect(result).toBe('NT$500');
    });

    it('GivenCustomSymbol_WhenFormatCurrency_ShouldUseThatSymbol', () => {
      // Given
      const amount = 500;
      // When
      const result = formatCurrency(amount, { symbol: '$' });
      // Then
      expect(result).toBe('$500');
    });
  });

  describe('Edge Cases', () => {
    it('GivenZero_WhenFormatCurrency_ShouldReturnNT$0', () => {
      expect(formatCurrency(0)).toBe('NT$0');
    });

    it('GivenNegativeAmount_WhenFormatCurrency_ShouldHandleCorrectly', () => {
      expect(formatCurrency(-1234)).toBe('NT$-1,234');
    });
  });

  describe('Error Cases', () => {
    it('GivenNaN_WhenFormatCurrency_ShouldReturnNT$0', () => {
      // Given
      const amount = NaN;
      // When
      const result = formatCurrency(amount);
      // Then
      expect(result).toBe('NT$0');
    });

    it('GivenInfinity_WhenFormatCurrency_ShouldReturnNT$0', () => {
      expect(formatCurrency(Infinity)).toBe('NT$0');
      expect(formatCurrency(-Infinity)).toBe('NT$0');
    });
  });
});
