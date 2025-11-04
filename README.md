# video-metadata-hub
Specification and examples for IPTC's Video Metadata Hub

## Quick Start - Generate Artifacts for Latest Version

```bash
./build_spec.sh
```

This generates all specification artifacts from the IPTC Video Metadata Working Group's Google Sheets data source.

## Specification (aka Recommendation)

The `specification` folder contains the HTML files used on https://iptc.org/std/videometadatahub/recommendation/

These are generated from Google Sheets using the modern tooling in `tools/`. See:
- `MAINTENANCE.md` - Version update workflow
- `tools/README.md` - Complete documentation
- `tools/GETTING_STARTED.md` - Quick start guide

## Example files

The `examples` folder provides small video files with embedded IPTC Video Metadata Hub properties in various formats.

## System Architecture

- **Configuration**: `vmhub_configuration.json` - All version settings
- **Tools**: `tools/` - Generator scripts and shared library
- **Build**: `build_spec.sh` - One-command artifact generation
- **Output**: `specification/` - Generated artifacts
