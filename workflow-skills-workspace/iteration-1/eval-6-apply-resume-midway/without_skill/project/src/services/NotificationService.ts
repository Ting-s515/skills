// NotificationService 負責處理訂單狀態變更後的 email 通知流程

const EMAIL_TEMPLATES: Record<string, string> = {
  shipped: '訂單已出貨',
  delivered: '訂單已送達',
  cancelled: '訂單已取消',
  pending: '訂單待處理',
};

// T2: 實作各狀態的 email 模板選擇與發送
export async function sendOrderStatusEmail(orderId: string, status: string, buyerEmail: string): Promise<void> {
  const template = EMAIL_TEMPLATES[status];
  if (!template) {
    console.error(`[NotificationService] 未知的訂單狀態: ${status}`);
    return;
  }

  // 嘗試發送 email，失敗時啟動重試機制
  await sendWithRetry(orderId, buyerEmail, template);
}

// T3: 重試機制，最多重試 3 次，每次間隔 5 分鐘（300000ms）
async function sendWithRetry(
  orderId: string,
  buyerEmail: string,
  template: string,
  maxRetries: number = 3,
  retryIntervalMs: number = 5 * 60 * 1000
): Promise<void> {
  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      await dispatchEmail(buyerEmail, template);
      console.log(`[NotificationService] 通知信發送成功 orderId=${orderId} attempt=${attempt}`);
      return;
    } catch (error) {
      // 判斷是否仍有重試機會
      const isLastAttempt = attempt === maxRetries;

      if (isLastAttempt) {
        // 重試 3 次皆失敗，記錄錯誤 log，不再重試
        console.error(
          `[NotificationService] 通知信發送失敗，已達最大重試次數 orderId=${orderId} error=${error}`
        );
        return;
      }

      // 尚有重試機會，等待後繼續
      console.warn(
        `[NotificationService] 通知信發送失敗，將在 ${retryIntervalMs / 1000} 秒後重試 ` +
        `orderId=${orderId} attempt=${attempt}/${maxRetries} error=${error}`
      );
      await sleep(retryIntervalMs);
    }
  }
}

// 模擬實際的 email 發送（由外部 email 服務實作）
async function dispatchEmail(to: string, template: string): Promise<void> {
  // 實際整合時替換為真實 email 客戶端呼叫
  throw new Error('email 服務尚未整合');
}

function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}
