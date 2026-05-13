// 依訂單狀態對應的 email 模板名稱
const EMAIL_TEMPLATES: Record<string, string> = {
  shipped: 'order-shipped',
  delivered: 'order-delivered',
  cancelled: 'order-cancelled',
};

// 重試機制常數：最多重試 3 次，間隔 5 分鐘
const MAX_RETRY_COUNT = 3;
const RETRY_INTERVAL_MS = 5 * 60 * 1000;

export class NotificationService {
  constructor(
    private readonly emailClient: EmailClient,
    private readonly logger: Logger
  ) {}

  // 依訂單狀態選擇模板並寄出通知信給買家
  async sendOrderStatusEmail(order: Order): Promise<void> {
    const template = EMAIL_TEMPLATES[order.status];

    if (!template) {
      this.logger.warn(`No email template for status: ${order.status}`);
      return;
    }

    await this.sendWithRetry(order, template);
  }

  // 發送 email 並在失敗時進入重試機制，最多重試 MAX_RETRY_COUNT 次
  private async sendWithRetry(order: Order, template: string): Promise<void> {
    let attempt = 0;

    while (attempt <= MAX_RETRY_COUNT) {
      try {
        await this.emailClient.send({
          to: order.buyerEmail,
          template,
          data: { orderId: order.id, status: order.status },
        });

        this.logger.info(
          `Notification email sent for order ${order.id}, status: ${order.status}`
        );
        return;
      } catch (error) {
        attempt += 1;

        // 已超過最大重試次數，記錄錯誤 log 並停止重試
        if (attempt > MAX_RETRY_COUNT) {
          this.logger.error(
            `Failed to send notification email for order ${order.id} after ${MAX_RETRY_COUNT} retries`,
            error
          );
          return;
        }

        this.logger.warn(
          `Notification email failed for order ${order.id}, attempt ${attempt}/${MAX_RETRY_COUNT}. Retrying in ${RETRY_INTERVAL_MS / 1000}s...`
        );

        // 等待重試間隔後再次嘗試
        await this.delay(RETRY_INTERVAL_MS);
      }
    }
  }

  private delay(ms: number): Promise<void> {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }
}

// Type definitions
interface Order {
  id: string;
  status: string;
  buyerEmail: string;
}

interface EmailClient {
  send(options: { to: string; template: string; data: Record<string, unknown> }): Promise<void>;
}

interface Logger {
  info(message: string): void;
  warn(message: string): void;
  error(message: string, error?: unknown): void;
}
