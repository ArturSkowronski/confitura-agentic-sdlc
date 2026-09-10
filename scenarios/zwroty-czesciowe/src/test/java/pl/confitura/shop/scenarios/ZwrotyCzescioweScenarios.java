package pl.confitura.shop.scenarios;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import pl.confitura.shop.payments.PaymentsModule;
import pl.confitura.shop.payments.api.PaymentController.RefundResponse;

class ZwrotyCzescioweScenarios {

    @Test
    @DisplayName("Zwrot części płatności zwraca dokładnie tę część")
    void partialRefund() {
        PaymentsModule payments = PaymentsModule.production();
        payments.captured("p-1", "o-1", "90.00");

        RefundResponse refund = payments.controller().refundPartially("p-1", "30.00");

        assertEquals("30.00 PLN", refund.refunded());
    }

    @Test
    @DisplayName("Dwa zwroty częściowe tej samej płatności oba dochodzą do klienta")
    void twoPartialRefunds() {
        PaymentsModule payments = PaymentsModule.production();
        payments.captured("p-2", "o-2", "90.00");

        payments.controller().refundPartially("p-2", "30.00");
        RefundResponse second = payments.controller().refundPartially("p-2", "30.00");

        assertEquals("60.00 PLN", second.refunded());
    }

    @Test
    @DisplayName("Zwrot większy niż pozostała kwota jest odrzucony")
    void refundAboveRemainingIsRejected() {
        PaymentsModule payments = PaymentsModule.production();
        payments.captured("p-3", "o-3", "90.00");
        payments.controller().refundPartially("p-3", "80.00");

        assertThrows(IllegalArgumentException.class, () -> payments.controller().refundPartially("p-3", "20.00"));
    }
}
