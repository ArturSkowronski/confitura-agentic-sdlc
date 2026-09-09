package pl.confitura.shop.scenarios;

import static org.junit.jupiter.api.Assertions.assertEquals;

import java.util.List;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import pl.confitura.shop.orders.OrdersModule;
import pl.confitura.shop.orders.api.OrderController.LineRequest;
import pl.confitura.shop.orders.api.OrderController.OrderResponse;
import pl.confitura.shop.orders.api.OrderController.PlaceOrderRequest;
import pl.confitura.shop.payments.PaymentsModule;
import pl.confitura.shop.payments.api.PaymentController.RefundResponse;

class RegresjaScenarios {

    @Test
    @DisplayName("Małe zamówienie kosztuje dokładnie sumę pozycji")
    void smallOrderCostsSumOfLines() {
        OrderResponse order = OrdersModule.production().controller().place(new PlaceOrderRequest("klient-1", List.of(
                new LineRequest("KONFITURA-WISNIA", 2, "24.99"),
                new LineRequest("KONFITURA-MALINA", 1, "19.99"))));

        assertEquals("69.97 PLN", order.total());
        assertEquals("0.00 PLN", order.discount());
    }

    @Test
    @DisplayName("Pełny zwrot wykonany dwa razy wypłaca pieniądze raz")
    void fullRefundIsIdempotent() {
        PaymentsModule payments = PaymentsModule.production();
        payments.captured("p-1", "o-1", "99.00");

        payments.controller().refund("p-1");
        RefundResponse again = payments.controller().refund("p-1");

        assertEquals("REFUNDED", again.status());
        assertEquals("99.00 PLN", again.refunded());
    }
}
