package pl.confitura.shop.payments;

import pl.confitura.shop.payments.api.PaymentController;
import pl.confitura.shop.payments.domain.Payment;
import pl.confitura.shop.payments.domain.PaymentStatus;
import pl.confitura.shop.payments.domain.RefundService;
import pl.confitura.shop.payments.infra.FakeCardGatewayClient;
import pl.confitura.shop.payments.infra.InMemoryPaymentRepository;
import pl.confitura.shop.pricing.Money;

/**
 * Punkt składania serwisu płatności. Scenariusze akceptacyjne wchodzą do systemu tylko
 * przez ten moduł, z zaślepką operatora kart, która zachowuje się jak prawdziwy operator.
 */
public final class PaymentsModule {

    private final InMemoryPaymentRepository payments = new InMemoryPaymentRepository();
    private final PaymentController controller = new PaymentController(new RefundService(payments, new FakeCardGatewayClient()));

    public static PaymentsModule production() {
        return new PaymentsModule();
    }

    public PaymentController controller() {
        return controller;
    }

    /** Płatność pobrana u operatora (w prawdziwym systemie przychodzi webhookiem). */
    public void captured(String paymentId, String orderId, String amount) {
        payments.save(new Payment(paymentId, orderId, Money.of(amount), Money.ZERO, PaymentStatus.CAPTURED));
    }
}
