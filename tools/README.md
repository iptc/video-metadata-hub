# IPTC Video Metadata Hub - Artifact Generation Tools

**Developer Documentation**

Modern, multi-version system for generating all VMHub artifacts from the
"Video Metadata Hub Working Document" on Google Sheets.

**For maintainers:** See `/MAINTENANCE.md` for the quick start workflow.
**For developers:** This document covers the system architecture and how to extend it.

## Quick Start

### Generate All Artifacts for Default Version

```bash
# From repository root (recommended)
./build_spec.sh

# The script is located at the repository root for easy discovery
```

### Generate for Specific Version

```bash
./build_spec.sh 1.6  # From repository root
```

### Generate Individual Artifacts

```bash
# Properties HTML page
python3 tools/generate_properties_html.py --version 1.7

# JSON Schema
python3 tools/generate_json_schema.py --version 1.7
```

## Architecture

### Single Configuration File

All version configurations are stored in `/vmhub_configuration.json` at the repository root. This includes:
- Version metadata (dates, copyright)
- Google Sheet tab names and ranges
- Column indices (handles schema changes between versions)
- Row ranges
- Feature flags

### Core Library

Located in `tools/lib/`:
- `version_loader.py` - Loads and validates configuration from JSON
- `vmhub_data.py` - Version-aware data loading from Google Sheets
- `constants.py` - Version-independent constants (mappings, categories)
- `credentials.py` - Google Sheets API authentication

### Templates

Located in `tools/templates/`:
- `html/` - HTML page templates (properties, mappings)
- `json/` - JSON Schema template
- `userguide_includes/` - AsciiDoc templates for user guide
- `custom_metadata_panel/` - Adobe Custom Metadata Panel configuration templates
- `techref/` - Tech reference document templates

### Generator Scripts

Each generator is a standalone Python script that:
- Accepts `--version` parameter
- Uses the shared library to load data
- Renders templates with the data
- Outputs to the appropriate location

Available generators:
- `generate_properties_html.py` - Properties specification page
- `generate_json_schema.py` - JSON Schema
- More generators to be added...

## Setup

### 1. Install Dependencies

```bash
cd tools
pip3 install -r requirements.txt
```

### 2. Google Sheets Authentication

1. Download `client_secret.json` from Google Cloud Console
2. Place it in the `tools/` directory
3. First run will prompt for OAuth authentication
4. Token is saved as `token.json` for future use

### 3. Verify Configuration

```bash
python3 tools/lib/version_loader.py
```

This will validate the configuration and show available versions.

## Configuration

### Adding a New Version

Edit `/vmhub_configuration.json` and add a new version entry:

```json
{
  "default_version": "1.8",
  "versions": {
    "1.8": {
      "version": "1.8",
      "approval_date": "DD Month YYYY",
      "revision_date": "DD Month YYYY",
      "copyright_year": "YYYY",
      "header_appendix": "",
      "google_sheet_tabs": {
        "properties": "PropertiesRec 1.8!A3:W",
        "structures": "PropertiesRec 1.8!A109:W236",
        "mappings": "MappingsRec 1.8!A6:V",
        "examples": "Examples!A3:AB99",
        "errata": "PropErrata!A3:E"
      },
      "column_indices": {
        "category": 0,
        "property_name": 2,
        "definition": 4,
        "core_sort": 11,
        ...
      },
      "row_ranges": {
        "first_property_row": 0,
        "last_property_row": 104,
        ...
      },
      "features": {
        "has_core_sort_column": true,
        "supports_custom_panel_core": true
      }
    }
  }
}
```

Then generate artifacts:

```bash
./build_spec.sh 1.8
```

### Column Indices

Column indices are 0-based and correspond to columns in the Google Sheet. Key columns:
- `category` (0): Property group/category
- `property_name` (2): Property name
- `definition` (4): Property definition
- `type_cardinality` (8): Type and cardinality
- `core_sort` (11): Core properties sort order (v1.7+, null for earlier versions)
- `xmp_prop` (14): XMP property name
- `xmp_type` (16): XMP data type
- `json_prop` (18): JSON/PVMD property name
- `json_type` (20): JSON data type

### Feature Flags

- `has_core_sort_column`: Whether this version has the core sort column (v1.7+)
- `supports_custom_panel_core`: Whether core Adobe panel can be generated

## Multi-Version Support

The system is designed to handle multiple versions of VMHub simultaneously:

### Regenerate Old Versions

```bash
# Regenerate v1.6 after fixing a template bug
./build_spec.sh 1.6
```

### Compare Versions

```bash
# Generate two versions side by side
./build_spec.sh 1.6
./build_spec.sh 1.7
```

### Benefits

1. **Single Source of Truth**: Google Sheets remains authoritative
2. **Version Isolation**: Each version has its own configuration
3. **Backward Compatible**: Can regenerate any previous version
4. **Forward Compatible**: Easy to add new versions
5. **Template-Based**: One template works for all versions
6. **Maintainable**: Clear separation of config, code, and templates

## Testing

### Test Data Loading

```bash
python3 tools/lib/vmhub_data.py
```

### Test Version Loading

```bash
python3 tools/lib/version_loader.py
```

### Test Individual Generator

```bash
python3 tools/generate_properties_html.py --version 1.7
```

## Troubleshooting

### "Configuration file not found"

- Ensure `vmhub_configuration.json` exists in the repository root

### "Client secret not found"

- Download `client_secret.json` from Google Cloud Console
- Place in `tools/` directory

### "Version X.X not found"

- Check `vmhub_configuration.json` has an entry for that version
- Use `python3 tools/lib/version_loader.py` to see available versions

### Column Index Errors

- Verify column indices in configuration match the Google Sheet structure
- Remember indices are 0-based
- Column L (core_sort) was added in v1.7; set to `null` for earlier versions

## Development

### Adding a New Generator

1. Create `generate_xxx.py` in `tools/`
2. Import from `lib.version_loader` and `lib.vmhub_data`
3. Accept `--version` parameter
4. Load version config: `get_version_config(version)`
5. Load data using version config
6. Render template or generate output
7. Add to build script

### Adding a New Template

1. Create template in appropriate `tools/templates/` subdirectory
2. Use Jinja2 syntax
3. Accept version-specific variables from config
4. Test with multiple versions

## Repository Structure

```
video-metadata-hub/
├── build_spec.sh                # Build script (top-level)
├── MAINTENANCE.md               # Maintenance workflow (top-level)
├── vmhub_configuration.json     # Configuration (top-level)
├── README.md                    # Repository overview
├── tools/
│   ├── lib/                     # Core library
│   │   ├── version_loader.py   # Config loader
│   │   ├── vmhub_data.py        # Data loading
│   │   ├── constants.py         # Constants
│   │   └── credentials.py       # Google auth
│   ├── templates/               # Jinja2 templates
│   │   ├── html/                # HTML templates
│   │   ├── json/                # JSON templates
│   │   ├── userguide_includes/  # AsciiDoc templates
│   │   ├── custom_metadata_panel/# Adobe panel templates
│   │   └── techref/             # Tech reference templates
│   ├── generate_*.py            # Generator scripts
│   ├── requirements.txt         # Python dependencies
│   ├── README.md                # This file
│   └── legacy/                  # Deprecated old scripts
├── specification/               # Generated artifacts (output)
└── examples/                    # Example videos
```

## License

Copyright © 2025, IPTC - all rights reserved.

Made available under the MIT Licence. See LICENCE.md in the top-level folder for details.

## Support

For issues or questions:
- Check this README
- Review configuration file structure
- Test individual components
- Post to the IPTC public mailing list https://groups.io/g/iptc-videometadata
- Contact IPTC: https://iptc.org/about-iptc/contact-us/
