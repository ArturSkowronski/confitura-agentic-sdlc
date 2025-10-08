package pl.confitura.shop.payments.domain;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

import org.junit.jupiter.api.Test;
import pl.confitura.shop.payments.infra.FakeCardGatewayClient;
import pl.confitura.shop.payments.infra.InMemoryPaymentRepository;
import pl.confitura.shop.pricing.Money;

class RefundServiceTest {

    private final InMemoryPaymentRepository repository = new InMemoryPaymentRepository();
    private final RefundService service = new RefundService(repository, new FakeCardGatewayClient());

    @Test
    void refundsInFull() {
        repository.save(new Payment("p-1", "o-1", Money.of("99.00"), Money.ZERO, PaymentStatus.CAPTURED));

        Payment refunded = service.refundInFull("p-1");

        assertEquals(PaymentStatus.REFUNDED, refunded.status());
        assertEquals(Money.of("99.00"), refunded.refunded());
    }

    @Test
    void rejectsUnknownPayment() {
        assertThrows(IllegalArgumentException.class, () -> service.refundInFull("nope"));
    }
}
