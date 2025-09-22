package pl.confitura.shop.pricing;

import java.util.List;
import java.util.Objects;

public final class PriceCalculator {

    private final DiscountPolicy discountPolicy;

    public PriceCalculator(DiscountPolicy discountPolicy) {
        this.discountPolicy = Objects.requireNonNull(discountPolicy, "discountPolicy");
    }

    public Quote quote(List<Money> lineTotals) {
        Money subtotal = lineTotals.stream().reduce(Money.ZERO, Money::plus);
        Money discount = discountPolicy.discountFor(subtotal);
        return new Quote(subtotal, discount, subtotal.minus(discount));
    }
}
