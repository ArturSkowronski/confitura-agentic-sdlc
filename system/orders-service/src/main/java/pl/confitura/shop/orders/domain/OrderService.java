package pl.confitura.shop.orders.domain;

import java.util.List;
import java.util.UUID;
import pl.confitura.shop.pricing.PriceCalculator;
import pl.confitura.shop.pricing.Quote;

public class OrderService {

    private final OrderRepository repository;
    private final PriceCalculator priceCalculator;

    public OrderService(OrderRepository repository, PriceCalculator priceCalculator) {
        this.repository = repository;
        this.priceCalculator = priceCalculator;
    }

    public Order placeOrder(String customerId, List<OrderLine> lines) {
        if (lines.isEmpty()) {
            throw new IllegalArgumentException("Zamówienie musi mieć co najmniej jedną pozycję");
        }
        Quote quote = priceCalculator.quote(lines.stream().map(OrderLine::lineTotal).toList());
        Order order = new Order(UUID.randomUUID().toString(), customerId, lines, quote, OrderStatus.PLACED);
        repository.save(order);
        return order;
    }
}
