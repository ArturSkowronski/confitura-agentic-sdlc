#!/usr/bin/env python3
"""Ilustracje do warsztatu, w stylu JVM Weekly.

    python3 warsztat/grafiki/gen.py --list
    python3 warsztat/grafiki/gen.py cover-fabryka --dry-run
    python3 warsztat/grafiki/gen.py --all

Styl i referencja postaci pochodzą z ~/Priv/jvm-weekly (tools/illugen.py). Klucz
bierze się z OPENAI_API_KEY i nigdzie nie jest zapisywany. Każdy PNG dostaje obok
.txt z modelem, ustawieniami i pełnym promptem, żeby dobry wynik dało się powtórzyć.
"""
import argparse, base64, datetime as dt, os, re, sys
from pathlib import Path

G = Path(__file__).resolve().parent
PROMPTS = G / "prompts.md"
OUT = G / "out"
REF = Path.home() / "Priv/jvm-weekly/grafiki/ref/avatar.png"
MODELS = {"sunburst": "gpt-image-2.5-sunburst", "flare": "gpt-image-2.5-flare"}
META = {"Style lock", "Negative"}


def api_key(source: str = "auto") -> tuple:
    """Ten sam łańcuch co w jvm-weekly/tools/illugen.py. Klucz nie jest zapisywany."""
    k = os.environ.get("OPENAI_API_KEY", "").strip()
    if k and source in ("auto", "env"):
        return k, "OPENAI_API_KEY (środowisko)"
    if source == "env":
        sys.exit("--key-from env, ale OPENAI_API_KEY jest puste")
    for path in (Path.home() / ".config/openai/key", G.parent.parent / ".env"):
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        m = re.search(r"^\s*(?:export\s+)?OPENAI_API_KEY\s*=\s*[\'\"]?([^\'\"\s]+)", text, re.M)
        if m:
            return m.group(1), str(path)
        if path.name == "key" and text.strip():
            return text.strip(), str(path)
    sys.exit("brak klucza: ustaw OPENAI_API_KEY albo wpisz go do ~/.config/openai/key")


def sections(md: str) -> dict:
    out, cur, buf = {}, None, []
    for line in md.splitlines():
        m = re.match(r"^## (.+?)\s*$", line)
        if m:
            if cur:
                out[cur] = "\n".join(buf).strip()
            cur, buf = m.group(1), []
        elif cur:
            buf.append(line)
    if cur:
        out[cur] = "\n".join(buf).strip()
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("scenes", nargs="?", default="")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--variants", type=int, default=1)
    ap.add_argument("--quality", default="high",
                    choices=("low", "medium", "high", "xhigh", "max", "auto"))
    ap.add_argument("--model", default="sunburst", choices=tuple(MODELS))
    ap.add_argument("--size", default="1536x1024")
    ap.add_argument("--key-from", default="auto", choices=("auto", "env", "file"))
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    secs = sections(PROMPTS.read_text(encoding="utf-8"))
    names = [k for k in secs if k not in META]
    if a.list:
        for n in names:
            print(f"{n:18} {secs[n][:72]}…")
        return 0
    todo = names if a.all else [s.strip() for s in a.scenes.split(",") if s.strip()]
    if not todo:
        ap.error("podaj sceny, --all albo --list")
    for n in todo:
        if n not in secs:
            sys.exit(f"brak sekcji '## {n}'. Są: {', '.join(names)}")

    def prompt_for(n):
        parts = [secs["Style lock"], secs[n]]
        if secs.get("Negative"):
            parts.append("Avoid: " + " ".join(secs["Negative"].split()))
        return "\n\n".join(parts)

    if a.dry_run:
        for n in todo:
            print(f"===== {n}\n{prompt_for(n)}\n")
        return 0
    if not REF.exists():
        sys.exit(f"brak referencji postaci: {REF}")
    key, where = api_key(a.key_from)
    print(f"klucz: {where}")

    from openai import OpenAI
    client = OpenAI(api_key=key)
    OUT.mkdir(parents=True, exist_ok=True)
    model = MODELS[a.model]
    for n in todo:
        done = sorted(OUT.glob(f"{n}-v*.png"))
        start = len(done) + 1
        print(f"{n}: {a.variants} × {model} {a.size} {a.quality} …", flush=True)
        try:
            with open(REF, "rb") as fh:
                r = client.images.edit(model=model, image=[fh], prompt=prompt_for(n),
                                       n=a.variants, size=a.size, quality=a.quality)
        except Exception as e:  # jedna scena nie może zabić całego przebiegu
            print(f"  !! {type(e).__name__}: {str(e)[:200]}", flush=True)
            continue
        for i, item in enumerate(r.data):
            png = OUT / f"{n}-v{start + i}.png"
            png.write_bytes(base64.b64decode(item.b64_json))
            png.with_suffix(".txt").write_text(
                f"model: {model}\nsize: {a.size}\nquality: {a.quality}\n"
                f"ref: {REF.name}\nwhen: {dt.datetime.now().isoformat(timespec='seconds')}\n\n"
                f"{prompt_for(n)}\n", encoding="utf-8")
            print(f"  -> {png.name}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
