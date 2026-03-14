# INC-2026-03-14: Podwójny zwrot przy ponowieniu żądania

- Ważność: SEV-2
- Moduły: payments-service
- Czas trwania: 3 h 40 min
- Straty: 212 zwrotów wypłaconych dwa razy, ok. 18 400 PLN

## Co się stało

Nowa obsługa zwrotów częściowych wysyłała do operatora kart żądanie bez klucza
idempotencji. Gdy operator odpowiadał z opóźnieniem, klient ponawiał żądanie i operator
wypłacał zwrot drugi raz. Zmiana miała 40 linii, wyglądała poprawnie i przeszła review.

## Co zmieniliśmy

1. Każde wywołanie `PaymentGateway` ma klucz idempotencji.
2. Zwroty częściowe są wyłączone do czasu testu na ponowienie żądania.
3. payments-service stał się ścieżką krytyczną (ADR-0002).
