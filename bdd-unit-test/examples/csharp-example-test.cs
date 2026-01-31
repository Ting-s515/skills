using System;
using System.Collections.Generic;
using System.Threading.Tasks;
using Moq;
using Xunit;
using FluentAssertions;

namespace MyApp.Tests.Services;

/// <summary>
/// C#/xUnit BDD 單元測試範例
///
/// 示範：支付服務的單元測試，使用 Moq + FluentAssertions
/// 命名規範：Given條件_When動作_Should預期行為
/// </summary>
public class PaymentServiceTests
{
    private readonly Mock<IPaymentGateway> _mockPaymentGateway;
    private readonly Mock<IOrderRepository> _mockOrderRepository;
    private readonly Mock<INotificationService> _mockNotificationService;
    private readonly PaymentService _paymentService;

    public PaymentServiceTests()
    {
        // 初始化 Mock 物件
        _mockPaymentGateway = new Mock<IPaymentGateway>();
        _mockOrderRepository = new Mock<IOrderRepository>();
        _mockNotificationService = new Mock<INotificationService>();

        // 建立被測試的服務
        _paymentService = new PaymentService(
            _mockPaymentGateway.Object,
            _mockOrderRepository.Object,
            _mockNotificationService.Object
        );
    }

    #region ProcessPayment Tests

    [Fact]
    public async Task GivenGatewayApproves_WhenProcessPayment_ShouldCompletePayment()
    {
        // Given - 支付閘道批准交易
        var orderId = Guid.NewGuid();
        var order = new Order
        {
            Id = orderId,
            Amount = 100.00m,
            Status = OrderStatus.Pending,
            CustomerId = "CUST-001"
        };

        _mockOrderRepository
            .Setup(r => r.GetByIdAsync(orderId))
            .ReturnsAsync(order);

        _mockPaymentGateway
            .Setup(g => g.ChargeAsync(It.IsAny<PaymentRequest>()))
            .ReturnsAsync(new PaymentResult
            {
                Success = true,
                TransactionId = "TXN-12345"
            });

        // When - 處理支付
        var result = await _paymentService.ProcessPaymentAsync(orderId, "4111111111111111");

        // Then - 支付應成功完成
        result.Should().NotBeNull();
        result.Success.Should().BeTrue();
        result.TransactionId.Should().Be("TXN-12345");

        // 驗證訂單狀態被更新
        _mockOrderRepository.Verify(
            r => r.UpdateAsync(It.Is<Order>(o => o.Status == OrderStatus.Paid)),
            Times.Once
        );

        // 驗證通知被發送
        _mockNotificationService.Verify(
            n => n.SendPaymentConfirmationAsync("CUST-001", orderId),
            Times.Once
        );
    }

    [Fact]
    public async Task GivenOrderNotFound_WhenProcessPayment_ShouldThrowException()
    {
        // Given - 訂單不存在
        var orderId = Guid.NewGuid();

        _mockOrderRepository
            .Setup(r => r.GetByIdAsync(orderId))
            .ReturnsAsync((Order)null!);

        // When & Then - 應拋出 OrderNotFoundException
        await _paymentService
            .Invoking(s => s.ProcessPaymentAsync(orderId, "4111111111111111"))
            .Should()
            .ThrowAsync<OrderNotFoundException>()
            .WithMessage($"Order with ID {orderId} was not found");
    }

    [Fact]
    public async Task GivenOrderAlreadyPaid_WhenProcessPayment_ShouldThrowException()
    {
        // Given - 訂單已支付
        var orderId = Guid.NewGuid();
        var order = new Order
        {
            Id = orderId,
            Amount = 100.00m,
            Status = OrderStatus.Paid  // 已支付
        };

        _mockOrderRepository
            .Setup(r => r.GetByIdAsync(orderId))
            .ReturnsAsync(order);

        // When & Then - 應拋出 InvalidOperationException
        await _paymentService
            .Invoking(s => s.ProcessPaymentAsync(orderId, "4111111111111111"))
            .Should()
            .ThrowAsync<InvalidOperationException>()
            .WithMessage("Order has already been paid");
    }

    [Fact]
    public async Task GivenGatewayDeclines_WhenProcessPayment_ShouldMarkOrderFailed()
    {
        // Given - 支付閘道拒絕交易
        var orderId = Guid.NewGuid();
        var order = new Order
        {
            Id = orderId,
            Amount = 100.00m,
            Status = OrderStatus.Pending
        };

        _mockOrderRepository
            .Setup(r => r.GetByIdAsync(orderId))
            .ReturnsAsync(order);

        _mockPaymentGateway
            .Setup(g => g.ChargeAsync(It.IsAny<PaymentRequest>()))
            .ReturnsAsync(new PaymentResult
            {
                Success = false,
                ErrorMessage = "Insufficient funds"
            });

        // When - 處理支付
        var result = await _paymentService.ProcessPaymentAsync(orderId, "4111111111111111");

        // Then - 支付應失敗
        result.Success.Should().BeFalse();
        result.ErrorMessage.Should().Be("Insufficient funds");

        // 驗證訂單狀態被標記為失敗
        _mockOrderRepository.Verify(
            r => r.UpdateAsync(It.Is<Order>(o => o.Status == OrderStatus.PaymentFailed)),
            Times.Once
        );

        // 驗證不應發送確認通知
        _mockNotificationService.Verify(
            n => n.SendPaymentConfirmationAsync(It.IsAny<string>(), It.IsAny<Guid>()),
            Times.Never
        );
    }

    #endregion

    #region RefundPayment Tests

    [Theory]
    [InlineData(50.00, true)]   // 部分退款
    [InlineData(100.00, true)]  // 全額退款
    public async Task GivenValidAmount_WhenRefundPayment_ShouldProcessRefund(
        decimal refundAmount, bool expectedSuccess)
    {
        // Given - 有效的退款金額
        var orderId = Guid.NewGuid();
        var order = new Order
        {
            Id = orderId,
            Amount = 100.00m,
            Status = OrderStatus.Paid,
            TransactionId = "TXN-12345"
        };

        _mockOrderRepository
            .Setup(r => r.GetByIdAsync(orderId))
            .ReturnsAsync(order);

        _mockPaymentGateway
            .Setup(g => g.RefundAsync(It.IsAny<RefundRequest>()))
            .ReturnsAsync(new RefundResult { Success = true });

        // When - 處理退款
        var result = await _paymentService.RefundPaymentAsync(orderId, refundAmount);

        // Then - 退款應成功
        result.Success.Should().Be(expectedSuccess);
    }

    [Fact]
    public async Task GivenAmountExceedsOriginal_WhenRefundPayment_ShouldThrowException()
    {
        // Given - 退款金額超過原始金額
        var orderId = Guid.NewGuid();
        var order = new Order
        {
            Id = orderId,
            Amount = 100.00m,
            Status = OrderStatus.Paid
        };

        _mockOrderRepository
            .Setup(r => r.GetByIdAsync(orderId))
            .ReturnsAsync(order);

        // When & Then - 應拋出 InvalidRefundAmountException
        await _paymentService
            .Invoking(s => s.RefundPaymentAsync(orderId, 150.00m))
            .Should()
            .ThrowAsync<InvalidRefundAmountException>()
            .WithMessage("Refund amount cannot exceed original payment amount");
    }

    #endregion

    #region Edge Cases

    [Theory]
    [InlineData("")]
    [InlineData("   ")]
    [InlineData(null)]
    public async Task GivenInvalidCardNumber_WhenProcessPayment_ShouldThrowException(
        string invalidCardNumber)
    {
        // Given - 無效的卡號
        var orderId = Guid.NewGuid();
        var order = new Order
        {
            Id = orderId,
            Amount = 100.00m,
            Status = OrderStatus.Pending
        };

        _mockOrderRepository
            .Setup(r => r.GetByIdAsync(orderId))
            .ReturnsAsync(order);

        // When & Then - 應拋出 ArgumentException
        await _paymentService
            .Invoking(s => s.ProcessPaymentAsync(orderId, invalidCardNumber))
            .Should()
            .ThrowAsync<ArgumentException>()
            .WithMessage("Card number is required*");
    }

    [Fact]
    public async Task GivenNotificationFails_WhenProcessPayment_ShouldStillSucceed()
    {
        // Given - 通知服務拋出例外
        var orderId = Guid.NewGuid();
        var order = new Order
        {
            Id = orderId,
            Amount = 100.00m,
            Status = OrderStatus.Pending,
            CustomerId = "CUST-001"
        };

        _mockOrderRepository
            .Setup(r => r.GetByIdAsync(orderId))
            .ReturnsAsync(order);

        _mockPaymentGateway
            .Setup(g => g.ChargeAsync(It.IsAny<PaymentRequest>()))
            .ReturnsAsync(new PaymentResult { Success = true, TransactionId = "TXN-12345" });

        _mockNotificationService
            .Setup(n => n.SendPaymentConfirmationAsync(It.IsAny<string>(), It.IsAny<Guid>()))
            .ThrowsAsync(new NotificationException("Email service unavailable"));

        // When & Then - 應拋出例外但支付仍成功（通知失敗不影響支付）
        // 注意：這取決於業務邏輯，此處示範通知失敗不回滾支付
        var result = await _paymentService.ProcessPaymentAsync(orderId, "4111111111111111");

        result.Success.Should().BeTrue();
        result.Warning.Should().Contain("Notification failed");
    }

    #endregion
}
