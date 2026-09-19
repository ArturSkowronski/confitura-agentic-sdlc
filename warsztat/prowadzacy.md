# Notatki prowadzącego

Metryka warsztatu: **odsłony na minutę**. Odsłona to moment, w którym coś zielonego okazuje
się złe albo fabryka robi coś, czego sala się nie spodziewa. Plan: 11 odsłon w 120 minutach,
średnio jedna co 11 minut, a w środkowej części (stacje 2-4) jedna co 7-8 minut.

## Odsłony

| # | Minuta | Slajd | Odsłona | Co musi być gotowe |
|---|---|---|---|---|
| 1 | 0:04 | 3 | PR zielony, czytelny, w złym module, przyjęty lights-out | repo `sdlc-demo-start` z gotowym przebiegiem rabatu |
| 2 | 0:15 | 6 | Fabryka odsyła zlecenie z pytaniami | zlecenie „Anulowanie” u uczestników |
| 3 | 0:20 | 7 | „Zamówienie” ×9 wygrywa z „rabatem”: routing wyjaśniony liczbami | komentarz Routing |
| 4 | 0:33 | 9 | Jedna linia YAML i przebieg staje z przyciskiem Approve | stacja 2 |
| 5 | 0:44 | 11 | Czwarte zlecenie czeka w kolejce i rusza samo po Approve | 3 zlecenia w toku w repo demo |
| 6 | 0:57 | 13 | jqwik mówi do agenta | terminal na projektorze, `mvn -B verify` |
| 7 | 1:00 | 14 | Incydent z marca łapie scenariusz, zanim ktoś czyta kod | przebieg zwrotów, próba 1 |
| 8 | 1:13 | 17 | Fabryka sama odsyła do poprawki, ryzyko rośnie z próbą | dwa przebiegi zwrotów obok siebie |
| 9 | 1:27 | 19 | Jedno słowo w księdze i łańcuch pokazuje linię | pobrana księga z przebiegu |
| 10 | 1:33 | 20 | `/rule` → reguła od agenta → `critical`, czeka na człowieka | dowolny PR od agenta |
| 11 | 1:45 | 23 | Hala: produkcja kontra przyjęcie dla całej sali | `tower/index.html` + PAT |

Między odsłonami są slajdy z tezą. Każda teza ma dowód z repo, nie z internetu.

## Przed warsztatem

| Kiedy | Co |
|---|---|
| do 18.09 | Upublicznij repo z gałęziami `stacja-1`…`stacja-5` i `final`. Poprawki wspólne rób na `main`, potem `scripts/restack.sh --push`. |
| do 18.09 | Postaw dwa repo demo: `REPO_NAME=sdlc-demo-start make bootstrap` i `REPO_NAME=sdlc-demo-final FACTORY_MODE=lights-out make bootstrap`, w drugim `make catch-up N=final`. |
| do 18.09 | Przejdź trzy zlecenia (rabat, zwroty, anulowanie) na prawdziwym modelu w obu repo. Zmierz czasy przebiegów i koszt z kart zleceń. |
| do 19.09 | Wyślij mail z setupem (`warsztat/mail-setup.md`). Uzupełnij dzień, godzinę i salę. |
| 21-23.09 | Odpowiedz osobom z czerwonym `make doctor`. |
| 24.09 | Wygeneruj 12 kluczy OpenRouter z limitem 8 USD każdy. Wydrukuj na kartkach. |
| 24.09 | Nagraj ekran z odsłonami 1, 7 i 8 (plan B, gdy padnie sieć). |
| 24.09 | Utwórz fine-grained PAT tylko do odczytu publicznych repo dla hali. |
| po warsztacie | Unieważnij klucze OpenRouter. |

Koszt: przebieg agenta na Sonnet 5 to rząd 0,5-1 USD, poprawka drugie tyle. 10 osób × 5
przebiegów mieści się w 60 USD. Soczewki review i pytania z przyjęcia na DeepSeek V4 Flash
kosztują grosze.

## Przebieg (120 min)

| Czas | Blok | Slajdy |
|---|---|---|
| 0:00 | Otwarcie, teza, poziomy autonomii | 1-4 |
| 0:09 | Plan, klucze (`make key`) | 5 |
| 0:15 | Stacja 1: przyjęcie i kontekst | 6-8 |
| 0:33 | Stacja 2: linia, światło, uprawnienia, WIP | 9-11 |
| 0:51 | Stacja 3: kontrola jakości, jqwik, wyrocznia, macierz | 12-15 |
| 1:09 | Stacja 4: wyrocznia się zużywa, poprawki, ryzyko | 16-18 |
| 1:27 | Stacja 5: księga, `/rule`, kapitał, metryki | 19-22 |
| 1:45 | Klamra: hala, mapa, zamknięcie | 23-25 |

Jeśli jesteś spóźniony, stacja 5 idzie jako demo (slajdy 19-20), bez ćwiczeń.

## Plan B

| Problem | Co robisz |
|---|---|
| Model nie odpowiada albo skończył się limit | `gh variable set AGENT -b replay`. Wszystkie stacje działają na nagraniach, łącznie z pętlą poprawek. |
| Wi-Fi padło, GitHub niedostępny | `make replay T="..."` i `make oracle T="..."` lokalnie. Nagrania odsłon. |
| Uczestnik utknął | `make catch-up N=<stacja>` |
| Przebieg trwa za długo | Pokaż gotowy przebieg z repo demo, bieżący zostaw w tle. |
| Ktoś nie ma setupu | Paruje się z sąsiadem. Grupa 10 osób, to działa. |

## Znane zachowania

- jqwik 1.10.1 wypisuje w logu testów tekst do agentów AI. Zostawiamy celowo (odsłona 6).
  Wersja 1.9.3 jest czysta, gdyby agent zaczął na to reagować.
- PR otwarty przez `GITHUB_TOKEN` nie uruchamia innych workflowów. Dlatego kontrola jakości
  i review są wołane z `agent.yml` jako reusable workflows. Wyjątek: `workflow_dispatch`
  z `GITHUB_TOKEN` uruchamia przebieg, więc na tym stoi pętla poprawek i kolejka.
- Na gałęzi `stacja-2` job `approve` nie ma `environment:`, więc nie czeka. Zapisuje wtedy
  w księdze `human.approval_missing`, a zmiana nie dostaje `accepted`.
- Scenariusze są w publicznym repo, więc „agent nie widzi” znaczy: nie dostaje ich w checkoucie,
  a sięgnięcie po nie zapisujemy jako `holdout.peek`. W produkcji sejf trzymasz w osobnym repo.
- `FACTORY_MODE=dry-run` (domyślnie u uczestników) przyjmuje zmianę etykietą `accepted`, bez
  merge'a. Dzięki temu `main` uczestnika zostaje stabilne między stacjami.
