package pl.confitura.shop.orders.api;

import java.util.List;
import pl.confitura.shop.orders.domain.Order;
import pl.confitura.shop.orders.domain.OrderLine;
import pl.confitura.shop.orders.domain.OrderService;
import pl.confitura.shop.pricing.Money;

/** Cienka warstwa HTTP. Bez frameworka, żeby build trwał sekundy, a nie minuty. */
public class OrderController {

    public record LineRequest(String sku, int quantity, String unitPrice) {
    }

    public record PlaceOrderRequest(String customerId, List<LineRequest> lines) {
    }

    public record OrderResponse(String id, String subtotal, String discount, String total) {
    }

    private final OrderService orderService;

    public OrderController(OrderService orderService) {
        this.orderService = orderService;
    }

    public OrderResponse place(PlaceOrderRequest request) {
        List<OrderLine> lines = request.lines().stream()
                .map(l -> new OrderLine(l.sku(), l.quantity(), Money.of(l.unitPrice())))
                .toList();
        Order order = orderService.placeOrder(request.customerId(), lines);
        return new OrderResponse(order.id(),
                order.quote().subtotal().toString(),
                order.quote().discount().toString(),
                order.quote().total().toString());
    }
}
