package pl.confitura.shop.payments.infra;

import java.util.HashSet;
import java.util.Set;
import pl.confitura.shop.payments.domain.PaymentGateway;
import pl.confitura.shop.pricing.Money;

/** Zaślepka operatora kart. Odrzuca powtórzony klucz idempotencji tak jak prawdziwy operator. */
public class FakeCardGatewayClient implements PaymentGateway {

    private final Set<String> seenKeys = new HashSet<>();

    @Override
    public void refund(String paymentId, Money amount, String idempotencyKey) {
        if (!seenKeys.add(idempotencyKey)) {
            throw new IllegalStateException("Powtórzony klucz idempotencji: " + idempotencyKey);
        }
    }
}
