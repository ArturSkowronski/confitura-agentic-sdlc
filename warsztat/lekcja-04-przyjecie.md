# Lekcja 4: Przyjęcie zlecenia (12 min)

**Teza.** Fabryka jest dokładnie tak dobra jak zlecenia, które przyjmuje. Wąskie gardło
przesuwa się z pisania kodu na pisanie specyfikacji. Dlatego pierwsza bramka stoi przed
agentem: zlecenie bez kryteriów akceptacji wraca do autora z pytaniami. Sprawdzenie jest
deterministyczne (`sdlc/intake.py`). Agent `przyjecie` tylko formułuje pytania. Nie decyduje.

Zlecenia to pliki w `zlecenia/`: pierwsza linia to tytuł, sekcja `Kryteria:` to lista punktów.
Bez GitHub Issues, bez Jiry. Plik w repo przechodzi review jak kod.

| Zlecenie | Plik | Co pokazuje |
|---|---|---|
| Rabat 10% powyżej 500 zł | `zlecenia/rabat.md` | zły moduł bez `owns`, pełna linia z wyrocznią |
| Zwroty częściowe | `zlecenia/zwroty-czesciowe.md` | incydent z marca wraca, pętla poprawek, ścieżka krytyczna |
| Anulowanie zamówienia | `zlecenia/anulowanie.md` | brak kryteriów, brak scenariuszy |
| Twoje zlecenie | `zlecenia/wolne.md` | co zrobi fabryka z Twoim pomysłem |

## Co masz

1. Przyjmij rabat lokalnie: `make przyjecie Z=rabat`. Wynik: przyjęte na linię.
2. Przyjmij anulowanie: `make przyjecie Z=anulowanie`. Wynik: odesłane, z pytaniami od agenta.
3. Zobacz, co sprawdza przyjęcie: `sdlc/intake.py`, funkcja `assess`. Same regexy i routing.

Przyjęcie odsyła też zlecenia za duże: pojęcia z dwóch modułów-właścicieli to zwykle dwa
zlecenia. Yield spada z rozmiarem zlecenia.

## Ćwiczenie: kryteria dla anulowania (8 min)

1. Przeczytaj pytania agenta z kroku 2.
2. Otwórz `zlecenia/anulowanie.md`.
3. Dopisz sekcję `Kryteria:` z co najmniej dwoma punktami. Odpowiedz na pytania agenta liczbami
   i stanami, nie przymiotnikami.
4. Sprawdź: `make przyjecie Z=anulowanie`. Wynik: przyjęte, z ostrzeżeniem o braku scenariuszy.
5. Zrób commit.

Dla anulowania nie ma scenariuszy holdout. Fabryka zbuduje zmianę, ale nie wypuści jej bez
człowieka (lekcja 9).

## Do dyskusji

- Kto w Twojej organizacji pisze dziś kryteria akceptacji? Kto będzie je pisał, gdy kod
  piszą agenci?
- Pytania agenta są dobre, ale niedeterministyczne. Decyzja o przyjęciu jest deterministyczna.
  Gdzie jeszcze warto tak rozdzielić „model radzi” od „system decyduje”?
