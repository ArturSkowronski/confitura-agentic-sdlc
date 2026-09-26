"""Fabryka na GitHubie (finał): issue jest zleceniem, PR jest wynikiem. Tylko biblioteka standardowa.

GitHub stoi po obu stronach linii, a linia zostaje w Argo:

  issue z etykietą `fabryka`  → CronWorkflow `fabryka-ciagnie` bierze najstarsze (fabryka ciągnie, nie pcha)
  przyjęcie odrzuca           → komentarz z pytaniami pod issue, etykieta fabryka:odeslane
  lights-out | człowiek       → PR z opisem, kartą, księgą i pierwszym review fabryki; lights-out włącza auto-merge
  andon albo awaria linii     → komentarz pod issue, etykieta fabryka:andon

Token (GH_TOKEN) i repo (GH_REPO=owner/nazwa) widzą tylko kroki, które rozmawiają z GitHubem. Kroki, które
budują kod agenta, nie mają ani tokena, ani klucza cosign. Git dostaje token nagłówkiem, nigdy w URL-u.

Każdy uczestnik pracuje na swoim forku: GH_REPO to fork, PR-y idą do main forka.

Użycie:
  python3 sdlc/github.py fork                                      # przygotuj fork: issues, actions, auto-merge,
                                                                   # etykiety, ochrona main, klucz cosign na main
  python3 sdlc/github.py etykiety                                  # załóż etykiety fabryki w repo
  python3 sdlc/github.py issue rabat                               # issue ze zlecenia zlecenia/rabat.md
  python3 sdlc/github.py ciagnij                                   # weź najstarsze issue do linii
  python3 sdlc/github.py zlecenie --issue 12                       # JSON {name, title, body, issue, url}
  python3 sdlc/github.py git fetch -q {remote} main                # git z tokenem w nagłówku
  python3 sdlc/github.py odeslij --issue 12 --file intake.md
  python3 sdlc/github.py andon --issue 12 --file andon.md
  python3 sdlc/github.py pr --issue 12 --out /work/out/issue-12/proba-2 --decision lights-out
  python3 sdlc/github.py koniec --issue 12 --status Failed        # onExit: issue nie zostaje „w toku”
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

import slad
import zlecenia
from lib import ROOT, outputs

API = os.environ.get("GITHUB_API", "https://api.github.com")
LABELS = {
    "fabryka": ("0e8a16", "Zlecenie dla fabryki: linia weźmie je sama"),
    "fabryka:w-toku": ("fbca04", "Linia pracuje nad zleceniem"),
    "fabryka:odeslane": ("d93f0b", "Przyjęcie odesłało zlecenie z pytaniami"),
    "fabryka:andon": ("b60205", "Linia stanęła, decyduje człowiek"),
    "fabryka:pr": ("1d76db", "Zlecenie ma PR od fabryki"),
    "fabryka:lights-out": ("5319e7", "PR bez człowieka: merge po zielonych bramkach GitHuba"),
    "fabryka:czlowiek": ("fbca04", "PR czeka na review człowieka (ryzyko albo review blokujące)"),
}
# Nazwy jobów z .github/workflows/fabryka.yml: wymagane checki na main, od nich zależy auto-merge.
CHECKS = ["bramki", "wyrocznia", "review", "pochodzenie"]
COSIGN_PUB = "platforma/linia/cosign/cosign.pub"
BUSY = {"fabryka:w-toku", "fabryka:odeslane", "fabryka:andon", "fabryka:pr"}
REVIEW_MARKER = "<!-- fabryka-review -->"


def repo() -> str:
    value = os.environ.get("GH_REPO", "")
    if not re.fullmatch(r"[\w.-]+/[\w.-]+", value):
        sys.exit("GH_REPO musi mieć postać owner/repo (make github)")
    return value


def call(method: str, path: str, data: dict | None = None, *, ok_missing: bool = False):
    url = path if path.startswith("http") else f"{API}{path}"
    request = urllib.request.Request(url, method=method, data=json.dumps(data).encode() if data is not None else None,
                                     headers={"Authorization": f"Bearer {os.environ['GH_TOKEN']}",
                                              "Accept": "application/vnd.github+json",
                                              "X-GitHub-Api-Version": "2022-11-28",
                                              "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            body = response.read()
    except urllib.error.HTTPError as err:
        if ok_missing and err.code == 404:
            return None
        body = err.read()[:300]
        if err.code == 403 and b"not accessible by integration" in body:
            raise SystemExit("GitHub odmówił (403): to token codespace'a, który nie zmienia ustawień repo.\n"
                             "Zaloguj się swoim kontem: env -u GITHUB_TOKEN gh auth login -h github.com -s repo,workflow\n"
                             "Potem jeszcze raz: make github") from err
        raise RuntimeError(f"GitHub {method} {path}: HTTP {err.code} {body!r}") from err
    return json.loads(body) if body else None


def graphql(query: str, variables: dict) -> dict:
    result = call("POST", f"{API}/graphql", {"query": query, "variables": variables})
    if result.get("errors"):
        raise RuntimeError("; ".join(e.get("message", "?") for e in result["errors"]))
    return result["data"]


# ---------------------------------------------------------------- issue → zlecenie

def ensure_labels() -> list[str]:
    existing = {l["name"] for l in call("GET", f"/repos/{repo()}/labels?per_page=100")}
    created = []
    for name, (color, description) in LABELS.items():
        if name not in existing:
            call("POST", f"/repos/{repo()}/labels", {"name": name, "color": color, "description": description})
            created.append(name)
    return created


def pick(issues: list[dict]) -> dict | None:
    """Najstarsze otwarte issue z etykietą `fabryka`, którego linia jeszcze nie dotknęła. PR-y to też issues: pomijamy."""
    for issue in sorted(issues, key=lambda i: i["number"]):
        labels = {l["name"] for l in issue.get("labels", [])}
        if "pull_request" not in issue and "fabryka" in labels and not labels & BUSY:
            return issue
    return None


def label(issue: int, add: list[str] = (), remove: list[str] = ()) -> None:
    if add:
        call("POST", f"/repos/{repo()}/issues/{issue}/labels", {"labels": list(add)})
    for name in remove:
        call("DELETE", f"/repos/{repo()}/issues/{issue}/labels/{urllib.request.quote(name)}", ok_missing=True)


def comment(issue: int, body: str) -> None:
    call("POST", f"/repos/{repo()}/issues/{issue}/comments", {"body": body})


def order(issue: dict) -> dict:
    """Issue w formacie zlecenia: tytuł to tytuł, treść to kryteria. Przyjęcie (intake.py) sprawdza je tak samo jak plik."""
    return {"name": f"issue-{issue['number']}", "title": issue["title"].strip(), "body": (issue.get("body") or "").strip(),
            "issue": issue["number"], "url": issue["html_url"]}


def issue_from_file(name: str) -> dict:
    local = zlecenia.load(name)
    return call("POST", f"/repos/{repo()}/issues", {"title": local["title"], "body": local["body"], "labels": ["fabryka"]})


def prepare_fork() -> list[str]:
    """Fork ma domyślnie wyłączone issues i Actions. Włączamy to, czego fabryka potrzebuje, i mówimy, czego się nie dało."""
    notes = []
    call("PATCH", f"/repos/{repo()}", {"has_issues": True, "allow_auto_merge": True, "allow_merge_commit": True,
                                      "delete_branch_on_merge": True})
    notes.append("issues, auto-merge i merge commit włączone")
    try:
        call("PUT", f"/repos/{repo()}/actions/permissions", {"enabled": True, "allowed_actions": "all"})
        notes.append("GitHub Actions włączone")
    except RuntimeError as err:
        notes.append(f"⚠️ Actions: włącz ręcznie w zakładce Actions forka ({err})")
    created = ensure_labels()
    notes.append(f"etykiety: {', '.join(created) or 'już były'}")
    notes.append(sync_cosign_pub())  # przed ochroną main: to jedyny zapis na main poza PR-ami
    try:
        call("PUT", f"/repos/{repo()}/branches/main/protection", {
            "required_status_checks": {"strict": False, "contexts": CHECKS}, "enforce_admins": False,
            "required_pull_request_reviews": None, "restrictions": None})
        notes.append(f"main chroniony: merge tylko po zielonych {', '.join(CHECKS)}")
    except RuntimeError as err:
        notes.append(f"⚠️ ochrona main nie wyszła ({err}); bez niej auto-merge nie czeka na bramki")
    return notes


def sync_cosign_pub() -> str:
    """Job `pochodzenie` sprawdza podpis kluczem z main forka. Klucz powstał w Twoim klastrze, więc musi tam trafić."""
    local = ROOT / COSIGN_PUB
    if not local.exists():
        return "⚠️ brak lokalnego klucza cosign: make klucze-cosign, potem make github"
    remote = call("GET", f"/repos/{repo()}/contents/{COSIGN_PUB}?ref=main", ok_missing=True)
    content = local.read_bytes()
    if remote and base64.b64decode(remote["content"]) == content:
        return "klucz cosign na main forka = klucz Twojego klastra"
    call("PUT", f"/repos/{repo()}/contents/{COSIGN_PUB}", {
        "message": "fabryka: klucz publiczny księgi z mojego klastra", "branch": "main",
        "content": base64.b64encode(content).decode(), **({"sha": remote["sha"]} if remote else {})})
    return "klucz cosign Twojego klastra wgrany na main forka (commit przez API, tylko ten plik)"


# ---------------------------------------------------------------- git z tokenem

def git(*args: str) -> int:
    """git z tokenem w nagłówku HTTP (jak actions/checkout). `{remote}` w argumentach to adres repo na GitHubie."""
    auth = base64.b64encode(f"x-access-token:{os.environ['GH_TOKEN']}".encode()).decode()
    remote = f"https://github.com/{repo()}.git"
    command = ["git", "-c", f"http.https://github.com/.extraheader=AUTHORIZATION: basic {auth}",
               "-c", "core.hooksPath=/dev/null", "-c", "core.fsmonitor=false",
               *[a.replace("{remote}", remote) for a in args]]
    return subprocess.run(command).returncode


# ---------------------------------------------------------------- wynik → PR

def _read(folder: Path, name: str) -> str:
    path = folder / name
    return path.read_text(encoding="utf-8").strip() if path.exists() else ""


def pr_body(out: Path, issue: int, decision: str, zlecenie: str, trace_url: str, run_url: str) -> str:
    """Opis PR: po co (issue), co (opis agenta), jak przeszło (karta), gdzie ślad. Review idzie osobno jako review PR."""
    closes = f"Closes #{issue}" if decision in ("lights-out", "człowiek", "czeka") else f"Zlecenie #{issue}"
    who = ("🌑 **lights-out**: merge sam, gdy bramki GitHuba będą zielone." if decision == "lights-out" else
           "👤 **Czeka na człowieka**: ryzyko albo review blokujące. Zatwierdź albo odrzuć w tym PR.")
    links = [f"[ślad w Jaegerze]({trace_url})" if trace_url else "", f"[przebieg w hali]({run_url})" if run_url else "",
             f"księga: `.fabryka/{zlecenie}/ledger.jsonl` (podpis cosign obok, weryfikuje job `pochodzenie`)"]
    return "\n\n".join(p for p in [
        f"{closes}. {who}",
        _read(out, "opis.md"),
        _read(out, "karta.md"),
        " · ".join(l for l in links if l),
        "<sub>PR wystawiła fabryka. Kod pisał agent `wykonawca`, bramki są w klastrze i w GitHub Actions.</sub>",
    ] if p)


def review_comments(sarif: dict, changed: set[str]) -> list[dict]:
    """Znaleziska z SARIF-a jako komentarze w linii, tylko w plikach zmiany (GitHub odrzuca resztę)."""
    comments = []
    for run in sarif.get("runs", []):
        for result in run.get("results", []):
            for location in result.get("locations", [])[:1]:
                physical = location.get("physicalLocation", {})
                path = physical.get("artifactLocation", {}).get("uri", "")
                line = physical.get("region", {}).get("startLine")
                if path in changed and line:
                    level = {"error": "🚫", "warning": "⚠️"}.get(result.get("level"), "💡")
                    comments.append({"path": path, "line": line, "side": "RIGHT",
                                     "body": f"{level} **{result.get('ruleId', '')}** {result['message']['text']}"})
    return comments[:20]


def post_review(number: int, review_md: str, sarif: dict, changed: set[str]) -> None:
    """Pierwsze review od fabryki jako review PR (COMMENT, nie APPROVE: decyzję zostawiamy bramkom i człowiekowi)."""
    body = f"{REVIEW_MARKER}\n{review_md or 'Review fabryki: brak raportu.'}"
    comments = review_comments(sarif, changed)
    try:
        call("POST", f"/repos/{repo()}/pulls/{number}/reviews", {"event": "COMMENT", "body": body, "comments": comments})
    except RuntimeError as err:
        if not comments:
            raise
        print(f"review w linii odrzucone ({err}), wysyłam samo podsumowanie", file=sys.stderr)
        call("POST", f"/repos/{repo()}/pulls/{number}/reviews", {"event": "COMMENT", "body": body})


def open_pr(branch: str, title: str, body: str, draft: bool = False) -> dict:
    owner = repo().split("/")[0]
    existing = call("GET", f"/repos/{repo()}/pulls?state=open&head={owner}:{urllib.request.quote(branch)}")
    if existing:
        return call("PATCH", f"/repos/{repo()}/pulls/{existing[0]['number']}", {"title": title, "body": body})
    return call("POST", f"/repos/{repo()}/pulls", {"title": title, "head": branch, "base": "main", "body": body, "draft": draft})


def auto_merge(pr: dict) -> str:
    try:
        graphql("mutation($id: ID!) { enablePullRequestAutoMerge(input: {pullRequestId: $id, mergeMethod: MERGE}) "
                "{ pullRequest { number } } }", {"id": pr["node_id"]})
        return "auto-merge włączony: merge po zielonych wymaganych bramkach"
    except RuntimeError as err:
        return f"auto-merge niedostępny ({err}). Włącz „Allow auto-merge” i ochronę main z wymaganymi checkami"


def publish(issue: int, out: Path, decision: str, zlecenie: str, trace_url: str, run_url: str) -> dict:
    title = json.loads((ROOT / ".sdlc" / "zlecenie.json").read_text(encoding="utf-8"))["title"]
    branch = f"agent/{zlecenie}"
    body = pr_body(out, issue, decision, zlecenie, trace_url, run_url)
    pr = open_pr(branch, title, body)
    changed = {f["filename"] for f in call("GET", f"/repos/{repo()}/pulls/{pr['number']}/files?per_page=100")}
    sarif_path = out / "review.sarif"
    post_review(pr["number"], _read(out, "review-1-ryzyko.md") + "\n\n" + _read(out, "review-2-review.md"),
                json.loads(sarif_path.read_text(encoding="utf-8")) if sarif_path.exists() else {}, changed)
    decided = "fabryka:lights-out" if decision == "lights-out" else "fabryka:czlowiek"
    label(pr["number"], add=[decided])
    label(issue, add=["fabryka:pr"], remove=["fabryka:w-toku"])
    merge = auto_merge(pr) if decision == "lights-out" else "merge po review człowieka"
    comment(issue, f"🏭 Fabryka wystawiła {pr['html_url']} ({decision}). {merge}.")
    print(f"PR: {pr['html_url']} ({decision}). {merge}")
    return pr


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("fork")
    sub.add_parser("etykiety")
    sub.add_parser("ciagnij")
    i = sub.add_parser("issue")
    i.add_argument("name")
    z = sub.add_parser("zlecenie")
    z.add_argument("--issue", type=int, required=True)
    g = sub.add_parser("git")
    g.add_argument("args", nargs=argparse.REMAINDER)
    for name in ("odeslij", "andon"):
        s = sub.add_parser(name)
        s.add_argument("--issue", type=int, required=True)
        s.add_argument("--file", required=True)
    p = sub.add_parser("pr")
    p.add_argument("--issue", type=int, required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--decision", required=True)
    k = sub.add_parser("koniec")
    k.add_argument("--issue", type=int, required=True)
    k.add_argument("--status", required=True)
    args = parser.parse_args()

    trace_url = slad.url(slad.Step().trace_id)
    run = os.environ.get("FABRYKA_RUN", "")
    run_url = f"{os.environ.get('FABRYKA_HALA', 'http://localhost:2746')}/workflows/fabryka/{run}" if run else ""

    if args.cmd == "fork":
        print("\n".join(f"  {n}" for n in prepare_fork()))
    elif args.cmd == "etykiety":
        print("etykiety:", ", ".join(ensure_labels()) or "wszystkie już są")
    elif args.cmd == "issue":
        created = issue_from_file(args.name)
        print(f"issue #{created['number']}: {created['html_url']}")
    elif args.cmd == "ciagnij":
        issue = pick(call("GET", f"/repos/{repo()}/issues?state=open&labels=fabryka&per_page=100"))
        if not issue:
            print("brak nowych zleceń z etykietą fabryka")
            outputs(issue="")
            return
        label(issue["number"], add=["fabryka:w-toku"])
        print(f"biorę #{issue['number']}: {issue['title']}")
        outputs(issue=str(issue["number"]))
    elif args.cmd == "zlecenie":
        print(json.dumps(order(call("GET", f"/repos/{repo()}/issues/{args.issue}")), ensure_ascii=False, indent=2))
    elif args.cmd == "git":
        sys.exit(git(*args.args))
    elif args.cmd == "odeslij":
        comment(args.issue, "↩️ Fabryka nie przyjęła zlecenia. Uzupełnij opis i zdejmij etykietę "
                "`fabryka:odeslane`, a linia weźmie je ponownie.\n\n" + Path(args.file).read_text(encoding="utf-8"))
        label(args.issue, add=["fabryka:odeslane"], remove=["fabryka:w-toku"])
    elif args.cmd == "andon":
        link = f"\n\n[Ślad przebiegu]({trace_url}) · [hala]({run_url})" if trace_url else ""
        comment(args.issue, "🚨 **Andon**: linia stanęła, fabryka nie zgaduje dalej.\n\n"
                + Path(args.file).read_text(encoding="utf-8") + link)
        label(args.issue, add=["fabryka:andon"], remove=["fabryka:w-toku"])
    elif args.cmd == "pr":
        publish(args.issue, Path(args.out), args.decision, f"issue-{args.issue}", trace_url, run_url)
    elif args.cmd == "koniec":
        labels = {l["name"] for l in call("GET", f"/repos/{repo()}/issues/{args.issue}/labels")}
        if "fabryka:w-toku" in labels:
            comment(args.issue, f"🚨 Linia skończyła się stanem `{args.status}` bez decyzji fabryki. "
                    f"Sprawdź [przebieg]({run_url})" + (f" i [ślad]({trace_url})." if trace_url else "."))
            label(args.issue, add=["fabryka:andon"], remove=["fabryka:w-toku"])


if __name__ == "__main__":
    main()
