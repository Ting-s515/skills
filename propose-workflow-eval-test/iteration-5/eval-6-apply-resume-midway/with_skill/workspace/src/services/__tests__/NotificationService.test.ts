/**
 * NotificationService BDD 單元測試
 *
 * 依據 02-gherkin.md 驗收條件撰寫
 * 測試範圍：sendOrderStatusEmail、sendEmailWithRetry 的行為邏輯
 */

import { NotificationService } from '../NotificationService';

describe('NotificationService', () => {
  let service: NotificationService;

  beforeEach(() => {
    service = new NotificationService();
    jest.useFakeTimers();
  });

  afterEach(() => {
    jest.useRealTimers();
    jest.restoreAllMocks();
  });

  // =========================================================
  // Scenario: 訂單狀態更新後寄出通知信
  // =========================================================
  describe('sendOrderStatusEmail', () => {
    it('GivenOrderExists_WhenStatusUpdatedToShipped_ShouldSendShippedEmail', async () => {
      // Given - 買家有一筆訂單
      const sendEmailSpy = jest
        .spyOn(service, 'sendEmail')
        .mockResolvedValue();
      const consoleSpy = jest.spyOn(console, 'log').mockImplementation();

      // When - 管理員將訂單狀態更新為「已出貨」
      await service.sendOrderStatusEmail('order-001', 'shipped');

      // Then - 系統寄出「訂單已出貨」通知信給買家
      expect(sendEmailSpy).toHaveBeenCalledWith('order-001', '訂單已出貨');
      expect(consoleSpy).toHaveBeenCalledWith(
        expect.stringContaining('[SUCCESS]')
      );
    });

    it('GivenOrderExists_WhenStatusUpdatedToDelivered_ShouldSendDeliveredEmail', async () => {
      // Given - 買家有一筆訂單
      const sendEmailSpy = jest
        .spyOn(service, 'sendEmail')
        .mockResolvedValue();

      // When - 訂單狀態更新為「已送達」
      await service.sendOrderStatusEmail('order-002', 'delivered');

      // Then - 系統寄出對應模板
      expect(sendEmailSpy).toHaveBeenCalledWith('order-002', '訂單已送達');
    });

    it('GivenOrderExists_WhenStatusIsUnknown_ShouldSendFallbackEmail', async () => {
      // Given - 訂單狀態為未知類型
      const sendEmailSpy = jest
        .spyOn(service, 'sendEmail')
        .mockResolvedValue();

      // When - 訂單狀態更新為未定義狀態
      await service.sendOrderStatusEmail('order-003', 'processing');

      // Then - 系統寄出預設模板
      expect(sendEmailSpy).toHaveBeenCalledWith(
        'order-003',
        '訂單狀態更新：processing'
      );
    });
  });

  // =========================================================
  // Scenario: 通知信發送失敗時進行重試
  // =========================================================
  describe('sendEmailWithRetry', () => {
    it('GivenOrderStatusUpdated_WhenEmailServiceUnavailable_ShouldRetryAfter5Minutes', async () => {
      // Given - 訂單狀態已更新，email 服務暫時不可用
      let callCount = 0;
      const sendEmailSpy = jest
        .spyOn(service, 'sendEmail')
        .mockImplementation(async () => {
          callCount++;
          if (callCount <= 1) {
            throw new Error('Email service unavailable');
          }
        });
      const warnSpy = jest.spyOn(console, 'warn').mockImplementation();

      // When - email 服務暫時不可用
      const sendPromise = service.sendEmailWithRetry('order-004', '訂單已出貨', 0);

      // 等待初次嘗試失敗
      await sendPromise;

      // Then - 系統在 5 分鐘後安排重試
      expect(warnSpy).toHaveBeenCalledWith(
        expect.stringContaining('[RETRY 1/3]')
      );

      // 推進計時器 5 分鐘，觸發重試
      jest.advanceTimersByTime(5 * 60 * 1000);

      // 確認第二次呼叫 sendEmail
      expect(sendEmailSpy).toHaveBeenCalledTimes(2);
    });

    it('GivenEmailFailed_WhenRetryCount2_ShouldScheduleAnotherRetry', async () => {
      // Given - 通知信第 2 次重試仍失敗
      const sendEmailSpy = jest
        .spyOn(service, 'sendEmail')
        .mockRejectedValue(new Error('Still unavailable'));
      const warnSpy = jest.spyOn(console, 'warn').mockImplementation();
      jest.spyOn(console, 'error').mockImplementation();

      // When - 在第 2 次重試時呼叫
      await service.sendEmailWithRetry('order-005', '訂單已出貨', 1);

      // Then - 系統安排第 3 次重試（最後一次）
      expect(warnSpy).toHaveBeenCalledWith(
        expect.stringContaining('[RETRY 2/3]')
      );
    });

    // =========================================================
    // Scenario: 重試 3 次仍失敗時記錄錯誤
    // =========================================================
    it('GivenRetried3Times_WhenStillFails_ShouldLogErrorAndStop', async () => {
      // Given - 通知信已重試 3 次，第 3 次仍失敗
      const sendEmailSpy = jest
        .spyOn(service, 'sendEmail')
        .mockRejectedValue(new Error('Persistent failure'));
      const errorSpy = jest.spyOn(console, 'error').mockImplementation();
      const warnSpy = jest.spyOn(console, 'warn').mockImplementation();

      // When - 已達最大重試次數（retryCount = 3 代表第 3 次失敗後）
      await service.sendEmailWithRetry('order-006', '訂單已出貨', 3);

      // Then - 系統記錄錯誤 log，不再重試
      expect(errorSpy).toHaveBeenCalledWith(
        expect.stringContaining('[ERROR]'),
        expect.any(Error)
      );
      // 不應安排下一次重試（warn 不應被呼叫）
      expect(warnSpy).not.toHaveBeenCalled();
    });

    it('GivenEmailServiceWorking_WhenSendEmail_ShouldLogSuccess', async () => {
      // Given - email 服務正常運作
      jest.spyOn(service, 'sendEmail').mockResolvedValue();
      const consoleSpy = jest.spyOn(console, 'log').mockImplementation();

      // When - 發送 email
      await service.sendEmailWithRetry('order-007', '訂單已出貨', 0);

      // Then - 記錄成功 log
      expect(consoleSpy).toHaveBeenCalledWith(
        expect.stringContaining('[SUCCESS]')
      );
    });
  });
});
