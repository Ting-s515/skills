export type LineItem = {
  price: number;
  quantity: number;
};

export type Coupon = {
  amount: number;
} | null;

export function calculateOrderTotal(items: LineItem[], coupon: Coupon) {
  const subtotal = items.reduce((sum, item) => sum + item.price * item.quantity, 0);
  const discount = coupon ? Math.min(coupon.amount, subtotal) : 0;
  const discountedSubtotal = subtotal - discount;
  const tax = Math.round(discountedSubtotal * 0.05 * 100) / 100;

  return {
    subtotal,
    discount,
    tax,
    total: discountedSubtotal + tax,
  };
}
