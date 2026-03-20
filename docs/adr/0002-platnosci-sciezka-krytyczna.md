# ADR-0002: payments-service to ścieżka krytyczna

- Status: przyjęty
- Data: 2026-03-20
- Moduły: payments-service

## Kontekst

Po incydencie INC-2026-03-14 (podwójny zwrot) okazało się, że zmiana w zwrotach przeszła
review w 11 minut, bo diff był krótki i czytelny.

## Decyzja

Każda zmiana w `system/payments-service/` wymaga akceptacji właściciela modułu, niezależnie
od tego, kto ją napisał: człowiek czy agent. Każde wywołanie operatora kart ma klucz
idempotencji. Zwroty częściowe są wyłączone, dopóki nie będą miały testu na ponowienie.

## Konsekwencje

Zmiany w płatnościach czekają na człowieka. Reszta systemu nie czeka.
