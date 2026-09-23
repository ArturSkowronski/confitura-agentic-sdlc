package pl.confitura.shop.pricing;

import static org.junit.jupiter.api.Assertions.assertEquals;

import org.junit.jupiter.api.Test;

class ThresholdDiscountTest {

    private final ThresholdDiscount tenPercentAbove500 = new ThresholdDiscount(Money.of("500.00"), 10);

    @Test
    void noDiscountAtOrBelowThreshold() {
        assertEquals(Money.ZERO, tenPercentAbove500.discountFor(Money.of("500.00")));
        assertEquals(Money.ZERO, tenPercentAbove500.discountFor(Money.of("120.00")));
    }

    @Test
    void tenPercentOfWholeAmountAboveThreshold() {
        assertEquals(Money.of("60.00"), tenPercentAbove500.discountFor(Money.of("600.00")));
        assertEquals(Money.of("50.00"), tenPercentAbove500.discountFor(Money.of("500.01")));
    }
}
