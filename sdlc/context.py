"""Warstwa kontekstu (stacja 1).

Zamiast kazać agentowi „odkrywać” repo przy każdym issue, kompilujemy wiedzę raz,
deterministycznie, z pięciu poziomów:

  L1 system       katalog modułów, zależności, blast radius   (module.json, pom.xml)
  L2 kod          konwencje i reguły architektury             (docs/conventions.md, ArchUnit)
  L3 organizacja  faktyczni właściciele, nie tylko nominalni   (git log, CODEOWNERS)
  L4 historia     decyzje architektoniczne                    (docs/adr)
  L5 operacje     incydenty                                   (ops/incidents)

Użycie:
  python3 sdlc/context.py index                 # .sdlc/index.json
  python3 sdlc/context.py agents-md             # AGENTS.md dla agenta
  python3 sdlc/context.py route --title T --body B [--out-md plik]
"""

from __future__ import annotations

import argparse
import re
from collections import Counter
from pathlib import Path

from lib import ROOT, STATE, git, outputs, load_json, modules, split_camel, summary_md, stem, tokens, write_json


# ---------------------------------------------------------------- L3: organizacja

def codeowners() -> dict[str, str]:
    owners = {}
    path = ROOT / "CODEOWNERS"
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip() and not line.startswith("#"):
            pattern, *who = line.split()
            owners[pattern.strip("/")] = " ".join(who)
    return owners


def real_owners(module_path: str, limit: int = 200) -> list[dict]:
    """Kto naprawdę zmienia ten moduł. Ten sam commit daje zawsze ten sam wynik."""
    try:
        authors = git("log", f"-{limit}", "--no-merges", "--format=%an", "--", module_path).split("\n")
    except RuntimeError:
        return []
    counts = Counter(a for a in authors if a and "[bot]" not in a)
    total = sum(counts.values()) or 1
    return [{"name": name, "commits": n, "share": round(n / total, 2)} for name, n in counts.most_common(3)]


def churn(module_path: str, days: int = 30) -> int:
    try:
        return len([l for l in git("log", f"--since={days}.days", "--format=%h", "--", module_path).splitlines() if l])
    except RuntimeError:
        return 0


# ---------------------------------------------------------------- L4/L5: historia i operacje

def documents(folder: str) -> list[dict]:
    docs = []
    for path in sorted((ROOT / folder).glob("*.md")):
        text = path.read_text(encoding="utf-8")
        title = text.splitlines()[0].lstrip("# ").strip()
        listed = re.search(r"Moduły:\s*(.+)", text)
        docs.append({
            "path": str(path.relative_to(ROOT)),
            "title": title,
            "modules": [m.strip() for m in listed.group(1).split(",")] if listed else [],
        })
    return docs


# ---------------------------------------------------------------- L2: kod

def architecture_rules() -> list[dict]:
    source = next((ROOT / "system" / "architecture").rglob("ArchitectureRulesTest.java"), None)
    if source is None:
        return []
    text = source.read_text(encoding="utf-8")
    rules = []
    for match in re.finditer(r"ArchRule (\w+) =(.*?);\n", text, re.S):
        because = re.search(r'\.because\("([^"]+)"\)', match.group(2))
        rules.append({"name": match.group(1), "because": because.group(1) if because else ""})
    return rules


def class_names(module_path: str) -> list[str]:
    return sorted(p.stem for p in (ROOT / module_path).rglob("src/main/java/**/*.java"))


# ---------------------------------------------------------------- indeks

def build_index() -> dict:
    catalog = modules()
    nominal = codeowners()
    adrs, incidents = documents("docs/adr"), documents("ops/incidents")
    for module in catalog:
        module["dependents"] = [m["name"] for m in catalog if module["name"] in m["depends_on"]]
        module["owners_nominal"] = nominal.get(module["path"], module.get("owners", "?"))
        module["owners_real"] = real_owners(module["path"])
        module["churn_30d"] = churn(module["path"])
        module["classes"] = class_names(module["path"])
        module["adrs"] = [d for d in adrs if module["name"] in d["modules"]]
        module["incidents"] = [d for d in incidents if module["name"] in d["modules"]]
    index = {
        "commit": _head(),
        "modules": catalog,
        "rules": architecture_rules(),
        "conventions": (ROOT / "docs" / "conventions.md").read_text(encoding="utf-8"),
    }
    write_json(STATE / "index.json", index)
    return index


def _head() -> str:
    try:
        return git("rev-parse", "--short", "HEAD").strip()
    except RuntimeError:
        return "brak-commita"


def load_index() -> dict:
    path = STATE / "index.json"
    return load_json(path) if path.exists() else build_index()


def blast_radius(name: str, catalog: list[dict]) -> list[str]:
    """Moduły, do których zmiana może dotrzeć: przechodnio po zależnościach odwrotnych."""
    by_name = {m["name"]: m for m in catalog}
    seen, todo = set(), [name]
    while todo:
        for dependent in by_name[todo.pop()]["dependents"]:
            if dependent not in seen and by_name[dependent]["kind"] != "tests":
                seen.add(dependent)
                todo.append(dependent)
    return sorted(seen)


# ---------------------------------------------------------------- routing

def route(title: str, body: str, index: dict) -> dict:
    """W którym module zrobić zmianę.

    Dwie reguły, obie do wytłumaczenia na slajdzie:
    1. Własność pojęcia wygrywa z częstością słów. Issue o rabacie w zamówieniach
       idzie do właściciela pojęcia „rabat”, choć słowo „zamówienie” pada częściej.
    2. Bez własności liczymy trafienia: słowa kluczowe x3, cel modułu x1, nazwy klas x1.
    """
    words = Counter(tokens(f"{title}\n{body}"))
    scored = []
    for module in index["modules"]:
        owned = {stem(w): w for w in module.get("owns", [])}
        weights = Counter()
        for w in module.get("keywords", []):
            weights[stem(w)] = max(weights[stem(w)], 3)
        for w in tokens(module.get("purpose", "")):
            weights[w] = max(weights[w], 1)
        for cls in module.get("classes", []):
            for w in split_camel(cls):
                weights[stem(w)] = max(weights[stem(w)], 1)
        hits = {w: n * weights[w] for w, n in words.items() if weights.get(w)}
        owned_hits = sorted(owned[w] for w in words if w in owned)
        scored.append({
            "module": module["name"],
            "owned": owned_hits,
            "score": sum(hits.values()),
            "hits": dict(sorted(hits.items(), key=lambda kv: -kv[1])),
        })
    scored.sort(key=lambda s: (len(s["owned"]) > 0, s["score"]), reverse=True)
    best, runner_up = scored[0], (scored[1] if len(scored) > 1 else None)
    module = next(m for m in index["modules"] if m["name"] == best["module"])
    reason = (f"moduł jest właścicielem pojęcia: {', '.join(best['owned'])}" if best["owned"]
              else "najwięcej trafień w słowach kluczowych i nazwach klas")
    confident = bool(best["owned"]) or not runner_up or best["score"] >= 1.5 * max(runner_up["score"], 1)
    radius = blast_radius(module["name"], index["modules"])
    critical = [m["name"] for m in index["modules"] if m.get("critical") and (m["name"] == module["name"] or m["name"] in radius)]
    return {
        "module": module["name"],
        "path": module["path"],
        "reason": reason,
        "confident": confident,
        "blast_radius": radius,
        "critical_in_radius": critical,
        "owners_nominal": module["owners_nominal"],
        "owners_real": module["owners_real"],
        "adrs": module["adrs"],
        "incidents": module["incidents"],
        "candidates": scored,
    }


def route_markdown(result: dict) -> str:
    who = ", ".join(f"{o['name']} ({int(o['share'] * 100)}%)" for o in result["owners_real"]) or "no history"
    lines = [
        "### 🧭 Routing",
        "",
        f"**Zmiana trafia do `{result['module']}`**, bo {result['reason']}."
        + ("" if result["confident"] else " ⚠️ Niepewne: dwa moduły mają podobny wynik, sprawdź przed merge."),
        "",
        "| | |",
        "|---|---|",
        f"| Właściciel nominalny (CODEOWNERS) | {result['owners_nominal']} |",
        f"| Właściciel faktyczny (git log) | {who} |",
        f"| Blast radius | {', '.join(result['blast_radius']) or 'tylko ten moduł'} |",
        f"| Ścieżka krytyczna w zasięgu | {', '.join(result['critical_in_radius']) or 'nie'} |",
    ]
    context = [f"- 📐 [{d['title']}]({d['path']})" for d in result["adrs"]]
    context += [f"- 🔥 [{d['title']}]({d['path']})" for d in result["incidents"]]
    if context:
        lines += ["", "**Kontekst, który dostaje agent:**", *context]
    lines += ["", "<details><summary>Punktacja kandydatów</summary>", "", "| moduł | własność | wynik | trafienia |", "|---|---|---|---|"]
    for c in result["candidates"]:
        hits = ", ".join(f"{w}×{n}" for w, n in list(c["hits"].items())[:5])
        lines.append(f"| {c['module']} | {', '.join(c['owned']) or '-'} | {c['score']} | {hits} |")
    lines += ["", "</details>"]
    return "\n".join(lines)


# ---------------------------------------------------------------- AGENTS.md

def agents_md(index: dict) -> str:
    out = [
        "# AGENTS.md",
        "",
        "<!-- Generated by sdlc/context.py. Do not edit by hand: "
        "change the sources (module.json, docs/, ops/, git history) and rebuild. -->",
        "",
        "Context for coding agents working in this repository. Organization documents are in Polish.",
        "",
        "## L1 System",
        "",
        "| module | kind | purpose | depends on | used by | critical |",
        "|---|---|---|---|---|---|",
    ]
    for m in index["modules"]:
        out.append(f"| `{m['path']}` | {m['kind']} | {m['purpose']} | {', '.join(m['depends_on']) or '-'} "
                   f"| {', '.join(m['dependents']) or '-'} | {'**yes**' if m.get('critical') else 'no'} |")
    out += ["", "## L2 Code", "", "Architecture rules (they break the build and cannot be bypassed in a change):", ""]
    out += [f"- `{r['name']}`: {r['because']}" for r in index["rules"]]
    out += ["", "Conventions (docs/conventions.md):", ""]
    out += [line for line in index["conventions"].splitlines() if line.startswith("- ")]
    out += ["", "## L3 Organization", ""]
    for m in index["modules"]:
        real = ", ".join(f"{o['name']} ({int(o['share'] * 100)}%)" for o in m["owners_real"]) or "no history"
        out.append(f"- `{m['name']}`: nominal owner {m['owners_nominal']}, actual {real}; changes in 30 days: {m['churn_30d']}")
    out += ["", "## L4 Decisions", ""]
    seen = set()
    for m in index["modules"]:
        for d in m["adrs"]:
            if d["path"] not in seen:
                seen.add(d["path"])
                out.append(f"- [{d['title']}]({d['path']}), applies to: {', '.join(d['modules'])}")
    out += ["", "## L5 Operations", ""]
    seen = set()
    for m in index["modules"]:
        for d in m["incidents"]:
            if d["path"] not in seen:
                seen.add(d["path"])
                out.append(f"- [{d['title']}]({d['path']}), applies to: {', '.join(d['modules'])}")
    out += ["", "## How to work", "",
            "1. Change only the module named in the task. If another one must be touched, say why in the description.",
            "2. Read the ADRs and incidents linked in the task before you start.",
            "3. Add a test for every behavior change.",
            "4. Run `mvn -B -q verify` in `system/` and fix everything that is red.",
            "5. Do not change the rules in `system/architecture/` or the files in `sdlc/` to make the build pass.", ""]
    return "\n".join(out)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("index")
    sub.add_parser("agents-md")
    r = sub.add_parser("route")
    r.add_argument("--title", required=True)
    r.add_argument("--body", default="")
    r.add_argument("--out-md")
    args = parser.parse_args()

    if args.cmd == "index":
        index = build_index()
        print(f"Indeks: {len(index['modules'])} moduły, {len(index['rules'])} reguł -> .sdlc/index.json")
    elif args.cmd == "agents-md":
        (ROOT / "AGENTS.md").write_text(agents_md(build_index()), encoding="utf-8")
        print("AGENTS.md przebudowany")
    elif args.cmd == "route":
        result = route(args.title, args.body, build_index())
        write_json(STATE / "route.json", result)
        markdown = route_markdown(result)
        if args.out_md:
            Path(args.out_md).write_text(markdown, encoding="utf-8")
        print(markdown)
        summary_md(markdown)
        outputs(module=result["module"], path=result["path"], critical=str(bool(result["critical_in_radius"])).lower())


if __name__ == "__main__":
    main()
