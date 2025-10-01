package pl.confitura.shop.orders.domain;

import java.util.List;
import pl.confitura.shop.pricing.Quote;

public record Order(String id, String customerId, List<OrderLine> lines, Quote quote, OrderStatus status) {

    public Order {
        lines = List.copyOf(lines);
    }
}
