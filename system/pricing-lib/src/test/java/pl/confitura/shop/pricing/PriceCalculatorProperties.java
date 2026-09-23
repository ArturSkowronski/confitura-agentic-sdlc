package pl.confitura.shop.pricing;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.math.BigDecimal;
import java.util.List;
import net.jqwik.api.Arbitraries;
import net.jqwik.api.Arbitrary;
import net.jqwik.api.ForAll;
import net.jqwik.api.Property;
import net.jqwik.api.Provide;

/**
 * Własności, które musi spełniać każda polityka rabatowa. Setki losowych koszyków
 * zamiast trzech ręcznie wybranych przykładów.
 */
class PriceCalculatorProperties {

    @Property
    void totalIsNeverNegativeAndNeverAboveSubtotal(@ForAll("baskets") List<Money> lines,
                                                   @ForAll("policies") DiscountPolicy policy) {
        Quote quote = new PriceCalculator(policy).quote(lines);

        assertTrue(quote.total().compareTo(Money.ZERO) >= 0);
        assertTrue(quote.total().compareTo(quote.subtotal()) <= 0);
        assertEquals(quote.subtotal(), quote.total().plus(quote.discount()));
    }

    @Provide
    Arbitrary<List<Money>> baskets() {
        return Arbitraries.bigDecimals()
                .between(BigDecimal.ZERO, new BigDecimal("10000"))
                .ofScale(2)
                .map(Money::new)
                .list().ofMaxSize(20);
    }

    @Provide
    Arbitrary<DiscountPolicy> policies() {
        // Każda nowa polityka rabatowa powinna trafić na tę listę.
        return Arbitraries.of(new NoDiscount(), new ThresholdDiscount(Money.of("500.00"), 10));
    }
}
