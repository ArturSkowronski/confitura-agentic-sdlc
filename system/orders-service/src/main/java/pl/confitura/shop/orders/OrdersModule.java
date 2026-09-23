package pl.confitura.shop.orders;

import pl.confitura.shop.orders.api.OrderController;
import pl.confitura.shop.orders.domain.OrderService;
import pl.confitura.shop.orders.infra.InMemoryOrderRepository;
import pl.confitura.shop.pricing.DiscountPolicy;
import pl.confitura.shop.pricing.Money;
import pl.confitura.shop.pricing.NoDiscount;
import pl.confitura.shop.pricing.ThresholdDiscount;
import pl.confitura.shop.pricing.PriceCalculator;

/**
 * Punkt składania serwisu zamówień: tu zapada decyzja, która polityka rabatowa działa
 * na produkcji. Scenariusze akceptacyjne wchodzą do systemu tylko przez ten moduł.
 */
public final class OrdersModule {

    private final OrderController controller;

    private OrdersModule(DiscountPolicy discountPolicy) {
        OrderService service = new OrderService(new InMemoryOrderRepository(), new PriceCalculator(discountPolicy));
        this.controller = new OrderController(service);
    }

    /** Konfiguracja produkcyjna: rabat 10% od koszyka powyżej 500 zł (polityka z pricing-lib). */
    public static OrdersModule production() {
        return new OrdersModule(new ThresholdDiscount(Money.of("500.00"), 10));
    }

    public OrderController controller() {
        return controller;
    }
}
