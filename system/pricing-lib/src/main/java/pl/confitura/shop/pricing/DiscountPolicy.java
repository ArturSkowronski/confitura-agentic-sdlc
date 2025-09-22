package pl.confitura.shop.pricing;

/** Reguła rabatowa. Nowe rabaty dodajemy jako kolejne implementacje w tej bibliotece. */
public interface DiscountPolicy {

    /** Kwota rabatu dla danej sumy częściowej. Nigdy większa niż sama suma. */
    Money discountFor(Money subtotal);
}
