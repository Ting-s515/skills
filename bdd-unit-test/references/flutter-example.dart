/// Flutter/Dart BDD 單元測試範例
///
/// 示範：購物車服務的單元測試
/// 命名規範：Given條件_When動作_Should預期行為
/// 框架：flutter_test + mocktail

import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';

import '../cart_service.dart';
import '../product_repository.dart';

// Mock 外部依賴
class MockProductRepository extends Mock implements ProductRepository {}

void main() {
  // 共用的測試變數
  late CartService cartService;
  late MockProductRepository mockProductRepo;

  // 每個測試前重置狀態
  setUp(() {
    mockProductRepo = MockProductRepository();
    cartService = CartService(mockProductRepo);
  });

  group('CartService', () {
    group('addItem', () {
      test('GivenProductExists_WhenAddItem_ShouldAddToCart', () {
        // Given - 產品存在於倉庫中
        final product = Product(id: 1, name: 'Apple', price: 100);
        when(() => mockProductRepo.findById(1)).thenReturn(product);

        // When - 將產品加入購物車
        final result = cartService.addItem(1, 2);

        // Then - 購物車應包含該產品
        expect(result.items, hasLength(1));
        expect(result.items.first.productId, equals(1));
        expect(result.items.first.quantity, equals(2));
        expect(result.items.first.subtotal, equals(200));
      });

      test('GivenProductNotExists_WhenAddItem_ShouldThrowError', () {
        // Given - 產品不存在
        when(() => mockProductRepo.findById(999)).thenReturn(null);

        // When & Then - 應拋出 ProductNotFoundException
        expect(
          () => cartService.addItem(999, 1),
          throwsA(isA<ProductNotFoundException>()),
        );
      });

      test('GivenItemAlreadyInCart_WhenAddSameItem_ShouldIncreaseQuantity', () {
        // Given - 購物車已有該產品
        final product = Product(id: 1, name: 'Apple', price: 100);
        when(() => mockProductRepo.findById(1)).thenReturn(product);
        cartService.addItem(1, 2); // 先加入 2 個

        // When - 再加入 3 個
        final result = cartService.addItem(1, 3);

        // Then - 數量應累加為 5
        expect(result.items.first.quantity, equals(5));
        expect(result.items.first.subtotal, equals(500));
      });
    });

    group('removeItem', () {
      test('GivenItemInCart_WhenRemoveItem_ShouldRemoveFromCart', () {
        // Given - 購物車有產品
        final product = Product(id: 1, name: 'Apple', price: 100);
        when(() => mockProductRepo.findById(1)).thenReturn(product);
        cartService.addItem(1, 2);

        // When - 移除該產品
        final result = cartService.removeItem(1);

        // Then - 購物車應為空
        expect(result.items, isEmpty);
      });

      test('GivenItemNotInCart_WhenRemoveItem_ShouldDoNothing', () {
        // Given - 購物車為空

        // When - 嘗試移除不存在的產品
        final result = cartService.removeItem(999);

        // Then - 不應拋出錯誤，購物車保持為空
        expect(result.items, isEmpty);
      });
    });

    group('calculateTotal', () {
      test('GivenEmptyCart_WhenCalculateTotal_ShouldReturnZero', () {
        // Given - 空購物車

        // When - 計算總金額
        final total = cartService.calculateTotal();

        // Then - 總金額應為 0
        expect(total, equals(0));
      });

      test('GivenMultipleItems_WhenCalculateTotal_ShouldReturnCorrectSum', () {
        // Given - 購物車有多個產品
        when(() => mockProductRepo.findById(1))
            .thenReturn(Product(id: 1, name: 'Apple', price: 100));
        when(() => mockProductRepo.findById(2))
            .thenReturn(Product(id: 2, name: 'Banana', price: 50));

        cartService.addItem(1, 2); // 100 * 2 = 200
        cartService.addItem(2, 3); // 50 * 3 = 150

        // When - 計算總金額
        final total = cartService.calculateTotal();

        // Then - 總金額應為 350
        expect(total, equals(350));
      });

      test('GivenTotalExceedsThreshold_WhenCalculateTotal_ShouldApplyDiscount', () {
        // Given - 購物車總金額超過折扣門檻 (1000)
        when(() => mockProductRepo.findById(1))
            .thenReturn(Product(id: 1, name: 'Laptop', price: 500));
        cartService.addItem(1, 3); // 500 * 3 = 1500

        // When - 計算總金額（含 10% 折扣）
        final total = cartService.calculateTotal();

        // Then - 應套用 10% 折扣：1500 * 0.9 = 1350
        expect(total, equals(1350));
      });
    });
  });
}
