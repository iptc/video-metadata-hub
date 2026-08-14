#!/usr/bin/env python3
"""
Generate VMHub Tech Reference Files

Generates technical reference files in JSON and YAML formats for ExifTool
"""

import argparse
import json
import os
import re
from datetime import datetime, timezone
from jinja2 import Environment, FileSystemLoader

from lib.version_loader import get_version_config, list_available_versions
from lib.credentials import get_credentials
from lib.vmhub_data import load_properties_data, load_structures_data, filter_core_properties

try:
    import yaml
except ImportError:
    yaml = None
    print("Warning: pyyaml not installed. YAML output will be disabled.")
    print("Install with: pip install pyyaml")


def parse_type_cardinality(type_card_str):
    """
    Parse type/cardinality string from Google Sheets
    
    Examples:
        "Text / 0..1" -> {"datatype": "Text", "occurrence": "0..1"}
        "URI / 1..n" -> {"datatype": "URI", "occurrence": "1..n"}
        "Entity Structure / 0..n" -> {"datatype": "Entity Structure", "occurrence": "0..n"}
    
    Args:
        type_card_str: Type/cardinality string
        
    Returns:
        Dict with datatype and occurrence keys
    """
    if not type_card_str:
        return {}
    
    # Split on / and strip whitespace
    parts = [p.strip() for p in type_card_str.split('/')]
    
    result = {}
    if len(parts) >= 1:
        result['datatype'] = parts[0]
    if len(parts) >= 2:
        result['occurrence'] = parts[1]
    
    return result


def prepare_properties_for_template(properties, version_config):
    """
    Prepare properties data for template rendering
    
    Args:
        properties: List of property category dicts
        version_config: Version configuration
        
    Returns:
        List of property dicts with all necessary fields
    """
    template_props = []
    
    for category in properties:
        for prop in category['properties']:
            # Parse type/cardinality
            type_info = parse_type_cardinality(prop.get('type_cardinality', ''))
            
            template_prop = {
                'anchor': prop['anchor'],
                'name': prop['name'],
                'definition': prop.get('definition', ''),
                'category_id': category['id'],
                'sort_order': prop.get('sort_order', ''),
                'datatype': type_info.get('datatype', ''),
                'occurrence': type_info.get('occurrence', ''),
                'xmp_id': prop.get('xmp_id', ''),
                'exiftool_id': prop.get('exiftool_tag', '')
            }
            
            template_props.append(template_prop)
    
    return template_props


def prepare_structures_for_template(structures, version_config):
    """
    Prepare structures data for template rendering
    
    Args:
        structures: List of structure dicts
        version_config: Version configuration
        
    Returns:
        List of structure dicts with all necessary fields
    """
    template_structs = []
    
    for struct in structures:
        template_struct = {
            'anchor': struct['anchor'],
            'name': struct['name'],
            'properties': []
        }
        
        for prop in struct['properties']:
            # Parse type/cardinality
            type_info = parse_type_cardinality(prop.get('type_cardinality', ''))
            
            template_prop = {
                'anchor': prop['anchor'],
                'name': prop['name'],
                'definition': prop.get('definition', ''),
                'sort_order': prop.get('sort_order', ''),
                'datatype': type_info.get('datatype', ''),
                'occurrence': type_info.get('occurrence', ''),
                'xmp_id': prop.get('xmp_id', ''),
                'exiftool_id': prop.get('exiftool_tag', '')
            }
            
            template_struct['properties'].append(template_prop)
        
        template_structs.append(template_struct)
    
    return template_structs


def generate_techreference(version=None, output_dir=None, core_only=False):
    """
    Generate tech reference files for specified version
    
    Args:
        version: Version string (e.g., "1.7"). If None, uses default
        output_dir: Output directory. If None, uses ../specification/
        core_only: If True, generates only core properties
        
    Returns:
        List of generated file paths
    """
    # Load version configuration
    print(f"Loading configuration for version {version or 'default'}...")
    version_config = get_version_config(version)
    version = version_config['version']
    print(f"✓ Using version {version}")
    
    # Get credentials
    print("Authenticating with Google Sheets...")
    credentials = get_credentials()
    print("✓ Authenticated")
    
    # Load data
    print("Loading properties and structures...")
    properties = load_properties_data(version_config, credentials)
    structures = load_structures_data(version_config, credentials)
    
    # Filter to core if requested
    if core_only:
        if not version_config['features'].get('has_core_sort_column'):
            print("✗ Core filtering not supported for this version")
            return None
        print("Filtering to core properties only...")
        properties = filter_core_properties(properties, version_config)
    
    print(f"✓ Loaded {sum(len(cat['properties']) for cat in properties)} properties")
    print(f"✓ Loaded {len(structures)} structures")
    
    # Prepare data for template
    template_props = prepare_properties_for_template(properties, version_config)
    template_structs = prepare_structures_for_template(structures, version_config)
    
    # Build JSON data structure directly (don't use template for JSON)
    timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    
    # Build properties dict
    vmh_top = {}
    for prop in template_props:
        prop_data = {
            'name': prop['name'],
            'definition': prop['definition'],
            'ugtopic': prop['category_id'],
            'sortorder': prop['sort_order'],
            'specidx': f"#{prop['anchor']}"
        }
        if prop['datatype']:
            prop_data['datatype'] = prop['datatype']
        if prop['occurrence']:
            prop_data['propoccurrence'] = prop['occurrence']
        if prop['xmp_id']:
            prop_data['XMPid'] = prop['xmp_id']
        if prop['exiftool_id']:
            prop_data['etXMP'] = prop['exiftool_id']
        
        vmh_top[prop['anchor']] = prop_data
    
    # Build structures dict
    vmh_struct = {}
    for struct in template_structs:
        struct_data = {}
        for prop in struct['properties']:
            prop_data = {
                'name': prop['name'],
                'definition': prop['definition'],
                'sortorder': prop['sort_order'],
                'specidx': f"#{prop['anchor']}"
            }
            if prop['datatype']:
                prop_data['datatype'] = prop['datatype']
            if prop['occurrence']:
                prop_data['propoccurrence'] = prop['occurrence']
            if prop['xmp_id']:
                prop_data['XMPid'] = prop['xmp_id']
            if prop['exiftool_id']:
                prop_data['etXMP'] = prop['exiftool_id']
            
            struct_data[prop['anchor']] = prop_data
        
        vmh_struct[struct['anchor']] = struct_data
    
    # Build complete JSON structure
    json_data = {
        'documentation_available_at': 'https://iptc.org/std/photometadata/documentation/techreference',
        'release_comment': f'IPTC Video Metadata Hub version {version}',
        'release_timestamp': timestamp,
        'vmh_top': vmh_top,
        'vmh_struct': vmh_struct
    }
    
    # Setup output directory
    if output_dir is None:
        output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'specification')
    os.makedirs(output_dir, exist_ok=True)
    
    # Determine file suffix
    suffix = 'core' if core_only else 'full'
    
    # Write JSON output
    json_file = os.path.join(output_dir, f'vmhub-techref-{version}-{suffix}.json')
    
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, indent=2, ensure_ascii=False)
    
    print(f"✓ Generated JSON: {json_file}")
    generated_files = [json_file]
    
    # Write YAML output if pyyaml is available
    if yaml:
        yaml_file = os.path.join(output_dir, f'vmhub-techref-{version}-{suffix}.yml')
        with open(yaml_file, 'w', encoding='utf-8') as f:
            yaml.dump(json_data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
        print(f"✓ Generated YAML: {yaml_file}")
        generated_files.append(yaml_file)
    else:
        print("⚠ Skipped YAML generation (pyyaml not installed)")
    
    return generated_files


def main():
    parser = argparse.ArgumentParser(
        description='Generate VMHub tech reference files from Google Sheets data'
    )
    parser.add_argument(
        '--version',
        help=f'VMHub version to generate (available: {", ".join(list_available_versions())})'
    )
    parser.add_argument(
        '--output-dir',
        help='Output directory (default: ../specification/)'
    )
    parser.add_argument(
        '--core',
        action='store_true',
        help='Generate core properties only (default: all properties)'
    )
    
    args = parser.parse_args()
    
    try:
        # Generate full version
        print("=" * 60)
        print("Generating full tech reference...")
        print("=" * 60)
        full_files = generate_techreference(args.version, args.output_dir, core_only=False)
        
        # Generate core version if supported
        if args.core:
            print("\n" + "=" * 60)
            print("Generating core tech reference...")
            print("=" * 60)
            core_files = generate_techreference(args.version, args.output_dir, core_only=True)
            if core_files:
                full_files.extend(core_files)
        
        if full_files:
            print(f"\n✓ Success! Generated {len(full_files)} file(s)")
            return 0
        else:
            print("\n✗ Failed to generate tech reference files")
            return 1
            
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    exit(main())

