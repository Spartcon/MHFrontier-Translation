#!/usr/bin/env python3
"""
Validate translation CSV files.

Checks:
  - Header is exactly: location,source,target
  - location is a non-empty integer
  - source is non-empty
  - No duplicate locations within a file

Usage:
    python scripts/validate.py translations/fr/dat/armors/head.csv
    python scripts/validate.py translations/          # validate all CSVs recursively
    python scripts/validate.py --changed-only         # validate only git-changed files
"""

import argparse
import csv
import os
import subprocess
import sys

REQUIRED_HEADER = ["location", "source", "target"]


def validate_file(path: str) -> list[str]:
    errors = []
    seen_locations: set[str] = set()

    try:
        with open(path, encoding="utf-8", newline="") as f:
            reader = csv.reader(f)
            try:
                header = next(reader)
            except StopIteration:
                return [f"{path}: file is empty"]

            if header != REQUIRED_HEADER:
                return [f"{path}: wrong header {header!r}, expected {REQUIRED_HEADER!r}"]

            for lineno, row in enumerate(reader, start=2):
                if len(row) != 3:
                    errors.append(f"{path}:{lineno}: expected 3 columns, got {len(row)}")
                    continue

                loc, source, target = row

                if not loc.strip():
                    errors.append(f"{path}:{lineno}: empty location")
                    continue

                try:
                    int(loc)
                except ValueError:
                    errors.append(f"{path}:{lineno}: location is not an integer: {loc!r}")

                if not source.strip():
                    errors.append(f"{path}:{lineno}: empty source (location {loc})")

                if loc in seen_locations:
                    errors.append(f"{path}:{lineno}: duplicate location {loc!r}")
                seen_locations.add(loc)

    except UnicodeDecodeError as e:
        errors.append(f"{path}: encoding error (must be UTF-8): {e}")

    return errors


def collect_csvs(path: str) -> list[str]:
    if os.path.isfile(path):
        return [path]
    result = []
    for root, _, files in os.walk(path):
        for f in files:
            if f.endswith(".csv"):
                result.append(os.path.join(root, f))
    return sorted(result)


def changed_csvs() -> list[str]:
    """Return CSVs modified in the current git diff (staged + unstaged)."""
    try:
        out = subprocess.check_output(
            ["git", "diff", "--name-only", "HEAD"], text=True
        )
    except subprocess.CalledProcessError:
        out = subprocess.check_output(
            ["git", "diff", "--name-only", "--cached"], text=True
        )
    return [p for p in out.splitlines() if p.endswith(".csv") and os.path.isfile(p)]


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("paths", nargs="*", default=["translations/"],
                        help="Files or directories to validate (default: translations/)")
    parser.add_argument("--changed-only", action="store_true",
                        help="Validate only git-changed CSV files")
    args = parser.parse_args()

    if args.changed_only:
        files = changed_csvs()
        if not files:
            print("No changed CSV files.")
            sys.exit(0)
    else:
        files = []
        for path in args.paths:
            files.extend(collect_csvs(path))

    if not files:
        print("No CSV files found.")
        sys.exit(0)

    all_errors = []
    for f in files:
        all_errors.extend(validate_file(f))

    if all_errors:
        for err in all_errors:
            print(err, file=sys.stderr)
        print(f"\n{len(all_errors)} error(s) in {len(files)} file(s).", file=sys.stderr)
        sys.exit(1)
    else:
        print(f"OK — {len(files)} file(s) validated.")


if __name__ == "__main__":
    main()
