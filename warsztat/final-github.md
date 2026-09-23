# Finał: fabryka na GitHubie (12 min)

**Teza.** Wszystko, co zbudowałeś, działa tak samo, gdy zlecenie przychodzi z GitHuba, a wynik tam wraca.
Linia zostaje w klastrze. GitHub stoi po obu stronach: issue to zlecenie, PR to wynik, a Actions to
druga warstwa bramek, której agent nie dotknie. Każdy PR ma księgę, podpis i ślad, więc da się sprawdzić,
skąd przyszedł kod, zanim trafi do `main`.

```
issue (etykieta fabryka) ─▶ fabryka-ciagnie ─▶ linia w Argo ─▶ PR na Twoim forku ─▶ Actions ─▶ merge
   │  co 2 min, najstarsze      przyjęcie, agent,     opis, karta, księga,   bramki, wyrocznia,   lights-out: sam
   │  (fabryka ciągnie)         bramki, decyzja       review fabryki         review, pochodzenie  człowiek: Ty
   └◀── komentarz: pytania (odesłane) albo andon ◀──┘
                     ślad: Jaeger, od węzła Argo po wywołanie modelu i narzędzia
```

| Element | Gdzie |
|---|---|
| Issue → przebieg | `platforma/github/ciagnij.yaml` (CronWorkflow), `sdlc/github.py ciagnij` |
| Przebieg → PR | krok `github` w `platforma/linia/fabryka.yaml`, `sdlc/github.py pr` |
| Bramki na GitHubie | `.github/workflows/fabryka.yml`: `bramki`, `wyrocznia`, `review`, `pochodzenie` |
| Pochodzenie | `sdlc/pochodzenie.py`: łańcuch księgi, podpis cosign, commit z księgi = kod PR, granice agenta |
| Ślad | Argo (trace przebiegu) → `sdlc/slad.py` (kroki, narzędzia) → kagent (agent, model) → Jaeger |

## Przed finałem (w domu, razem z SETUP.md)

1. Zrób fork `ArturSkowronski/confitura-agentic-sdlc` na swoim koncie i ustaw go jako `origin`:
   `git remote set-url origin https://github.com/<login>/confitura-agentic-sdlc`.
2. Zaloguj się: `gh auth login` (zakres `repo` wystarczy).

## Co masz

1. Podłącz fork: `make github`. Skrypt włącza w forku issues, Actions i auto-merge, zakłada etykiety,
   chroni `main` czterema checkami, wgrywa klucz cosign Twojego klastra na `main`, a w klastrze tworzy
   Secret `fabryka-github` i poller `fabryka-ciagnie`.
2. Zleć rabat: `make issue Z=rabat`. Otwórz issue na GitHubie.
3. Nie czekaj na crona: `make ciagnij` (bez modelu: `make ciagnij AGENT=replay`). W hali pojawia się
   `fabryka-issue-<n>-…`, a issue dostaje etykietę `fabryka:w-toku`.
4. Po kilku minutach w forku jest PR. Zobacz w nim:
   - opis agenta i kartę zlecenia z linkiem do śladu,
   - review fabryki jako review PR, ze znaleziskami w liniach kodu,
   - commit `fabryka: księga zlecenia`, czyli `.fabryka/issue-<n>/` z księgą i podpisem,
   - cztery checki z Actions. Po zielonych auto-merge scala PR, a `Closes #<n>` zamyka issue.
5. Kliknij link do śladu. Jeden trace: przebieg Argo, kroki fabryki (`próba 1 · wykonawca`), pod nim agent
   (`invoke_agent`, `generate_content`, `execute_tool`) i narzędzia warsztatu (`warsztat · write_file …`).
   Odrzucone próby agenta (✋) są na czerwono.

## Ćwiczenie: pochodzenie (6 min)

1. Zleć zwroty: `make issue Z=zwroty-czesciowe`, potem `make ciagnij`. Payments to ścieżka krytyczna, więc PR
   dostaje `fabryka:czlowiek` i czeka na Ciebie bez auto-merge.
2. Zanim go zatwierdzisz, dopisz ręcznie jedną linię do kodu na gałęzi agenta:
   `git fetch origin && git switch agent/issue-<n>`, zmień dowolny plik w `system/`, potem `git commit -am "szybka poprawka" && git push`.
3. Patrz na check `pochodzenie`: jest czerwony, a w podsumowaniu jobu masz komunikat
   „po commicie z księgi zmieniono kod”. Kod w PR nie jest już tym, który przeszedł bramki w klastrze.
4. Cofnij swoją zmianę (`git revert HEAD && git push`). `pochodzenie` wraca na zielono. Teraz zatwierdź PR jako człowiek.

Druga próba, jeśli masz czas: `make issue Z=anulowanie`. Przyjęcie odsyła zlecenie z pytaniami agenta
w komentarzu pod issue. Dopisz `Kryteria:` w opisie issue i zdejmij etykietę `fabryka:odeslane`,
a linia weźmie zlecenie jeszcze raz.

## Do dyskusji

- Actions biorą bramki i narzędzia z `main`, a nie z PR. Agent może zaproponować nową regułę ArchUnit,
  ale obowiązuje ona dopiero po merge'u przez człowieka. To teza lekcji 10, tylko egzekwowana przez GitHuba.
- Token GitHuba widzą tylko kroki `krok-github`, a klucz cosign tylko krok księgi. Krok, który buduje
  i testuje kod agenta, nie ma żadnego sekretu. Sprawdź to: `kubectl get workflowtemplate fabryka -n fabryka -o yaml | grep -B3 secretKeyRef`.
- Klaster nie przyjmie webhooka z internetu, więc fabryka odpytuje GitHuba co dwie minuty. W firmie zamienisz
  to na webhook albo GitHub App. Model „fabryka ciągnie, jedno zlecenie naraz” zostaje.

## Znane ograniczenia

- Jaeger all-in-one trzyma ślady w pamięci: restart poda je kasuje. Link w PR działa tylko na Twoim laptopie.
- Jedno zlecenie z GitHuba naraz (wspólny dysk `/work`). Ręczne `make zlecenie` w tym samym czasie popsuje przebieg.
- Bez sieci ten finał nie działa. Plan B: `make zlecenie Z=… AGENT=replay` i wynik z `make odbierz`.
