package pl.confitura.shop.payments.infra;

import pl.confitura.shop.payments.domain.PaymentGateway;
import pl.confitura.shop.pricing.Money;

/** Zaślepka operatora kart. */
public class FakeCardGatewayClient implements PaymentGateway {

    @Override
    public void refund(String paymentId, Money amount) {
    }
}
