package pl.confitura.shop.payments.domain;

import java.util.Optional;

public interface PaymentRepository {

    void save(Payment payment);

    Optional<Payment> findById(String id);
}
