#!/usr/bin/env python3
"""
Export translation CSVs to JSON for downstream consumers.

Output format:
{
  "fr": {
    "dat/armors/head": [
      {"index": "0", "source": "装備無し", "target": "Casque"},
      ...
    ],
    ...
  }
}

Flags:
  --only-translated   Omit rows where target is empty (sections with no
                      qualifying rows are dropped entirely).
  --no-source         Drop the ``source`` field from each row. The
                      FrontierTextHandler importer resolves rows by
                      ``index``, so launchers don't need it. Combined with
                      ``--only-translated --gzip``, this is the smallest
                      payload suitable for ``mhf-outpost``.
  --gzip              Compress the output with gzip. The output filename
                      gets a ``.gz`` suffix appended automatically.
  --lang CODE         Export a single language (default: all).

Usage:
    python scripts/export_json.py --out translations.json
    python scripts/export_json.py --out translations-fr.json \\
        --lang fr --only-translated --no-source --gzip
"""

import argparse
import csv
import gzip
import json
import os
import sys

csv.field_size_limit(sys.maxsize)


def load_section(path: str, *, drop_source: bool) -> list[dict]:
    rows = []
    with open(path, encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            entry = {"index": row["index"], "target": row["target"]}
            if not drop_source:
                entry["source"] = row["source"]
            rows.append(entry)
    return rows


def build_output(
    translations_dir: str,
    lang_filter: str | None,
    only_translated: bool,
    drop_source: bool,
) -> dict:
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
                rows = load_section(full_path, drop_source=drop_source)
                if only_translated:
                    rows = [r for r in rows if r["target"]]
                if rows:
                    lang_data[xpath] = rows

        if lang_data:
            result[lang] = lang_data

    return result


def write_json(data: dict, path: str, *, compress: bool) -> str:
    payload = json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8")
    if compress:
        if not path.endswith(".gz"):
            path += ".gz"
        with gzip.open(path, "wb", compresslevel=9) as f:
            f.write(payload)
    else:
        with open(path, "wb") as f:
            f.write(payload)
    return path


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--translations-dir", default="translations",
                        help="Root translations directory (default: translations/)")
    parser.add_argument("--out", default="translations.json",
                        help="Output JSON file (default: translations.json)")
    parser.add_argument("--lang", help="Only export a specific language (e.g. fr)")
    parser.add_argument("--only-translated", action="store_true",
                        help="Omit strings where target is empty")
    parser.add_argument("--no-source", action="store_true",
                        help="Drop the source field (smaller payload for launchers)")
    parser.add_argument("--gzip", action="store_true",
                        help="Compress output with gzip; appends .gz to --out")
    args = parser.parse_args()

    data = build_output(
        args.translations_dir,
        args.lang,
        args.only_translated,
        args.no_source,
    )

    total = sum(len(rows) for lang in data.values() for rows in lang.values())
    translated = sum(
        sum(1 for r in rows if r["target"])
        for lang in data.values() for rows in lang.values()
    )

    out_path = write_json(data, args.out, compress=args.gzip)
    size = os.path.getsize(out_path)
    print(
        f"Wrote {out_path} ({size:,} bytes): {translated}/{total} strings "
        f"translated across {len(data)} language(s)"
    )


if __name__ == "__main__":
    main()
