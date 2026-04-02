// 通知服務：負責依訂單狀態選擇 email 模板並發送，失敗時進行重試

const MAX_RETRY_COUNT = 3;
const RETRY_INTERVAL_MS = 5 * 60 * 1000; // 5 分鐘

type OrderStatus = 'shipped' | 'paid' | 'cancelled';

interface Order {
  id: string;
  buyerEmail: string;
  status: OrderStatus;
}

// 依訂單狀態對應 email 模板名稱
function getEmailTemplate(status: OrderStatus): string {
  const templates: Record<OrderStatus, string> = {
    shipped: 'order-shipped',
    paid: 'order-paid',
    cancelled: 'order-cancelled',
  };
  return templates[status];
}

// 模擬發送 email（實際實作需替換為真實 email 服務呼叫）
async function sendEmail(to: string, template: string): Promise<void> {
  // TODO: 替換為實際 email 服務整合
  console.log(`[NotificationService] Sending email to ${to} using template ${template}`);
}

// 等待指定毫秒數（用於重試間隔）
function delay(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

// 發送訂單狀態通知信，失敗時最多重試 MAX_RETRY_COUNT 次，間隔 RETRY_INTERVAL_MS
export async function sendOrderStatusEmail(order: Order): Promise<void> {
  const template = getEmailTemplate(order.status);
  let attempt = 0;

  while (attempt < MAX_RETRY_COUNT) {
    try {
      await sendEmail(order.buyerEmail, template);
      console.log(`[NotificationService] Email sent successfully for order ${order.id}`);
      return;
    } catch (error) {
      attempt += 1;

      // 達到最大重試次數時記錄錯誤 log，不再繼續重試
      if (attempt >= MAX_RETRY_COUNT) {
        console.error(
          `[NotificationService] Failed to send email for order ${order.id} after ${MAX_RETRY_COUNT} attempts`,
          error
        );
        return;
      }

      console.warn(
        `[NotificationService] Email send failed for order ${order.id}, retrying (${attempt}/${MAX_RETRY_COUNT})...`
      );
      await delay(RETRY_INTERVAL_MS);
    }
  }
}
