#!/usr/bin/env python3
"""Migrate join markers from <join at="NNN"> to {j} in all translation CSVs.

One-shot migration for FTH 1.6.0 format. Also clears target columns where
target == source (untranslated rows per 1.6.0 convention: empty target).

Usage:
    python scripts/migrate_join_markers.py                    # dry-run (default)
    python scripts/migrate_join_markers.py --apply            # apply changes
    python scripts/migrate_join_markers.py translations/fr/   # specific directory
"""

import argparse
import csv
import io
import re
import sys
from pathlib import Path

JOIN_RE = re.compile(r'<join at="[^"]*">')


def migrate_csv(path: Path, apply: bool) -> dict:
    """Migrate a single CSV file. Returns stats dict."""
    stats = {"joins_converted": 0, "targets_cleared": 0, "unchanged": True}

    with open(path, encoding="utf-8", newline="") as f:
        content = f.read()

    # Parse
    reader = csv.reader(io.StringIO(content))
    try:
        header = next(reader)
    except StopIteration:
        return stats

    if header != ["index", "source", "target"]:
        return stats

    rows = list(reader)
    new_rows = []
    for row in rows:
        if len(row) != 3:
            new_rows.append(row)
            continue

        idx, source, target = row

        # Convert join markers in source
        new_source = JOIN_RE.sub("{j}", source)
        if new_source != source:
            stats["joins_converted"] += source.count("<join") - new_source.count("<join")

        # Convert join markers in target
        new_target = JOIN_RE.sub("{j}", target)
        if new_target != target:
            stats["joins_converted"] += target.count("<join") - new_target.count("<join")

        # Clear target if it equals source (untranslated)
        if new_target and new_target == new_source:
            stats["targets_cleared"] += 1
            new_target = ""

        if new_source != source or new_target != target:
            stats["unchanged"] = False

        new_rows.append([idx, new_source, new_target])

    if not stats["unchanged"] and apply:
        out = io.StringIO()
        writer = csv.writer(out, lineterminator="\n")
        writer.writerow(header)
        writer.writerows(new_rows)
        with open(path, "w", encoding="utf-8", newline="") as f:
            f.write(out.getvalue())

    return stats


def main():
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "paths",
        nargs="*",
        default=["translations/"],
        help="Files or directories to process (default: translations/)",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Write changes (default: dry-run)",
    )
    args = parser.parse_args()

    files: list[Path] = []
    for p in args.paths:
        root = Path(p)
        if root.is_file():
            files.append(root)
        else:
            files.extend(sorted(root.rglob("*.csv")))

    if not files:
        print("No CSV files found.")
        sys.exit(0)

    total_joins = 0
    total_cleared = 0
    changed_files = 0

    for f in files:
        stats = migrate_csv(f, apply=args.apply)
        if not stats["unchanged"]:
            changed_files += 1
            rel = f.relative_to(Path.cwd()) if f.is_relative_to(Path.cwd()) else f
            print(
                f"  {rel}: {stats['joins_converted']} joins, "
                f"{stats['targets_cleared']} targets cleared"
            )
        total_joins += stats["joins_converted"]
        total_cleared += stats["targets_cleared"]

    mode = "APPLIED" if args.apply else "DRY-RUN"
    print(f"\n[{mode}] {changed_files}/{len(files)} files changed")
    print(f"  {total_joins:,} join markers converted")
    print(f"  {total_cleared:,} untranslated targets cleared")
    if not args.apply and changed_files:
        print("\nRe-run with --apply to write changes.")


if __name__ == "__main__":
    main()
