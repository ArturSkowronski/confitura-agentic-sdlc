package pl.confitura.shop.orders.domain;

import java.util.Optional;

/** Port. Implementacja siedzi w warstwie infra, domena o niej nie wie (ADR-0003). */
public interface OrderRepository {

    void save(Order order);

    Optional<Order> findById(String id);
}
