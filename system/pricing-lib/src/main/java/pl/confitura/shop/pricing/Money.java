package pl.confitura.shop.pricing;

import java.math.BigDecimal;
import java.math.RoundingMode;
import java.util.Objects;

/**
 * Kwota w złotówkach. Cała arytmetyka pieniędzy w systemie przechodzi przez tę klasę
 * (ADR-0001), żeby zaokrąglenia działały tak samo w zamówieniach i w płatnościach.
 */
public record Money(BigDecimal amount) implements Comparable<Money> {

    public static final Money ZERO = Money.of("0.00");

    public Money {
        Objects.requireNonNull(amount, "amount");
        if (amount.signum() < 0) {
            throw new IllegalArgumentException("Kwota nie może być ujemna: " + amount);
        }
        amount = amount.setScale(2, RoundingMode.HALF_EVEN);
    }

    public static Money of(String amount) {
        return new Money(new BigDecimal(amount));
    }

    public Money plus(Money other) {
        return new Money(amount.add(other.amount));
    }

    public Money minus(Money other) {
        return new Money(amount.subtract(other.amount));
    }

    public Money times(int quantity) {
        if (quantity < 0) {
            throw new IllegalArgumentException("Ilość nie może być ujemna: " + quantity);
        }
        return new Money(amount.multiply(BigDecimal.valueOf(quantity)));
    }

    /** Procent z kwoty, np. {@code percent(10)} to 10% tej kwoty. */
    public Money percent(int percent) {
        if (percent < 0 || percent > 100) {
            throw new IllegalArgumentException("Procent spoza zakresu 0-100: " + percent);
        }
        return new Money(amount.multiply(BigDecimal.valueOf(percent)).divide(BigDecimal.valueOf(100), 2, RoundingMode.HALF_EVEN));
    }

    public boolean isGreaterThan(Money other) {
        return compareTo(other) > 0;
    }

    public Money min(Money other) {
        return compareTo(other) <= 0 ? this : other;
    }

    @Override
    public int compareTo(Money other) {
        return amount.compareTo(other.amount);
    }

    @Override
    public String toString() {
        return amount.toPlainString() + " PLN";
    }
}
