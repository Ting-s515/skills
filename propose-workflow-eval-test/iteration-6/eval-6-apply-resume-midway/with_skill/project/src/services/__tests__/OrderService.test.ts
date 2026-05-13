import { OrderService, Order } from '../OrderService';
import { NotificationService } from '../NotificationService';

// Mock NotificationService，隔離外部 email 發送依賴
jest.mock('../NotificationService');

describe('OrderService', () => {
  let orderService: OrderService;
  let mockNotificationService: jest.Mocked<NotificationService>;

  beforeEach(() => {
    // 每次測試前重置 mock 狀態
    mockNotificationService = new NotificationService(
      null as any,
      null as any,
    ) as jest.Mocked<NotificationService>;
    mockNotificationService.sendOrderStatusEmail = jest.fn().mockResolvedValue(undefined);
    orderService = new OrderService(mockNotificationService);
  });

  describe('updateOrderStatus', () => {
    // ✅ Happy Path：Scenario 1 - 訂單狀態更新後應寄出通知信給買家
    it('GivenOrderExists_WhenUpdateStatusToShipped_ShouldSendNotificationToBuyer', async () => {
      // Given - 買家有一筆訂單
      const order: Order = {
        id: 'order-001',
        buyerEmail: 'buyer@example.com',
        status: 'pending',
      };

      // When - 管理員將訂單狀態更新為「已出貨」
      const updatedOrder = await orderService.updateOrderStatus(order, 'shipped');

      // Then - 系統應觸發通知信發送給買家
      expect(updatedOrder.status).toBe('shipped');
      expect(mockNotificationService.sendOrderStatusEmail).toHaveBeenCalledTimes(1);
      expect(mockNotificationService.sendOrderStatusEmail).toHaveBeenCalledWith(
        'buyer@example.com',
        'shipped',
      );
    });

    // ✅ Happy Path：狀態更新應回傳包含新狀態的訂單物件
    it('GivenOrderWithPendingStatus_WhenUpdateStatus_ShouldReturnOrderWithNewStatus', async () => {
      // Given - 訂單初始狀態為 pending
      const order: Order = {
        id: 'order-002',
        buyerEmail: 'test@example.com',
        status: 'pending',
      };

      // When - 更新為 delivered
      const result = await orderService.updateOrderStatus(order, 'delivered');

      // Then - 回傳的訂單應反映新狀態，原始訂單不被修改
      expect(result.status).toBe('delivered');
      expect(result.id).toBe('order-002');
      expect(order.status).toBe('pending'); // 原始物件不可變
    });

    // ⚠️ Edge Case：通知服務拋出例外時，訂單更新流程應一併拋出
    it('GivenNotificationServiceFails_WhenUpdateStatus_ShouldPropagateError', async () => {
      // Given - NotificationService 發送時拋出例外（超過重試上限後理論上不拋出，此測試針對非預期錯誤）
      mockNotificationService.sendOrderStatusEmail.mockRejectedValueOnce(
        new Error('Unexpected notification error'),
      );
      const order: Order = {
        id: 'order-003',
        buyerEmail: 'buyer@example.com',
        status: 'pending',
      };

      // When & Then - 應將例外向上傳遞
      await expect(orderService.updateOrderStatus(order, 'shipped')).rejects.toThrow(
        'Unexpected notification error',
      );
    });
  });
});
