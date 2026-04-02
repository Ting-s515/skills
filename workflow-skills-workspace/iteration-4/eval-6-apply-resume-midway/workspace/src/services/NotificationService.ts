// NotificationService：負責訂單狀態通知信的發送邏輯
// 依照訂單狀態選擇對應 email 模板，並在失敗時進行重試

const MAX_RETRY = 3;
const RETRY_INTERVAL_MS = 5 * 60 * 1000; // 5 分鐘

export class NotificationService {
  // 依訂單狀態選擇對應 email 模板並發送通知信
  async sendOrderStatusEmail(orderId: string, status: string, buyerEmail: string): Promise<void> {
    const template = this.getEmailTemplate(status);
    await this.sendWithRetry(buyerEmail, template, orderId);
  }

  // 依訂單狀態對應 email 模板文字
  private getEmailTemplate(status: string): string {
    const templates: Record<string, string> = {
      shipped: '您的訂單已出貨，請注意查收。',
      delivered: '您的訂單已送達，感謝您的購買。',
      cancelled: '您的訂單已取消，如有疑問請聯繫客服。',
    };
    return templates[status] ?? `您的訂單狀態已更新為：${status}`;
  }

  // 發送 email，失敗時進行重試機制（最多 3 次，間隔 5 分鐘）
  private async sendWithRetry(
    buyerEmail: string,
    template: string,
    orderId: string,
    attempt = 1
  ): Promise<void> {
    try {
      await this.sendEmail(buyerEmail, template);
      console.log(`[NotificationService] 通知信發送成功 orderId=${orderId}`);
    } catch (err) {
      if (attempt < MAX_RETRY) {
        // 尚未達到最大重試次數，等待後重試
        console.warn(
          `[NotificationService] 通知信發送失敗，${RETRY_INTERVAL_MS / 60000} 分鐘後重試（第 ${attempt} 次）orderId=${orderId}`
        );
        await this.delay(RETRY_INTERVAL_MS);
        await this.sendWithRetry(buyerEmail, template, orderId, attempt + 1);
      } else {
        // 已達到最大重試次數，記錄錯誤 log 不再重試
        console.error(
          `[NotificationService] 通知信重試 ${MAX_RETRY} 次仍失敗，放棄發送 orderId=${orderId}`,
          err
        );
      }
    }
  }

  // 實際寄送 email 的介接點（由外部 email 服務實作）
  private async sendEmail(to: string, body: string): Promise<void> {
    // TODO: 介接真實 email 服務（如 SendGrid、SES）
    throw new Error('email service not implemented');
  }

  private delay(ms: number): Promise<void> {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }
}
