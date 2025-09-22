package pl.confitura.shop.pricing;

public record Quote(Money subtotal, Money discount, Money total) {
}
