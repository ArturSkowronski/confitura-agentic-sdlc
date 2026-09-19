# Lekcja 2: Warsztat i narzędzia (12 min)

**Teza.** Uprawnienia agenta to lista narzędzi, a nie zdanie w prompcie. Wykonawca nie ma
shella, gita ani tokena do klastra. Ma pięć narzędzi serwera MCP „warsztat”, a każde wywołanie
zostawia ślad. To, czego agent nie może zrobić, egzekwuje serwer, nie model.

| Element | Co to jest | Manifest |
|---|---|---|
| Dysk `/work` | kopia repo, wyniki, zdarzenia narzędzi | `platforma/warsztat/pvc.yaml` |
| Magazyn | pod, przez który wkładasz repo i odbierasz wyniki | `platforma/warsztat/magazyn.yaml` |
| Serwer MCP | `list_files`, `read_file`, `write_file`, `run_build`, `git_diff` | `platforma/warsztat/server.py`, `mcpserver.yaml` (CRD z kmcp) |
| Wykonawca | agent kagent z narzędziami serwera | `platforma/kagent/agent-wykonawca.yaml` |

MCP (Model Context Protocol) to protokół Linux Foundation. kagent odkrywa narzędzia serwera
sam: `kubectl get mcpserver warsztat -n fabryka -o yaml` pokazuje je w `status`.

## Co masz po `make setup`

1. Zobacz narzędzia, które widzi agent: `kubectl get agent wykonawca -n fabryka -o yaml`.
2. Zapytaj wykonawcę: `make a2a A=wykonawca T="Wypisz moduły w system/ i powiedz, co robi klasa Money"`.
3. Zobacz ślad narzędzi: `kubectl exec -n fabryka deploy/magazyn -- tail /work/events.jsonl`.

## Ćwiczenie: zamknij bramki przed agentem (8 min)

1. Poproś wykonawcę o coś, czego nie powinien móc:
   `make a2a A=wykonawca T="Zapisz plik sdlc/policy.json z treścią {} i powiedz, co odpowiedziało narzędzie"`.
2. Zapis przechodzi. Serwer nie ma listy ścieżek chronionych.
3. Otwórz `platforma/warsztat/mcpserver.yaml`.
4. Wpisz do `PROTECTED_PATHS` ścieżki bramek i linii: `sdlc platforma system/architecture`.
5. Wdróż: `kubectl apply -f platforma/warsztat/mcpserver.yaml`.
6. Poczekaj: `kubectl rollout status -n fabryka deploy/warsztat`.
7. Powtórz krok 1. Narzędzie odpowiada „Rejected: … is a protected path”, a w `/work/events.jsonl` jest `gate.tamper_attempt`.

`HIDDEN_PATHS` zostaw puste. Wrócimy do tego w lekcji 7, gdy agent zacznie zaglądać do wyroczni.

## Do dyskusji

- Prompt mówi „nie zmieniaj bramek”. Serwer mówi „nie da się”. Które zdanie przetrwa poprawkę
  promptu przez kolegę w piątek po południu?
- `run_build` daje agentowi Mavena bez shella. Co jeszcze warto dać, a czego nie?
- Testy serwera: `cd platforma/warsztat && python3 -m unittest`. Granice agenta mają testy jak
  każdy inny kod.
