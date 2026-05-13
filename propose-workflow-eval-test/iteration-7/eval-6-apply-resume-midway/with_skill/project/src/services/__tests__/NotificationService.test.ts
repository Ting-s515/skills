/**
 * NotificationService BDD 單元測試
 *
 * 涵蓋 02-gherkin.md 定義的三個 Scenario：
 * 1. 訂單狀態更新後寄出通知信
 * 2. 通知信發送失敗時進行重試（最多 3 次，間隔 5 分鐘）
 * 3. 重試 3 次仍失敗時記錄錯誤 log，不再重試
 */

import { NotificationService, EmailClient, Logger, OrderStatus } from '../NotificationService';

describe('NotificationService', () => {
  let service: NotificationService;
  let mockEmailClient: jest.Mocked<EmailClient>;
  let mockLogger: jest.Mocked<Logger>;

  beforeEach(() => {
    // 使用 fake timers 控制 sleep 間隔，避免測試真實等待 5 分鐘
    jest.useFakeTimers();

    mockEmailClient = {
      send: jest.fn(),
    };

    mockLogger = {
      info: jest.fn(),
      warn: jest.fn(),
      error: jest.fn(),
    };

    service = new NotificationService(mockEmailClient, mockLogger);
  });

  afterEach(() => {
    jest.useRealTimers();
    jest.clearAllMocks();
  });

  describe('sendOrderStatusEmail', () => {
    // =========================================================
    // Scenario 1: 訂單狀態更新後寄出通知信
    // =========================================================

    it('GivenOrderWithShippedStatus_WhenSendEmail_ShouldSendCorrectTemplate', async () => {
      // Given - 買家有一筆訂單，狀態為已出貨
      mockEmailClient.send.mockResolvedValue(undefined);
      const orderId = 'order-001';
      const buyerEmail = 'buyer@example.com';
      const status: OrderStatus = 'shipped';

      // When - 管理員將訂單狀態更新為「已出貨」，觸發通知
      await service.sendOrderStatusEmail(orderId, buyerEmail, status);

      // Then - 系統寄出「訂單已出貨」通知信給買家
      expect(mockEmailClient.send).toHaveBeenCalledTimes(1);
      expect(mockEmailClient.send).toHaveBeenCalledWith({
        to: buyerEmail,
        subject: '您的訂單已出貨',
        body: `您的訂單 ${orderId} 已出貨，請注意收件。`,
      });
    });

    it('GivenEmailSentSuccessfully_WhenSendEmail_ShouldLogSuccess', async () => {
      // Given - email 服務正常可用
      mockEmailClient.send.mockResolvedValue(undefined);

      // When - 寄送通知信
      await service.sendOrderStatusEmail('order-001', 'buyer@example.com', 'shipped');

      // Then - 應記錄成功 log
      expect(mockLogger.info).toHaveBeenCalledTimes(1);
      expect(mockLogger.info).toHaveBeenCalledWith(
        expect.stringContaining('通知信寄送成功')
      );
      expect(mockLogger.error).not.toHaveBeenCalled();
    });

    // =========================================================
    // Scenario 2: 通知信發送失敗時進行重試（最多 3 次，間隔 5 分鐘）
    // =========================================================

    it('GivenEmailServiceUnavailable_WhenSendFails_ShouldRetryAfter5Minutes', async () => {
      // Given - 訂單狀態已更新，email 服務第一次失敗、第二次成功
      mockEmailClient.send
        .mockRejectedValueOnce(new Error('Service unavailable'))
        .mockResolvedValueOnce(undefined);

      // When - 發送通知信（非同步執行，搭配 fake timers 推進時間）
      const sendPromise = service.sendOrderStatusEmail('order-002', 'buyer@example.com', 'shipped');

      // 第一次失敗後，推進 5 分鐘讓重試發生
      await jest.advanceTimersByTimeAsync(5 * 60 * 1000);
      await sendPromise;

      // Then - 系統應重試一次，共呼叫 email 兩次
      expect(mockEmailClient.send).toHaveBeenCalledTimes(2);
      // 應記錄 warn（重試中）
      expect(mockLogger.warn).toHaveBeenCalledWith(
        expect.stringContaining('將於 300s 後重試')
      );
    });

    it('GivenEmailServiceUnavailable_WhenSendFails_ShouldRetryAtMost3Times', async () => {
      // Given - 訂單狀態已更新，email 服務持續不可用
      mockEmailClient.send.mockRejectedValue(new Error('Service unavailable'));

      // When - 發送通知信，推進足夠時間讓 3 次重試都發生
      const sendPromise = service.sendOrderStatusEmail('order-003', 'buyer@example.com', 'shipped');

      // 推進兩個 5 分鐘間隔（第1次失敗→等5分鐘→第2次失敗→等5分鐘→第3次失敗→停止）
      await jest.advanceTimersByTimeAsync(5 * 60 * 1000);
      await jest.advanceTimersByTimeAsync(5 * 60 * 1000);
      await sendPromise;

      // Then - 共嘗試 3 次（最多重試 3 次）
      expect(mockEmailClient.send).toHaveBeenCalledTimes(3);
    });

    // =========================================================
    // Scenario 3: 重試 3 次仍失敗時記錄錯誤 log，不再重試
    // =========================================================

    it('GivenEmailFailedAfter3Retries_WhenMaxRetriesReached_ShouldLogErrorAndStop', async () => {
      // Given - 通知信已重試 3 次，每次都失敗
      mockEmailClient.send.mockRejectedValue(new Error('Persistent failure'));

      // When - 發送通知信，推進足夠時間讓所有重試執行
      const sendPromise = service.sendOrderStatusEmail('order-004', 'buyer@example.com', 'shipped');

      await jest.advanceTimersByTimeAsync(5 * 60 * 1000);
      await jest.advanceTimersByTimeAsync(5 * 60 * 1000);
      await sendPromise;

      // Then - 系統記錄錯誤 log，不再重試（第 3 次後停止）
      expect(mockLogger.error).toHaveBeenCalledTimes(1);
      expect(mockLogger.error).toHaveBeenCalledWith(
        expect.stringContaining('已達最大重試次數'),
        expect.any(Error)
      );
      // 確認在第 3 次失敗後不再呼叫 email send
      expect(mockEmailClient.send).toHaveBeenCalledTimes(3);
      expect(mockLogger.info).not.toHaveBeenCalled();
    });

    it('GivenEmailFailedAfter3Retries_WhenMaxRetriesReached_ShouldNotThrow', async () => {
      // Given - 所有嘗試都失敗
      mockEmailClient.send.mockRejectedValue(new Error('Persistent failure'));

      // When - 執行並推進時間
      const sendPromise = service.sendOrderStatusEmail('order-005', 'buyer@example.com', 'shipped');
      await jest.advanceTimersByTimeAsync(5 * 60 * 1000);
      await jest.advanceTimersByTimeAsync(5 * 60 * 1000);

      // Then - 不應拋出例外（錯誤已被 log 處理）
      await expect(sendPromise).resolves.toBeUndefined();
    });
  });
});
