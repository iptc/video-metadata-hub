# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

This repo produces the published artifacts of the **IPTC Video Metadata Hub (VMHub)** specification. The authoritative source of metadata definitions is the Google Sheet "Video Metadata Hub Working Document"; everything in `specification/`, `user-guide/`, and the example files is **generated** from that sheet via Python scripts in `tools/`. There is no application to run — the deliverables are static HTML, JSON Schema, AsciiDoc, and example video files.

## Common commands

All build scripts live at the repo root and must be run from there. They auto-activate `venv/` if present.

```bash
./build_all.sh [version]        # Spec + user guide
./build_spec.sh [version]       # Specification artifacts only
./build_userguide.sh [version]  # User guide only (runs generators + asciidoctor)
```

If `version` is omitted, `default_version` from `vmhub_configuration.json` is used. The same scripts can regenerate any older configured version (e.g. `./build_spec.sh 1.6`).

Run an individual generator (useful when iterating on one output):

```bash
python3 tools/generate_properties_html.py --version 1.7
python3 tools/generate_json_schema.py --version 1.7
python3 tools/generate_custom_panel.py --version 1.7 --panel-type core   # also: --panel-type full
```

Validate / inspect:

```bash
python3 tools/lib/version_loader.py       # validate config, list versions
python3 tools/lib/vmhub_data.py           # smoke-test Google Sheets data load
check-jsonschema --schemafile specification/iptc-vmhub-1.7-schema.json examples/json/VMH-JSON-Examples-*
```

First-time setup:

```bash
python3 -m venv venv && source venv/bin/activate
pip install -r tools/requirements.txt
# Then place client_secret.json (from Google Cloud Console, project green-bedrock-150715) in tools/
```

Google OAuth runs on first invocation and writes `tools/token.json`.

## Architecture

The system is a **config-driven, version-aware Jinja2 template renderer over a Google Sheets data source**. There is one piece of state — `vmhub_configuration.json` — that controls everything; the generators are otherwise version-agnostic.

**Data flow per generator:**
1. `argparse` reads `--version` (falls back to `default_version`).
2. `tools/lib/version_loader.py` loads the version's entry from `vmhub_configuration.json` (sheet tab ranges, **column indices**, row ranges, feature flags, dates).
3. `tools/lib/vmhub_data.py` fetches rows from the Google Sheet using those tab/range strings, indexing columns via the configured indices.
4. `tools/lib/constants.py` supplies cross-version constants (mapping target names, category labels).
5. The generator renders a Jinja2 template from `tools/templates/<kind>/` and writes the output.

**Why column indices live in config:** The Google Sheet's column layout shifts between VMHub versions (e.g. column L `core_sort` was added in v1.7). Each version's `column_indices` block remaps logical fields → sheet column positions, so the same generator code handles all versions. When adding a new VMHub version, the most error-prone step is getting these indices right — if a column was inserted, every index after it shifts by 1.

**Feature flags** (`features` block per version) gate version-specific output, e.g. `has_core_sort_column`, `supports_custom_panel_core`.

**Generators and their outputs:**

| Generator | Output |
|---|---|
| `generate_properties_html.py` | `specification/IPTC-VideoMetadataHub-props-Rec_<v>.html` |
| `generate_mappings_html.py` | XMP / JSON / ExifTool / etc. mapping HTML pages |
| `generate_json_schema.py` | `specification/iptc-vmhub-<v>-schema.json` |
| `generate_techreference.py` | Tech reference docs (Photo-Metadata-Tech-Reference style) |
| `generate_custom_panel.py` | Adobe Bridge / Premiere custom metadata panel JSON (core + full) |
| `generate_example_videos.py` | Example `.mp4` files with embedded metadata (in `examples/`) |
| `generate_userguide_properties.py` | `user-guide/_includes/properties.adoc` |
| `generate_userguide_structures.py` | `user-guide/_includes/structures.adoc` |
| `generate_userguide_examples.py` | 6 example `.adoc` includes for different use cases |

The user-guide build then runs `user-guide/asciidoctor-to-html.sh` to produce `user-guide/index.html` from `IPTC-VideoMetadata-UserGuide.adoc` + the generated `_includes/`.

**`generator/`** is a separate, unrelated artifact — a static JS-based "metadata generator" web tool, not part of the build pipeline.

## Adding a new VMHub version

1. Edit `vmhub_configuration.json`: bump `default_version`, copy the previous version block, update `approval_date` / `revision_date` / `copyright_year`, update `google_sheet_tabs` to point at the new `PropertiesRec X.Y` / `MappingsRec X.Y` tabs, **recheck every `column_indices` value against the sheet**, update `row_ranges`, set `features` flags.
2. `python3 tools/lib/version_loader.py` to validate.
3. `./build_all.sh X.Y`.

See `MAINTENANCE.md` for the publishing workflow (upload destination on iptc.org, previous-versions archive).

## Notes for editing

- Templates are Jinja2; the spec HTML and user-guide AsciiDoc templates intentionally share structure so the same data shape can drive both.
- `tools/lib/constants.py` is the right place for anything truly version-independent (e.g. mapping target identifiers). Anything that *might* differ between versions belongs in `vmhub_configuration.json`, not constants.
- `client_secret.json` and `token.json` in `tools/` are gitignored credentials — never commit.
