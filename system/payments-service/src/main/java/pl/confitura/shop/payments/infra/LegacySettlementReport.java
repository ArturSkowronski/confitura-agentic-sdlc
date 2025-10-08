package pl.confitura.shop.payments.infra;

import java.text.SimpleDateFormat;
import java.util.Date;

/**
 * Stary raport rozliczeń. Używa java.util.Date, czego już nie wolno w nowym kodzie.
 * Reguła ArchUnit jest „zamrożona”: to naruszenie jest znane, nowe blokujemy.
 */
public class LegacySettlementReport {

    public String header(Date day) {
        return "Rozliczenie z dnia " + new SimpleDateFormat("yyyy-MM-dd").format(day);
    }
}
