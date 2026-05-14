function formatCurrency(amount, options = {}) {
  const symbol = options.symbol ?? 'NT$';
  const decimals = Number.isInteger(options.decimals) ? options.decimals : 0;

  // 無效金額不應讓 UI 顯示 NaN 或 Infinity。
  if (!Number.isFinite(amount)) {
    return `${symbol}0`;
  }

  const fixedAmount = amount.toFixed(decimals);
  const [integerPart, decimalPart] = fixedAmount.split('.');
  const formattedInteger = integerPart.replace(/\B(?=(\d{3})+(?!\d))/g, ',');

  if (decimalPart) {
    return `${symbol}${formattedInteger}.${decimalPart}`;
  }

  return `${symbol}${formattedInteger}`;
}

module.exports = {
  formatCurrency,
};
