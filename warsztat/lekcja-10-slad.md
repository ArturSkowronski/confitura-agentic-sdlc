# Lekcja 10: Ślad i hala (12 min)

**Teza.** Gdy coś pójdzie źle, nikt nie powinien przez tydzień odtwarzać, co zrobił agent.
Każde zdarzenie (przyjęcie, prompt, wywołanie narzędzia, commit, bramka, decyzja, akceptacja)
to linia w księdze z hashem poprzedniej linii. Linia podpisuje księgę kluczem fabryki (Sigstore
cosign, OpenSSF) i zapisuje **hash konfiguracji linii**: linia musi być powtarzalna, choć
pracownik nie jest. Ślady z kagent (OpenTelemetry) pokazują każde wywołanie modelu i narzędzia.

| Ślad | Skąd | Gdzie oglądać |
|---|---|---|
| Księga zdarzeń | `sdlc/ledger.py`, krok `ksiega` w linii | `.sdlc/out/<zlecenie>/proba-N/ledger.jsonl` po `make odbierz` |
| Podpis | `cosign sign-blob` kluczem z Secretu `fabryka-cosign` | `ledger.sigstore.json`, `make ksiega-verify` |
| Karta zlecenia | `sdlc/factory.py card` | `karta.md` w wynikach |
| Ślady agentów | kagent → OTLP → Jaeger | http://localhost:16686, serwis `wykonawca` |
| Hala | Argo Workflows UI | http://localhost:2746, wszystkie przebiegi na sali |

## Ćwiczenie A: manipulacja (5 min)

1. Odbierz wyniki ostatniego przebiegu: `make odbierz`.
2. Sprawdź księgę: `make ksiega-verify F=.sdlc/out/zwroty-czesciowe/proba-2/ledger.jsonl`. Wynik: łańcuch OK, podpis OK.
3. Otwórz plik. Zmień `human.approved` na `human.skipped` albo imię osoby akceptującej.
4. Uruchom weryfikację ponownie.

Łańcuch pokazuje linię, w której zmieniono treść. Podpis przestaje pasować do pliku. Ta sama
księga zawiera `holdout.peek` (jeśli agent zaglądał do wyroczni) i `gate.tamper_attempt`.

## Ćwiczenie B: co zrobił agent (5 min)

1. Otwórz Jaegera: `make hala`, potem serwis `wykonawca`, ostatni ślad.
2. Policz wywołania modelu i narzędzi. Porównaj z `narzedzia.jsonl` w wynikach.
3. Otwórz `karta.md`: czas, próby, decyzja, hash linii, kto zaakceptował.

## Hala (prowadzący, na projektorze)

Argo UI z filtrem na namespace `fabryka` pokazuje wszystkie linie na sali: gdzie jest każde
zlecenie, co czeka na człowieka (żółte), co stanęło (czerwone), co poszło lights-out.

## Dwie metryki na poniedziałek

- **Minuty człowieka na przyjętą zmianę**, liczone także w górę strumienia: specyfikacje,
  scenariusze, andony. Nie tylko review.
- **Ucieczki**: defekty, które przeszły przez fabrykę. Bez atrybucji defektu do zmiany nie ma
  z czego „zarobić” autonomii.

## Do dyskusji

- Agent może proponować prawa (nową regułę ArchUnit, konwencję), ale nie może ich uchwalać:
  taka zmiana dotyka bramek, więc dostaje ryzyko `critical` i czeka na człowieka.
- Wszystko, co dziś widziałeś, stoi na projektach Linux Foundation. Co z tego postawisz w firmie
  w poniedziałek, a co zamienisz na to, co już masz?
