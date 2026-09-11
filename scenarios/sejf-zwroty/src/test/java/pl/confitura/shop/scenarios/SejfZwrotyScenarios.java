package pl.confitura.shop.scenarios;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import pl.confitura.shop.payments.PaymentsModule;

/**
 * Sejf. Te scenariusze nigdy nie wracają do agenta, nawet jako nazwa. Porażka tutaj nie
 * uruchamia poprawki, tylko andon: każda informacja zwrotna z sejfu zamieniłaby go
 * w zbiór treningowy.
 */
class SejfZwrotyScenarios {

    @Test
    @DisplayName("Po pełnym zwrocie zwrot częściowy jest odrzucony")
    void noPartialRefundAfterFullRefund() {
        PaymentsModule payments = PaymentsModule.production();
        payments.captured("s-1", "o-1", "50.00");
        payments.controller().refund("s-1");

        assertThrows(IllegalArgumentException.class, () -> payments.controller().refundPartially("s-1", "10.00"));
    }

    @Test
    @DisplayName("Zwroty częściowe do pełnej kwoty zamykają płatność")
    void partialRefundsUpToFullAmountCloseThePayment() {
        PaymentsModule payments = PaymentsModule.production();
        payments.captured("s-2", "o-2", "30.00");
        payments.controller().refundPartially("s-2", "10.00");
        payments.controller().refundPartially("s-2", "10.00");

        assertEquals("REFUNDED", payments.controller().refundPartially("s-2", "10.00").status());
    }
}
