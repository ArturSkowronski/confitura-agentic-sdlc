# Start: od forka do działającej fabryki

Masz dwie drogi. Obie kończą się tym samym klastrem i tymi samymi komendami.

## A. W przeglądarce: GitHub Codespaces (polecana)

Nic nie instalujesz na laptopie. Codespaces jest darmowy dla kont GitHub Free: 120 core-godzin
i 15 GB w miesiącu, czyli 30 godzin pracy na maszynie 4-rdzeniowej. Po wyczerpaniu limitu bez karty
GitHub blokuje dalsze użycie, nie wystawia rachunku.

1. Zrób fork https://github.com/ArturSkowronski/confitura-agentic-sdlc na swoim koncie.
2. Na forku: **Code → Codespaces → Create codespace on main**. Maszyna 4-rdzeniowa, 16 GB.
   Kontener buduje się około 5 minut i sam instaluje kind, argo, cosign, Javę, Mavena, gh, Claude Code
   i narzędzie `fabryka`.
3. W terminalu codespace'a: `fabryka start` (pierwszy raz około 10 minut).
4. `fabryka lekcja 1` i jedziesz.

Hala (Argo), Jaeger i dashboard kagent są w zakładce **PORTS** (2746, 16686, 8082). Codespace
zasypia po 30 minutach bezczynności. Po warsztacie usuń go w github.com/codespaces.

### A2. To samo z terminala: `gh`

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

## B. Na laptopie

1. Fork i klon forka, narzędzia z [SETUP.md](../SETUP.md).
2. `make narzedzia` (instaluje `fabryka` w `~/.local/bin` i komendę `/fabryka-autopilot` w Claude Code).
3. `fabryka start`, potem `fabryka lekcja 1`.

## Jak się poruszać

| Komenda | Co robi |
|---|---|
| `fabryka lekcja N` | repo na tagu `lekcja-NN` (Twoje zmiany idą do `git stash`) i klaster w stanie tej lekcji |
| `fabryka mapa` | które bloczki fabryki działają: od agenta w klastrze po poller GitHuba |
| `fabryka sprawdz N` | czy ćwiczenie lekcji N jest zrobione; deterministycznie, bez modelu |
| `fabryka rozwiazanie N` | wstawia rozwiązanie (pliki z lekcji N+1) i wdraża je do klastra |
| `fabryka autopilot N` | prompt autopilota; w Claude Code po prostu `/fabryka-autopilot N` |
| `fabryka reset` | klaster od zera, gdy stan jest nie do odratowania |

Możesz zacząć od dowolnej lekcji. `fabryka lekcja 7` stawia repo na lekcji 7 z rozwiązaniami 1–6
i wdraża do klastra dokładnie to, co ta lekcja przewiduje. Ćwiczenie 7 czeka na Ciebie jako TODO.

## Bloczek po bloczku

| Lekcja | Bloczek, który się zapala | Rodzaj reguły |
|---|---|---|
| 1 | agent jako zasób w klastrze; agent przyjecie, który tylko pyta | słowo |
| 2 | serwer MCP z pięcioma narzędziami; ścieżki, do których agent nie zapisze | ściana |
| 3 | kontekst L1–L5; routing po własności pojęcia | kontekst |
| 4 | przyjęcie: bez kryteriów nie ma zlecenia | bramka |
| 5 | linia w Argo: przygotuj, przyjęcie, wykonawca, zmiana | ściana |
| 6 | bramki: ArchUnit, osłabianie testów, sekrety, mutacje | bramka |
| 7 | wyrocznia, której agent nie przeczyta | ściana |
| 8 | ryzyko, review z kryteriami, pętla poprawek | bramka |
| 9 | człowiek w linii (suspend), limit WIP, Kyverno na narzędzia | polityka |
| 10 | podpisana księga i jeden ślad zlecenia | ślad |
| finał | issue → linia → PR → GitHub Actions | integracja |

## Autopilot

Każda lekcja ma prompt dla Claude, który sam przestawia repo i klaster, robi ćwiczenie, sprawdza je
`fabryka sprawdz`, a gdy nie wychodzi, wstawia rozwiązanie i pokazuje różnicę. Na koniec mówi, który
bloczek się zapalił. Wszystkie prompty: [autopilot.md](autopilot.md). Zasada, której autopilot nie łamie:
niczego nie zatwierdza za człowieka.

Claude Code w codespace: uruchom `claude` i zaloguj się swoim kontem albo kluczem API. Klucz do modelu
dla samej fabryki (agenci w klastrze) dostajesz na sali: `make klucz`. Bez niego wszystko działa w replay.

## Gdy coś nie działa

- `fabryka start` pada na kind: za mała maszyna. Codespace 4-rdzeniowy z 16 GB to minimum.
- Przebiegi wiszą jako Pending: limit WIP 3 i jeden wspólny dysk. Poczekaj albo `argo stop -n fabryka --all`.
- Stan klastra jest dziwny po skakaniu między lekcjami w tył: `fabryka reset`.
