#!/usr/bin/env python3
"""
Generate Adobe Custom Metadata Panel Configuration

Generates Adobe Premiere Pro custom metadata panel JSON files
"""

import argparse
import hashlib
import json
import os
import re
from jinja2 import Environment, FileSystemLoader

from lib.version_loader import get_version_config, list_available_versions
from lib.credentials import get_credentials
from lib.vmhub_data import load_properties_data, load_structures_data, filter_core_properties


# XMP namespace mappings
XMP_NAMESPACES = {
    'dc': 'http://purl.org/dc/elements/1.1/',
    'xmp': 'http://ns.adobe.com/xap/1.0/',
    'photoshop': 'http://ns.adobe.com/photoshop/1.0/',
    'Iptc4xmpCore': 'http://iptc.org/std/Iptc4xmpCore/1.0/xmlns/',
    'Iptc4xmpExt': 'http://iptc.org/std/Iptc4xmpExt/2008-02-29/',
    'plus': 'http://ns.useplus.org/ldf/xmp/1.0/',
    'exif': 'http://ns.adobe.com/exif/1.0/'
}


def generate_unique_id(property_name, prefix=''):
    """
    Generate a unique ID for a property based on its name
    
    Args:
        property_name: Name of the property
        prefix: Optional prefix for the ID
        
    Returns:
        22-character unique ID string
    """
    # Create a hash of the property name
    hash_obj = hashlib.sha256((prefix + property_name).encode())
    hash_hex = hash_obj.hexdigest()
    
    # Convert to base62-like string and take first 22 chars
    chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    result = ''
    for i in range(0, 44, 2):
        byte_val = int(hash_hex[i:i+2], 16)
        result += chars[byte_val % len(chars)]
    
    return result[:22]


def parse_xmp_id(xmp_id):
    """
    Parse XMP ID to extract namespace and property name
    
    Args:
        xmp_id: XMP identifier (e.g., "dc:title")
        
    Returns:
        Tuple of (prefix, property_name, namespace)
    """
    if ':' in xmp_id:
        prefix, prop_name = xmp_id.split(':', 1)
        namespace = XMP_NAMESPACES.get(prefix, '')
        return prefix, prop_name, namespace
    return '', xmp_id, ''


def map_vmhub_type_to_adobe(type_cardinality, xmp_id=''):
    """
    Map VMHub type/cardinality to Adobe field type
    
    Args:
        type_cardinality: VMHub type/cardinality string
        xmp_id: XMP identifier (for special cases)
        
    Returns:
        Dict with Adobe field type and additional properties
    """
    if not type_cardinality:
        return {'type': 'Text'}
    
    # Parse type/cardinality
    # First split by ' / ' for type/cardinality format
    parts = [p.strip() for p in type_cardinality.split('/')]
    datatype_with_card = parts[0].strip()
    
    # Extract cardinality in parentheses if present (e.g., "Date (0..1)" -> "Date", "(0..1)")
    cardinality_match = re.search(r'\s*\(([^)]+)\)\s*$', datatype_with_card)
    if cardinality_match:
        cardinality = cardinality_match.group(1)
        datatype = datatype_with_card[:cardinality_match.start()].strip().lower()
    else:
        datatype = datatype_with_card.lower()
        cardinality = parts[1] if len(parts) > 1 else ''
    
    # Check if it's an array (cardinality like "0..n", "1..n", "0..unbounded")
    is_array = 'n' in cardinality or 'unbounded' in cardinality
    
    # Map data types (case-insensitive)
    if 'structure' in datatype:
        return {'type': 'Structure', 'is_structure': True}
    elif datatype in ['date', 'datetime', 'date/time']:
        return {'type': 'Date', 'dateFormat': 'YYYY-MM-DD', 'timeFormat': 'HH:mm:ss', 'hideTime': 'datetime'}
    elif datatype in ['number', 'integer', 'real']:
        return {'type': 'Number', 'decimal': 'integer' not in datatype}
    elif datatype in ['boolean', 'bool']:
        return {'type': 'Checkbox'}
    elif is_array and datatype in ['text', 'string', 'uri', 'url']:
        return {'type': 'MultiText', 'arrayType': 'bag'}
    else:
        # Default to Text
        return {'type': 'Text', 'multiLine': False}


def create_adobe_field(prop, category_id='', prefix_for_id=''):
    """
    Create Adobe field definition from VMHub property
    
    Args:
        prop: Property dict from VMHub
        category_id: Category identifier
        prefix_for_id: Prefix for generating unique IDs
        
    Returns:
        Dict with Adobe field definition
    """
    # Parse XMP ID
    xmp_prefix, xmp_prop_name, namespace = parse_xmp_id(prop.get('xmp_id', ''))
    
    # Generate unique ID
    field_id = generate_unique_id(prop['name'], prefix_for_id)
    
    # Get Adobe field type
    type_info = map_vmhub_type_to_adobe(prop.get('type_cardinality', ''), prop.get('xmp_id', ''))
    
    # Build base field (only common properties)
    field = {
        'id': field_id,
        'displayName': prop['name'],
        'type': type_info['type'],
        'customToolTip': prop.get('definition', ''),
        'dependencies': [],
        'disabled': False,
        'readOnly': False,
        'syncToFile': []
    }
    
    # Add namespace and property info
    if namespace:
        field['namespace'] = namespace
    if xmp_prefix:
        field['prefix'] = xmp_prefix
    if xmp_prop_name:
        field['propertyName'] = xmp_prop_name
    
    # Add type-specific properties
    if type_info['type'] == 'Text':
        # Check if field supports multiple languages (based on XMP type or definition)
        supports_alt_lang = ('lang' in prop.get('xmp_type', '').lower() or
                           'language' in prop.get('definition', '').lower())
        
        field.update({
            'altLang': [],
            'altLangDefault': '' if not supports_alt_lang else 'en',
            'altLangEnabled': supports_alt_lang,
            'customDefaultText': '',
            'dateFormat': 'YYYY-MM-DD',
            'hideTime': 'datetime',
            'linkToFile': {},
            'multiLine': type_info.get('multiLine', False),
            'options': [],
            'timeFormat': 'hh:mm a'
        })
    elif type_info['type'] == 'MultiText':
        field.update({
            'arrayType': type_info.get('arrayType', 'bag'),
            'customDefaultText': 'Enter a single value',
            'dateFormat': 'YYYY-MM-DD',
            'timeFormat': 'hh:mm a'
        })
    elif type_info['type'] == 'Date':
        field.update({
            'customDefaultText': '',
            'dateFormat': 'YYYY-MM-DD',
            'hideTime': type_info.get('hideTime', 'datetime'),
            'timeFormat': 'HH:mm:ss'
        })
    elif type_info['type'] == 'Number':
        field.update({
            'customDefaultText': '',
            'dateFormat': 'YYYY-MM-DD',
            'decimal': type_info.get('decimal', True),
            'prependZeroes': False,
            'timeFormat': 'hh:mm a'
        })
    
    return field


def create_structure_field(prop, structures_data, prefix_for_id=''):
    """
    Create Adobe structure field with nested properties
    
    Args:
        prop: Property dict from VMHub (the property that uses the structure)
        structures_data: List of all structures (for looking up details)
        prefix_for_id: Prefix for generating unique IDs
        
    Returns:
        Dict with Adobe structure field definition
    """
    # Extract structure name from type_cardinality
    # e.g., "Location structure (0..n)" -> "Location Structure"
    type_card = prop.get('type_cardinality', '')
    struct_name = type_card.split('/')[0].strip() if '/' in type_card else type_card.strip()
    
    # Remove cardinality if present (e.g., "(0..1)", "(0..n)", "(0..unbounded)")
    struct_name = re.sub(r'\s*\([^)]+\)\s*$', '', struct_name).strip()
    
    # Find the structure definition (case-insensitive match)
    struct_def = next((s for s in structures_data if s['name'].lower() == struct_name.lower()), None)
    
    if not struct_def:
        print(f"  Warning: Structure '{struct_name}' not found for property '{prop['name']}'")
        return None
    
    # Parse XMP ID from the property
    xmp_prefix, xmp_prop_name, namespace = parse_xmp_id(prop.get('xmp_id', ''))
    
    # Generate unique ID
    field_id = generate_unique_id(prop['name'], prefix_for_id)
    
    # Build structure field
    field = {
        'id': field_id,
        'displayName': prop['name'],
        'type': 'Structure',
        'customToolTip': prop.get('definition', ''),
        'dateFormat': 'YYYY-MM-DD',
        'dependencies': [],
        'disabled': False,
        'readOnly': False,
        'syncToFile': [],
        'timeFormat': 'hh:mm a',
        'arrayType': 'bag'
    }
    
    # Add namespace and property info
    if namespace:
        field['namespace'] = namespace
    if xmp_prefix:
        field['prefix'] = xmp_prefix
    if xmp_prop_name:
        field['propertyName'] = xmp_prop_name
    
    # Build nested fields
    nested_fields = []
    for nested_prop in struct_def['properties']:
        nested_field = create_adobe_field(nested_prop, prefix_for_id=prop['name'])
        nested_fields.append(nested_field)
    
    field['structure'] = {
        'fields': nested_fields,
        'isArray': True,
        'shouldOverwrite': True
    }
    
    return field


def generate_custom_panel(version=None, output_dir=None, panel_type='core'):
    """
    Generate Adobe custom metadata panel configuration
    
    Args:
        version: Version string (e.g., "1.7"). If None, uses default
        output_dir: Output directory. If None, uses ../adobe-custom-metadata-panel/
        panel_type: 'core' or 'full'
        
    Returns:
        Path to generated file
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
    if panel_type == 'core':
        if not version_config['features'].get('supports_custom_panel_core'):
            print("✗ Core panel not supported for this version")
            return None
        print("Filtering to core properties only...")
        properties = filter_core_properties(properties, version_config)
    
    print(f"✓ Loaded {sum(len(cat['properties']) for cat in properties)} properties")
    print(f"✓ Loaded {len(structures)} structures")
    
    # Build panel data
    categories = []
    
    for category in properties:
        category_data = {
            'id': generate_unique_id(category['name']),
            'display_name': category['name'],
            'properties': []
        }
        
        for prop in category['properties']:
            # Check if it's a structure
            type_card = prop.get('type_cardinality', '').lower()
            
            if 'structure' in type_card:
                # It's a structure - need to build nested field
                field = create_structure_field(prop, structures, category['name'])
                if field:
                    # Convert to JSON string for template
                    field_json = json.dumps(field, indent=3)
                    category_data['properties'].append({'json': field_json})
            else:
                # Regular property
                field = create_adobe_field(prop, category['id'], category['name'])
                field_json = json.dumps(field, indent=3)
                category_data['properties'].append({'json': field_json})
        
        if category_data['properties']:
            categories.append(category_data)
    
    # Setup Jinja2
    templates_dir = os.path.join(os.path.dirname(__file__), 'templates', 'custom_metadata_panel')
    env = Environment(
        loader=FileSystemLoader(templates_dir)
    )
    template = env.get_template('panel.json')
    
    # Render template
    panel_title = f"IPTC Video Metadata Hub ({'core' if panel_type == 'core' else 'full'} properties)"
    output = template.render(
        header_id=generate_unique_id('header'),
        panel_title=panel_title,
        section_link='https://www.iptc.org/std/videometadatahub/',
        categories=categories,
        footer_id=generate_unique_id('footer'),
        footer_text=f"IPTC Video Metadata Hub ({panel_type}) view version: {version}"
    )
    
    # Setup output directory
    if output_dir is None:
        output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'adobe-custom-metadata-panel')
    os.makedirs(output_dir, exist_ok=True)
    
    # Write output
    output_file = os.path.join(output_dir, f'iptc-vmhub-{panel_type}-{version}.json')
    
    # Parse and pretty-print JSON
    json_data = json.loads(output)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, indent=3, ensure_ascii=False)
    
    print(f"✓ Generated: {output_file}")
    return output_file


def main():
    parser = argparse.ArgumentParser(
        description='Generate Adobe custom metadata panel from Google Sheets data'
    )
    parser.add_argument(
        '--version',
        help=f'VMHub version to generate (available: {", ".join(list_available_versions())})'
    )
    parser.add_argument(
        '--output-dir',
        help='Output directory (default: ../adobe-custom-metadata-panel/)'
    )
    parser.add_argument(
        '--panel-type',
        choices=['core', 'full'],
        default='core',
        help='Panel type: core (core properties only) or full (all properties)'
    )
    
    args = parser.parse_args()
    
    try:
        output_file = generate_custom_panel(args.version, args.output_dir, args.panel_type)
        if output_file:
            print(f"\n✓ Success! Generated: {output_file}")
            return 0
        else:
            print("\n✗ Failed to generate custom panel")
            return 1
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    exit(main())

