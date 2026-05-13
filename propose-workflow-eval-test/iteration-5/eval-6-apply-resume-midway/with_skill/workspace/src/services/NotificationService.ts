// NotificationService: 處理訂單通知信的發送邏輯，含重試機制
const MAX_RETRY_COUNT = 3;
const RETRY_INTERVAL_MS = 5 * 60 * 1000; // 5 分鐘

export class NotificationService {
  // 依訂單狀態選擇對應 email 模板並發送，失敗時進入重試流程（T2 + T3 實作）
  async sendOrderStatusEmail(orderId: string, status: string): Promise<void> {
    const template = this.getEmailTemplate(status);
    await this.sendEmailWithRetry(orderId, template);
  }

  // 根據訂單狀態取得對應的 email 模板主旨
  private getEmailTemplate(status: string): string {
    const templates: Record<string, string> = {
      shipped: '訂單已出貨',
      delivered: '訂單已送達',
      cancelled: '訂單已取消',
    };
    return templates[status] ?? `訂單狀態更新：${status}`;
  }

  // 帶重試機制的 email 發送邏輯（T3 實作）
  // 最多重試 MAX_RETRY_COUNT 次，間隔 RETRY_INTERVAL_MS，全部失敗記錄錯誤 log
  async sendEmailWithRetry(
    orderId: string,
    subject: string,
    retryCount: number = 0
  ): Promise<void> {
    try {
      await this.sendEmail(orderId, subject);
      console.log(`[SUCCESS] Email sent for order ${orderId}: ${subject}`);
    } catch (error) {
      if (retryCount < MAX_RETRY_COUNT) {
        // 尚未達到最大重試次數，排程下一次重試
        console.warn(
          `[RETRY ${retryCount + 1}/${MAX_RETRY_COUNT}] Email failed for order ${orderId}, retrying in 5 minutes...`
        );
        setTimeout(() => {
          this.sendEmailWithRetry(orderId, subject, retryCount + 1);
        }, RETRY_INTERVAL_MS);
      } else {
        // 已達最大重試次數，記錄錯誤 log 並停止重試
        console.error(
          `[ERROR] Email failed after ${MAX_RETRY_COUNT} retries for order ${orderId}: ${subject}`,
          error
        );
      }
    }
  }

  // 發送 email（底層方法，供測試 mock 使用）
  async sendEmail(orderId: string, subject: string): Promise<void> {
    // 實際 email 發送邏輯（整合 email 服務）
    console.log(`Sending email for order ${orderId}: ${subject}`);
  }
}
