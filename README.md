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

Najprościej w przeglądarce: zrób fork, a na forku **Code → Codespaces → Create codespace on main**.
Codespace sam instaluje wszystkie narzędzia. Potem w terminalu:

```bash
fabryka start       # kind + Argo Workflows + kagent + Kyverno + Jaeger i wszystko, co przewiduje lekcja
fabryka lekcja 1    # albo dowolny numer: repo i klaster w stanie tej lekcji
fabryka mapa        # które bloczki fabryki już działają
fabryka sprawdz 1   # czy ćwiczenie jest zrobione
```

Utknąłeś: w Claude Code `/fabryka-autopilot 1`, albo `fabryka rozwiazanie 1`. Szczegóły, także
droga przez laptopa: [warsztat/start.md](warsztat/start.md). Setup na laptopie: [SETUP.md](SETUP.md).

### Z terminala: `gh`

Jeśli wolisz terminal od klikania, całą drogę zrobisz przez `gh` (GitHub CLI):

```bash
gh auth refresh -h github.com -s codespace          # raz: gh potrzebuje uprawnienia do Codespaces
gh repo fork ArturSkowronski/confitura-agentic-sdlc --clone=false
gh codespace create -R <login>/confitura-agentic-sdlc -b main -m standardLinux32gb   # 4 rdzenie, 16 GB
gh codespace ssh -c <nazwa>                          # terminal w codespace (nazwa: gh codespace list)
fabryka start                                        # już w codespace
gh codespace ports forward 2746:2746 16686:16686 8082:8082 -c <nazwa>   # hala, Jaeger, kagent na localhost
gh codespace stop -c <nazwa>                         # po warsztacie; gh codespace delete usuwa go całkiem
```

Dodatkowo:

- Błąd `This API operation needs the "codespace" scope` znaczy, że pominąłeś pierwszą linię.
  `gh auth refresh` otworzy przeglądarkę, żeby potwierdzić nowe uprawnienie.
- `gh codespace ssh` łączy się z serwerem SSH w kontenerze (feature `sshd` w `.devcontainer`).
  Pierwsze połączenie może chwilę czekać, aż codespace się uruchomi.
- Codespace zasypia po 30 minutach bezczynności i nie zużywa wtedy limitu obliczeń, tylko miejsce na dysku.
  `gh codespace list` pokazuje stan, a `gh codespace delete` zwalnia miejsce.
- Fork zawsze na swoim koncie: finał warsztatu otwiera issues i PR-y na Twoim forku, nie w repo prowadzącego.

## Lekcje

Każda lekcja to tag `lekcja-NN`. Commit lekcji zawiera jej infrastrukturę i ćwiczenie; rozwiązanie
jest w następnym commicie. Zostałeś w tyle? `make lekcja N=4` ustawia gałąź `praca` na start lekcji 4.

| # | Lekcja | Teza |
|---|---|---|
| 1 | [Klaster i pierwszy agent](warsztat/lekcja-01-klaster.md) | Agent to zasób w klastrze, nie skrypt na laptopie |
| 2 | [Warsztat i narzędzia](warsztat/lekcja-02-warsztat.md) | Uprawnienia agenta to lista narzędzi, nie prompt |
| 3 | [Kontekst L1–L5](warsztat/lekcja-03-kontekst.md) | Własność pojęcia wygrywa z częstością słów |
| 4 | [Przyjęcie zlecenia](warsztat/lekcja-04-przyjecie.md) | Fabryka nie przyjmuje zlecenia bez specyfikacji |
| 5 | [Linia](warsztat/lekcja-05-linia.md) | Linia to wersjonowany graf, nie skrypt |
| 6 | [Kontrola jakości](warsztat/lekcja-06-kontrola.md) | Zielony build dowodzi tylko, że model zgadza się sam ze sobą |
| 7 | [Wyrocznia](warsztat/lekcja-07-wyrocznia.md) | Holdout zużywa się z każdym użyciem |
| 8 | [Ryzyko, review, poprawki](warsztat/lekcja-08-review.md) | Każda poprawka przesuwa agenta od wymagania w stronę bramki |
| 9 | [Światło, WIP i polityka](warsztat/lekcja-09-polityka.md) | Człowiek to węzeł z rolą; linię rysuje plik |
| 10 | [Ślad i hala](warsztat/lekcja-10-slad.md) | Agent może proponować prawa, ale nie może ich uchwalać |
| finał | [Fabryka na GitHubie](warsztat/final-github.md) | Issue to zlecenie, PR to wynik, a Actions sprawdzają pochodzenie |

## Co jest w środku

| Ścieżka | Co to jest |
|---|---|
| `system/` | Sklep z konfiturami: `pricing-lib`, `orders-service`, `payments-service` (ścieżka krytyczna), `architecture` (ArchUnit) |
| `scenarios/` | Wyrocznia: scenariusze holdout pisane przez produkt. Agent ich nie widzi |
| `docs/adr/`, `ops/incidents/`, `docs/conventions.md` | Wiedza organizacji: decyzje, incydent, konwencje |
| `sdlc/` | Mózg fabryki w Pythonie (instrukcje dla modeli po angielsku, odpowiedzi po polsku): kontekst, przyjęcie, agent, bramki, ryzyko, review, księga. `a2a.py` woła agentów kagent |
| `platforma/` | Manifesty klastra: kagent (agenci, model), warsztat (narzędzia MCP), linia (Argo), Kyverno, Jaeger, poller GitHuba |
| `.github/workflows/fabryka.yml` | Finał: bramki fabryki na GitHubie (build, wyrocznia, review, pochodzenie księgi) |
| `zlecenia/` | Zlecenia dla fabryki (od lekcji 4) |
| `warsztat/narzedzia/` | CLI `fabryka` (lekcja, mapa, sprawdz, rozwiazanie, autopilot) i prompty autopilota. Instalacja: `make narzedzia` |
| `.devcontainer/` | GitHub Codespaces: cały stos w przeglądarce, bez instalacji na laptopie |
| `warsztat/` | Materiały lekcji, notatki prowadzącego i trzy decki: `keynote/` (pptx w stylistyce Visdoma), `przewodnik.html` (48 slajdów krok po kroku z kartą wykonawcy), `slajdy.html` (tezy) |
| `warsztat/grafiki/` | Dwanaście ilustracji w stylu JVM Weekly: sceny w `prompts.md`, generator `gen.py` |

## Licencja

MIT. Kod sklepu, ADR-y, incydent, scenariusze i osoby w historii gita są fikcyjne.
