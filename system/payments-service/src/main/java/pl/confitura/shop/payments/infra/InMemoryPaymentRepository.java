package pl.confitura.shop.payments.infra;

import java.util.Map;
import java.util.Optional;
import java.util.concurrent.ConcurrentHashMap;
import pl.confitura.shop.payments.domain.Payment;
import pl.confitura.shop.payments.domain.PaymentRepository;

public class InMemoryPaymentRepository implements PaymentRepository {

    private final Map<String, Payment> payments = new ConcurrentHashMap<>();

    @Override
    public void save(Payment payment) {
        payments.put(payment.id(), payment);
    }

    @Override
    public Optional<Payment> findById(String id) {
        return Optional.ofNullable(payments.get(id));
    }
}
