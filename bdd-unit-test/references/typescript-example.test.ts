/**
 * TypeScript/Jest BDD 單元測試範例
 *
 * 示範：購物車服務的單元測試
 * 命名規範：Given條件_When動作_Should預期行為
 */

import { CartService } from '../CartService';
import { ProductRepository } from '../ProductRepository';

// Mock 外部依賴
jest.mock('../ProductRepository');

describe('CartService', () => {
  // 共用的測試變數
  let cartService: CartService;
  let mockProductRepo: jest.Mocked<ProductRepository>;

  // 每個測試前重置狀態
  beforeEach(() => {
    mockProductRepo = new ProductRepository() as jest.Mocked<ProductRepository>;
    cartService = new CartService(mockProductRepo);
  });

  describe('addItem', () => {
    it('GivenProductExists_WhenAddItem_ShouldAddToCart', () => {
      // Given - 產品存在於倉庫中
      const product = { id: 1, name: 'Apple', price: 100 };
      mockProductRepo.findById.mockReturnValue(product);

      // When - 將產品加入購物車
      const result = cartService.addItem(1, 2);

      // Then - 購物車應包含該產品
      expect(result.items).toHaveLength(1);
      expect(result.items[0]).toEqual({
        productId: 1,
        quantity: 2,
        subtotal: 200,
      });
    });

    it('GivenProductNotExists_WhenAddItem_ShouldThrowError', () => {
      // Given - 產品不存在
      mockProductRepo.findById.mockReturnValue(null);

      // When & Then - 應拋出 ProductNotFoundError
      expect(() => cartService.addItem(999, 1)).toThrow('Product not found');
    });

    it('GivenItemAlreadyInCart_WhenAddSameItem_ShouldIncreaseQuantity', () => {
      // Given - 購物車已有該產品
      const product = { id: 1, name: 'Apple', price: 100 };
      mockProductRepo.findById.mockReturnValue(product);
      cartService.addItem(1, 2); // 先加入 2 個

      // When - 再加入 3 個
      const result = cartService.addItem(1, 3);

      // Then - 數量應累加為 5
      expect(result.items[0].quantity).toBe(5);
      expect(result.items[0].subtotal).toBe(500);
    });
  });

  describe('removeItem', () => {
    it('GivenItemInCart_WhenRemoveItem_ShouldRemoveFromCart', () => {
      // Given - 購物車有產品
      const product = { id: 1, name: 'Apple', price: 100 };
      mockProductRepo.findById.mockReturnValue(product);
      cartService.addItem(1, 2);

      // When - 移除該產品
      const result = cartService.removeItem(1);

      // Then - 購物車應為空
      expect(result.items).toHaveLength(0);
    });

    it('GivenItemNotInCart_WhenRemoveItem_ShouldDoNothing', () => {
      // Given - 購物車為空

      // When - 嘗試移除不存在的產品
      const result = cartService.removeItem(999);

      // Then - 不應拋出錯誤，購物車保持為空
      expect(result.items).toHaveLength(0);
    });
  });

  describe('calculateTotal', () => {
    it('GivenEmptyCart_WhenCalculateTotal_ShouldReturnZero', () => {
      // Given - 空購物車

      // When - 計算總金額
      const total = cartService.calculateTotal();

      // Then - 總金額應為 0
      expect(total).toBe(0);
    });

    it('GivenMultipleItems_WhenCalculateTotal_ShouldReturnCorrectSum', () => {
      // Given - 購物車有多個產品
      mockProductRepo.findById
        .mockReturnValueOnce({ id: 1, name: 'Apple', price: 100 })
        .mockReturnValueOnce({ id: 2, name: 'Banana', price: 50 });

      cartService.addItem(1, 2);  // 100 * 2 = 200
      cartService.addItem(2, 3);  // 50 * 3 = 150

      // When - 計算總金額
      const total = cartService.calculateTotal();

      // Then - 總金額應為 350
      expect(total).toBe(350);
    });

    it('GivenTotalExceedsThreshold_WhenCalculateTotal_ShouldApplyDiscount', () => {
      // Given - 購物車總金額超過折扣門檻 (1000)
      mockProductRepo.findById.mockReturnValue({ id: 1, name: 'Laptop', price: 500 });
      cartService.addItem(1, 3);  // 500 * 3 = 1500

      // When - 計算總金額（含 10% 折扣）
      const total = cartService.calculateTotal();

      // Then - 應套用 10% 折扣：1500 * 0.9 = 1350
      expect(total).toBe(1350);
    });
  });
});
