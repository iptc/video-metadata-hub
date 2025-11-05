# video-metadata-hub
Specification and examples for IPTC's Video Metadata Hub

## Quick Start - Generate All Artifacts for Latest Version

```bash
./build_all.sh
```

This generates both specification and user guide artifacts from the IPTC Video Metadata Working Group's Google Sheets data source.

You can also generate artifacts separately:
- `./build_spec.sh` - Specification artifacts only (HTML, JSON Schema, examples)
- `./build_userguide.sh` - User guide artifacts only (AsciiDoc includes and HTML)

## Specification (aka Recommendation)

The `specification` folder contains the HTML files used on https://iptc.org/std/videometadatahub/recommendation/

These are generated from Google Sheets using the modern tooling in `tools/`. 

**First time setup:**
```bash
# Create virtual environment and install dependencies
python3 -m venv venv
source venv/bin/activate
pip install -r tools/requirements.txt
```

For more information, see:
- **`MAINTENANCE.md`** - How to maintain and generate new versions (start here!)
- **`tools/README.md`** - Developer documentation and system architecture

## Example files

The `examples` folder provides small video files with embedded IPTC Video Metadata Hub properties in various formats.

## System Architecture

- **Configuration**: `vmhub_configuration.json` - All version settings
- **Tools**: `tools/` - Generator scripts and shared library
- **Build Scripts**: 
  - `build_all.sh` - Generate all artifacts (specification + user guide)
  - `build_spec.sh` - Generate specification artifacts only
  - `build_userguide.sh` - Generate user guide artifacts only
- **Output**: 
  - `specification/` - Generated specification artifacts
  - `video-metadata-guidelines/` - User guide (AsciiDoc and HTML)
