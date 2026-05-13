// NotificationService: 負責發送訂單狀態相關的通知 email，包含重試機制與錯誤記錄
export class NotificationService {
  private emailClient: EmailClient;
  private logger: Logger;

  // 重試設定：最多重試 3 次，每次間隔 5 分鐘（300000ms）
  private static readonly MAX_RETRY_COUNT = 3;
  private static readonly RETRY_INTERVAL_MS = 5 * 60 * 1000;

  constructor(emailClient: EmailClient, logger: Logger) {
    this.emailClient = emailClient;
    this.logger = logger;
  }

  // 依訂單狀態選擇對應的 email 模板並寄送給買家，失敗時啟動重試機制
  async sendOrderStatusEmail(orderId: string, buyerEmail: string, status: OrderStatus): Promise<void> {
    const template = this.resolveEmailTemplate(status);

    await this.sendWithRetry(orderId, buyerEmail, template);
  }

  // 發送 email，失敗時依重試策略重試，超過次數則記錄錯誤 log
  private async sendWithRetry(
    orderId: string,
    buyerEmail: string,
    template: EmailTemplate,
    attempt: number = 1
  ): Promise<void> {
    try {
      await this.emailClient.send({
        to: buyerEmail,
        subject: template.subject,
        body: template.body(orderId),
      });

      // 發送成功，記錄成功 log
      this.logger.info(`[NotificationService] 通知信寄送成功 orderId=${orderId} attempt=${attempt}`);
    } catch (error) {
      // 判斷是否已達最大重試次數
      if (attempt >= NotificationService.MAX_RETRY_COUNT) {
        // 超過重試次數，記錄錯誤 log，不再重試
        this.logger.error(
          `[NotificationService] 通知信寄送失敗，已達最大重試次數 orderId=${orderId} attempt=${attempt}`,
          error
        );
        return;
      }

      // 未達最大次數，等待間隔後重試
      this.logger.warn(
        `[NotificationService] 通知信寄送失敗，將於 ${NotificationService.RETRY_INTERVAL_MS / 1000}s 後重試 orderId=${orderId} attempt=${attempt}`
      );

      await this.sleep(NotificationService.RETRY_INTERVAL_MS);
      await this.sendWithRetry(orderId, buyerEmail, template, attempt + 1);
    }
  }

  // 根據訂單狀態回傳對應 email 模板
  private resolveEmailTemplate(status: OrderStatus): EmailTemplate {
    const templates: Record<OrderStatus, EmailTemplate> = {
      shipped: {
        subject: '您的訂單已出貨',
        body: (orderId: string) => `您的訂單 ${orderId} 已出貨，請注意收件。`,
      },
      cancelled: {
        subject: '您的訂單已取消',
        body: (orderId: string) => `您的訂單 ${orderId} 已取消。`,
      },
      delivered: {
        subject: '您的訂單已送達',
        body: (orderId: string) => `您的訂單 ${orderId} 已送達，感謝您的購買。`,
      },
    };

    return templates[status];
  }

  private sleep(ms: number): Promise<void> {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }
}

export type OrderStatus = 'shipped' | 'cancelled' | 'delivered';

interface EmailTemplate {
  subject: string;
  body: (orderId: string) => string;
}

export interface EmailClient {
  send(options: { to: string; subject: string; body: string }): Promise<void>;
}

export interface Logger {
  info(message: string): void;
  warn(message: string): void;
  error(message: string, error?: unknown): void;
}
