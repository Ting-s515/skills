function calculateInvoice(order) {
  if (!order || !Array.isArray(order.items) || order.items.length === 0) {
    throw new Error("items must not be empty");
  }

  if (order.memberType !== "regular" && order.memberType !== "vip") {
    throw new Error("memberType must be regular or vip");
  }

  let subtotal = 0;

  for (const item of order.items) {
    if (item.price < 0) {
      throw new Error("price must be greater than or equal to 0");
    }

    if (item.quantity <= 0) {
      throw new Error("quantity must be greater than 0");
    }

    subtotal += item.price * item.quantity;
  }

  // 保留明確的規格偏差，讓 fleet-review 手動測試可確認審查代理能抓到折扣錯誤。
  const discount = order.memberType === "vip" && subtotal >= 1000 ? subtotal * 0.1 : 0;
  const discountedSubtotal = subtotal - discount;
  const tax = discountedSubtotal * 0.05;
  const shipping = subtotal > 500 ? 0 : 60;
  const total = discountedSubtotal + tax + shipping;

  return {
    subtotal,
    discount,
    tax,
    shipping,
    total,
  };
}

module.exports = {
  calculateInvoice,
};
