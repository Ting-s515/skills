// T2 實作：依訂單狀態選擇對應 email 模板並發送通知信
// T3 實作：加入通知失敗時的重試機制（最多 3 次，間隔 5 分鐘）與錯誤 log

const MAX_RETRY_COUNT = 3;
const RETRY_INTERVAL_MS = 5 * 60 * 1000; // 5 分鐘

export class NotificationService {
  // 依訂單狀態送出對應通知信給買家，失敗時進入重試機制
  async sendOrderStatusEmail(orderId: string, status: string, buyerEmail: string): Promise<void> {
    const template = this.getEmailTemplate(status);
    if (!template) {
      console.error(`No email template found for status: ${status}`);
      return;
    }
    await this.sendWithRetry(buyerEmail, template.subject, template.body(orderId), orderId);
  }

  // 依訂單狀態取得對應 email 模板
  private getEmailTemplate(status: string): { subject: string; body: (orderId: string) => string } | null {
    const templates: Record<string, { subject: string; body: (orderId: string) => string }> = {
      shipped: {
        subject: '訂單已出貨通知',
        body: (orderId) => `您的訂單 ${orderId} 已出貨，請耐心等候。`,
      },
      delivered: {
        subject: '訂單已送達通知',
        body: (orderId) => `您的訂單 ${orderId} 已送達。`,
      },
      cancelled: {
        subject: '訂單已取消通知',
        body: (orderId) => `您的訂單 ${orderId} 已取消。`,
      },
    };
    return templates[status] ?? null;
  }

  // 發送 email 並在失敗時進行重試，最多重試 MAX_RETRY_COUNT 次，間隔 RETRY_INTERVAL_MS
  private async sendWithRetry(
    to: string,
    subject: string,
    body: string,
    orderId: string,
    attempt = 1
  ): Promise<void> {
    try {
      await this.sendEmail(to, subject, body);
      console.log(`[SUCCESS] Email sent to ${to} for order ${orderId} (attempt ${attempt})`);
    } catch (error) {
      if (attempt >= MAX_RETRY_COUNT) {
        // 已達最大重試次數，記錄錯誤 log，不再重試
        console.error(
          `[ERROR] Failed to send email for order ${orderId} after ${MAX_RETRY_COUNT} attempts. Error: ${error}`
        );
        return;
      }
      // 等待 RETRY_INTERVAL_MS 後重試
      console.warn(
        `[WARN] Email send failed for order ${orderId} (attempt ${attempt}), retrying in ${RETRY_INTERVAL_MS / 1000}s...`
      );
      await this.delay(RETRY_INTERVAL_MS);
      await this.sendWithRetry(to, subject, body, orderId, attempt + 1);
    }
  }

  // 發送 email（實際傳送邏輯）
  private async sendEmail(to: string, subject: string, body: string): Promise<void> {
    // 模擬 email 傳送
    console.log(`Sending email to ${to}: [${subject}] ${body}`);
  }

  // 等待指定毫秒數
  private delay(ms: number): Promise<void> {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }
}
