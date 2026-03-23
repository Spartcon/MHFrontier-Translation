#!/usr/bin/env python3
"""
Migrate translations from a monolithic Weblate CSV into the per-xpath layout.

Usage:
    python scripts/migrate.py \\
        --extracted-dir path/to/FrontierTextHandler/output \\
        --translated  path/to/mhfdat-all-fr.csv \\
        --lang fr \\
        --out translations/

FrontierTextHandler must have been run with --extract-all first so that
per-section CSVs (one per xpath) are available in --extracted-dir.
Those CSVs provide the source text and the canonical location integers.
The --translated CSV supplies the existing target translations.

The script matches on the `location` column (integer offset) and writes
one output file per xpath under translations/<lang>/<xpath>.csv.
"""

import argparse
import csv
import os
import sys


def load_translations(path: str) -> dict[str, str]:
    """Load a CSV and return {location: target} for rows with a non-empty target."""
    result = {}
    with open(path, encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        if "location" not in (reader.fieldnames or []):
            sys.exit(f"ERROR: {path} has no 'location' column")
        for row in reader:
            loc = row.get("location", "").strip()
            target = row.get("target", "").strip()
            if loc and target:
                result[loc] = target
    return result


def migrate_section(extracted_csv: str, translations: dict[str, str], out_path: str) -> tuple[int, int]:
    """
    Write out_path CSV by merging source rows from extracted_csv with
    known translations.  Returns (total_rows, translated_rows).
    """
    rows = []
    with open(extracted_csv, encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            loc = row.get("location", "").strip()
            source = row.get("source", row.get("text", "")).strip()
            target = translations.get(loc, "")
            rows.append((loc, source, target))

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["location", "source", "target"])
        writer.writerows(rows)

    translated = sum(1 for _, _, t in rows if t)
    return len(rows), translated


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--extracted-dir", required=True,
                        help="Directory containing FrontierTextHandler --extract-all output CSVs")
    parser.add_argument("--translated", required=True,
                        help="Monolithic translated CSV (e.g. mhfdat-all-fr.csv)")
    parser.add_argument("--lang", default="fr",
                        help="Target language code (default: fr)")
    parser.add_argument("--out", default="translations",
                        help="Output root directory (default: translations/)")
    args = parser.parse_args()

    print(f"Loading translations from {args.translated}...")
    translations = load_translations(args.translated)
    print(f"  {len(translations)} translated strings found")

    # FrontierTextHandler names extracted files like "dat-armors-head.csv"
    # which maps to xpath "dat/armors/head".
    extracted_dir = args.extracted_dir
    if not os.path.isdir(extracted_dir):
        sys.exit(f"ERROR: --extracted-dir '{extracted_dir}' does not exist")

    total_sections = 0
    total_rows = 0
    total_translated = 0

    for fname in sorted(os.listdir(extracted_dir)):
        if not fname.endswith(".csv"):
            continue
        # Convert filename to xpath: "dat-armors-head.csv" → "dat/armors/head"
        xpath = fname[:-4].replace("-", "/", fname.count("-"))
        # FrontierTextHandler uses dashes as separators but xpaths use slashes.
        # Simple heuristic: replace all dashes with slashes.
        xpath = fname[:-4].replace("-", "/")
        out_path = os.path.join(args.out, args.lang, xpath + ".csv")
        extracted_csv = os.path.join(extracted_dir, fname)

        rows, translated = migrate_section(extracted_csv, translations, out_path)
        pct = f"{100*translated//rows}%" if rows else "n/a"
        print(f"  {xpath}: {translated}/{rows} strings translated ({pct})")
        total_sections += 1
        total_rows += rows
        total_translated += translated

    overall = f"{100*total_translated//total_rows}%" if total_rows else "n/a"
    print(f"\nDone: {total_sections} sections, {total_translated}/{total_rows} strings translated ({overall})")


if __name__ == "__main__":
    main()
