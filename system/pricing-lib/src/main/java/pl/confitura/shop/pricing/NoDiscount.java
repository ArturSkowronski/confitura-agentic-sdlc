package pl.confitura.shop.pricing;

public final class NoDiscount implements DiscountPolicy {

    @Override
    public Money discountFor(Money subtotal) {
        return Money.ZERO;
    }
}
