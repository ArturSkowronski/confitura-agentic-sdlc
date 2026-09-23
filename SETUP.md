# Setup przed warsztatem (około 20 minut)

Zrób to w domu albo w biurze, nie na konferencyjnym Wi-Fi. Na koniec `make doctor` ma być
zielony. Klaster działa na Twoim laptopie; na sali potrzebujesz sieci tylko do modelu.

## Potrzebujesz

- laptopa z 16 GB RAM, na którym możesz instalować programy,
- Dockera (Docker Desktop, OrbStack albo Colima) z co najmniej 6 GB pamięci dla kontenerów,
- `git`, `make`, `python3` (3.10+), `java` 21 i `mvn`,
- narzędzi klastra: `kind`, `kubectl`, `helm`, `argo`, `cosign`.

- konta na GitHubie i `gh` (finał warsztatu pracuje na Twoim forku).

macOS z Homebrew:

```bash
brew install kind kubectl helm argo cosign maven openjdk@21 gh
```

Linux: każde z tych narzędzi ma binarkę do pobrania w releasach na GitHubie. Windows: użyj WSL2.

Model językowy nie jest potrzebny. Klucz dostaniesz na miejscu; do tego czasu linia działa
w trybie replay (nagrane zmiany zamiast modelu).

## Kroki

1. Zrób fork https://github.com/ArturSkowronski/confitura-agentic-sdlc na swoim koncie i sklonuj fork:
   `git clone https://github.com/<login>/confitura-agentic-sdlc`
2. Wejdź do katalogu: `cd confitura-agentic-sdlc` i zaloguj się do GitHuba: `gh auth login`
3. Postaw klaster: `make klaster` (pierwszy raz 5 do 10 minut, ciągnie obrazy).
4. Zbuduj obrazy fabryki: `make setup` (kilka minut, od lekcji 2).
5. Sprawdź: `make doctor`. Wszystko ma być zielone.
6. Zapytaj agenta: `make a2a A=probny T="Przedstaw się"`. Bez klucza dostaniesz błąd modelu i to jest OK.

## Co robi `make klaster`

- tworzy klaster kind `fabryka` z portami UI na localhost (2746 Argo, 8082 i 8083 kagent, 16686 Jaeger),
- instaluje Argo Workflows (linia), kagent 0.10.1 (agenci), Kyverno (polityka) i Jaegera (ślady),
- tworzy ModelConfig `fabryka-model` i agenta `probny`.

Wszystko jest w Twoim Dockerze. Po warsztacie: `kind delete cluster --name fabryka`.

## Jeśli coś nie działa

- `kind create cluster` wisi: Docker ma za mało pamięci. Ustaw 6 GB i spróbuj ponownie.
- `helm` na macOS mówi o keychain: uruchom raz `docker login ghcr.io` albo zaloguj się do
  keychaina i ponów `make klaster`.
- Pody `kagent-controller` restartują się kilka razy na starcie: czekają na Postgresa, to normalne.
- Czerwony `make doctor`: odpisz mi na maila z wynikiem.
