# CLAUDE.md

Project-specific guidance for the MHFrontier-Translation repository.

## Project role

Per-section CSV translations of Monster Hunter Frontier text, organized as
`translations/<lang>/<xpath>.csv`. Source data is extracted via
[FrontierTextHandler](../../tools/FrontierTextHandler) (see sibling
`mhfrontier/tools/FrontierTextHandler/CLAUDE.md`).

## CSV format

`index,source,target` where `index` is the slot number in the section's
pointer table (FTH `--with-index` output). Indexes are stable across
upstream string-length changes that used to shift raw byte offsets.

**Required FTH version: ≥ 1.5.0** (`--with-index` and the index-aware
importer landed in 1.5.0). Earlier releases will reject these CSVs.

The legacy `location,source,target` format (with `0xHEX@file.bin` keys) was
retired in April 2026. Importing an index-keyed CSV with FTH **requires
`--xpath`** so the importer can resolve indexes against the live pointer
table; in this repo the xpath is implicit from the file path
(`translations/fr/dat/armors/head.csv` → `dat/armors/head`). `build_bins.py`
derives it automatically.

## Copyright posture on Japanese source text

The original Japanese strings in the `source` column belong to Capcom, but
hosting them here is consistent with established community practice and the
practical risk is very low:

- Other Monster Hunter fan-translation repos host JP source publicly:
  [NSACloud/MHR-EFX-Translator](https://github.com/NSACloud/MHR-EFX-Translator)
  (TSV of Rise EFX JP→EN strings) and
  [xl3lackout/MHFZ-Ferias-English-Project](https://github.com/xl3lackout/MHFZ-Ferias-English-Project)
  (HTML pages translating the JP Ferias MHF-Z info site, original JP text
  preserved alongside the English).
- Capcom's MH-related enforcement has targeted ROMs, asset rips, and server
  emulators — never translation source strings. MHF was shut down in 2019
  with no successor, so the preservation defense is strong.
- Short UI strings (item names, skill names, menu labels) have weak-to-no
  copyright protection individually.

**Practical guidance**: commit JP source freely for item names, skill names,
armor/weapon names, and UI strings. Be more deliberate about bulk-importing
**scenario scripts, NPC monologues, and quest dialogue** — these are the only
category where the creative-content argument has any weight. Even there, the
risk is low; just avoid pasting huge blocks into public issue trackers or
commit messages where they'd be indexed without context.

## Layout

```
translations/
  fr/                 ← French (primary; currently empty post-migration)
  en/                 ← English (~74% coverage, carried from legacy bootstrap)
scripts/
  validate.py         ← CSV format check (header + index + uniqueness)
  stats.py            ← coverage report → stats.json
  export_json.py      ← bundle as translations.json
  migrate_to_index.py ← one-shot: rewrite legacy location-keyed CSVs as index-keyed
  build_bins.py       ← apply translations and produce game-ready binaries
```

## Known data quality issues

1. **English-as-source pollution**: the PC `mhfdat-jp.bin` shipped with FTH
   was partially patched by an older English fan-translation, so some
   `pac/text_*`, `jmp/menu/*`, and `dat/items/*` rows still have English
   text in `source` instead of Japanese. The legacy fix used row-index
   matching against the v2064 Wii U dump (cracked with `cdecrypt`) and
   recovered ~130 rows. The remaining ~669 rows in 8 sections with
   mismatched row counts would need sequence alignment or a fresh
   unpatched PC JP dump. After the index-format migration, any future fix
   should re-extract with `--with-index` and run `migrate_to_index.py`.
2. **Dummy rows** (1,211 in `dat/items/source`): literal `dummy` strings in
   the binary. Confirmed as real unimplemented item-source slots — fixed-
   size pointer table padded with `dummy` for unused entries. Safe to leave
   with empty target; they don't render in-game.
3. **Control-code rows** (~6,643): `<join at=...>` glue and color codes —
   not translatable on their own.

## Workflows

```bash
python scripts/validate.py                       # validate all CSVs
python scripts/stats.py                          # regenerate stats.json
python scripts/export_json.py                    # bundle → translations.json

# One-shot legacy migration (from a fork keyed by location)
python scripts/migrate_to_index.py \
    --fth-output ../../tools/FrontierTextHandler/output
```
