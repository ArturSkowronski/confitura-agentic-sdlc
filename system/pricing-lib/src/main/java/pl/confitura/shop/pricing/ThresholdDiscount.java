package pl.confitura.shop.pricing;

import java.util.Objects;

/** Rabat procentowy od całej kwoty, gdy suma przekracza próg (np. 10% powyżej 500 zł). */
public final class ThresholdDiscount implements DiscountPolicy {

    private final Money threshold;
    private final int percent;

    public ThresholdDiscount(Money threshold, int percent) {
        this.threshold = Objects.requireNonNull(threshold, "threshold");
        if (percent < 0 || percent > 100) {
            throw new IllegalArgumentException("Procent spoza zakresu 0-100: " + percent);
        }
        this.percent = percent;
    }

    @Override
    public Money discountFor(Money subtotal) {
        return subtotal.isGreaterThan(threshold) ? subtotal.percent(percent) : Money.ZERO;
    }
}
