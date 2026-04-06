#!/usr/bin/env python3
"""
Replace English-as-source rows in translations/{fr,en}/ with clean Japanese
text extracted from a different binary (e.g. the v2064 Wii U dump).

Strategy: row-index matching within sections whose row counts match exactly.
For each fr/ CSV that has a same-count counterpart in --reference-dir (a
FrontierTextHandler --extract-all output directory), walk row-by-row; for
every row whose fr/ source classifies as "english" (per cleanup.classify),
substitute the source cell with the reference's source. The location and
target columns are preserved. The same substitution is applied to en/.

Sections whose row counts differ are skipped — they would need sequence
alignment, which is out of scope here.

Usage::

    python scripts/fix_pollution.py \\
        --reference-dir ../../tools/FrontierTextHandler/output
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

csv.field_size_limit(sys.maxsize)

from cleanup import classify  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
FR_DIR = ROOT / "translations" / "fr"
EN_DIR = ROOT / "translations" / "en"


def fr_to_fth_name(rel: Path) -> str:
    return "-".join(rel.with_suffix("").parts) + ".csv"


def read_csv(path: Path) -> tuple[list[str], list[list[str]]]:
    with open(path, encoding="utf-8", newline="") as f:
        reader = csv.reader(f)
        header = next(reader, [])
        rows = [r for r in reader if len(r) == 3]
    return header, rows


def write_csv(path: Path, header: list[str], rows: list[list[str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(header)
        w.writerows(rows)


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--reference-dir", required=True, type=Path,
                   help="FTH --extract-all output dir from a clean binary")
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()

    ref_dir: Path = args.reference_dir
    if not ref_dir.is_dir():
        raise SystemExit(f"Not a directory: {ref_dir}")

    sections_fixed = 0
    sections_skipped = 0
    rows_fixed = 0

    for src in sorted(FR_DIR.rglob("*.csv")):
        rel = src.relative_to(FR_DIR)
        ref_path = ref_dir / fr_to_fth_name(rel)
        if not ref_path.exists():
            continue

        fr_header, fr_rows = read_csv(src)
        try:
            _ref_header, ref_rows = read_csv(ref_path)
        except UnicodeDecodeError:
            continue

        # only consider sections with at least one polluted row
        polluted_idx = [i for i, r in enumerate(fr_rows)
                        if classify(r[1]) == "english"]
        if not polluted_idx:
            continue

        if len(fr_rows) != len(ref_rows):
            sections_skipped += 1
            print(f"SKIP {rel} (fr={len(fr_rows)} vs ref={len(ref_rows)}, "
                  f"{len(polluted_idx)} polluted)")
            continue

        en_path = EN_DIR / rel
        en_header, en_rows = read_csv(en_path) if en_path.exists() else (fr_header, [])
        en_lookup = {tuple(r[:2]): r for r in en_rows}

        replaced_here = 0
        for i in polluted_idx:
            new_source = ref_rows[i][1]
            if classify(new_source) != "jp":
                continue  # ref isn't actually clean at this row
            old_loc, old_source, target = fr_rows[i]
            fr_rows[i] = [old_loc, new_source, target]
            # update en/ row keyed by (loc, old_source)
            en_row = en_lookup.pop((old_loc, old_source), None)
            if en_row is not None:
                en_row[1] = new_source
            replaced_here += 1

        if not replaced_here:
            continue

        sections_fixed += 1
        rows_fixed += replaced_here
        print(f"FIX  {rel}: {replaced_here}/{len(polluted_idx)} rows")

        if not args.dry_run:
            write_csv(src, fr_header, fr_rows)
            if en_path.exists():
                write_csv(en_path, en_header, en_rows)

    print()
    print(f"Sections fixed: {sections_fixed}")
    print(f"Sections skipped (row count mismatch): {sections_skipped}")
    print(f"Rows fixed: {rows_fixed}")


if __name__ == "__main__":
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    main()
