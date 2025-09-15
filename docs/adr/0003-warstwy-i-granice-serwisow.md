# ADR-0003: Warstwy i granice serwisów

- Status: przyjęty
- Data: 2025-09-15
- Moduły: orders-service, payments-service

## Decyzja

Każdy serwis ma trzy pakiety: `api` (HTTP), `domain` (logika), `infra` (baza, operatorzy).
Domena nie zależy od `api` ani od `infra`; infra implementuje porty z domeny. Serwisy nie
importują nawzajem swoich klas. Jedyna wspólna zależność to biblioteka pricing-lib.
