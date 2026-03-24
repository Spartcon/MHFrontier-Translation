#!/usr/bin/env python3
"""
Export all translation CSVs to a single JSON file for downstream consumers.

Output format:
{
  "fr": {
    "dat/armors/head": [
      {"location": "0x46e000@mhfdat-jp.bin", "source": "装備無し", "target": "Casque"},
      ...
    ],
    ...
  }
}

With --only-translated, only entries with a non-empty target are included.
Sections with no qualifying entries are omitted entirely.

Usage:
    python scripts/export_json.py --out translations.json
    python scripts/export_json.py --out translations.json --lang fr
    python scripts/export_json.py --out translations.json --only-translated
"""

import argparse
import csv
import json
import os


def load_section(path: str) -> list[dict]:
    rows = []
    with open(path, encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append({
                "location": row["location"],
                "source": row["source"],
                "target": row["target"],
            })
    return rows


def build_output(translations_dir: str, lang_filter: str | None, only_translated: bool) -> dict:
    result = {}
    if not os.path.isdir(translations_dir):
        return result

    for lang in sorted(os.listdir(translations_dir)):
        if lang_filter and lang != lang_filter:
            continue
        lang_dir = os.path.join(translations_dir, lang)
        if not os.path.isdir(lang_dir):
            continue

        lang_data = {}
        for root, _, files in os.walk(lang_dir):
            for fname in sorted(files):
                if not fname.endswith(".csv"):
                    continue
                full_path = os.path.join(root, fname)
                xpath = os.path.relpath(full_path, lang_dir).replace(os.sep, "/")[:-4]
                rows = load_section(full_path)
                if only_translated:
                    rows = [r for r in rows if r["target"]]
                if rows:
                    lang_data[xpath] = rows

        if lang_data:
            result[lang] = lang_data

    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--translations-dir", default="translations",
                        help="Root translations directory (default: translations/)")
    parser.add_argument("--out", default="translations.json",
                        help="Output JSON file (default: translations.json)")
    parser.add_argument("--lang", help="Only export a specific language (e.g. fr)")
    parser.add_argument("--only-translated", action="store_true",
                        help="Omit strings where target is empty")
    args = parser.parse_args()

    data = build_output(args.translations_dir, args.lang, args.only_translated)

    total = sum(len(rows) for lang in data.values() for rows in lang.values())
    translated = sum(
        sum(1 for r in rows if r["target"])
        for lang in data.values() for rows in lang.values()
    )

    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"Wrote {args.out}: {translated}/{total} strings translated across {len(data)} language(s)")


if __name__ == "__main__":
    main()
