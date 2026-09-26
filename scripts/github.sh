#!/usr/bin/env bash
# Finał: podłącz fabrykę do Twojego forka na GitHubie.
#   1. fork: issues, Actions, auto-merge, etykiety fabryki, ochrona main (wymagane checki), klucz cosign na main
#   2. Secret fabryka-github w klastrze (token i repo) dla kroków linii, które rozmawiają z GitHubem
#   3. CronWorkflow fabryka-ciagnie: co dwie minuty bierze najstarsze issue z etykietą `fabryka`
# Repo: GH_REPO albo origin. Token: GH_TOKEN albo `gh auth token` (scope repo wystarczy).
set -euo pipefail
cd "$(dirname "$0")/.."
if [ -z "${GH_REPO:-}" ]; then
  url=$(git remote get-url origin 2>/dev/null || true)
  GH_REPO=$(printf '%s' "$url" | sed -nE 's#^(https://github\.com/|git@github\.com:)([^/]+/[^/.]+)(\.git)?$#\2#p')
fi
[ -n "${GH_REPO:-}" ] || { echo "Nie znam Twojego forka. Ustaw origin na fork albo podaj: make github GH_REPO=login/confitura-agentic-sdlc"; exit 1; }
if [ -z "${GH_TOKEN:-}" ]; then
  command -v gh >/dev/null || { echo "Brak GH_TOKEN i brak gh. Zaloguj się: gh auth login, albo podaj GH_TOKEN (fine-grained: contents, issues, pull requests, administration)"; exit 1; }
  if [ "${CODESPACES:-}" = true ]; then
    # W codespace gh domyślnie bierze GITHUB_TOKEN codespace'a. To token integracji: wypchnie kod i założy issue,
    # ale nie zmieni ustawień repo (HTTP 403 „Resource not accessible by integration”). Bierzemy Twoje logowanie gh.
    GH_TOKEN=$(env -u GITHUB_TOKEN -u GH_TOKEN gh auth token 2>/dev/null || true)
    if [ -z "$GH_TOKEN" ]; then
      cat <<'MSG'
W Codespaces make github potrzebuje Twojego logowania gh, nie tokenu codespace'a (ten nie zmienia ustawień repo).
Zaloguj się raz w tym terminalu (kod z terminala wpisujesz na github.com/login/device):

  env -u GITHUB_TOKEN gh auth login -h github.com -s repo,workflow

Potem jeszcze raz: make github
MSG
      exit 1
    fi
  else
    GH_TOKEN=$(gh auth token)
  fi
fi
export GH_REPO GH_TOKEN
echo "Fork: https://github.com/$GH_REPO"
python3 sdlc/github.py fork
kubectl create secret generic fabryka-github -n fabryka --from-literal=GH_TOKEN="$GH_TOKEN" --from-literal=GH_REPO="$GH_REPO" \
  --dry-run=client -o yaml | kubectl apply -f - >/dev/null
kubectl apply -f platforma/github/ciagnij.yaml >/dev/null
echo "Klaster: Secret fabryka-github i CronWorkflow fabryka-ciagnie gotowe."
echo "Zlecenie: make issue Z=rabat (albo załóż issue z etykietą fabryka). Fabryka weźmie je w ciągu dwóch minut; od razu: make ciagnij"
