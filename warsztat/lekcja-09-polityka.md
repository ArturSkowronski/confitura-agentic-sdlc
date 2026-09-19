# Lekcja 9: Światło, WIP i polityka (12 min)

**Teza.** Człowiek to węzeł z rolą, a nie podatek płacony od każdej zmiany. Linię, za którą
zmiana czeka na człowieka, rysuje wersjonowany plik (`sdlc/policy.json`), a nie nastrój
reviewera. Lights-out dostaje tylko zmiana o niskim lub średnim ryzyku **i** pokryta
scenariuszami. Druga teza: fabryka ciągnie, nie pcha. Limit WIP wyznacza przepustowość ludzi
na końcu linii, a nie liczba agentów.

| Mechanizm | Gdzie | Projekt |
|---|---|---|
| Kto czeka na człowieka | `sdlc/policy.json` → `autonomy` | plik w repo |
| Czekanie na człowieka | krok `czlowiek` w linii: `suspend` + `make zatwierdz` | Argo Workflows |
| Limit WIP | `platforma/linia/wip.yaml`, semafor na przebiegu | Argo Workflows |
| Uprawnienia agentów | `platforma/kyverno/agent-narzedzia.yaml` | Kyverno `ValidatingPolicy` (CEL) |

## Ćwiczenie A: linia staje na człowieku (5 min)

1. Otwórz `platforma/linia/fabryka.yaml`, szablon `czlowiek`.
2. Zamień krok z TODO na krok `czekaj` (szablon `suspend`, wyjście `kto`).
3. Wdróż: `make linia`.
4. Uruchom zwroty: `make replay Z=zwroty-czesciowe`. Próba 2 staje na żółto w hali.
5. Zatwierdź: `make zatwierdz W=<nazwa przebiegu>`. Twoje imię trafia do śladu jako `human.approved`.

## Ćwiczenie B: wykonawca ma tylko warsztat (5 min)

1. Spróbuj wdrożyć złego agenta: `kubectl apply -f platforma/kyverno/test/zly-agent.yaml`. Przechodzi.
2. Otwórz `platforma/kyverno/agent-narzedzia.yaml`.
3. Zamień `expression: "true"` na wyrażenie CEL: dla etykiety `fabryka.dev/rola=wykonawca` każde
   narzędzie ma `type == 'McpServer'` i `mcpServer.name == 'warsztat'`.
4. Wdróż: `kubectl apply -f platforma/kyverno/agent-narzedzia.yaml`.
5. Powtórz krok 1. Kyverno odrzuca manifest z Twoim komunikatem. Posprzątaj: `kubectl delete -f platforma/kyverno/test/zly-agent.yaml --ignore-not-found`.

## Demo prowadzącego: fabryka ciągnie

Limit WIP to 3 (`platforma/linia/wip.yaml`). Czwarte zlecenie wisi jako `Pending` z komunikatem
o semaforze i rusza samo, gdy zwolni się miejsce, np. po Twoim `make zatwierdz`.

## Do dyskusji

- Agent nie ma tokena do klastra: krok `wykonawca` woła A2A, a agent widzi tylko warsztat.
  Polityka Kyverno pilnuje, żeby tak zostało po piątkowym „dodam mu jeszcze kubectl”.
- Kto w Twojej organizacji rysuje dziś linię „tu musi spojrzeć człowiek”? Gdzie jest ten plik?
