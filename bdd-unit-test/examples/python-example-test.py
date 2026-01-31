"""
Python/pytest BDD 單元測試範例

示範：訂單服務的單元測試，使用 pytest + unittest.mock
命名規範：Given條件_When動作_Should預期行為
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from decimal import Decimal
from datetime import datetime

from order_service import OrderService
from exceptions import InsufficientStockError, InvalidOrderError


class TestOrderService:
    """OrderService 單元測試"""

    @pytest.fixture
    def mock_inventory_repo(self):
        """建立 mock 庫存倉庫"""
        return Mock()

    @pytest.fixture
    def mock_order_repo(self):
        """建立 mock 訂單倉庫"""
        return Mock()

    @pytest.fixture
    def order_service(self, mock_inventory_repo, mock_order_repo):
        """建立被測試的服務實例"""
        return OrderService(
            inventory_repo=mock_inventory_repo,
            order_repo=mock_order_repo
        )

    class TestCreateOrder:
        """create_order 方法的測試"""

        def test_GivenSufficientStock_WhenCreateOrder_ShouldCreateSuccessfully(
            self, order_service, mock_inventory_repo, mock_order_repo
        ):
            """應該在庫存充足時成功建立訂單"""
            # Given - 產品有足夠庫存
            mock_inventory_repo.get_stock.return_value = 100
            mock_inventory_repo.reserve_stock.return_value = True
            mock_order_repo.save.return_value = {
                "id": "ORD-001",
                "product_id": "PROD-A",
                "quantity": 5,
                "status": "CREATED"
            }

            # When - 建立訂單
            result = order_service.create_order(
                product_id="PROD-A",
                quantity=5,
                customer_id="CUST-001"
            )

            # Then - 訂單應被建立
            assert result["id"] == "ORD-001"
            assert result["status"] == "CREATED"
            # 驗證庫存被保留
            mock_inventory_repo.reserve_stock.assert_called_once_with("PROD-A", 5)

        def test_GivenInsufficientStock_WhenCreateOrder_ShouldRaiseError(
            self, order_service, mock_inventory_repo
        ):
            """應該在庫存不足時拋出 InsufficientStockError"""
            # Given - 產品庫存不足
            mock_inventory_repo.get_stock.return_value = 3

            # When & Then - 應拋出庫存不足錯誤
            with pytest.raises(InsufficientStockError) as exc_info:
                order_service.create_order(
                    product_id="PROD-A",
                    quantity=10,
                    customer_id="CUST-001"
                )

            assert "Insufficient stock" in str(exc_info.value)
            assert "PROD-A" in str(exc_info.value)

        def test_GivenZeroOrNegativeQuantity_WhenCreateOrder_ShouldRaiseError(
            self, order_service
        ):
            """應該在數量為零或負數時拋出 InvalidOrderError"""
            # Given - 無效的數量

            # When & Then - 數量為零
            with pytest.raises(InvalidOrderError) as exc_info:
                order_service.create_order(
                    product_id="PROD-A",
                    quantity=0,
                    customer_id="CUST-001"
                )
            assert "Quantity must be positive" in str(exc_info.value)

            # When & Then - 數量為負數
            with pytest.raises(InvalidOrderError):
                order_service.create_order(
                    product_id="PROD-A",
                    quantity=-5,
                    customer_id="CUST-001"
                )

    class TestCancelOrder:
        """cancel_order 方法的測試"""

        def test_GivenOrderExists_WhenCancel_ShouldCancelAndReleaseStock(
            self, order_service, mock_order_repo, mock_inventory_repo
        ):
            """應該取消訂單並釋放庫存"""
            # Given - 訂單存在且狀態為 CREATED
            mock_order_repo.find_by_id.return_value = {
                "id": "ORD-001",
                "product_id": "PROD-A",
                "quantity": 5,
                "status": "CREATED"
            }

            # When - 取消訂單
            result = order_service.cancel_order("ORD-001")

            # Then - 訂單應被取消且庫存釋放
            assert result["status"] == "CANCELLED"
            mock_inventory_repo.release_stock.assert_called_once_with("PROD-A", 5)

        def test_GivenOrderAlreadyShipped_WhenCancel_ShouldRaiseError(
            self, order_service, mock_order_repo
        ):
            """應該在訂單已出貨時拋出錯誤"""
            # Given - 訂單已出貨
            mock_order_repo.find_by_id.return_value = {
                "id": "ORD-001",
                "status": "SHIPPED"
            }

            # When & Then - 應拋出無法取消錯誤
            with pytest.raises(InvalidOrderError) as exc_info:
                order_service.cancel_order("ORD-001")

            assert "Cannot cancel shipped order" in str(exc_info.value)

        def test_GivenOrderNotExists_WhenCancel_ShouldRaiseError(
            self, order_service, mock_order_repo
        ):
            """應該在訂單不存在時拋出錯誤"""
            # Given - 訂單不存在
            mock_order_repo.find_by_id.return_value = None

            # When & Then - 應拋出訂單不存在錯誤
            with pytest.raises(InvalidOrderError) as exc_info:
                order_service.cancel_order("ORD-999")

            assert "Order not found" in str(exc_info.value)

    class TestCalculateOrderTotal:
        """calculate_order_total 方法的測試"""

        def test_GivenOrderItems_WhenCalculateTotal_ShouldReturnCorrectSum(
            self, order_service, mock_order_repo
        ):
            """應該正確計算無折扣的訂單總額"""
            # Given - 訂單項目
            mock_order_repo.find_by_id.return_value = {
                "id": "ORD-001",
                "items": [
                    {"product_id": "A", "quantity": 2, "unit_price": Decimal("100.00")},
                    {"product_id": "B", "quantity": 3, "unit_price": Decimal("50.00")},
                ]
            }

            # When - 計算總額
            total = order_service.calculate_order_total("ORD-001")

            # Then - 總額應為 2*100 + 3*50 = 350
            assert total == Decimal("350.00")

        def test_GivenTotalExceedsThreshold_WhenCalculate_ShouldApplyDiscount(
            self, order_service, mock_order_repo
        ):
            """應該在總額超過門檻時套用折扣"""
            # Given - 訂單總額超過 1000（10% 折扣門檻）
            mock_order_repo.find_by_id.return_value = {
                "id": "ORD-001",
                "items": [
                    {"product_id": "A", "quantity": 10, "unit_price": Decimal("150.00")},
                ]
            }

            # When - 計算總額（含折扣）
            total = order_service.calculate_order_total("ORD-001")

            # Then - 應套用 10% 折扣：1500 * 0.9 = 1350
            assert total == Decimal("1350.00")

        def test_GivenNoItems_WhenCalculateTotal_ShouldReturnZero(
            self, order_service, mock_order_repo
        ):
            """應該在訂單無項目時返回零"""
            # Given - 空訂單
            mock_order_repo.find_by_id.return_value = {
                "id": "ORD-001",
                "items": []
            }

            # When - 計算總額
            total = order_service.calculate_order_total("ORD-001")

            # Then - 總額應為 0
            assert total == Decimal("0.00")


class TestOrderServiceWithDatetime:
    """測試涉及時間的場景（示範如何 mock datetime）"""

    @patch('order_service.datetime')
    def test_GivenFixedTime_WhenCreateOrder_ShouldSetCreatedAtCorrectly(
        self, mock_datetime
    ):
        """應該將建立時間設為當前時間"""
        # Given - 固定當前時間
        fixed_time = datetime(2024, 1, 15, 10, 30, 0)
        mock_datetime.now.return_value = fixed_time

        mock_inventory_repo = Mock()
        mock_inventory_repo.get_stock.return_value = 100
        mock_inventory_repo.reserve_stock.return_value = True

        mock_order_repo = Mock()
        mock_order_repo.save.side_effect = lambda order: {
            **order,
            "id": "ORD-001"
        }

        service = OrderService(mock_inventory_repo, mock_order_repo)

        # When - 建立訂單
        result = service.create_order(
            product_id="PROD-A",
            quantity=1,
            customer_id="CUST-001"
        )

        # Then - 建立時間應為固定時間
        saved_order = mock_order_repo.save.call_args[0][0]
        assert saved_order["created_at"] == fixed_time
