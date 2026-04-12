# Changelog

All notable changes to MHFrontier-Translation are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/).

Versioning: **MAJOR** = breaking format change, **MINOR** = new translations
or sections, **PATCH** = fixes to existing translations.

## [0.2.0] - 2026-04-12

**Breaking**: requires **FrontierTextHandler >= 1.6.0**.

### Changed

- Migrated join markers from `<join at="NNN">` to `{j}` (477,105 markers
  across 42 files).
- Migrated color codes from `‾CNN` to `{cNN}/{/c}` (ASCII-safe brace form).
- Bumped FTH version requirement from 1.5.1 to 1.6.0 in release workflow.

### Added

- `scripts/migrate_join_markers.py`: one-shot `<join>` to `{j}` migration.

### Fixed

- Repaired 36 truncated `‾C0` terminal color markers.
- Tagged releases now marked as "latest" on GitHub.

## [0.1.0] - 2026-04-12

First tagged release. Requires **FrontierTextHandler >= 1.5.1**.

### Format

- Migrated CSV key format from `location` (byte offsets) to `index`
  (stable pointer-table slots). Indexes survive upstream string-length
  changes that used to shift raw byte offsets.
- Untranslated rows now have empty `target` instead of copying `source`.

### Added

- **en/**: bootstrapped English translations from patched binary (~42.8%
  coverage, 97,672 / 228,211 translatable strings).
- **fr/**: seeded French item names from Ezemania binary and Spartcon
  import (~1.4% coverage, 3,090 / 228,211 strings).
- **fr/**: translated items/name rows 0-150 (consumables, ammo, tools).
- `docs/glossary.fr.md`: canonical French terminology reference.
- `docs/style.fr.md`: French style guide (tone, typography, control codes).
- `scripts/validate.py`: CSV format validation.
- `scripts/stats.py`: coverage statistics generator.
- `scripts/export_json.py`: JSON export with per-language gzipped payloads.
- `scripts/build_bins.py`: build game-ready binaries from CSVs.
- `scripts/migrate_to_index.py`: one-shot legacy location-to-index migration.
- GitHub Pages dashboard with per-section progress bars.
- CI: validation on PRs, rolling + tagged releases with JSON artifacts.

### Fixed

- Recovered 130 JP source rows polluted by old English fan-translation
  (matched against v2064 Wii U dump).
- Realigned 15 misplaced "Monster List book" entries in en/dat/items.
- Excluded untranslatable rows (control-code-only, dummy, partial
  pass-throughs) from coverage statistics.
