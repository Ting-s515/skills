import { formatCurrency } from '../currency.js';

describe('formatCurrency', () => {
  describe('Happy Path', () => {
    it('GivenInteger1234_WhenFormatCurrency_ShouldReturnNT$1,234', () => {
      expect(formatCurrency(1234)).toBe('NT$1,234');
    });

    it('GivenDecimalWithDecimals2_WhenFormatCurrency_ShouldRoundAndFormat', () => {
      expect(formatCurrency(1234.567, { decimals: 2 })).toBe('NT$1,234.57');
    });

    it('GivenCustomSymbol_WhenFormatCurrency_ShouldUseThatSymbol', () => {
      expect(formatCurrency(500, { symbol: '$' })).toBe('$500');
    });

    it('GivenSmallAmount_WhenFormatCurrency_ShouldReturnWithoutComma', () => {
      expect(formatCurrency(500)).toBe('NT$500');
    });
  });

  describe('Error Cases', () => {
    it('GivenNaN_WhenFormatCurrency_ShouldReturnNT$0', () => {
      expect(formatCurrency(NaN)).toBe('NT$0');
    });

    it('GivenInfinity_WhenFormatCurrency_ShouldReturnNT$0', () => {
      expect(formatCurrency(Infinity)).toBe('NT$0');
    });
  });
});
