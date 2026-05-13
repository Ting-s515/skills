import { NotificationService, EmailClient, Logger } from '../NotificationService';
import { OrderStatus } from '../OrderService';

describe('NotificationService', () => {
  let mockEmailClient: jest.Mocked<EmailClient>;
  let mockLogger: jest.Mocked<Logger>;
  let mockDelay: jest.Mock<Promise<void>, [number]>;

  beforeEach(() => {
    // 每次測試前重置所有 mock 狀態
    mockEmailClient = {
      send: jest.fn(),
    };
    mockLogger = {
      info: jest.fn(),
      error: jest.fn(),
    };
    // 注入立即解析的 delay，避免測試等待真實 5 分鐘
    mockDelay = jest.fn().mockResolvedValue(undefined);
  });

  describe('sendOrderStatusEmail', () => {
    // ✅ Happy Path：Scenario 1 對應 - 發送成功時應記錄 info log
    it('GivenOrderStatusShipped_WhenSendEmail_ShouldSendCorrectTemplateAndLogSuccess', async () => {
      // Given - email 服務正常可用，訂單狀態為「已出貨」
      mockEmailClient.send.mockResolvedValueOnce(undefined);
      const service = new NotificationService(mockEmailClient, mockLogger, mockDelay);

      // When - 發送訂單狀態通知信
      await service.sendOrderStatusEmail('buyer@example.com', 'shipped');

      // Then - 應以正確主旨發送，且記錄成功 log
      expect(mockEmailClient.send).toHaveBeenCalledTimes(1);
      expect(mockEmailClient.send).toHaveBeenCalledWith(
        'buyer@example.com',
        '您的訂單已出貨',
        '您好，您的訂單已出貨，請耐心等候配送。',
      );
      expect(mockLogger.info).toHaveBeenCalledWith(
        expect.stringContaining('通知信發送成功'),
      );
    });

    // 🔄 State Change：Scenario 2 - email 服務暫時不可用時，應重試最多 3 次
    it('GivenEmailServiceUnavailable_WhenSendEmail_ShouldRetryUpTo3Times', async () => {
      // Given - email 服務前兩次失敗，第三次成功（模擬暫時不可用後恢復）
      mockEmailClient.send
        .mockRejectedValueOnce(new Error('Service unavailable'))
        .mockRejectedValueOnce(new Error('Service unavailable'))
        .mockResolvedValueOnce(undefined);
      const service = new NotificationService(mockEmailClient, mockLogger, mockDelay);

      // When - 發送通知信
      await service.sendOrderStatusEmail('buyer@example.com', 'shipped');

      // Then - 應嘗試 3 次（2 次失敗 + 1 次成功），且呼叫兩次 delay（每次失敗後等待）
      expect(mockEmailClient.send).toHaveBeenCalledTimes(3);
      expect(mockDelay).toHaveBeenCalledTimes(2);
      expect(mockLogger.info).toHaveBeenCalledWith(
        expect.stringContaining('通知信發送成功'),
      );
    });

    // ❌ Error Case：Scenario 3 - 重試 3 次仍失敗時，應記錄錯誤 log 並停止重試
    it('GivenEmailServiceAlwaysFails_WhenSendEmailAfter3Retries_ShouldLogErrorAndStop', async () => {
      // Given - email 服務持續無法使用（3 次嘗試全部失敗）
      mockEmailClient.send.mockRejectedValue(new Error('Permanent failure'));
      const service = new NotificationService(mockEmailClient, mockLogger, mockDelay);

      // When - 發送通知信（預期不拋出例外，而是靜默記錄錯誤）
      await service.sendOrderStatusEmail('buyer@example.com', 'shipped');

      // Then - 應恰好嘗試 3 次後停止，且記錄最終錯誤 log
      expect(mockEmailClient.send).toHaveBeenCalledTimes(3);
      expect(mockLogger.error).toHaveBeenLastCalledWith(
        expect.stringContaining('已重試 3 次，停止重試'),
        expect.any(Error),
      );
      // 確認不再重試（delay 只在前兩次失敗後呼叫，第三次失敗直接結束）
      expect(mockDelay).toHaveBeenCalledTimes(2);
      // 不應記錄成功 log
      expect(mockLogger.info).not.toHaveBeenCalled();
    });

    // ⚠️ Edge Case：重試間隔應使用正確的延遲時間（5 分鐘）
    it('GivenEmailServiceFails_WhenRetrying_ShouldWait5MinutesBetweenRetries', async () => {
      // Given - 前兩次失敗，第三次成功
      mockEmailClient.send
        .mockRejectedValueOnce(new Error('timeout'))
        .mockRejectedValueOnce(new Error('timeout'))
        .mockResolvedValueOnce(undefined);
      const service = new NotificationService(mockEmailClient, mockLogger, mockDelay);

      // When - 觸發重試
      await service.sendOrderStatusEmail('buyer@example.com', 'delivered');

      // Then - 每次重試間隔應為 300,000ms（5 分鐘）
      expect(mockDelay).toHaveBeenCalledWith(5 * 60 * 1000);
    });
  });
});
