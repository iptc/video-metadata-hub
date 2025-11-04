# Legacy Scripts

**These scripts are deprecated and kept for reference only.**

The artifact generation system has been modernized. Please use the new system documented in `/tools/README.md`.

## Deprecated Files

- `VMHprocessProps1.py` - Replaced by `generate_properties_html.py`
- `VMHprocessMappings1.py` - Replaced by `generate_mappings_html.py`
- `VMHprocessJSONschema1.py` - Replaced by `generate_json_schema.py`
- `VMHprocessJSON-LD1.py` - No longer needed
- `VMHprocessQualVocab1.py` - No longer needed
- `build_iptc_pmd_techreference_v05.py` - Replaced by `generate_techreference.py`

## Migration Notes

The old scripts used:
- Hardcoded column indices
- lxml for HTML generation
- Separate constants for each version
- No version parameterization

The new system uses:
- JSON configuration for all versions
- Jinja2 templates for HTML generation
- Shared library for data loading
- Multi-version support via `--version` parameter

Please do not use these files for new work.

