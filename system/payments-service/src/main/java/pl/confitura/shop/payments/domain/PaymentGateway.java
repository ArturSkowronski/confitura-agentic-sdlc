package pl.confitura.shop.payments.domain;

import pl.confitura.shop.pricing.Money;

/** Port do operatora kart. */
public interface PaymentGateway {

    void refund(String paymentId, Money amount);
}
