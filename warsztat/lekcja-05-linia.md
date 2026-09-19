# Lekcja 5: Linia (12 min)

**Teza.** Linia to wersjonowany graf, a nie skrypt. Każdy krok to kontener z tym samym obrazem
i tym samym dyskiem; różni się tylko skryptem. Argo Workflows (CNCF Graduated) rysuje graf,
trzyma logi i pozwala zatrzymać przebieg na człowieku (lekcja 9). Agent jest jednym węzłem
grafu i jest wymienny: `kagent` albo `replay`.

```
przygotuj ─▶ przyjęcie ─▶ wykonawca ─▶ zmiana
  gałąź       routing      A2A do        commit na gałęzi agent/<zlecenie>,
  zlecenia    + kryteria   wykonawcy     łatka i opis w /work/out
```

| Element | Plik |
|---|---|
| Szablon linii | `platforma/linia/fabryka.yaml` (WorkflowTemplate `fabryka`) |
| Konto kroków | `platforma/linia/rbac.yaml` |
| Sterownik agenta | `sdlc/agent.py`: prompt z kontekstu L1–L5, potem A2A albo nagrana łatka |
| Nagrania | `sdlc/replays/`: łatka wybierana po zleceniu, module z routingu i numerze próby |

## Co masz po `make linia`

1. Uruchom rabat bez modelu: `make replay Z=rabat`.
2. Otwórz halę: `make hala`. Kliknij przebieg, zobacz graf i logi kroków.
3. Odbierz wynik: `make odbierz`. Otwórz `.sdlc/out/rabat/proba-1/zmiana.patch` i `opis.md`.
4. Nałóż łatkę lokalnie, jeśli chcesz: `git apply .sdlc/out/rabat/proba-1/zmiana.patch`.

Kroki linii nie mają dostępu do modelu. Tylko krok `wykonawca` woła agenta, i to przez A2A
do kontrolera kagent, nigdy bezpośrednio do API modelu. Klucz do modelu widzi tylko pod agenta.

## Ćwiczenie: ten sam graf, prawdziwy agent (8 min)

1. Ustaw klucz, jeśli jeszcze nie masz: `make klucz`.
2. Uruchom: `make zlecenie Z=rabat`. To potrwa dwie do pięciu minut.
3. W hali otwórz krok `wykonawca` i patrz na log. Równolegle:
   `kubectl exec -n fabryka deploy/magazyn -- tail -f /work/events.jsonl` pokazuje każde narzędzie.
4. Odbierz wynik: `make odbierz`. Porównaj `.sdlc/out/rabat/proba-1/zmiana.patch` z wersją replay.
5. Zajrzyj do Jaegera (http://localhost:16686), serwis `wykonawca`: ślad z każdym wywołaniem modelu i narzędzia.

Z `owns` z lekcji 3 zmiana trafia do `pricing-lib`. Wróć na chwilę do pustego `owns` i uruchom
jeszcze raz: ten sam agent liczy rabat w `OrderService`, testy zielone, moduł zły. Kontekst
zmienia wynik, nie prompt.

## Do dyskusji

- Co widzi hala, czego nie widać w logach agenta? Co widzą logi agenta, czego nie widać w hali?
- Gdzie w tym grafie postawiłbyś dzisiaj człowieka? Zapisz odpowiedź, wrócimy do niej w lekcji 9.
- Zmiana jeszcze nie przeszła żadnej kontroli. Zielony build agenta to nie bramka (lekcja 6).
