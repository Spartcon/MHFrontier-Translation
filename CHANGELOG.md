# Changelog

All notable changes to MHFrontier-Translation are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/).

Versioning: **MAJOR** = breaking format change, **MINOR** = new translations
or sections, **PATCH** = fixes to existing translations.

## [0.1.0] - 2026-04-12

First tagged release. Requires **FrontierTextHandler >= 1.6.0**.

### Format

- Migrated CSV key format from `location` (byte offsets) to `index`
  (stable pointer-table slots).
- Migrated join markers from `<join at="NNN">` to `{j}`.
- Migrated color codes from `‾CNN` to `{cNN}/{/c}` (ASCII-safe).
- Untranslated rows now have empty `target` instead of copying `source`.

### Added

- **en/**: bootstrapped English translations from patched binary (~42.8%
  coverage, 97,672 / 228,211 translatable strings).
- **fr/**: seeded French item names from Ezemania binary and Spartcon
  import (~1.4% coverage, 3,090 / 228,211 strings).
- `docs/glossary.fr.md`: canonical French terminology reference.
- `docs/style.fr.md`: French style guide (tone, typography, control codes).
- `scripts/validate.py`: CSV format validation.
- `scripts/stats.py`: coverage statistics generator.
- `scripts/export_json.py`: JSON export with per-language gzipped payloads.
- `scripts/build_bins.py`: build game-ready binaries from CSVs.
- `scripts/migrate_to_index.py`: one-shot legacy location-to-index migration.
- `scripts/migrate_join_markers.py`: one-shot `<join>` to `{j}` migration.
- GitHub Pages dashboard with per-section progress bars.
- CI: validation on PRs, rolling + tagged releases with JSON artifacts.

### Fixed

- Recovered 130 JP source rows polluted by old English fan-translation
  (matched against v2064 Wii U dump).
- Realigned 15 misplaced "Monster List book" entries in en/dat/items.
- Repaired 36 truncated `‾C0` terminal color markers.
- Excluded untranslatable rows (control-code-only, dummy, partial
  pass-throughs) from coverage statistics.
