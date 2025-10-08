package pl.confitura.shop.payments.domain;

public class RefundService {

    private final PaymentRepository payments;
    private final PaymentGateway gateway;

    public RefundService(PaymentRepository payments, PaymentGateway gateway) {
        this.payments = payments;
        this.gateway = gateway;
    }

    public Payment refundInFull(String paymentId) {
        Payment payment = payments.findById(paymentId)
                .orElseThrow(() -> new IllegalArgumentException("No payment " + paymentId));
        gateway.refund(payment.id(), payment.amount());
        Payment refunded = new Payment(payment.id(), payment.orderId(), payment.amount(), payment.amount(), PaymentStatus.REFUNDED);
        payments.save(refunded);
        return refunded;
    }
}
