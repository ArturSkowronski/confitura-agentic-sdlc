# Lekcja 3: Kontekst L1–L5 (12 min)

**Teza.** Agent, który przy każdym zleceniu sam „odkrywa” repo, jest drogi, wolny i za każdym
razem trafia gdzie indziej. Wiedzę o systemie kompilujemy raz, deterministycznie, na pięciu
poziomach. Routing zlecenia do modułu poprawiasz danymi, nie promptem. Własność pojęcia
wygrywa z częstością słów.

| Poziom | Skąd | W tym repo |
|---|---|---|
| L1 system | katalog modułów, zależności | `system/*/module.json`, `pom.xml` |
| L2 kod | konwencje, reguły architektury | `docs/conventions.md`, ArchUnit |
| L3 ludzie | faktyczni właściciele, nie tylko nominalni | `git log` kontra `CODEOWNERS` |
| L4 decyzje | ADR-y | `docs/adr/` |
| L5 operacje | incydenty | `ops/incidents/` |

Wszystko liczy `sdlc/context.py`. Wynik to `AGENTS.md` (dla agenta) i `.sdlc/route.json`
(dla linii). Ten sam commit daje zawsze ten sam wynik: bez modelu, bez losowości.

## Co masz

1. Przebuduj kontekst: `make agents-md`. Otwórz `AGENTS.md`.
2. Zobacz właścicieli faktycznych w sekcji L3. Nominalnie payments to zespół, faktycznie dwie osoby.
3. Sprawdź routing: `make route T="Rabat 10% dla zamówień powyżej 500 zł"`.

Routing wskazuje `orders-service`, bo „zamówienie” pada częściej niż „rabat”. Gdybyś wysłał to
zlecenie na linię, wykonawca policzyłby rabat w `OrderService`, testy byłyby zielone, a ADR-0001
mówi, że rabaty liczy tylko `pricing-lib`. Zielony build w złym module.

## Ćwiczenie: własność pojęcia (8 min)

1. Otwórz `docs/adr/0001-arytmetyka-pieniedzy-tylko-w-pricing.md`.
2. Otwórz `system/pricing-lib/module.json`.
3. Wpisz do pola `owns` pojęcia, których właścicielem jest ten moduł. Podpowiedź: rabat, cena, kwota.
4. Sprawdź: `make route T="Rabat 10% dla zamówień powyżej 500 zł"`. Ma wskazać `pricing-lib`.
5. Przebuduj `AGENTS.md`: `make agents-md`.
6. Zrób commit.

Pole `owns` bije `keywords`: jedno trafienie we własności ważniejsze niż dziesięć w słowach.
Tak samo działa `critical: true` w payments: routing raportuje ścieżkę krytyczną w zasięgu zmiany.

## Do dyskusji

- Dlaczego routing danymi ma znaczenie przy dziesięciu agentach, a nie przy jednym?
- Po Twoim commicie w tabeli L3 dla pricing-lib pojawisz się także Ty. Kto zna payments?
- Blast radius: zlecenie z pojęciami z dwóch modułów to zwykle dwa zlecenia (lekcja 4).
