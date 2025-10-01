package pl.confitura.shop.orders.domain;

import pl.confitura.shop.pricing.Money;

public record OrderLine(String sku, int quantity, Money unitPrice) {

    public OrderLine {
        if (quantity <= 0) {
            throw new IllegalArgumentException("Ilość musi być dodatnia: " + quantity);
        }
    }

    public Money lineTotal() {
        return unitPrice.times(quantity);
    }
}
