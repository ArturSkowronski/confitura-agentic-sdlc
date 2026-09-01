package pl.confitura.shop.payments.api;

import pl.confitura.shop.payments.domain.Payment;
import pl.confitura.shop.payments.domain.RefundService;

public class PaymentController {

    public record RefundResponse(String paymentId, String status, String refunded) {
    }

    private final RefundService refundService;

    public PaymentController(RefundService refundService) {
        this.refundService = refundService;
    }

    public RefundResponse refund(String paymentId) {
        Payment payment = refundService.refundInFull(paymentId);
        return new RefundResponse(payment.id(), payment.status().name(), payment.refunded().toString());
    }
}
