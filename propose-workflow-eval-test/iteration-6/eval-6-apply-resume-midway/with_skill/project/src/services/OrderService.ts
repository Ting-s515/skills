import { NotificationService } from './NotificationService';

export type OrderStatus = 'pending' | 'shipped' | 'delivered' | 'cancelled';

export interface Order {
  id: string;
  buyerEmail: string;
  status: OrderStatus;
}

export class OrderService {
  constructor(private notificationService: NotificationService) {}

  // 更新訂單狀態，並在更新後觸發通知
  async updateOrderStatus(order: Order, newStatus: OrderStatus): Promise<Order> {
    const updatedOrder: Order = { ...order, status: newStatus };

    // 狀態更新後，觸發通知事件給買家
    await this.notificationService.sendOrderStatusEmail(updatedOrder.buyerEmail, newStatus);

    return updatedOrder;
  }
}
