// OrderService: 訂單業務邏輯，狀態更新後觸發通知事件
import { NotificationService } from './NotificationService';

export class OrderService {
  constructor(private notificationService: NotificationService) {}

  // 更新訂單狀態，並在更新成功後觸發通知
  async updateOrderStatus(orderId: string, status: string): Promise<void> {
    // 實際應用中這裡會更新資料庫
    console.log(`Order ${orderId} status updated to ${status}`);

    // 訂單狀態更新後觸發通知事件（T1 實作）
    await this.notificationService.sendOrderStatusEmail(orderId, status);
  }
}
