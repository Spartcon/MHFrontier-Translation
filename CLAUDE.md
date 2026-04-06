# CLAUDE.md

Project-specific guidance for the MHFrontier-Translation repository.

## Project role

Per-section CSV translations of Monster Hunter Frontier text, organized as
`translations/<lang>/<xpath>.csv`. Source data is extracted via
[FrontierTextHandler](../../tools/FrontierTextHandler) (see sibling
`mhfrontier/tools/FrontierTextHandler/CLAUDE.md`).

## Copyright: do not commit raw Japanese source text

The original Japanese strings in the `source` column belong to Capcom. The
copyright risk of redistributing them in this repo is low but real, and worth
keeping deliberate:

- **Avoid bulk-importing JP source text** into commits whenever possible.
  Prefer storing only `location` + `target` once a clean tooling path exists,
  or hashing/eliding the source column.
- **Never paste large blocks of JP text** into issues, PR descriptions, or
  CLAUDE memory.
- The current `translations/fr/` files do contain JP source as a transitional
  measure (needed for human reviewers and for migration). Plan to remove or
  hash the source column before any future bulk re-extraction.

When in doubt, treat JP `source` cells as proprietary and minimize their
footprint.

## Layout

```
translations/
  fr/                 ← French (primary)
  en/                 ← English (bootstrapped from polluted source rows)
scripts/
  validate.py         ← CSV format check
  stats.py            ← coverage report → stats.json
  export_json.py      ← bundle for FrontierTextHandler --merge-json
  migrate.py          ← import a monolithic Weblate CSV
  cleanup.py          ← classify rows, bootstrap translations/en/
```

## Known data quality issues

1. **English-as-source pollution**: the PC binary used for extraction had
   been partially patched by an older English fan-translation, leaving English
   in the `source` column for ~799 rows in `pac/text_*` and `jmp/menu/*`.
   FTH's `data/mhf*-jp.bin` reference files are themselves contaminated
   (3,188 English-source rows). **Partially fixed** by cracking the v2064 Wii U
   dump (`mhfrontier/client/wiiu/Monster Hunter Frontier G [0005000E1014DA00]
   (v2064)/`) with `cdecrypt`, extracting via FTH, and row-index matching
   sections with identical row counts — see `scripts/fix_pollution.py`. This
   recovered 130 rows across 17 sections. The remaining ~669 polluted rows
   live in 8 sections whose row counts differ between PC and Wii U
   (`pac/text_34`, `pac/text_40`, `dat/items/name`, etc.) and would need
   sequence alignment or a fresh unpatched PC JP dump.
2. **Dummy rows** (1,348 in fr/, 1,211 confirmed in `dat/items/source.csv`):
   literal `dummy` strings embedded in the binary at fixed offsets. Confirmed
   as **real unimplemented item-source slots**: they appear identically in
   every PC binary extracted (contaminated and "JP" reference), so they are
   not an extraction artifact. The game keeps a fixed-size offset table for
   item-source descriptions and pads unused entries with `dummy`. Safe to
   leave with empty target — they don't render in-game.
3. **Control-code rows** (~6,643): `<join at=...>` glue and color codes — not
   translatable on their own.

Run `python scripts/cleanup.py --audit` for the current breakdown.

## Workflows

```bash
python scripts/validate.py                       # validate all CSVs
python scripts/stats.py                          # regenerate stats.json
python scripts/cleanup.py --audit                # classify rows
python scripts/cleanup.py --bootstrap-en         # mirror fr/ → en/
python scripts/migrate.py --extracted-dir <FTH-output> \
    --translated <weblate.csv> --lang fr         # import Weblate dump
```
