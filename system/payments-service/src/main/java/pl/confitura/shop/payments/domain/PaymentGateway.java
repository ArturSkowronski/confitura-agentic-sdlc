package pl.confitura.shop.payments.domain;

import pl.confitura.shop.pricing.Money;

/** Port do operatora kart. Każde wywołanie musi mieć klucz idempotencji (INC-2026-03-14). */
public interface PaymentGateway {

    void refund(String paymentId, Money amount, String idempotencyKey);
}
