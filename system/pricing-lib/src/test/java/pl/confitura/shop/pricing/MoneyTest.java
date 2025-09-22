package pl.confitura.shop.pricing;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import org.junit.jupiter.api.Test;

class MoneyTest {

    @Test
    void addsAndSubtracts() {
        assertEquals(Money.of("12.50"), Money.of("10.00").plus(Money.of("2.50")));
        assertEquals(Money.of("7.50"), Money.of("10.00").minus(Money.of("2.50")));
    }

    @Test
    void multipliesByQuantity() {
        assertEquals(Money.of("30.00"), Money.of("10.00").times(3));
    }

    @Test
    void rejectsNegativeAmounts() {
        assertThrows(IllegalArgumentException.class, () -> Money.of("-1.00"));
        assertThrows(IllegalArgumentException.class, () -> Money.of("1.00").minus(Money.of("2.00")));
    }

    @Test
    void comparesAmounts() {
        assertTrue(Money.of("500.01").isGreaterThan(Money.of("500.00")));
    }
}
