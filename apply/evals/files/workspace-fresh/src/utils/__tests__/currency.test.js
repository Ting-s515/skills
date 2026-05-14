const assert = require('node:assert/strict');
const test = require('node:test');

const { formatCurrency } = require('../index');

test('GivenIntegerAmount_WhenFormatCurrency_ShouldReturnAmountWithThousandsSeparator', () => {
  const result = formatCurrency(1234);

  assert.equal(result, 'NT$1,234');
});

test('GivenDecimalAmountAndDecimals_WhenFormatCurrency_ShouldReturnRoundedAmount', () => {
  const result = formatCurrency(1234.567, { decimals: 2 });

  assert.equal(result, 'NT$1,234.57');
});

test('GivenNaNAmount_WhenFormatCurrency_ShouldReturnZeroAmount', () => {
  const result = formatCurrency(NaN);

  assert.equal(result, 'NT$0');
});

test('GivenCustomSymbol_WhenFormatCurrency_ShouldReturnAmountWithCustomSymbol', () => {
  const result = formatCurrency(500, { symbol: '$' });

  assert.equal(result, '$500');
});

test('GivenSmallAmount_WhenFormatCurrency_ShouldReturnAmountWithoutThousandsSeparator', () => {
  const result = formatCurrency(500);

  assert.equal(result, 'NT$500');
});
