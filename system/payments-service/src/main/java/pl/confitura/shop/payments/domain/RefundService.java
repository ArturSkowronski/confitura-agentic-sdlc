package pl.confitura.shop.payments.domain;

/**
 * Zwroty. Na razie tylko pełne: zwroty częściowe wyłączyliśmy po incydencie
 * INC-2026-03-14 (podwójny zwrot przy ponowieniu żądania), zob. ops/incidents.
 */
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
        if (payment.status() == PaymentStatus.REFUNDED) {
            return payment; // idempotentnie: drugi zwrot nic nie robi
        }
        gateway.refund(payment.id(), payment.amount(), "refund-" + payment.id());
        Payment refunded = new Payment(payment.id(), payment.orderId(), payment.amount(), payment.amount(), PaymentStatus.REFUNDED);
        payments.save(refunded);
        return refunded;
    }
}
