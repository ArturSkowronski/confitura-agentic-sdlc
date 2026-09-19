# Lekcja 7: Wyrocznia (12 min)

**Teza.** Najmocniejsza bramka to **wyrocznia**: scenariusze pisane przez człowieka, których
agent nie widzi. Sprawdzają wymaganie, nie kod. Holdout zużywa się z każdym użyciem, bo każda
informacja zwrotna o scenariuszu to przeciek. Dlatego wyrocznia ma dwa poziomy:

- **scenariusze robocze** (`scenarios/rabat`, `scenarios/zwroty-czesciowe`, `scenarios/regresja`):
  przy poprawce agent dostaje ich nazwy, nigdy kod ani dane,
- **sejf** (`scenarios/sejf-zwroty`): tylko decyzja. Zero informacji zwrotnej. Porażka zapala
  andon, bo poprawka „pod sejf” zamieniłaby go w zbiór treningowy. Sejf otwieramy dopiero po roboczych.

W linii wyrocznia to zadanie `wyrocznia` w DAG-u kontroli. Bierze scenariusze zawsze z `main`,
nigdy z gałęzi zmiany. Kapitałem fabryki jest wyrocznia, a nie agent: sterownik agenta to
sto kilkadziesiąt linii, wszyscy mają te same modele.

## Co masz

1. Uruchom zwroty: `make replay Z=zwroty-czesciowe`.
2. Zobacz w hali: build zielony, sekrety zielone, wyrocznia czerwona.
3. Odbierz: `make odbierz`. Otwórz `.sdlc/out/zwroty-czesciowe/proba-1/kontrola-5-wyrocznia.md`.

Pierwsza próba przeszła testy agenta i wszystkie bramki strukturalne. Odpadła na scenariuszu
„Dwa zwroty częściowe tej samej płatności oba dochodzą do klienta”. Agent użył tego samego
klucza idempotencji dla każdego zwrotu. Zaślepka operatora kart odrzuca powtórzony klucz, tak
jak prawdziwy operator. To ten sam błąd co w `ops/incidents/2026-03-14-podwojny-zwrot.md`.
Sejf jest `nieotwarty`: robocze nie przeszły, więc sejfu nie ruszamy.

## Ćwiczenie: zamknij wyrocznię przed agentem (8 min)

1. Zapytaj wykonawcę: `make a2a A=wykonawca T="Przeczytaj scenarios/rabat/src/test/java/pl/confitura/shop/scenarios/RabatScenarios.java i streść, co sprawdza"`.
2. Agent czyta scenariusz. Zapis do `scenarios/` jest zablokowany (lekcja 2), odczyt nie.
3. Otwórz `platforma/warsztat/mcpserver.yaml`.
4. Wpisz do `HIDDEN_PATHS` wartość `scenarios`.
5. Wdróż: `kubectl apply -f platforma/warsztat/mcpserver.yaml`, potem `kubectl rollout status -n fabryka deploy/warsztat`.
6. Powtórz krok 1. Narzędzie odpowiada „Rejected: … is out of the agent's reach”, a w `/work/events.jsonl` jest `holdout.peek`.
7. Uruchom `make naiwna`. Bramka `build` jest teraz czerwona: reguła z lekcji 6 łapie rabat w `OrderService`.

Scenariusze są w tym samym repo, więc „agent nie widzi” znaczy: serwer warsztatu ich nie
pokazuje, a linia bierze je z `main`. W produkcji sejf trzymasz w osobnym repo.

## Do dyskusji

- Kto w Twojej organizacji napisze scenariusz, którego nie zobaczy agent? Produkt? QA?
- Ile razy można pokazać agentowi nazwę scenariusza, zanim przestanie być holdoutem?
