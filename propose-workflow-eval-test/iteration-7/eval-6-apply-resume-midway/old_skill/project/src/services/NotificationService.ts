// 依訂單狀態選擇對應 email 模板並發送通知信給買家
export class NotificationService {
  // 各訂單狀態對應的 email 模板映射
  private readonly emailTemplates: Record<string, string> = {
    shipped: 'order-shipped',
    delivered: 'order-delivered',
    cancelled: 'order-cancelled',
    pending: 'order-pending',
  };

  // 根據訂單狀態選擇模板並發送 email 給買家
  async sendOrderStatusEmail(orderId: string, status: string, buyerEmail: string): Promise<void> {
    const template = this.emailTemplates[status];

    if (!template) {
      throw new Error(`未知訂單狀態：${status}`);
    }

    await this.sendEmail(buyerEmail, template, { orderId, status });
    console.log(`[NotificationService] 通知信已送出 orderId=${orderId} status=${status}`);
  }

  private async sendEmail(to: string, template: string, data: Record<string, string>): Promise<void> {
    // 實際 email 發送邏輯（透過 email provider）
    console.log(`[NotificationService] sendEmail to=${to} template=${template}`, data);
  }
}
