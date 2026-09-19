# Fabryka na kagent i stacku LF: plan wdrożenia

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Zamienić linię na GitHub Actions na linię w klastrze kind: kagent orkiestruje agentów, Argo Workflows prowadzi zlecenie, Kyverno pilnuje deklaracji, cosign podpisuje księgę; całość w 10 commitach-lekcjach.

**Architecture:** Mózg fabryki zostaje w `sdlc/*.py` (biblioteka standardowa). Nowy katalog `platforma/` trzyma manifesty K8s i dwa obrazy (`fabryka-toolbox`, `fabryka-warsztat`). Agent kodujący to kagent `Agent` z narzędziami MCP na PVC `/work`. Linia to jeden `WorkflowTemplate` z rekurencją na poprawki i `suspend` na człowieka.

**Tech Stack:** kind 0.33, K8s 1.36, kagent 0.10.1 (Helm OCI, runtime Go ADK), kmcp `MCPServer`, Argo Workflows 4.1.4, Kyverno 1.19 `ValidatingPolicy`, Jaeger 2.11, cosign 3.1, Python 3.12+ (`mcp` tylko w serwerze narzędzi), Java 21 + Maven.

**Spec:** `docs/superpowers/specs/2026-09-19-kagent-lf-stack-design.md`

## Global Constraints

- kagent przypięty do `0.10.1` (`KAGENT_HELM_VERSION=0.10.1`), API `kagent.dev/v1alpha2`, `MCPServer` `kagent.dev/v1alpha1`.
- Argo CRD instalowane `kubectl apply --server-side` (adnotacja > 256 KiB).
- Skrypty w `sdlc/` bez zależności poza biblioteką standardową; `mcp` tylko w obrazie `fabryka-warsztat`.
- Materiały po polsku, jedno polecenie na zdanie w krokach ćwiczeń, bez em dashy.
- Każdy tag `lekcja-NN` ma działający `make doctor`; od `lekcja-05` także `make replay Z=rabat`.
- Commit lekcji N zawiera TODO ćwiczenia N; rozwiązanie ląduje w commicie N+1.
- Nazwy w repo: `zlecenia/` (zamiast issues), `platforma/`, `warsztat/lekcja-NN-*.md`, `make lekcja N=`.

---

## Struktura plików (stan końcowy, `lekcja-10`)

| Plik | Odpowiedzialność |
|---|---|
| `Makefile` | jedyne wejście: `klaster`, `setup`, `doctor`, `lekcja`, `zlecenie`, `replay`, `odbierz`, `zatwierdz`, `hala`, `klucz`, `test`, `route`, `oracle`, `ksiega-verify` |
| `scripts/klaster.sh` | kind + Argo + kagent + Kyverno + Jaeger, idempotentne |
| `scripts/obrazy.sh` | build `fabryka-toolbox`, `fabryka-warsztat`, `kind load` |
| `scripts/doctor.sh` | kontrola klastra i narzędzi lokalnych |
| `scripts/lekcja.sh` | `git stash -u`, `git switch -C praca lekcja-NN` |
| `scripts/zlecenie.sh` | snapshot repo → magazyn, `argo submit --from workflowtemplate/fabryka` |
| `scripts/odbierz.sh` | `kubectl cp` z `/work/out` do `.sdlc/out/` |
| `scripts/restack.sh` | przestawia łańcuch tagów po poprawce wspólnej |
| `platforma/kind.yaml` | klaster jednowęzłowy z mapowaniem portów UI |
| `platforma/kagent/values.yaml` | profil helm: bez agentów przykładowych, OTel do Jaegera |
| `platforma/kagent/modelconfig.yaml` | `fabryka-model`: OpenAI-compatible z `baseUrl` (OpenRouter) |
| `platforma/kagent/agent-probny.yaml` | lekcja 1 |
| `platforma/kagent/agent-przyjecie.yaml` | lekcja 2 (rozwiązanie ćw. 1) |
| `platforma/kagent/agent-wykonawca.yaml` | lekcja 2 |
| `platforma/kagent/agent-recenzent.yaml` | lekcja 8 |
| `platforma/warsztat/server.py`, `test_server.py`, `Dockerfile`, `mcpserver.yaml`, `pvc.yaml`, `magazyn.yaml` | serwer MCP na `/work` + magazyn |
| `platforma/toolbox/Dockerfile` | temurin 21 + maven + python3 + git + gitleaks + cosign |
| `platforma/linia/fabryka.yaml` | WorkflowTemplate: rośnie z lekcji 5 do 10 |
| `platforma/linia/rbac.yaml`, `wip.yaml` | SA `fabryka`, semafor WIP |
| `platforma/kyverno/agent-narzedzia.yaml` | ValidatingPolicy na Agent CR |
| `platforma/otel/jaeger.yaml` | Jaeger all-in-one |
| `sdlc/a2a.py` | klient A2A JSON-RPC: `send(agent, text, *, session=None) -> str` |
| `sdlc/agent.py` | `prompt`, `run` (kagent przez a2a albo replay) |
| `sdlc/intake.py`, `review.py` | wołają `a2a.send` zamiast `llm.chat` |
| `sdlc/lib.py` | bez `gh_output`/`step_summary`; `outputs()` pisze do `/tmp/outputs/<k>` dla Argo |
| `zlecenia/*.md` | `# tytuł`, treść, `Kryteria:` |
| `warsztat/lekcja-01..10.md`, `prowadzacy.md`, `slajdy.html`, `mail-setup.md` | materiały |

## Task 1: Lekcja 1, klaster i pierwszy agent

**Files:** `platforma/kind.yaml`, `platforma/kagent/values.yaml`, `platforma/kagent/modelconfig.yaml`, `platforma/kagent/agent-probny.yaml`, `platforma/otel/jaeger.yaml`, `scripts/klaster.sh`, `scripts/doctor.sh`, `scripts/lekcja.sh`, `sdlc/a2a.py`, `sdlc/lib.py` (usunąć GH), `Makefile`, `SETUP.md`, `README.md`, `warsztat/lekcja-01-klaster.md`; usunąć `.github/workflows`, `tower/`, `scripts/bootstrap.sh`, `scripts/issues.sh`, `scripts/catch-up.sh`, `compose.yaml`, `Dockerfile`; przenieść `.github/CODEOWNERS` → `CODEOWNERS`.

**Interfaces:** `a2a.send(agent: str, text: str, *, namespace="kagent", base=env KAGENT_URL or http://localhost:8083, timeout=600) -> str` (tekst ostatniego artefaktu). `make a2a A=probny T="..."`.

- [ ] `scripts/klaster.sh`: kind create (jeśli brak), Argo server-side, `kagent install` z `KAGENT_HELM_VERSION=0.10.1` i `--profile minimal` albo helm z `platforma/kagent/values.yaml`, Kyverno helm odchudzony, Jaeger, `kubectl apply -f platforma/kagent/modelconfig.yaml agent-probny.yaml`.
- [ ] `sdlc/a2a.py` z testem `sdlc/test_a2a.py` (serwer HTTP w wątku zwraca sztuczny task).
- [ ] `make doctor` zielony; `make a2a A=probny T="Przedstaw się"` zwraca zdanie.
- [ ] Ćwiczenie w lekcji: plik `platforma/kagent/agent-przyjecie.yaml` z `TODO`.
- [ ] Commit `lekcja 1: klaster i pierwszy agent`, tag `lekcja-01`.

## Task 2: Lekcja 2, warsztat i narzędzia

**Files:** `platforma/warsztat/{server.py,test_server.py,Dockerfile,pvc.yaml,magazyn.yaml,mcpserver.yaml}`, `platforma/kagent/{agent-przyjecie.yaml (rozwiązanie), agent-wykonawca.yaml}`, `scripts/obrazy.sh`, `Makefile` (`setup`, `wyslij`), `warsztat/lekcja-02-warsztat.md`.

**Interfaces:** narzędzia MCP: `list_files(path=".") -> str`, `read_file(path) -> str`, `write_file(path, content) -> str`, `run_build(module="") -> str` (mvn -B -q verify w `/work/repo/system`, tail 60 linii), `git_diff() -> str`. Env: `WORK_DIR=/work/repo`, `PROTECTED_PATHS`, `HIDDEN_PATHS`, `EVENTS_FILE=/work/events.jsonl`. Zapis w chronioną ścieżkę → `Odrzucone: ścieżka chroniona` i zdarzenie `gate.tamper_attempt`; odczyt ukrytej → zdarzenie `holdout.peek`.

- [ ] Testy `test_server.py` (unittest, bez sieci): chronione, ukryte, listowanie, diff.
- [ ] Serwer FastMCP streamable HTTP na `:3000/mcp`.
- [ ] `MCPServer` CR (kmcp, `transportType: http`, `deployment.image: fabryka-warsztat:lekcja`, `volumes` PVC) + `RemoteMCPServer` niepotrzebny, kagent odkrywa `MCPServer`. Sprawdzić w klastrze `status.discoveredTools`.
- [ ] Agent `wykonawca` z `tools[].mcpServer{kind: MCPServer, name: warsztat}`. `make a2a A=wykonawca T="Wypisz moduły w system/"` działa.
- [ ] TODO w commicie: `PROTECTED_PATHS` puste w `mcpserver.yaml` (ćw. 2), rozwiązanie w 3.
- [ ] Commit, tag `lekcja-02`.

## Task 3: Lekcja 3, kontekst L1–L5

**Files:** `sdlc/context.py` (CODEOWNERS z roota, bez GH), `AGENTS.md`, `warsztat/lekcja-03-kontekst.md`, `system/pricing-lib/module.json` (`owns` puste = TODO).

- [ ] `make route T="Rabat 10% dla zamówień powyżej 500 zł"` → `orders-service` (błędnie) w commicie 3, `pricing-lib` w commicie 4.
- [ ] `make agents-md` przebudowuje `AGENTS.md`.
- [ ] Commit, tag `lekcja-03`.

## Task 4: Lekcja 4, przyjęcie zlecenia

**Files:** `sdlc/intake.py` (pytania przez `a2a.send("przyjecie", ...)`), `zlecenia/{rabat,zwroty-czesciowe,anulowanie,wolne}.md`, `sdlc/zlecenia.py` (`load(name) -> {title, body}`), `Makefile` (`przyjecie Z=`), `warsztat/lekcja-04-przyjecie.md`.

- [ ] `make przyjecie Z=anulowanie` → odesłane z pytaniami; `Z=rabat` → przyjęte.
- [ ] TODO: `zlecenia/anulowanie.md` bez `Kryteria:`; rozwiązanie w 5.
- [ ] Commit, tag `lekcja-04`.

## Task 5: Lekcja 5, linia

**Files:** `platforma/linia/{fabryka.yaml,rbac.yaml}`, `platforma/toolbox/Dockerfile`, `sdlc/agent.py` (kagent/replay), `scripts/{zlecenie.sh,odbierz.sh}`, `Makefile` (`zlecenie`, `replay`, `odbierz`, `hala`), `warsztat/lekcja-05-linia.md`.

**Interfaces:** WorkflowTemplate `fabryka` parametry `zlecenie`, `agent` (`kagent|replay`), `proba`. Kroki: `przygotuj` (kopia snapshotu do `/work/repo`, gałąź `agent/<zlecenie>`), `przyjecie`, `wykonawca`, `zmiana` (commit + `git format-patch` do `/work/out/<zlecenie>/proba-N/zmiana.patch`). Wyjścia kroków przez `outputs.parameters.valueFrom.path`.

- [ ] `make replay Z=rabat` kończy się `Succeeded`, `make odbierz` daje `.sdlc/out/rabat/proba-1/zmiana.patch`.
- [ ] `make zlecenie Z=rabat AGENT=kagent` na prawdziwym modelu (OpenAI) daje łatkę w `orders-service` (zły moduł, zgodnie z tezą).
- [ ] Commit, tag `lekcja-05`.

## Task 6: Lekcja 6, kontrola jakości

**Files:** `platforma/linia/fabryka.yaml` (DAG `kontrola`: build, weakening, secrets, mutation), `sdlc/gates.py`, `sdlc/mutation.py` (bez GH), `system/architecture/.../ArchitectureRulesTest.java` (TODO), `Makefile` (`naiwna Z=rabat` = replay łatki w orders), `warsztat/lekcja-06-kontrola.md`.

- [ ] Replay rabatu w orders: bramki zielone w commicie 6, ArchUnit czerwony w 7.
- [ ] Commit, tag `lekcja-06`.

## Task 7: Lekcja 7, wyrocznia

**Files:** `platforma/linia/fabryka.yaml` (krok `wyrocznia` z `scenarios/` z `main`), `sdlc/scenarios.py`, `platforma/warsztat/mcpserver.yaml` (`HIDDEN_PATHS` TODO), `warsztat/lekcja-07-wyrocznia.md`.

- [ ] `make replay Z=zwroty-czesciowe`: próba 1 pada na scenariuszu idempotencji, `vault` nie odpalony.
- [ ] Commit, tag `lekcja-07`.

## Task 8: Lekcja 8, ryzyko, review, poprawki

**Files:** `sdlc/risk.py`, `sdlc/review.py` (recenzent przez A2A), `platforma/kagent/agent-recenzent.yaml`, `platforma/linia/fabryka.yaml` (krok `review`, `decyzja`, rekurencja `proba`), `sdlc/factory.py feedback`, `sdlc/review-rules.json` (TODO), `warsztat/lekcja-08-review.md`.

- [ ] `make replay Z=zwroty-czesciowe`: próba 1 → poprawka → próba 2 → człowiek (bez suspend, log `human.approval_missing`).
- [ ] Commit, tag `lekcja-08`.

## Task 9: Lekcja 9, światło, WIP i polityka

**Files:** `platforma/linia/{fabryka.yaml (suspend TODO), wip.yaml}`, `scripts/zatwierdz.sh`, `platforma/kyverno/agent-narzedzia.yaml` (TODO reguła), `warsztat/lekcja-09-polityka.md`.

- [ ] Po rozwiązaniu: workflow stoi na `czlowiek`, `make zatwierdz W=<wf>` zapisuje `human.approved{by}`.
- [ ] Kyverno odrzuca `Agent` z etykietą `fabryka.dev/rola=wykonawca` i narzędziem innym niż `warsztat` (`kubectl apply` pliku `platforma/kyverno/test/zly-agent.yaml` → błąd).
- [ ] Commit, tag `lekcja-09`.

## Task 10: Lekcja 10, ślad i hala

**Files:** `platforma/linia/fabryka.yaml` (krok `ksiega`: merge, verify, karta, cosign), `sdlc/ledger.py`, `sdlc/factory.py card`, `scripts/klucze-cosign.sh`, `Makefile` (`ksiega-verify`, `hala`, `slady`), `platforma/kagent/values.yaml` (OTel on), `warsztat/lekcja-10-slad.md`, `warsztat/prowadzacy.md`, `warsztat/slajdy.html`, `warsztat/mail-setup.md`, `README.md`.

- [ ] `make odbierz` → `ledger.jsonl`, `ledger.sigstore.json`; `make ksiega-verify F=...` OK; po edycji: łańcuch pęka i podpis nie pasuje.
- [ ] Jaeger pokazuje ślad `wykonawca` (LLM + narzędzia).
- [ ] Commit, tag `lekcja-10`, `main` = `lekcja-10`.

## Zamknięcie

- [ ] `scripts/restack.sh` na tagach; `make lekcja N=3` przetestowane.
- [ ] Wszystkie tagi: `make doctor`; od 5: `make replay Z=rabat`.
- [ ] Pamięć: zaktualizować `confitura-2026-agentic-sdlc-workshop.md`.
