import { OrderStatus } from './OrderService';

export interface EmailClient {
  send(to: string, subject: string, body: string): Promise<void>;
}

export interface Logger {
  info(message: string): void;
  error(message: string, error?: unknown): void;
}

// 重試機制設定：最多 3 次，每次間隔 5 分鐘（300,000ms）
const MAX_RETRY_COUNT = 3;
const RETRY_INTERVAL_MS = 5 * 60 * 1000;

export class NotificationService {
  constructor(
    private emailClient: EmailClient,
    private logger: Logger,
    // 允許注入延遲函式，方便測試覆寫
    private delayFn: (ms: number) => Promise<void> = (ms) =>
      new Promise((resolve) => setTimeout(resolve, ms)),
  ) {}

  // 依訂單狀態選擇對應 email 模板，並發送通知信給買家
  // 若發送失敗，進入重試機制（最多 3 次，間隔 5 分鐘）
  async sendOrderStatusEmail(buyerEmail: string, status: OrderStatus): Promise<void> {
    const { subject, body } = this.getEmailTemplate(status);
    await this.sendWithRetry(buyerEmail, subject, body);
  }

  // 帶有重試邏輯的 email 發送，失敗時等待後重試，超過上限則記錄錯誤 log
  private async sendWithRetry(to: string, subject: string, body: string): Promise<void> {
    let attempt = 0;

    while (attempt < MAX_RETRY_COUNT) {
      try {
        await this.emailClient.send(to, subject, body);
        this.logger.info(`通知信發送成功：${to}，主旨：${subject}`);
        return;
      } catch (error) {
        attempt++;

        if (attempt >= MAX_RETRY_COUNT) {
          // 超過最大重試次數，記錄錯誤 log 並停止重試
          this.logger.error(
            `通知信發送失敗，已重試 ${MAX_RETRY_COUNT} 次，停止重試。收件人：${to}`,
            error,
          );
          return;
        }

        // 尚未達到重試上限，等待後繼續重試
        this.logger.error(
          `通知信發送失敗（第 ${attempt} 次），${RETRY_INTERVAL_MS / 1000 / 60} 分鐘後重試。收件人：${to}`,
          error,
        );
        await this.delayFn(RETRY_INTERVAL_MS);
      }
    }
  }

  // 根據訂單狀態回傳對應的 email 標題與內容
  private getEmailTemplate(status: OrderStatus): { subject: string; body: string } {
    switch (status) {
      case 'shipped':
        return {
          subject: '您的訂單已出貨',
          body: '您好，您的訂單已出貨，請耐心等候配送。',
        };
      case 'delivered':
        return {
          subject: '您的訂單已送達',
          body: '您好，您的訂單已送達，感謝您的購買！',
        };
      case 'cancelled':
        return {
          subject: '您的訂單已取消',
          body: '您好，您的訂單已取消，如有疑問請聯繫客服。',
        };
      default:
        return {
          subject: '您的訂單狀態已更新',
          body: `您好，您的訂單狀態已更新為：${status}`,
        };
    }
  }
}
