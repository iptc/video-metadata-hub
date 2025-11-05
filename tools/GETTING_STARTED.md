# Getting Started with the New VMHub Artifact Generation System

## First-Time Setup

### 1. Install Python Dependencies

```bash
cd tools
pip3 install -r requirements.txt
```

This installs:
- Google Sheets API client
- Jinja2 templating engine
- PyYAML
- JSON Schema validation tools

### 2. Setup Google Sheets Authentication

Download credentials from Google Cloud Console:

1. Visit: https://console.cloud.google.com/apis/credentials?project=green-bedrock-150715
2. Download `client_secret.json`
3. Place it in the `tools/` directory

On first run, you'll be prompted to authorize access in your browser. The system will save a `token.json` for future use.

### 3. Verify Everything Works

```bash
# Test configuration loading
python3 lib/version_loader.py

# Test data loading (requires network and auth)
python3 lib/vmhub_data.py
```

## Generate Artifacts

### Quick: Generate Everything

```bash
# From repository root (build_spec.sh is at top level)
./build_spec.sh
```

This generates all artifacts for the default version (currently 1.7):
- Properties HTML page
- All mapping HTML pages  
- JSON Schema

### Generate for Specific Version

```bash
./build_spec.sh 1.6
```

### Generate Individual Artifacts

```bash
# Just the properties page
python3 generate_properties_html.py --version 1.7

# Just the JSON schema
python3 generate_json_schema.py --version 1.7

# Just mappings
python3 generate_mappings_html.py --version 1.7

# Example videos (requires exiftool and source video)
python3 generate_example_videos.py --version 1.7
```

## Updating for a New VMHub Version

When IPTC approves version 1.8:

### Step 1: Update Configuration

Edit `/vmhub_configuration.json` in the repository root:

```json
{
  "default_version": "1.8",
  "versions": {
    "1.8": {
      "version": "1.8",
      "approval_date": "15 May 2026",
      "revision_date": "15 May 2026",
      "copyright_year": "2026",
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
        "category_modified_flag": 1,
        "property_name": 2,
        "property_name_modified_flag": 3,
        "definition": 4,
        "definition_modified_flag": 5,
        "user_notes": 6,
        "user_notes_modified_flag": 7,
        "type_cardinality": 8,
        "type_cardinality_modified_flag": 9,
        "change_notes": 10,
        "core_sort": 11,
        "xmp_prop": 12,
        "xmp_type": 14,
        "json_prop": 16,
        "json_type": 18
      },
      "row_ranges": {
        "first_property_row": 0,
        "last_property_row": 110,
        "first_structure_row": 113,
        "last_structure_row": 245,
        "mappings_first_property_row": 2,
        "mappings_last_property_row": 220
      },
      "features": {
        "has_core_sort_column": true,
        "supports_custom_panel_core": true
      }
    }
  }
}
```

**Notes:**
- Copy the 1.7 entry and modify for 1.8
- Update tab names to match Google Sheet
- Adjust row ranges if the number of properties changed
- Update dates

### Step 2: Generate Artifacts

```bash
cd tools
./build_spec.sh 1.8
```

### Step 3: Validate

```bash
# Check HTML in browser
open ../specification/IPTC-VideoMetadataHub-props-Rec_1.8.html

# Validate JSON Schema
check-jsonschema --schemafile ../specification/iptc-vmhub-1.8-schema.json ../examples/json/VMH-JSON-Examples-*.json
```

### Step 4: Upload to iptc.org

Upload generated files from `specification/` to:
https://www.iptc.org/std/videometadatahub/recommendation/

Archive previous version to:
https://www.iptc.org/std/videometadatahub/recommendation/previous-versions/

See `/MAINTENANCE.md` for complete workflow.

## Troubleshooting

### "Configuration file not found"

Make sure you're running from the `tools/` directory and that `vmhub_configuration.json` exists in the repository root.

### "Client secret not found"

Download `client_secret.json` and place in `tools/` directory.

### "Version X.X not found"

Edit `vmhub_configuration.json` and add that version's configuration.

### Column Index Mismatch

If Google Sheet structure changes:
1. Note which column was added/removed
2. Update column indices in configuration for that version
3. All indices after the change need to shift

### Import Errors

Install dependencies: `pip3 install -r requirements.txt`

## Tips

- Always test with `./build_spec.sh` before uploading to iptc.org
- Keep old version configs in `vmhub_configuration.json` for reproducibility
- Test individual generators before running full build
- Review generated HTML in browser to catch formatting issues
- Use `--version` parameter to regenerate old versions after template fixes

## What's Different from the Old System

| Aspect | Old System | New System |
|--------|-----------|------------|
| Configuration | Hardcoded in Python | Single JSON file |
| Column Indices | Scattered in code | Centralized in config |
| HTML Generation | lxml (verbose) | Jinja2 templates |
| Versioning | Edit code files | Edit JSON only |
| Regenerate Old Version | Restore old code | `./build_spec.sh 1.6` |
| Add New Generator | Copy/paste logic | Import library, render template |
| Maintainability | Difficult | Easy |

The new system follows modern software engineering practices and will save significant time on future VMHub releases!

