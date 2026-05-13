// OrderService: 負責訂單狀態管理，並在狀態變更後觸發通知事件
import { NotificationService, OrderStatus } from './NotificationService';

export class OrderService {
  private notificationService: NotificationService;

  constructor(notificationService: NotificationService) {
    this.notificationService = notificationService;
  }

  // 更新訂單狀態，並觸發對應的通知信給買家
  async updateOrderStatus(
    orderId: string,
    buyerEmail: string,
    newStatus: OrderStatus
  ): Promise<void> {
    // 更新訂單狀態（資料庫操作省略）
    await this.persistOrderStatus(orderId, newStatus);

    // 狀態更新後觸發通知
    await this.notificationService.sendOrderStatusEmail(orderId, buyerEmail, newStatus);
  }

  private async persistOrderStatus(orderId: string, status: OrderStatus): Promise<void> {
    // 實際資料庫更新邏輯
  }
}
