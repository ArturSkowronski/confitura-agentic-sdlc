# Notatki prowadzącego

Metryka warsztatu: **odsłony na minutę**. Odsłona to moment, w którym coś zielonego okazuje
się złe albo fabryka robi coś, czego sala się nie spodziewa. Plan: 12 odsłon w 120 minutach.

## Odsłony

| # | Minuta | Lekcja | Odsłona | Co musi być gotowe |
|---|---|---|---|---|
| 1 | 0:03 | otwarcie | Łatka zielona, czytelna, w złym module, przyjęta lights-out | klaster demo z gotowym przebiegiem rabatu bez `owns` |
| 2 | 0:08 | 1 | `kubectl get agent`: agent to Deployment i Service, karta A2A pod `.well-known` | klaster uczestników |
| 3 | 0:19 | 2 | Wykonawca zapisuje `sdlc/policy.json`, bo serwer nie ma listy chronionych ścieżek | agent wykonawca, pusty `PROTECTED_PATHS` |
| 4 | 0:30 | 3 | „Zamówienie” ×6 wygrywa z „rabatem”: routing wyjaśniony liczbami | `make route` na projektorze |
| 5 | 0:41 | 4 | Fabryka odsyła anulowanie z pytaniami od agenta | `make przyjecie Z=anulowanie` |
| 6 | 0:52 | 5 | Ten sam graf, prawdziwy agent: 12 wywołań narzędzi, `run_build` zielony, łatka w pricing-lib | klucze rozdane, `make zlecenie Z=rabat` |
| 7 | 1:03 | 6 | jqwik mówi do agenta w logu `run_build`; naiwny rabat przechodzi wszystkie bramki | `make naiwna` |
| 8 | 1:14 | 7 | Incydent z marca łapie scenariusz, zanim ktoś czyta kod; sejf nieotwarty | `make replay Z=zwroty-czesciowe` |
| 9 | 1:25 | 8 | Węzeł `poprawka` to znowu cała linia; recenzent wytyka losowy UUID jako klucz idempotencji | przebieg zwrotów z modelem |
| 10 | 1:36 | 9 | Linia staje na żółto; `make zatwierdz` i imię w księdze; Kyverno odrzuca złego agenta | suspend, polityka CEL |
| 11 | 1:47 | 10 | Jedno słowo w księdze i łańcuch pokazuje linię, podpis pęka | `make ksiega-verify` |
| 12 | 1:52 | klamra | Hala: wszystkie przebiegi sali w Argo UI, ślady wykonawcy w Jaegerze | Argo UI na projektorze |

Między odsłonami są slajdy z tezą. Każda teza ma dowód z repo, nie z internetu.

## Przed warsztatem

| Kiedy | Co |
|---|---|
| do 22.09 | Wypchnij repo z tagami `lekcja-01` … `lekcja-10`: `scripts/restack.sh --push`. `main` = lekcja 10. |
| do 22.09 | Opublikuj obrazy `fabryka-toolbox` i `fabryka-warsztat` na ghcr.io (plan B dla osób, którym build nie przejdzie) i dopisz w SETUP.md. |
| do 22.09 | Wyślij mail z setupem (`warsztat/mail-setup.md`). Uzupełnij salę. |
| 23.09 | Przejdź na czysto: `kind delete cluster --name fabryka`, `make klaster`, `make setup`, `make doctor`, `make replay Z=rabat`, `make zlecenie Z=zwroty-czesciowe`. Zmierz czasy. |
| 24.09 | Wygeneruj 12 kluczy OpenRouter z limitem 8 USD każdy. Wydrukuj na kartkach. |
| 24.09 | Nagraj ekran z odsłonami 6, 8 i 9 (plan B, gdy padnie sieć albo model). |
| 25.09 | Laptop demo: klaster z przebiegami rabatu (bez `owns` i z `owns`), zwrotów (2 próby, zatwierdzone) i naiwnej zmiany. Hala otwarta. |
| po warsztacie | Unieważnij klucze OpenRouter. |

Czasy z prób 19.09 (M5 Pro, 8 GB dla Dockera): `make klaster` od zera 2 min, `make setup` (build
obrazów z rozgrzanym Mavenem) 6 min, replay rabatu z pełną linią 1,5 min, przebieg z modelem
(gpt-5-mini przez kagent) 2 min na próbę plus 1 min na review, zwroty z dwiema próbami 5,5 min.
Koszt: próba wykonawcy na Sonnet 5 to rząd 0,3 do 0,8 USD, soczewki review grosze. 10 osób ×
6 przebiegów mieści się w 60 USD.

## Dwa decki

| Plik | Do czego |
|---|---|
| `warsztat/slajdy.html` | tezy i odsłony, 25 slajdów: na projektor między ćwiczeniami |
| `warsztat/przewodnik.html` | krok po kroku, 45 slajdów: każda lekcja w czterech krokach (gdzie jesteśmy, rozejrzyj się, ćwiczenie, sprawdź) z komendami, fragmentami kodu i oczekiwanym wyjściem; do wysłania uczestnikom i na drugi ekran |

## Przebieg (120 min)

| Czas | Blok | Slajdy |
|---|---|---|
| 0:00 | Otwarcie, teza, poziomy autonomii, stack LF | 1-4 |
| 0:05 | Lekcja 1: klaster i pierwszy agent | 5-6 |
| 0:16 | Lekcja 2: warsztat i narzędzia | 7-8 |
| 0:27 | Lekcja 3: kontekst L1–L5 | 9-10 |
| 0:38 | Lekcja 4: przyjęcie, klucze (`make klucz`) | 11 |
| 0:49 | Lekcja 5: linia | 12-13 |
| 1:00 | Lekcja 6: kontrola jakości | 14-15 |
| 1:11 | Lekcja 7: wyrocznia | 16-17 |
| 1:22 | Lekcja 8: ryzyko, review, poprawki | 18-19 |
| 1:33 | Lekcja 9: światło, WIP, polityka | 20-21 |
| 1:44 | Lekcja 10: ślad | 22-23 |
| 1:55 | Klamra: hala, mapa, zamknięcie | 24-25 |

Jeśli jesteś spóźniony: lekcja 3 i 4 jako demo (bez ćwiczeń), lekcja 10 tylko odsłona 11.
Ćwiczenia, których nie wolno pominąć: 2 (chronione ścieżki), 6 (ArchUnit), 9A (suspend).

## Plan B

| Problem | Co robisz |
|---|---|
| Model nie odpowiada albo skończył się limit | `make replay Z=…`. Wszystkie lekcje działają na nagraniach, łącznie z pętlą poprawek (nagrania próby 2 są z prawdziwego agenta). Review bez modelu zostaje na regexach. |
| Wi-Fi padło | Nic się nie dzieje: klaster, obrazy i cache Mavena są na laptopie. Tylko model potrzebuje sieci. |
| Uczestnik utknął | `make lekcja N=<numer>`. Jego zmiany lądują w `git stash`. |
| Build obrazów nie przeszedł u uczestnika | obrazy z ghcr.io (`IMAGE_TAG` w `scripts/workshop.env`) albo para z sąsiadem. |
| Przebieg trwa za długo | Pokaż gotowy przebieg z laptopa demo, bieżący zostaw w tle w hali. |
| Ktoś nie ma klastra | Paruje się z sąsiadem. Grupa 10 osób, to działa. |

## Znane zachowania

- Instrukcje dla modeli (systemMessage agentów, prompt wykonawcy, soczewki review, opisy narzędzi MCP,
  szkielet `AGENTS.md`) są po angielsku, odpowiedzi i materiały po polsku. Dokumenty organizacji
  (ADR-y, konwencje, incydent) zostają po polsku i tak trafiają do agenta.
- `platforma/kagent/modelconfig.yaml` ma `${LLM_MODEL}` i `${LLM_BASE_URL}`: wdrażaj przez `make klucz`
  albo `make klaster`, nie `kubectl apply -f platforma/kagent/` na cały katalog (zepsuje ModelConfig).

- jqwik 1.10.1 wypisuje w logu testów tekst do agentów AI. Zostawiamy celowo (odsłona 7).
  Wersja 1.9.3 jest czysta, gdyby agent zaczął na to reagować.
- `kagent invoke` w CLI 0.10.1 nie dekoduje odpowiedzi (błąd `ClientResponse.error.data`).
  Wszystko idzie przez `sdlc/a2a.py` (JSON-RPC `message/send`). CLI służy do `install` i `dashboard`.
- Świeżo wdrożony agent jest `Ready` chwilę przed tym, jak jego pod przyjmuje połączenia.
  `a2a.py` ponawia „connection refused” cztery razy.
- kagent 1.0.0-alpha1 (z 18.09) ma inne API (`AgentTemplate`, `Harness`, A2A po gRPC) i wymaga
  gVisor oraz K8s 1.37. Pinujemy 0.10.1 w `scripts/klaster.sh` i w `KAGENT_HELM_VERSION`.
- Port 8083 kagent nie ma uwierzytelniania (tożsamość z nagłówka `X-User-Id`). Zostaje w klastrze.
- Dysk `/work` jest jeden (ReadWriteOnce, jeden węzeł kind). Dwa przebiegi tego samego zlecenia
  naraz nadpisują sobie gałąź. Semafor WIP nie chroni przed tym: to świadome uproszczenie warsztatu.
- Helm na macOS w sesji bez TTY nie umie pobrać chartu OCI (keychain). U uczestników w terminalu
  działa; gdyby nie, `KAGENT_CHART` i `KAGENT_CHART_CRDS` w `scripts/klaster.sh` przyjmują ścieżkę do `.tgz`.
- Blokujące znalezisko review eskaluje do człowieka, nie do poprawki. Inaczej dobry model
  (recenzent trafnie wytknął losowy UUID) kończyłby zwroty andonem po dwóch próbach.
