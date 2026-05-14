// 依照 01-flow.md 規格實作：NaN/Infinity 回傳 symbol+0，toFixed 四捨五入，千分位逗號，前綴符號
export function formatCurrency(amount, options = {}) {
  const { symbol = 'NT$', decimals = 0 } = options;

  if (isNaN(amount) || !isFinite(amount)) {
    return `${symbol}0`;
  }

  const fixed = Number(amount).toFixed(decimals);
  const parts = fixed.split('.');
  const intPart = parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, ',');

  return parts[1] ? `${symbol}${intPart}.${parts[1]}` : `${symbol}${intPart}`;
}
