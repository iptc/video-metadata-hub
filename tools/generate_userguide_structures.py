#!/usr/bin/env python3
"""
Generate User Guide Structures Include

Generates the structures.adoc include file for the user guide
"""

import argparse
import os
from jinja2 import Environment, FileSystemLoader, select_autoescape
from googleapiclient.discovery import build

from lib.version_loader import get_version_config, list_available_versions
from lib.credentials import get_credentials
from lib.vmhub_data import load_structures_data, build_backrefs


def generate_userguide_structures(version=None, output_file=None):
    """
    Generate user guide structures AsciiDoc include
    
    Args:
        version: Version string (e.g., "1.7"). If None, uses default
        output_file: Output file path. If None, uses default location
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
    
    # Load properties first to build backrefs
    print("Loading properties for backreferences...")
    service = build('sheets', 'v4', credentials=credentials)
    sheet = service.spreadsheets()
    properties_range = version_config['google_sheet_tabs']['properties']
    result = sheet.values().get(
        spreadsheetId=version_config['spreadsheet_id'],
        range=properties_range
    ).execute()
    properties_raw = result.get('values', [])
    backrefs = build_backrefs(properties_raw, version_config)
    print(f"✓ Built backreferences")
    
    # Load structures data
    print("Loading structures...")
    structures = load_structures_data(version_config, credentials, backrefs)
    print(f"✓ Loaded {len(structures)} structures")
    
    # Setup Jinja2
    templates_dir = os.path.join(os.path.dirname(__file__), 'templates', 'userguide_includes')
    env = Environment(
        loader=FileSystemLoader(templates_dir),
        autoescape=select_autoescape()
    )
    template = env.get_template('structures.adoc')
    
    # Render template
    print("Rendering template...")
    output = template.render(structures=structures)
    
    # Write output
    if output_file is None:
        # Default to user-guide/_includes/structures.adoc
        base_dir = os.path.dirname(os.path.dirname(__file__))
        output_file = os.path.join(base_dir, 'user-guide', '_includes', 'structures.adoc')
    
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(output)
    
    print(f"✓ Generated: {output_file}")
    return output_file


def main():
    parser = argparse.ArgumentParser(
        description='Generate user guide structures AsciiDoc include from Google Sheets data'
    )
    parser.add_argument(
        '--version',
        help=f'VMHub version to generate (available: {", ".join(list_available_versions())})'
    )
    parser.add_argument(
        '--output',
        help='Output file path (default: ../user-guide/_includes/structures.adoc)'
    )
    
    args = parser.parse_args()
    
    try:
        output_file = generate_userguide_structures(args.version, args.output)
        print(f"\n✓ Success! Generated: {output_file}")
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == '__main__':
    exit(main())





