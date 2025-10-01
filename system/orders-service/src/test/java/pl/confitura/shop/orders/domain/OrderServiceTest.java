package pl.confitura.shop.orders.domain;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.util.List;
import org.junit.jupiter.api.Test;
import pl.confitura.shop.orders.infra.InMemoryOrderRepository;
import pl.confitura.shop.pricing.Money;
import pl.confitura.shop.pricing.NoDiscount;
import pl.confitura.shop.pricing.PriceCalculator;

class OrderServiceTest {

    private final InMemoryOrderRepository repository = new InMemoryOrderRepository();
    private final OrderService service = new OrderService(repository, new PriceCalculator(new NoDiscount()));

    @Test
    void placesOrderAndComputesTotal() {
        Order order = service.placeOrder("c-1", List.of(
                new OrderLine("KONFITURA-WISNIA", 2, Money.of("24.99")),
                new OrderLine("KONFITURA-MALINA", 1, Money.of("19.99"))));

        assertEquals(Money.of("69.97"), order.quote().total());
        assertEquals(OrderStatus.PLACED, order.status());
        assertTrue(repository.findById(order.id()).isPresent());
    }

    @Test
    void rejectsEmptyOrder() {
        assertThrows(IllegalArgumentException.class, () -> service.placeOrder("c-1", List.of()));
    }
}
