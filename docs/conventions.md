# Konwencje kodu

Ten plik czytają ludzie i agenci. Reguły z review, które się powtarzają, lądują tutaj
(komenda `/rule` w komentarzu do PR).

- Kwoty tylko przez `Money`. Rabaty tylko jako `DiscountPolicy` w pricing-lib.
- Nowa polityka rabatowa trafia na listę `policies()` w `PriceCalculatorProperties`.
- Czas przez `java.time`, nigdy `java.util.Date`.
- Bez `System.out` i `printStackTrace`.
- Test do każdej zmiany zachowania. Test sprawdza wymaganie, a nie kopiuje implementację.
- Build: `mvn -B -q verify` w katalogu `system/`.
