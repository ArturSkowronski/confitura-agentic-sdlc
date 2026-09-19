# Fabryka oprogramowania od podstaw

Warsztat na Confiturze 2026 w Warszawie (oficjalny tytuł: „Zbuduj prawdziwą agentową platformę SDLC od podstaw”).
120 minut, do 10 osób, poziom zaawansowany. Dziesięć lekcji, każda to jeden commit.

Ludzie piszą specyfikacje i scenariusze. Agenci piszą kod. Fabryka decyduje, gdzie zapala
światło. To repo jest działającą fabryką na stacku Linux Foundation, w klastrze na Twoim laptopie:

| Warstwa | Projekt |
|---|---|
| Klaster | kind, Kubernetes (CNCF) |
| Agenci | kagent (CNCF Sandbox), protokoły MCP i A2A (Agentic AI Foundation) |
| Linia | Argo Workflows (CNCF Graduated) |
| Polityka | Kyverno (CNCF) |
| Ślady | OpenTelemetry i Jaeger (CNCF) |
| Podpis | Sigstore cosign (OpenSSF) |

## Start

Setup zrób przed warsztatem, zajmuje około 20 minut: [SETUP.md](SETUP.md).

```bash
git clone https://github.com/ArturSkowronski/confitura-agentic-sdlc
cd confitura-agentic-sdlc
make klaster     # kind + Argo Workflows + kagent + Kyverno + Jaeger
make doctor      # wszystko zielone = gotowe
```

## Lekcje

Każda lekcja to tag `lekcja-NN`. Commit lekcji zawiera jej infrastrukturę i ćwiczenie; rozwiązanie
jest w następnym commicie. Zostałeś w tyle? `make lekcja N=4` ustawia gałąź `praca` na start lekcji 4.

| # | Lekcja | Teza |
|---|---|---|
| 1 | [Klaster i pierwszy agent](warsztat/lekcja-01-klaster.md) | Agent to zasób w klastrze, nie skrypt na laptopie |
| 2 | [Warsztat i narzędzia](warsztat/lekcja-02-warsztat.md) | Uprawnienia agenta to lista narzędzi, nie prompt |
| 3 | Kontekst L1–L5 | Własność pojęcia wygrywa z częstością słów |
| 4 | Przyjęcie zlecenia | Fabryka nie przyjmuje zlecenia bez specyfikacji |
| 5 | Linia | Linia to wersjonowany graf, nie skrypt |
| 6 | Kontrola jakości | Zielony build dowodzi tylko, że model zgadza się sam ze sobą |
| 7 | Wyrocznia | Holdout zużywa się z każdym użyciem |
| 8 | Ryzyko, review, poprawki | Każda poprawka przesuwa agenta od wymagania w stronę bramki |
| 9 | Światło, WIP i polityka | Człowiek to węzeł z rolą; linię rysuje plik |
| 10 | Ślad i hala | Agent może proponować prawa, ale nie może ich uchwalać |

## Co jest w środku

| Ścieżka | Co to jest |
|---|---|
| `system/` | Sklep z konfiturami: `pricing-lib`, `orders-service`, `payments-service` (ścieżka krytyczna), `architecture` (ArchUnit) |
| `scenarios/` | Wyrocznia: scenariusze holdout pisane przez produkt. Agent ich nie widzi |
| `docs/adr/`, `ops/incidents/`, `docs/conventions.md` | Wiedza organizacji: decyzje, incydent, konwencje |
| `sdlc/` | Mózg fabryki w Pythonie (instrukcje dla modeli po angielsku, odpowiedzi po polsku): kontekst, przyjęcie, agent, bramki, ryzyko, review, księga. `a2a.py` woła agentów kagent |
| `platforma/` | Manifesty klastra: kagent (agenci, model), warsztat (narzędzia MCP), linia (Argo), Kyverno, Jaeger |
| `zlecenia/` | Zlecenia dla fabryki (od lekcji 4) |
| `warsztat/` | Materiały lekcji, slajdy, notatki prowadzącego |

## Licencja

MIT. Kod sklepu, ADR-y, incydent, scenariusze i osoby w historii gita są fikcyjne.
