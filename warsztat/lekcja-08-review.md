# Lekcja 8: Ryzyko, review i poprawki (12 min)

**Teza 1. Ryzyko liczy kod, nie model.** `sdlc/risk.py` sumuje sygnały deterministyczne: ścieżka
krytyczna, rozmiar diffu, brak testów, historia modułu, numer próby. Od poziomu zależy, czy w ogóle
pytamy recenzenta (`llm_from_level` w `sdlc/policy.json`) i czy zmiana czeka na człowieka.

**Teza 2. Każda poprawka przesuwa agenta od wymagania w stronę bramki.** Numer próby podnosi
ryzyko, detektor osłabiania testów blokuje zmianę, a po `max_attempts` linia staje (andon).
Poprawka to ta sama linia z `proba+1`: rekurencja szablonu w Argo, cała historia w jednym grafie.

**Teza 3. Precyzja ponad recall.** Review ma trzy warstwy: regexy zawsze (`DET-*`), ryzyko
decyduje, soczewki LLM tylko od progu. Agent `recenzent` w kagent dostaje reguły z kryteriami
zaliczenia i niezaliczenia, odpowiada JSON-em, a fabryka tnie: próg pewności, limit znalezisk,
deduplikacja. Znalezisko blokujące nie odsyła do poprawki, tylko eskaluje do człowieka:
model radzi, człowiek decyduje. Poprawkę wymuszają wyłącznie bramki deterministyczne.

```
kontrola ‖ review ─▶ decyzja ─▶ lights-out | człowiek | poprawka (linia, próba+1) | andon
```

## Co masz

1. Uruchom zwroty: `make replay Z=zwroty-czesciowe`. Obserwuj w hali: próba 1 pada na wyroczni,
   fabryka sama uruchamia próbę 2 (węzeł `poprawka` to znowu cała `linia`).
2. Odbierz: `make odbierz`. Otwórz `.sdlc/out/zwroty-czesciowe/proba-1/feedback.md`: to wszystko,
   co dostał agent. Nazwy scenariuszy, nie kod.
3. Otwórz `proba-2/review-1-ryzyko.md`. Ryzyko `critical`, bo payments to ścieżka krytyczna
   i bo to poprawka. Decyzja: człowiek. Przebieg nie czekał (lekcja 9).
4. Otwórz `proba-2/review-2-review.md`. Recenzent z prawdziwym modelem znajduje tu coś, czego nie
   widzi wyrocznia: losowy UUID jako klucz idempotencji chroni przed podwójnym zwrotem, ale nie
   przed ponowieniem tego samego żądania. To jest dokładnie INC-2026-03-14 od drugiej strony.

## Ćwiczenie: reguła review z kryteriami (8 min)

1. Otwórz `proba-1/review-2-review.md`. Regex `DET-004` nie złapał błędu z próby 1: klucz
   idempotencji jest, tylko nie jest unikalny.
2. Otwórz `sdlc/review-rules.json`.
3. Dopisz regułę `kind: llm` w soczewce `correctness`. Podaj `rule`, `pass`, `fail`
   i `example_fail`. Podpowiedź: klucz idempotencji ma być unikalny dla każdego zwrotu,
   nie dla płatności.
4. Zrób commit i uruchom zwroty jeszcze raz: `make zlecenie Z=zwroty-czesciowe` (z modelem).

Teraz próba 1 odpada na dwóch niezależnych warstwach: wyroczni i review. Znalezisko ma poziom
pewności; poniżej `certain_confidence` jest oznaczone „do weryfikacji”.

## Do dyskusji

- Zmień `llm_from_level` na `high`. Co zyskujesz, co tracisz?
- Sejf nie przeszedł: andon, bez poprawki. Dlaczego fabryka woli zatrzymać linię niż spróbować
  jeszcze raz?
