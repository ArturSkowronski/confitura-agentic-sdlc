# Fabryka oprogramowania na stacku Linux Foundation: kagent jako orkiestrator agentów

Data: 2026-09-19. Status: zatwierdzony (decyzja własna w trybie autonomicznym, cel `/goal`).

## Cel

Przebudować warsztat „Zbuduj prawdziwą agentową platformę SDLC od podstaw” (Confitura 2026,
120 min, do 10 osób) tak, żeby:

1. orkiestratorem agentów był **kagent** (CNCF sandbox), a cała platforma stała na projektach
   Linux Foundation: Kubernetes (kind), Argo Workflows, Kyverno, OpenTelemetry + Jaeger,
   Sigstore cosign, protokoły MCP i A2A;
2. całość była podzielona na **10 lekcji**, gdzie uczestnik klonuje repo, a kolejne commity
   (tagi `lekcja-01` … `lekcja-10`) pchają go do przodu: commit N zawiera infrastrukturę
   lekcji N i ćwiczenie (TODO), commit N+1 zawiera rozwiązanie ćwiczenia N i lekcję N+1.

GitHub Actions, GitHub Issues, PR-y, Sigstore przez GitHub OIDC i hala `tower/` znikają.
Zlecenia są plikami w `zlecenia/`, linia jest Argo Workflow, „PR” to gałąź i łatka
odbierane z klastra.

## Co zostaje, co się zmienia

| Zostaje | Zmienia się |
|---|---|
| Sklep w Javie (`system/`), wyrocznia (`scenarios/`), ADR-y, incydent, konwencje, historia gita (L3) | Linia: `.github/workflows/*` → `platforma/linia/fabryka.yaml` (Argo WorkflowTemplate) |
| Mózg fabryki w Pythonie: `context`, `intake`, `risk`, `review`, `gates`, `mutation`, `scenarios`, `ledger`, `factory` (bez GitHub-izmów) | Agent: `agent.py` woła agenta **kagent** przez A2A (`sdlc/a2a.py`) albo replay; sterowniki OpenCode/Codex/Claude znikają |
| Osiem tez fabryki, metryka „odsłony na minutę”, plan B replay | Człowiek: `environment: critical-path` → Argo `suspend` + `make zatwierdz` |
| Polityka `sdlc/policy.json` | Uprawnienia agenta: lista narzędzi MCP + Kyverno ClusterPolicy zamiast `persist-credentials` |
| Księga z łańcuchem hashy | Podpis: `cosign sign-blob` kluczem fabryki (offline), nie attestation GitHuba |
| Tryb replay (nagrane łatki) | Hala: Argo UI + Jaeger zamiast `tower/index.html` |

## Architektura

```
uczestnik (laptop)                     kind: klaster „fabryka”
────────────────────                   ───────────────────────────────────────────────
make zlecenie Z=rabat ──git archive──▶ magazyn (Pod, PVC /work) ── repo snapshot
        │                                   │
        └── argo submit fabryka ──▶ Argo Workflows (ns fabryka)
                                       przyjęcie ─▶ [semafor WIP] ─▶ wykonawca ─▶ gates ‖ review ─▶ decyzja
                                            │                          │                     │
                                     A2A: agent przyjecie      A2A: agent wykonawca   A2A: agent recenzent
                                            └──────────── kagent (ns kagent) ─────────────┘
                                                              │  RemoteMCPServer „warsztat”
                                                              ▼
                                                  warsztat-mcp (Pod, PVC /work): read/write/list/run_build/git
                                       decyzja ─▶ lights-out | suspend(człowiek) | proba(attempt+1) | andon
                                       księga ─▶ ledger.jsonl + cosign.sig ─▶ /work/out/<zlecenie>/
make odbierz ◀──kubectl cp──────────── /work/out
Kyverno: ClusterPolicy na Agent CR (narzędzia, etykiety)       Jaeger: ślady OTel z kagent
```

### Komponenty

| Komponent | Technologia | Ścieżka w repo |
|---|---|---|
| Klaster | kind 0.33, K8s 1.36 | `platforma/kind.yaml`, `make klaster` |
| Orkiestrator agentów | kagent 0.10.1 (Helm OCI), runtime Go ADK; agenci i ModelConfig w namespace `fabryka` (kagent w `kagent`) | `platforma/kagent/` (ModelConfig, Agent ×4) |
| Narzędzia agenta | serwer MCP (Python `mcp`, streamable HTTP) na PVC `/work`, wdrożony przez CRD `MCPServer` (kmcp, `kagent.dev/v1alpha1`) | `platforma/warsztat/` (server.py, Dockerfile), obraz `fabryka-warsztat` |
| Linia | Argo Workflows 4.1 (quick-start-minimal, server-side apply CRD) | `platforma/linia/fabryka.yaml` |
| Kroki linii | obraz `fabryka-toolbox` (temurin 21 + maven + python3 + git + gitleaks + cosign) | `platforma/toolbox/Dockerfile` |
| Polityka | Kyverno 1.19 (admission only), `ValidatingPolicy` w CEL (`ClusterPolicy` jest deprecated, znika w 1.20) | `platforma/kyverno/` |
| Ślady | Jaeger 2.x all-in-one, OTLP gRPC 4317 | `platforma/otel/jaeger.yaml` |
| Podpis | cosign 3.x, para kluczy w Secret `fabryka-cosign` | `make klucze-cosign` |
| Zlecenia | pliki markdown z tytułem, treścią i kryteriami | `zlecenia/*.md` |

### Agenci kagent

| Agent | Rola | Narzędzia | Kiedy |
|---|---|---|---|
| `przyjecie` | pytania do autora zlecenia bez kryteriów (zamiast `llm.chat` w intake) | brak | lekcja 1 (ćwiczenie), 4 (w linii) |
| `wykonawca` | zmiana kodu w `/work/repo` | RemoteMCPServer `warsztat`: `list_files`, `read_file`, `write_file`, `run_build`, `git_diff` | lekcja 2 |
| `recenzent` | soczewki review od progu ryzyka (JSON z findings) | brak | lekcja 8 |

Serwer MCP egzekwuje granice, których agent nie może obejść: ścieżki chronione
(`sdlc/`, `platforma/`, `system/architecture/`) odrzuca przy zapisie, `scenarios/` odrzuca przy
odczycie i zapisuje próbę w `/work/events.jsonl` (`holdout.peek`). Agent nie ma tokena do
klastra ani gita: jedyne, co widzi, to pięć narzędzi.

### Linia (WorkflowTemplate `fabryka`)

Parametry: `zlecenie` (nazwa pliku), `agent` (`kagent`|`replay`), `proba` (1..max).

1. `przyjecie`: `context.py route`, `intake.py` (pytania przez A2A do `przyjecie`), limit WIP
   przez `synchronization.semaphore` (ConfigMap `fabryka-wip`).
2. `wykonawca`: `agent.py prompt` + `a2a.py` → agent `wykonawca` (albo replay: `git apply`).
   Commit na gałęzi `agent/<zlecenie>` w `/work/repo` jako `agent[bot]`.
3. `kontrola` (DAG, równolegle z `review`): build+ArchUnit+osłabianie testów, gitleaks,
   PIT, wyrocznia (scenariusze zawsze z `main` w `/work/repo`, nigdy z gałęzi).
4. `review`: `risk.py` + soczewki przez A2A do `recenzent` od progu z `policy.json`.
5. `decyzja`: lights-out / człowiek / poprawka / andon. Poprawka = rekurencyjne wywołanie
   szablonu `proba` z `proba+1` i raportem `feedback.md`. Andon = workflow kończy się błędem
   z komunikatem.
6. `czlowiek`: `suspend`. `make zatwierdz W=<workflow>` ustawia parametr `kto` i wznawia.
7. `ksiega`: merge fragmentów, `ledger.py verify`, karta zlecenia, `cosign sign-blob`,
   wynik do `/work/out/<zlecenie>/proba-<n>/`.

### Lekcje

| # | Lekcja (12 min) | Teza | Infrastruktura w commicie | Ćwiczenie (TODO → rozwiązane w N+1) |
|---|---|---|---|---|
| 1 | Klaster i pierwszy agent | Agent to zasób w klastrze, nie skrypt na laptopie | kind, kagent, ModelConfig, Agent `probny`, `sdlc/a2a.py`, `make klaster/doctor` | Napisz Agent CR `przyjecie` z instrukcją i wywołaj przez A2A |
| 2 | Warsztat i narzędzia | Uprawnienia agenta to lista narzędzi, nie prompt | PVC, `magazyn`, serwer MCP `warsztat`, RemoteMCPServer, Agent `wykonawca` | Dopisz ścieżki chronione do serwera MCP (zapis do `sdlc/` ma być odrzucony) |
| 3 | Kontekst L1–L5 | Własność pojęcia wygrywa z częstością słów | `context.py`, `AGENTS.md`, `module.json`, `make route` | Rabat trafia do złego modułu: wpisz `owns` w `pricing-lib/module.json` |
| 4 | Przyjęcie zlecenia | Fabryka nie przyjmuje zlecenia bez specyfikacji | `intake.py`, agent `przyjecie` w linii, `zlecenia/` | Dopisz `Kryteria:` do „Anulowanie zamówienia” |
| 5 | Linia | Linia to wersjonowany graf, nie skrypt | WorkflowTemplate: przyjęcie → wykonawca → zmiana; replay; `make zlecenie/odbierz` | Uruchom rabat w replay, odbierz łatkę; zmień `agent` na `kagent` i porównaj |
| 6 | Kontrola jakości | Zielony build dowodzi tylko, że model zgadza się sam ze sobą | DAG bramek: ArchUnit, osłabianie, gitleaks, PIT | Reguła ArchUnit: `BigDecimal` tylko w `pricing` |
| 7 | Wyrocznia | Holdout zużywa się z każdym użyciem | `scenarios.py` w linii, sejf, wyrocznia z `main`, `holdout.peek` | Zamknij wyrocznię: odczyt `scenarios/` w serwerze MCP ma być odrzucony i zapisany |
| 8 | Ryzyko, review, poprawki | Każda poprawka przesuwa agenta od wymagania w stronę bramki | `risk.py`, agent `recenzent`, rekurencja `proba+1`, andon | Reguła review LLM z kryteriami w `review-rules.json` |
| 9 | Światło, WIP i polityka | Człowiek to węzeł z rolą; linię rysuje plik | `policy.json` → decyzja, `suspend`, `make zatwierdz`, semafor WIP, Kyverno | Dodaj `suspend` do kroku `czlowiek`; ClusterPolicy: `wykonawca` ma tylko narzędzia `warsztat` |
| 10 | Ślad i hala | Agent może proponować prawa, ale nie może ich uchwalać | `ledger.py`, cosign, OTel → Jaeger, Argo UI jako hala, `make ksiega-verify` | Zmanipuluj księgę i sprawdź podpis; obejrzyj ślad wykonawcy w Jaegerze |

Poruszanie się: `make lekcja N=4` robi `git stash -u` i `git switch -C praca lekcja-04`.
`main` = `lekcja-10`. Prowadzący poprawia wspólne rzeczy skryptem `scripts/restack.sh`
(rebase łańcucha tagów).

## Fakty o stacku do materiałów (stan 19.09.2026)

- MCP jest projektem Agentic AI Foundation (LF) od 9.12.2025, spec 2026-07-28 z Streamable HTTP jako głównym transportem.
- A2A trafił do LF w czerwcu 2025, v1.0.0 z 12.03.2026, w AAIF od 17.08.2026. kagent 0.10 mówi A2A 0.3 (JSON-RPC), 1.0 przechodzi na gRPC.
- kagent: CNCF Sandbox od 22.05.2025. Jedyny projekt CNCF modelujący agenta jako zasób K8s z operatorem i natywnym MCP+A2A. Dapr Agents to biblioteka, agent-sandbox to tylko izolowany pod, agentgateway i Agent Router są w AAIF, nie w CNCF.
- Argo Workflows: CNCF Graduated. Tekton przeszedł z CDF do CNCF Incubating 13.03.2026.
- Sigstore: OpenSSF Graduated. cosign 3.x wymaga `--bundle`.
- Port 8083 kagent nie ma uwierzytelniania w OSS: tożsamość to nagłówek `X-User-Id`. To argument za bramą (agentgateway) w produkcji, na warsztacie zostaje w klastrze.

## Decyzje i odrzucone alternatywy

- **kagent Agent + MCP zamiast CLI kodującego w kontenerze.** AgentHarness/Substrate w kagent
  0.10.1 wymaga gVisor i snapshotów w GCS, nie działa na laptopie. Agent deklaratywny z pięcioma
  narzędziami MCP jest mniejszy, a lekcja „uprawnienia = lista narzędzi” jest wtedy dosłowna.
- **Argo Workflows zamiast Tekton/Argo Events.** Jeden manifest, UI z grafem, `suspend`,
  semafory i rekurencja szablonów pokrywają całą linię. Tekton wymaga Triggers do pętli.
- **kagent 0.10.1, nie 1.0.0-alpha1** (z 18.09): tydzień przed warsztatem pinujemy stabilne.
- **A2A przez własny klient Python.** `kagent invoke` w 0.10.1 nie dekoduje odpowiedzi
  (błąd `ClientResponse.error.data`). JSON-RPC `message/send` przez HTTP działa.
- **cosign z kluczem offline, nie keyless.** Konferencyjne Wi-Fi i logowanie OIDC w 10 osób
  to ryzyko; klucz w Secret daje tę samą lekcję (manipulacja psuje podpis).
- **Bez serwera git w klastrze.** Snapshot repo idzie do PVC przez `kubectl exec | tar`,
  wynik wraca przez `kubectl cp`. Zero kont, zero tokenów.
- **Helm OCI przez `kagent install` u uczestników**, u prowadzącego pobrany chart (keychain
  w sesji bez TTY blokuje OCI w Helmie na macOS).

## Ryzyka

| Ryzyko | Plan |
|---|---|
| PIT za wolny w kind (jeden węzeł, 8 GB) | próg 60% i tylko zmienione klasy; bramka opcjonalna w `policy.json` |
| Obrazy `fabryka-toolbox` i `fabryka-warsztat` budowane u uczestnika (kilka minut) | `make setup` buduje i `kind load` przed warsztatem; plan: publikacja na ghcr.io/arturskowronski |
| Model nie dowozi zmiany przez MCP (bez shella) | replay jako plan B; `run_build` zwraca skrócony log |
| Kagent A2A bez auth w klastrze | akceptowalne na warsztacie; wspomnieć agentgateway jako krok produkcyjny |

## Testy

- `make doctor`: klaster, CRD kagent, Argo, Kyverno, Jaeger, obrazy, klucz cosign.
- `make replay Z=rabat`: pełna linia bez modelu, wynik w `.sdlc/out/`.
- `platforma/warsztat/test_server.py`: ścieżki chronione, `holdout.peek`, `run_build`.
- Każdy tag `lekcja-NN` przechodzi `make doctor` i `make replay`, gdzie linia już istnieje.

## Odstępstwa od spec po wdrożeniu (19.09)

- Argo: `install.yaml` zamiast `quick-start-minimal` (quick-start w 4.1.4 wymusza plugin artefaktów „test”); serwer po HTTP z `--auth-mode=server`.
- Blokujące znalezisko review eskaluje do człowieka, nie do poprawki. Poprawkę wymuszają tylko bramki deterministyczne.
- Próg mutacji w `sdlc/policy.json` (`gates.mutation_threshold`, 50).
- Nagrania próby 2 (`sdlc/replays/*-poprawka.patch`): zwroty z prawdziwego agenta, rabat ręcznie (wpięcie polityki w `OrdersModule.production()`).
- cosign 3 offline: `sign-blob --key … --tlog-upload=false --use-signing-config=false --bundle …`, weryfikacja `verify-blob --key … --bundle … --insecure-ignore-tlog`.
- Snapshot repo niesie `.git` (L3 z historii) i commit working tree nazwiskiem uczestnika.
- Semafor WIP nie chroni przed dwoma przebiegami tego samego zlecenia naraz (wspólna gałąź na jednym dysku).
