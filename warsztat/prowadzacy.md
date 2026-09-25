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
| ✅ 23.09 | Rozwiązanie ćwiczenia 6 (`money_arithmetic_only_in_pricing`) jest w commicie „Lekcja 7:”, tagi przestawione `scripts/restack.sh`. `make test` zielone, naiwny rabat czerwony. |
| ✅ 23.09 | Repo publiczne: https://github.com/ArturSkowronski/confitura-agentic-sdlc, `main` = lekcja 10 + finał, tagi `lekcja-01` … `lekcja-10` po restacku. Kolejny restack przed forkami uczestników, potem już nie (forki mają kopie tagów). |
| do 24.09 | Dopisz do maila z setupem: fork, `gh auth login`, `brew install gh` (SETUP.md już to ma). |
| 24.09 | Przejdź finał na swoim forku: `make github`, `make issue Z=rabat`, `make ciagnij AGENT=replay`. PR, cztery zielone checki, auto-merge, issue zamknięte, link do śladu działa. |
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

## Trzy decki

| Plik | Do czego |
|---|---|
| `warsztat/keynote/fabryka-od-podstaw.pptx` | 17 slajdów na projektor, stylistyka Visdoma, ilustracje w stylu JVM Weekly. Keynote otwiera `.pptx` natywnie. Budowa: `cd warsztat/keynote && npm install && node build.mjs` |
| `warsztat/przewodnik.html` | 48 slajdów krok po kroku: zimne otwarcie, każda lekcja w czterech krokach (gdzie jesteśmy, rozejrzyj się, ćwiczenie, sprawdź), komendy i oczekiwane wyjście. Do wysłania uczestnikom i na drugi ekran |
| `warsztat/slajdy.html` | 25 slajdów z tezami i odsłonami, wersja sprzed przebudowy. Zostaje jako zapas |

Wszystkie trzy niosą tę samą kartę wykonawcy, więc puenta jest ta sama niezależnie od tego,
z czego prowadzisz. Ilustracje siedzą w `warsztat/grafiki/` (`gen.py`, `prompts.md`,
`optimize.sh`); oryginały 4 MB zostają lokalnie, do repo idą JPEG-i z `deck/`.

### Nić przewodnia: karta wykonawcy

Przewodnik trzyma się jednej klamry. **Zimne otwarcie** (slajdy 1 i 2) pokazuje zieloną łatkę
w złym module, przyjętą bez człowieka, i odsłania, że wszystko zadziałało zgodnie z regułami,
tyle że reguł nie było. Ta sama łatka wraca w lekcji 3 jako tabela routingu, w lekcji 5 jako
przebieg z prawdziwym agentem i w lekcji 6 jako czerwona bramka.

**Po każdym ćwiczeniu karta wykonawcy dostaje jedną nową regułę** i etykietę mówiącą, czym ta
reguła jest naprawdę: słowo, kontekst, ściana, bramka, polityka albo ślad. Karta rośnie
na czwartym kroku każdej lekcji, od jednej reguły do dziesięciu.

| # | Lekcja | Reguła | Rodzaj |
|---|---|---|---|
| 1 | 1 | Pytaj o to, czego brakuje. Nie proponuj rozwiązań. | słowo |
| 2 | 2 | Do `sdlc/`, `platforma/`, `system/architecture` nie zapiszesz. | ściana |
| 3 | 3 | Rabat, cena i kwota należą do pricing-lib. ADR-0001. | kontekst |
| 4 | 4 | Bez kryteriów akceptacji nie dostaniesz zlecenia. | bramka |
| 5 | 5 | Zadanie dostajesz przez A2A. Klucza do modelu nie zobaczysz. | ściana |
| 6 | 6 | Poza pakietem pricing nie liczysz na `BigDecimal`. | bramka |
| 7 | 7 | Katalog `scenarios/` dla ciebie nie istnieje. | ściana |
| 8 | 8 | Klucz idempotencji unikalny dla zwrotu, stabilny przy ponowieniu. | bramka |
| 9 | 9 | Ryzyko high i critical czeka na człowieka. Narzędzia: tylko warsztat. | polityka |
| 10 | 10 | Każde wywołanie jest w podpisanej księdze. | ślad |

Na slajdzie 4 zapowiadasz **zakład**: ile z dziesięciu reguł okaże się zwykłym zdaniem w prompcie?
Slajd 46 rozstrzyga: jedna. Dziewięć pozostałych działa, choćby model miał gorszy dzień albo
ktoś podmienił prompt. To jest puenta warsztatu, a reguła 3 kontra reguła 6 (ta sama treść
ADR-0001, raz jako kontekst, raz jako bramka) jest jej najkrótszym dowodem.

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

## Codespaces, fabryka i autopilot

Domyślna droga uczestnika to fork i GitHub Codespaces (`.devcontainer/`, maszyna 4-rdzeniowa, 16 GB).
Nic nie instaluje na laptopie, a darmowy limit konta GitHub Free (120 core-godzin) starcza na 30 godzin.
Poproś salę, żeby `fabryka start` zrobili przed warsztatem: pierwsze postawienie klastra trwa około 10 minut.

Narzędzie `fabryka` jest instalowane poza repo, więc skakanie po tagach go nie usuwa:

| Sytuacja na sali | Co mówisz |
|---|---|
| ktoś się spóźnił albo zgubił | `fabryka lekcja N`: repo i klaster w stanie lekcji N, zmiany w stash |
| nie wiadomo, czy ćwiczenie jest zrobione | `fabryka sprawdz N`: deterministycznie, bez modelu |
| ćwiczenie nie wychodzi | `/fabryka-autopilot N` w Claude Code, a w ostateczności `fabryka rozwiazanie N` |
| nikt nie rozumie, co już zbudowaliśmy | `fabryka mapa` na projektorze: bloczki fabryki zapalają się lekcja po lekcji |
| klaster w dziwnym stanie | `fabryka reset` (10 minut, więc raczej przerwa) |

Autopilot nigdy nie zatwierdza za człowieka: przy `make zatwierdz` i przy PR zatrzymuje się i pyta.
To dobry moment na zdanie z lekcji 9, pokazane na żywo.

## Finał na GitHubie

`warsztat/final-github.md`, 12 minut. Nie mieści się w obecnym przebiegu bez cięcia: lekcje 3 i 4 prowadź
jako demo bez ćwiczeń (zysk około 16 minut), finał po lekcji 10, klamra zostaje. Odsłona finału: ręczny
commit na gałęzi agenta i czerwony check `pochodzenie` („po commicie z księgi zmieniono kod”).

Co musi działać u uczestnika: fork jako `origin`, `gh auth login`, sieć do GitHuba. Bez sieci finał
pokazujesz z laptopa demo, a uczestnicy robią `make zlecenie … AGENT=replay`.

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
- Kontroler Argo wysyła ślady (OTLP do Jaegera) i daje krokom `TRACEPARENT`. `sdlc/a2a.py` przekazuje go
  do kagent, więc spany agenta są w śladzie przebiegu. Ślad Argo ma sporo spanów kontrolera
  (`reconcileTaskResult` itd.): w Jaegerze filtruj serwis `fabryka-linia` albo zwiń drzewo do kroków.
- Klucz cosign montuje tylko krok księgi, token GitHuba tylko `krok-github`. Build kodu agenta nie ma sekretów.
- Blokujące znalezisko review eskaluje do człowieka, nie do poprawki. Inaczej dobry model
  (recenzent trafnie wytknął losowy UUID) kończyłby zwroty andonem po dwóch próbach.
