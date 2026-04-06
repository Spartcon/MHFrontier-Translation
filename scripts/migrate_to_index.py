#!/usr/bin/env python3
"""
One-shot migration: convert legacy ``location,source,target`` CSVs to the new
``index,source,target`` format produced by FrontierTextHandler ``--with-index``.

For each freshly extracted FTH file:
- map old (source -> [targets]) FIFO from the matching translations/<lang>/ csv
- emit a new file keyed by index, carrying targets where source matches

New sections present in FTH but absent from translations/<lang>/ are written
out with empty targets so the layout is complete.

Usage::

    python scripts/migrate_to_index.py --fth-output ../../tools/FrontierTextHandler/output
"""

from __future__ import annotations

import argparse
import csv
import sys
from collections import defaultdict, deque
from pathlib import Path

csv.field_size_limit(sys.maxsize)

ROOT = Path(__file__).resolve().parent.parent
TRANS = ROOT / "translations"
LANGS = ("fr", "en")


def fth_name_to_rel(name: str) -> Path:
    """``dat-armors-head.csv`` -> ``dat/armors/head.csv``.

    Reverses the dash-joining done by FrontierTextHandler. Section names like
    ``pac-text_94-field_0.csv`` map to ``pac/text_94/field_0.csv``.
    """
    stem = name[:-4] if name.endswith(".csv") else name
    return Path(*stem.split("-")).with_suffix(".csv")


def read_old(path: Path) -> dict[str, deque[str]]:
    """Build {source: deque(targets)} from a legacy location-keyed CSV."""
    table: dict[str, deque[str]] = defaultdict(deque)
    if not path.exists():
        return table
    with open(path, encoding="utf-8", newline="") as f:
        reader = csv.reader(f)
        next(reader, None)
        for row in reader:
            if len(row) < 3:
                continue
            _loc, src, tgt = row[0], row[1], row[2]
            if tgt and tgt != src:
                table[src].append(tgt)
    return table


def migrate_section_inmem(fth_path: Path, old_map: dict[str, deque[str]],
                          new_path: Path) -> tuple[int, int]:
    """Write new index-keyed CSV at ``new_path``. Returns (carried, total)."""
    carried = total = 0
    new_path.parent.mkdir(parents=True, exist_ok=True)
    with open(fth_path, encoding="utf-8", newline="") as fin, \
         open(new_path, "w", encoding="utf-8", newline="") as fout:
        reader = csv.reader(fin)
        header = next(reader, None)
        if header != ["index", "source", "target"]:
            raise SystemExit(f"unexpected header in {fth_path}: {header}")
        writer = csv.writer(fout, lineterminator="\n")
        writer.writerow(["index", "source", "target"])
        for row in reader:
            if len(row) < 3:
                continue
            idx, src, _tgt = row[0], row[1], row[2]
            queue = old_map.get(src)
            target = queue.popleft() if queue else ""
            if target:
                carried += 1
            writer.writerow([idx, src, target])
            total += 1
    return carried, total


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--fth-output", required=True, type=Path,
                   help="Directory of FTH --extract-all --with-index output")
    args = p.parse_args()

    fth_dir: Path = args.fth_output
    if not fth_dir.is_dir():
        raise SystemExit(f"Not a directory: {fth_dir}")

    skip = {"merged.csv", "refrontier.csv"}
    fth_files = sorted(f for f in fth_dir.glob("*.csv") if f.name not in skip)

    for lang in LANGS:
        lang_dir = TRANS / lang
        # snapshot old data before wiping the tree
        old_maps: dict[Path, dict[str, deque[str]]] = {}
        for fth in fth_files:
            rel = fth_name_to_rel(fth.name)
            old_maps[rel] = read_old(lang_dir / rel)
        for old in lang_dir.rglob("*.csv"):
            old.unlink()

        total_c = total_n = 0
        for fth in fth_files:
            rel = fth_name_to_rel(fth.name)
            new_path = lang_dir / rel
            c, n = migrate_section_inmem(fth, old_maps[rel], new_path)
            total_c += c
            total_n += n
        print(f"{lang}: carried {total_c}/{total_n}")

    # prune empty parent directories left after deletion
    for lang in LANGS:
        for d in sorted((TRANS / lang).rglob("*"), reverse=True):
            if d.is_dir() and not any(d.iterdir()):
                d.rmdir()


if __name__ == "__main__":
    main()
