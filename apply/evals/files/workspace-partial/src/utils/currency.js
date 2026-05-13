export function formatCurrency(amount, options = {}) {
  const { symbol = 'NT$', decimals = 0 } = options;
  if (isNaN(amount) || !isFinite(amount)) {
    return `${symbol}0`;
  }
  const fixed = Number(amount).toFixed(decimals);
  const parts = fixed.split('.');
  const intPart = Number(parts[0]).toLocaleString('en-US');
  return parts[1] ? `${symbol}${intPart}.${parts[1]}` : `${symbol}${intPart}`;
}
