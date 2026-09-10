package pl.confitura.shop.scenarios;

import static org.junit.jupiter.api.Assertions.assertEquals;

import java.util.List;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import pl.confitura.shop.orders.OrdersModule;
import pl.confitura.shop.orders.api.OrderController.LineRequest;
import pl.confitura.shop.orders.api.OrderController.OrderResponse;
import pl.confitura.shop.orders.api.OrderController.PlaceOrderRequest;

class RabatScenarios {

    private OrderResponse order(LineRequest... lines) {
        return OrdersModule.production().controller().place(new PlaceOrderRequest("klient-1", List.of(lines)));
    }

    @Test
    @DisplayName("Zamówienie za równe 500 zł nie ma rabatu")
    void noDiscountAtThreshold() {
        OrderResponse order = order(new LineRequest("ZESTAW", 5, "100.00"));

        assertEquals("0.00 PLN", order.discount());
        assertEquals("500.00 PLN", order.total());
    }

    @Test
    @DisplayName("Zamówienie za 500,01 zł dostaje 50 zł rabatu")
    void discountJustAboveThreshold() {
        OrderResponse order = order(new LineRequest("ZESTAW", 1, "500.01"));

        assertEquals("50.00 PLN", order.discount());
        assertEquals("450.01 PLN", order.total());
    }

    @Test
    @DisplayName("Rabat liczy się od całego koszyka, a nie od pojedynczej pozycji")
    void discountFromWholeBasket() {
        OrderResponse order = order(
                new LineRequest("KONFITURA-WISNIA", 10, "24.99"),
                new LineRequest("KONFITURA-MALINA", 15, "19.99"));

        assertEquals("549.75 PLN", order.subtotal());
        assertEquals("54.98 PLN", order.discount());
        assertEquals("494.77 PLN", order.total());
    }
}
