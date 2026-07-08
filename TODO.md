# IPTC Video Metadata Hub - Remaining Work

**Last Updated:** November 5, 2025  
**Current Version:** 1.7

This document tracks remaining work for the VMHub artifact generation system.

---

## ✅ Completed Work

### Core Infrastructure
- ✅ Single JSON configuration system (`vmhub_configuration.json`)
- ✅ Shared library (`/tools/lib/`)
  - ✅ `version_loader.py` - Multi-version configuration
  - ✅ `vmhub_data.py` - Data loading from Google Sheets
  - ✅ `constants.py` - Version-independent constants
  - ✅ `credentials.py` - Google Sheets authentication
- ✅ Virtual environment setup with dependency management
- ✅ Build script automation

### Specification Generators
- ✅ `generate_properties_html.py` - Properties HTML page
- ✅ `generate_mappings_html.py` - All mapping pages (XMP, JSON, ExifTool, etc.)
- ✅ `generate_json_schema.py` - JSON Schema generation
- ✅ `generate_example_videos.py` - Example videos with metadata

### User Guide Generators
- ✅ `generate_userguide_properties.py` - Properties AsciiDoc include
- ✅ `generate_userguide_structures.py` - Structures AsciiDoc include
- ✅ `generate_userguide_examples.py` - 6 use-case example files

### Build System
- ✅ `build_spec.sh` - Specification artifacts
- ✅ `build_userguide.sh` - User guide artifacts  
- ✅ `build_all.sh` - Complete build orchestration

### Documentation
- ✅ `/README.md` - Repository overview
- ✅ `/MAINTENANCE.md` - Maintenance workflow
- ✅ `/tools/README.md` - Developer documentation
- ✅ `/IMPLEMENTATION_SUMMARY.md` - System implementation details
- ✅ `/TESTING_COMPLETE.md` - Test results

---

## 📋 TODO: High Priority

### 1. Tech Reference Generator

**Goal:** Generate IPTC Photo Metadata technical reference YAML files for ExifTool

**Status:** ⏳ Not Started

**Location:** `/make-techreference/`

**Tasks:**
- [ ] Review existing `build_iptc_pmd_techreference_v05.py` (legacy)
- [ ] Create new `generate_techreference.py` in `/tools/`
- [ ] Integrate with shared library (`lib/vmhub_data.py`)
- [ ] Create Jinja2 templates in `/tools/templates/techref/`
  - [ ] `iptc-pmd-techreference.yml` - Main template
  - [ ] `et_topwithprefix.yml` - ExifTool top-level with prefix
  - [ ] `et_topnoprefix.yml` - ExifTool top-level without prefix
  - [ ] `ipmd_struct1.yml` - Structure template
  - [ ] `ipmd_struct2.yml` - Alternative structure template
- [ ] Update `vmhub_configuration.json` with tech reference settings
- [ ] Integrate into `build_spec.sh`
- [ ] Test with ExifTool
- [ ] Document in `tools/README.md`

**Output Files:**
- `specification/vmhub-techref-<version>-full.json` - Complete tech reference (JSON format)
- `specification/vmhub-techref-<version>-core.json` - Core properties only
- Various YAML files for ExifTool

**Reference:**
- Existing work in `/make-techreference/`
- Templates in `/make-techreference/templates/`

---

### 2. Adobe Custom Metadata Panel Generators

**Goal:** Generate Adobe Premiere Pro custom metadata panel configurations

**Status:** ⏳ Not Started

**Location:** `/adobe-custom-metadata-panel/` exists with one manual file

**Tasks:**

#### 2.1 Core Properties Panel
- [ ] Create `generate_custom_panel_core.py` in `/tools/`
- [ ] Create Jinja2 template in `/tools/templates/custom_metadata_panel/`
  - [ ] `iptc-vmhub-core.json` template
- [ ] Filter properties where `sort_order` starts with "core"
- [ ] Generate Adobe XMP panel JSON format
- [ ] Test in Adobe Premiere Pro
- [ ] Output: `adobe-custom-metadata-panel/iptc-vmhub-core-{version}.json`

#### 2.2 Full Properties Panel
- [ ] Create `generate_custom_panel_full.py` in `/tools/`
- [ ] Create Jinja2 template
  - [ ] `iptc-vmhub-full.json` template
- [ ] Include all properties (not just core)
- [ ] Test in Adobe Premiere Pro
- [ ] Output: `adobe-custom-metadata-panel/iptc-vmhub-full-{version}.json`

#### 2.3 Integration
- [ ] Add to `build_spec.sh`
- [ ] Update `vmhub_configuration.json` with panel settings
- [ ] Document usage in `tools/README.md`
- [ ] Create installation instructions for Adobe users

**Reference:**
- Existing file: `adobe-custom-metadata-panel/iptc-vmhub-core-1.0.json`
- Adobe XMP panel documentation

---

### 3. Example Videos Enhancement

**Goal:** Create comprehensive example videos with full metadata

**Status:** ⚠️ Partially Complete (minimal examples exist)

**Current:** `generate_example_videos.py` creates basic examples

**Tasks:**
- [ ] Expand example video generation with rich metadata
  - [ ] Use full property sets from Google Sheets examples
  - [ ] Create different examples for each use case:
    - [ ] News agency example
    - [ ] Stock footage example
    - [ ] GLAM (Galleries, Libraries, Archives, Museums) example
    - [ ] Enterprise advertising/production example
    - [ ] Long-form production example
    - [ ] Broadcast media management example
- [ ] Embed metadata using ExifTool
- [ ] Validate embedded metadata
- [ ] Create reference videos for each VMHub version
- [ ] Document expected metadata values
- [ ] Add to automated testing

**Output Location:** `/examples/`

**Output Files:**
- `IPTC-VMHub-RefVideo-NewsAgency-v{version}.mp4`
- `IPTC-VMHub-RefVideo-Stock-v{version}.mp4`
- `IPTC-VMHub-RefVideo-GLAM-v{version}.mp4`
- Etc.

---

### 4. JSON Example Validation

**Goal:** Ensure all JSON examples validate against the generated schema

**Status:** ⚠️ Needs Work

**Current Issues:**
- JSON examples exist in `/examples/json/`
- JSON schema is generated
- Need to ensure examples validate

**Tasks:**
- [ ] Review all JSON example files:
  - [ ] `VMH-JSON-Examples-newsagency.json`
  - [ ] `VMH-JSON-Examples-eaprod.json`
  - [ ] `VMH-JSON-Examples-glam.json`
  - [ ] `VMH-JSON-Examples-stock.json`
  - [ ] `minimal-example.json`
- [ ] Run validation against generated schema:
  ```bash
  check-jsonschema --schemafile specification/iptc-vmhub-1.7-schema.json examples/json/*.json
  ```
- [ ] Fix any validation errors in examples
- [ ] Update example generator if needed
- [ ] Create validation test script
- [ ] Add to build process
- [ ] Document example structure in user guide

**Validation Command:**
```bash
cd /tools
python3 -c "
import json
from jsonschema import validate, ValidationError

schema = json.load(open('../specification/iptc-vmhub-1.7-schema.json'))
examples = [
    '../examples/json/VMH-JSON-Examples-newsagency.json',
    '../examples/json/VMH-JSON-Examples-stock.json',
]

for example_file in examples:
    try:
        example = json.load(open(example_file))
        validate(instance=example, schema=schema)
        print(f'✓ {example_file} is valid')
    except ValidationError as e:
        print(f'✗ {example_file} failed: {e.message}')
"
```

---

### 5. Automated Deployment with Ansible

**Goal:** Automate deployment to iptc.org website using Ansible

**Status:** ⏳ Not Started

**Tasks:**

#### 5.1 Ansible Setup
- [ ] Create `ansible/` directory in repository root
- [ ] Create Ansible inventory file:
  - [ ] `ansible/inventory/production.yml` - Production hosts
  - [ ] `ansible/inventory/staging.yml` - Staging/test hosts
- [ ] Create `ansible/ansible.cfg` configuration
- [ ] Set up SSH key authentication for deployment user
- [ ] Document Ansible requirements in `/MAINTENANCE.md`

#### 5.2 Specification Deployment Playbook
- [ ] Create `ansible/deploy_spec.yml` playbook
  - [ ] Pre-deployment validation tasks:
    - [ ] Verify files exist locally
    - [ ] Check file sizes are reasonable
    - [ ] Require explicit version parameter
    - [ ] Confirm deployment target
  - [ ] Backup tasks:
    - [ ] Create backup of existing files on remote server
    - [ ] Move old versions to `previous-versions/` subdirectory
  - [ ] Deployment tasks:
    - [ ] Upload to `https://www.iptc.org/std/videometadatahub/recommendation/`
    - [ ] Set correct file permissions (644 for files, 755 for directories)
    - [ ] Create symlinks for "latest" version (optional)
  - [ ] Post-deployment tasks:
    - [ ] Verify files deployed successfully
    - [ ] Log deployment history
    - [ ] Generate deployment report
- [ ] Create Ansible role: `ansible/roles/vmhub_spec/`
  - [ ] `tasks/main.yml` - Main deployment tasks
  - [ ] `handlers/main.yml` - Handlers (if needed)
  - [ ] `defaults/main.yml` - Default variables
  - [ ] `templates/` - Any config templates

**Files to Deploy:**
- `IPTC-VideoMetadataHub-props-Rec_{version}.html`
- `iptc-vmhub-{version}-schema.json`
- All mapping HTML files
- Tech reference files (when complete)

#### 5.3 User Guide Deployment Playbook
- [ ] Create `ansible/deploy_userguide.yml` playbook
  - [ ] Upload HTML, images, and stylesheets
  - [ ] Set proper file permissions
  - [ ] Create versioned archives
  - [ ] Handle GitHub Pages deployment (if applicable)
- [ ] Create Ansible role: `ansible/roles/vmhub_userguide/`

#### 5.4 Adobe Custom Panel Deployment
- [ ] Create `ansible/deploy_adobe_panels.yml` playbook
  - [ ] Deploy to appropriate download location
  - [ ] Create version-specific directories
  - [ ] Update "latest" symlinks

#### 5.5 Master Deployment Playbook
- [ ] Create `ansible/deploy_all.yml`
  - [ ] Import specification playbook
  - [ ] Import user guide playbook
  - [ ] Import Adobe panels playbook
  - [ ] Send notification emails (optional)
  - [ ] Slack/webhook notifications (optional)

#### 5.6 Deployment Configuration & Variables
- [ ] Create `ansible/group_vars/all.yml`:
  ```yaml
  vmhub_version: "{{ version | default('1.7') }}"
  
  deployment:
    spec:
      host: www.iptc.org
      remote_path: /var/www/html/std/videometadatahub/recommendation/
      remote_user: deploy
    userguide:
      host: www.iptc.org
      remote_path: /var/www/html/std/videometadatahub/userguide/
      remote_user: deploy
    backup_dir: /var/backups/vmhub/
  ```
- [ ] Create `ansible/group_vars/production.yml` - Production-specific vars
- [ ] Create `ansible/group_vars/staging.yml` - Staging-specific vars
- [ ] Add deployment settings reference to `vmhub_configuration.json`
- [ ] Secure credential storage using Ansible Vault:
  - [ ] `ansible/vault/production.yml` (encrypted)
  - [ ] `.gitignore` entry for vault password file

#### 5.7 Deployment Wrapper Scripts
- [ ] Create `deploy.sh` wrapper script:
  ```bash
  #!/bin/bash
  # Usage: ./deploy.sh [spec|userguide|all] [version] [environment]
  # Examples:
  #   ./deploy.sh all 1.7 production
  #   ./deploy.sh spec 1.7 staging
  ```
  - [ ] Activates virtual environment
  - [ ] Builds artifacts if needed
  - [ ] Runs appropriate Ansible playbook
  - [ ] Displays deployment summary

#### 5.8 Ansible Testing & Validation
- [ ] Add dry-run/check mode support:
  ```bash
  ansible-playbook ansible/deploy_all.yml --check --diff
  ```
- [ ] Create `ansible/test.yml` playbook for validation
- [ ] Test deployments to staging environment
- [ ] Document rollback procedures

**Security Considerations:**
- [ ] Use SSH keys (not passwords) for all deployments
- [ ] Use Ansible Vault for sensitive credentials
- [ ] Store vault password outside repository
- [ ] Implement `--check` mode for dry runs
- [ ] Add confirmation prompts in wrapper script
- [ ] Log all deployments with timestamps
- [ ] Restrict deployment user permissions on server
- [ ] Use become/sudo only where necessary

**Ansible Requirements:**
- [ ] Add to documentation:
  - [ ] Ansible >= 2.9
  - [ ] Python >= 3.8 on control node
  - [ ] SSH access to deployment servers
  - [ ] Installation: `pip install ansible`

---

## 📋 TODO: Medium Priority

### 6. Historical Version Support

**Goal:** Add configurations for older VMHub versions

**Status:** ⏳ Not Started

**Tasks:**
- [ ] Research version 1.3 schema
  - [ ] Google Sheet structure
  - [ ] Column indices
  - [ ] Feature flags
- [ ] Research version 1.4
- [ ] Research version 1.5
- [ ] Research version 1.6
- [ ] Add each to `vmhub_configuration.json`
- [ ] Test regeneration of old versions
- [ ] Archive old version outputs

**Benefits:**
- Regenerate old versions if needed
- Test backward compatibility
- Maintain historical record

---

### 7. Interactive Generator Web UI

**Goal:** Update the interactive generator at `/generator/`

**Status:** ⏳ Not Started

**Current:** `/generator/IPTC-VMHub-generator.html` exists but may be outdated

**Tasks:**
- [ ] Review current generator functionality
- [ ] Add new AI-related properties from version 1.7
- [ ] Test in modern browsers
- [ ] Update styling with modern CSS
- [ ] Add export functionality:
  - [ ] Export as JSON
  - [ ] Export as XMP
  - [ ] Export for ExifTool
- [ ] Document in user guide
- [ ] Deploy to iptc.org

---

### 8. Testing Suite

**Goal:** Automated testing for generators

**Status:** ⏳ Not Started

**Tasks:**
- [ ] Create `tests/` directory
- [ ] Unit tests for library functions:
  - [ ] `test_version_loader.py`
  - [ ] `test_vmhub_data.py`
  - [ ] `test_constants.py`
- [ ] Integration tests:
  - [ ] `test_spec_generators.py`
  - [ ] `test_userguide_generators.py`
- [ ] End-to-end tests:
  - [ ] `test_build_spec.py`
  - [ ] `test_build_userguide.py`
- [ ] Output validation:
  - [ ] HTML validation
  - [ ] JSON Schema validation
  - [ ] YAML validation
- [ ] Add pytest to `requirements.txt`
- [ ] Create `run_tests.sh`
- [ ] Add to CI/CD (if using)

---

### 9. C2PA Integration

**Goal:** Support Coalition for Content Provenance and Authenticity

**Status:** 📁 Examples exist at `/examples/c2pa/`

**Tasks:**
- [ ] Review C2PA examples
- [ ] Document C2PA workflow
- [ ] Create C2PA example generator
- [ ] Add to user guide
- [ ] Test with C2PA tools

---

### 10. Error Recovery & Robustness

**Goal:** Improve error handling and recovery

**Tasks:**
- [ ] Add retry logic for Google Sheets API
- [ ] Handle network failures gracefully
- [ ] Validate all data before processing
- [ ] Add schema validation for configuration
- [ ] Better error messages
- [ ] Logging system
- [ ] Debug mode flag

---

## 📋 TODO: Low Priority / Nice to Have

### 11. Performance Optimization

- [ ] Cache Google Sheets data
- [ ] Parallel generation of artifacts
- [ ] Incremental builds (only regenerate changed files)
- [ ] Build time metrics

### 12. Additional Output Formats

- [ ] Generate PDF user guide
- [ ] Generate markdown documentation
- [ ] Generate CSV property lists
- [ ] RDF/Linked Data output

### 13. Translation Support

- [ ] Multi-language property definitions
- [ ] Internationalized user guide
- [ ] Translation workflow

### 14. Quality Assurance Tools

- [ ] Link checker for generated HTML
- [ ] Spell checker for descriptions
- [ ] Consistency checker (naming conventions)
- [ ] Duplicate property detector

---

## 🎯 Recommended Implementation Order

### Phase 1: Core Functionality (High Value, High Impact)
1. **JSON Example Validation** (Quick win, ensures quality)
2. **Tech Reference Generator** (Completes core artifact set)
3. **Adobe Custom Metadata Panel** (High user demand)

### Phase 2: Production Readiness
4. **Automated Deployment Scripts** (Saves time, reduces errors)
5. **Example Videos Enhancement** (Improves documentation quality)
6. **Testing Suite** (Prevents regressions)

### Phase 3: Completeness
7. **Historical Version Support** (Nice to have)
8. **Interactive Generator Update** (User-facing tool)
9. **Error Recovery** (Production hardening)

### Phase 4: Enhancement
10. **C2PA Integration** (Emerging standard)
11. **Performance Optimization** (As needed)
12. **Additional Features** (As requested)

---

## 📊 Progress Tracking

### Overall Completion: ~60%

| Category | Progress | Notes |
|----------|----------|-------|
| Core Infrastructure | ✅ 100% | Complete |
| Specification Generators | ✅ 100% | Complete |
| User Guide Generators | ✅ 100% | Complete |
| Tech Reference | ⏳ 0% | Not started |
| Adobe Custom Panels | ⏳ 0% | Not started |
| Example Videos | ⚠️ 30% | Basic only |
| JSON Validation | ⚠️ 50% | Needs verification |
| Deployment | ⏳ 0% | Not started |
| Testing | ⏳ 0% | Not started |
| Documentation | ✅ 90% | Mostly complete |

---

## 🚀 Quick Wins (Low Effort, High Value)

1. **JSON Example Validation** - 1-2 hours
   - Run validation
   - Fix any errors
   - Add to build script

2. **Deployment Script (Basic)** - 2-4 hours
   - Simple rsync/scp script
   - Safety checks
   - Documentation

3. **Historical Versions** - 4-6 hours per version
   - Add config to JSON
   - Test generation
   - Archive outputs

---

## 📝 Notes

### Spec vs ExifTool discrepancies

Properties where the VMHub spec and ExifTool's serialisation differ.
Useful context when discussing future spec revisions or filing ExifTool
patches. The code-side workarounds live in `tools/lib/exiftool_tags.py`.

- **VideoDisplayAspectRatio**, **VideoPixelAspectRatio**: VMHub previously
  typed these as String (e.g. `"16:9"`). ExifTool implements them as
  decimal (`iptcExt`) / Rational struct (`xmpDM`). Spec updated to decimal
  to match implementation reality.
- **MetadataAuthority** (`XMP-iptcExt`): defined in the IPTC spec but not
  yet implemented in ExifTool. Listed in `EXIFTOOL_UNSUPPORTED_TAGS` in
  `tools/lib/exiftool_tags.py` so `generate_example_videos.py` skips it
  cleanly with a clear reason in the run summary. Re-check on each
  ExifTool release and remove from the set when support lands.
- **PLUS struct field naming**: PLUS structures flatten field names with
  the parent tag's local name as prefix (e.g. `CopyrightOwnerName` inside
  `XMP-plus:CopyrightOwner`), while IPTC Extension structures using the
  same logical struct type (e.g. `EntityWRole` inside `XMP-iptcExt:Creator`)
  use bare field names (`Name`). Handled via the
  `STRUCT_FIELD_OVERRIDES` table in `tools/lib/exiftool_tags.py`; add
  entries there when new PLUS-namespaced struct tags surface.

### Version 1.8 Preparation

When version 1.8 is ready:
- Update `vmhub_configuration.json` default_version
- Add v1.8 configuration block
- Run `./build_all.sh 1.8`
- Validate all outputs
- Deploy using deployment scripts (when available)

### Maintenance Frequency

**Regular (Weekly/Monthly):**
- Regenerate artifacts if Google Sheet changes
- Validate JSON examples
- Update version dates

**Per Version (Every ~6 months):**
- Add new version to configuration
- Generate all artifacts
- Deploy to iptc.org
- Archive previous version

---

**Last Updated:** November 5, 2025  
**Next Review:** When starting next task  
**Maintainer:** Brendan Quinn, IPTC

