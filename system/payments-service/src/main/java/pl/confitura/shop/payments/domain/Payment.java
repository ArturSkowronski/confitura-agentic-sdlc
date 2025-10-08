package pl.confitura.shop.payments.domain;

import pl.confitura.shop.pricing.Money;

public record Payment(String id, String orderId, Money amount, Money refunded, PaymentStatus status) {
}
