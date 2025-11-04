# ADR-0001: Arytmetyka pieniędzy tylko w pricing-lib

- Status: przyjęty
- Data: 2025-11-04
- Moduły: pricing-lib, orders-service, payments-service

## Kontekst

Zamówienia i płatności liczyły kwoty każdy po swojemu. Zamówienie zaokrąglało HALF_UP,
płatność HALF_EVEN, więc przy rabatach procentowych kwota do zapłaty i kwota zwrotu
rozjeżdżały się o grosz. Księgowość znajdowała to raz w miesiącu, ręcznie.

## Decyzja

Każda operacja na kwotach (dodawanie, odejmowanie, procenty, zaokrąglenia) idzie przez
`Money` z pricing-lib. Rabat to implementacja `DiscountPolicy` w pricing-lib, a nie `if`
w serwisie. Serwisy nie wywołują `add`, `subtract`, `multiply`, `divide` ani `setScale`
na `BigDecimal`. Na razie pilnuje tego review, automatycznej reguły jeszcze nie ma.

## Konsekwencje

Nowy rabat oznacza zmianę w pricing-lib, czyli w kodzie innego zespołu. To wolniejsze,
ale rozbieżności groszowe zniknęły.
