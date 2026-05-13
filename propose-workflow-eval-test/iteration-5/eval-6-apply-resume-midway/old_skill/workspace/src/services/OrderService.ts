import { NotificationService } from './NotificationService';

export class OrderService {
  private notificationService: NotificationService;

  constructor(notificationService: NotificationService) {
    this.notificationService = notificationService;
  }

  // 更新訂單狀態，並在更新後觸發通知事件
  async updateOrderStatus(orderId: string, status: string, buyerEmail: string): Promise<void> {
    // 更新訂單狀態（模擬資料庫操作）
    console.log(`Order ${orderId} status updated to ${status}`);

    // 觸發通知：訂單狀態更新後寄出通知信
    await this.notificationService.sendOrderStatusEmail(orderId, status, buyerEmail);
  }
}
