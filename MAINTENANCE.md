Maintenance of Video Metadata Hub Specification Files
=====================================================

**This document describes the modernized artifact generation system.**

For detailed documentation, see `/tools/README.md`

## Quick Start

### Setup (First Time)

1. Install Python dependencies:
   ```bash
   cd tools
   pip3 install -r requirements.txt
   ```

2. Download Google Sheets credentials:
   - Visit: https://console.cloud.google.com/apis/credentials?project=green-bedrock-150715
   - Download `client_secret.json`
   - Place in `tools/` directory

3. Verify configuration:
   ```bash
   cd tools
   python3 lib/version_loader.py
   ```

### Generate Artifacts for a New Version

The system uses `/vmhub_configuration.json` for all version settings.

#### 1. Update Configuration

Edit `/vmhub_configuration.json` in the repository root:
- Update `default_version` to the new version (e.g., "1.8")
- Add a new version entry with all settings (dates, sheet tabs, column indices)
- See existing versions for template

#### 2. Generate All Artifacts

```bash
# From repository root
./build_spec.sh 1.8
```

This generates:
- Properties HTML page: `IPTC-VideoMetadataHub-props-Rec_1.8.html`
- JSON Schema: `iptc-vmhub-1.8-schema.json`
- All mapping pages
- (More generators to be added)

#### 3. Validate Outputs

- Open HTML page in browser - check formatting, version numbers, content
- Validate JSON Schema:
  ```bash
  check-jsonschema --schemafile specification/iptc-vmhub-1.8-schema.json examples/json/VMH-JSON-Examples-*
  ```
- Review for new/modified property highlighting

#### 4. Upload to iptc.org

Upload files to https://www.iptc.org/std/videometadatahub/recommendation/

Move previous version files to:
https://www.iptc.org/std/videometadatahub/recommendation/previous-versions/

## Multi-Version Support

You can regenerate artifacts for any configured version:

```bash
# From repository root
./build_spec.sh 1.7  # Regenerate version 1.7
./build_spec.sh 1.6  # Regenerate version 1.6
```

## System Architecture

The new system consists of:
- **Configuration**: `/vmhub_configuration.json` - all version settings
- **Shared Library**: `/tools/lib/` - reusable data loading code
- **Templates**: `/tools/templates/` - Jinja2 templates for all outputs
- **Generators**: `/tools/generate_*.py` - scripts to create each artifact
- **Build Script**: `/build_spec.sh` - orchestrates generators

## Migration from Old System

Old scripts have been moved to `/tools/legacy/` and are deprecated. The old system used hardcoded column indices and lxml. The new system is template-based and supports multiple versions through configuration.

## For Complete Documentation

See `/tools/README.md` for:
- Detailed usage instructions
- Multi-version support details
- How to add new generators
- Troubleshooting guide
- Development guidelines

