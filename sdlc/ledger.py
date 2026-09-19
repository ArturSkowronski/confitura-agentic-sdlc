"""Księga zdarzeń fabryki (lekcja 10).

Każde zdarzenie (prompt, wywołanie narzędzia, edycja pliku, commit, decyzja bramki)
to linia JSONL z hashem poprzedniej linii. Zmiana jednego bajtu w środku psuje łańcuch
od tego miejsca do końca. Na koniec próby linia podpisuje plik kluczem fabryki (Sigstore cosign),
więc nie da się też podmienić całej księgi.

Użycie:
  python3 sdlc/ledger.py append --type gate.passed --data '{"gate": "archunit"}'
  python3 sdlc/ledger.py ingest --source warsztat --events narzedzia.jsonl
  python3 sdlc/ledger.py merge .sdlc/ledger-*.jsonl
  python3 sdlc/ledger.py verify
  python3 sdlc/ledger.py summary
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from lib import STATE, summary_md

DEFAULT = STATE / "ledger.jsonl"
GENESIS = "0" * 64


def canonical(record: dict) -> bytes:
    return json.dumps({k: v for k, v in record.items() if k != "hash"}, sort_keys=True, ensure_ascii=False,
                      separators=(",", ":")).encode()


def read(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def append(path: Path, event_type: str, data: dict) -> dict:
    records = read(path)
    record = {
        "seq": len(records),
        "ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "run": os.environ.get("FABRYKA_RUN", "local"),
        "job": os.environ.get("FABRYKA_STEP", "local"),
        "type": event_type,
        "data": data,
        "prev": records[-1]["hash"] if records else GENESIS,
    }
    record["hash"] = hashlib.sha256(canonical(record)).hexdigest()
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, ensure_ascii=False) + "\n")
    return record


def verify(path: Path) -> tuple[bool, str]:
    prev = GENESIS
    records = read(path)
    for i, record in enumerate(records):
        if record.get("seq") != i:
            return False, f"linia {i}: zły numer sekwencji ({record.get('seq')})"
        if record.get("prev") != prev:
            return False, f"linia {i}: przerwany łańcuch, prev nie zgadza się z hashem linii {i - 1}"
        if hashlib.sha256(canonical(record)).hexdigest() != record.get("hash"):
            return False, f"linia {i}: treść zmieniona po zapisie ({record['type']})"
        prev = record["hash"]
    return True, f"OK: {len(records)} zdarzeń, głowa łańcucha {prev[:12]}"


def ingest(path: Path, source: str, events_file: Path) -> int:
    """Wciąga strumień zdarzeń agenta (JSONL z --format json / --json / stream-json)."""
    count = 0
    if not events_file.exists():
        return 0
    for line in events_file.read_text(encoding="utf-8").splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        kind = event.get("type") or event.get("event") or "event"
        append(path, f"agent.{source}.{kind}", _shrink(event))
        count += 1
    return count


def _shrink(value, limit: int = 2000):
    """Długie wyjścia narzędzi przycinamy, ale hash zostaje z pełnej treści."""
    text = json.dumps(value, ensure_ascii=False)
    if len(text) <= limit:
        return value
    return {"truncated": text[:limit], "sha256": hashlib.sha256(text.encode()).hexdigest(), "bytes": len(text)}


def merge(path: Path, fragments: list[Path]) -> int:
    """Równoległe joby (bramki, review) piszą własne fragmenty. Wpinamy je do łańcucha
    w kolejności czasu pierwszego zdarzenia, zachowując oryginalny znacznik czasu i job."""
    loaded = [(read(f), f) for f in fragments if f.exists()]
    loaded = [(records, f) for records, f in loaded if records]
    loaded.sort(key=lambda item: item[0][0]["ts"])
    count = 0
    for records, fragment in loaded:
        ok, message = verify(fragment)
        if not ok:
            append(path, "ledger.fragment_rejected", {"fragment": fragment.name, "reason": message})
            continue
        for record in records:
            append(path, record["type"], {**record["data"], "_ts": record["ts"], "_job": record["job"]})
            count += 1
    return count


def summary(path: Path) -> str:
    records = read(path)
    ok, message = verify(path)
    kinds = Counter(r["type"].split(".")[0] if not r["type"].startswith("agent.") else "agent" for r in records)
    lines = [
        "### 🔗 Księga zdarzeń",
        "",
        f"{'✅' if ok else '❌'} {message}",
        "",
        "| rodzaj | zdarzeń |",
        "|---|---|",
        *[f"| {k} | {n} |" for k, n in kinds.most_common()],
    ]
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--file", default=str(DEFAULT))
    sub = parser.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("append")
    a.add_argument("--type", required=True)
    a.add_argument("--data", default="{}")
    i = sub.add_parser("ingest")
    i.add_argument("--source", required=True)
    i.add_argument("--events", required=True)
    m = sub.add_parser("merge")
    m.add_argument("fragments", nargs="+")
    sub.add_parser("verify")
    sub.add_parser("summary")
    args = parser.parse_args()
    path = Path(args.file)

    if args.cmd == "append":
        record = append(path, args.type, json.loads(args.data))
        print(f"#{record['seq']} {record['type']} {record['hash'][:12]}")
    elif args.cmd == "ingest":
        print(f"Wciągnięto {ingest(path, args.source, Path(args.events))} zdarzeń agenta")
    elif args.cmd == "merge":
        print(f"Wpięto {merge(path, [Path(f) for f in args.fragments])} zdarzeń z fragmentów")
    elif args.cmd == "verify":
        ok, message = verify(path)
        print(message)
        sys.exit(0 if ok else 1)
    elif args.cmd == "summary":
        text = summary(path)
        print(text)
        summary_md(text)


if __name__ == "__main__":
    main()
