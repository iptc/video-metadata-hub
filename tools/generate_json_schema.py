#!/usr/bin/env python3
"""
Generate VMHub JSON Schema

Generates the JSON Schema from Google Sheets data
"""

import argparse
import collections
import json
import os

from lib.version_loader import get_version_config, list_available_versions
from lib.credentials import get_credentials
from lib.vmhub_data import load_properties_data, load_structures_data
from lib.constants import JSONSCHEMA_REF_PREFIX
from googleapiclient.discovery import build


def parse_json_datatype(json_type_str):
    """
    Parse the JSON data type string from Google Sheets
    
    Format: type/format/occurrence or object/StructureName/array
    
    Returns:
        dict with type, format, ref, items, enum info
    """
    if not json_type_str:
        return {}
    
    # Split by | to get primary type (first one)
    datatype = json_type_str.split('|')[0]
    parts = datatype.split('/')
    
    result = {}
    
    if parts[0].lower() == 'object' and len(parts) > 1:
        # It's a structure reference
        ref_object_name = parts[1]
        if len(parts) > 2 and parts[2] == 'array':
            result['type'] = 'array'
            result['items'] = {
                '$ref': f'{JSONSCHEMA_REF_PREFIX}#/definitions/{ref_object_name}'
            }
        else:
            result['ref'] = f'{JSONSCHEMA_REF_PREFIX}#/definitions/{ref_object_name}'
    else:
        # It's a plain property
        prop_type = parts[0] if len(parts) > 0 else 'string'
        prop_format = parts[1] if len(parts) > 1 else ''
        more_params = parts[2] if len(parts) > 2 else ''
        
        if 'array' in more_params:
            result['type'] = 'array'
            item_spec = {'type': prop_type}
            if prop_format:
                item_spec['format'] = prop_format
            result['items'] = item_spec
        else:
            result['type'] = prop_type
            if prop_format:
                result['format'] = prop_format
        
        if 'enum' in more_params:
            result['enum'] = ["dummy1"]  # Placeholder - needs to be filled manually
    
    return result


def generate_json_schema(version=None, output_dir=None):
    """
    Generate JSON Schema for specified version
    
    Args:
        version: Version string (e.g., "1.7"). If None, uses default
        output_dir: Output directory. If None, uses ../specification/
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
    print("Loading properties...")
    properties = load_properties_data(version_config, credentials)
    
    # Build JSON Schema properties object
    json_properties = collections.OrderedDict()
    
    for category in properties:
        for prop in category['properties']:
            if not prop.get('json_schema_id'):
                continue
            
            prop_name = prop['json_schema_id']
            prop_data = {
                'title': prop['name'],
                'description': prop['definition']
            }
            
            # Parse the JSON type
            if prop.get('json_schema_type'):
                type_info = parse_json_datatype(prop['json_schema_type'])
                prop_data.update(type_info)
            
            json_properties[prop_name] = prop_data
    
    print(f"✓ Processed {len(json_properties)} properties")
    
    # Create the full schema structure
    schema = {
        "$schema": "http://json-schema.org/draft-04/schema#",
        "id": f"https://www.iptc.org/std/videometadatahub/recommendation/iptc-vmhub-{version}-schema.json",
        "title": "IPTC Video Metadata Hub JSON Schema",
        "description": f"Overall structure of video metadata of a single media asset - sets of metadata for the whole asset and fragments of the asset -- the properties comply with the IPTC Video Metadata Hub Recommendation {version} (IPTC/{version_config['approval_date']})",
        "type": "array",
        "minItems": 1,
        "items": {
            "type": "object",
            "properties": {
                "mediafragment": {
                    "$ref": f"{JSONSCHEMA_REF_PREFIX}#/definitions/MediaFragment"
                },
                "photoVideoMetadataIPTC": {
                    "description": "Container for IPTC photo/video metadata",
                    "type": "object",
                    "properties": json_properties,
                    "additionalProperties": False
                }
            },
            "required": ["photoVideoMetadataIPTC"],
            "patternProperties": {
                "^photoVideoMetadata_[a-zA-Z0-9_]+": {
                    "description": "Container for a set of metadata from a party other than IPTC",
                    "type": "object"
                }
            },
            "additionalProperties": False
        },
        "additionalProperties": False
    }
    
    # Write output
    if output_dir is None:
        output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'specification')
    
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, f'iptc-vmhub-{version}-schema.json')
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(schema, f, indent=4, ensure_ascii=False)
    
    print(f"✓ Generated: {output_file}")
    print("\nNote: Properties with 'enum' values have dummy placeholders that need manual editing.")
    return output_file


def main():
    parser = argparse.ArgumentParser(
        description='Generate VMHub JSON Schema from Google Sheets data'
    )
    parser.add_argument(
        '--version',
        help=f'VMHub version to generate (available: {", ".join(list_available_versions())})'
    )
    parser.add_argument(
        '--output-dir',
        help='Output directory (default: ../specification/)'
    )
    
    args = parser.parse_args()
    
    try:
        output_file = generate_json_schema(args.version, args.output_dir)
        print(f"\n✓ Success! Generated: {output_file}")
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == '__main__':
    exit(main())

