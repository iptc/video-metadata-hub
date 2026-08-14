#!/usr/bin/env python3
"""
Generate VMHub Properties HTML Page

Generates the properties specification page from Google Sheets data
"""

import argparse
import os
from jinja2 import Environment, FileSystemLoader, select_autoescape

from lib.version_loader import get_version_config, list_available_versions
from lib.credentials import get_credentials
from lib.vmhub_data import load_properties_data, load_structures_data, build_backrefs
from googleapiclient.discovery import build


def load_errata_data(version_config, credentials):
    """Load errata data from Google Sheets"""
    service = build('sheets', 'v4', credentials=credentials)
    sheet = service.spreadsheets()
    
    errata_range = version_config['google_sheet_tabs']['errata']
    spreadsheet_id = version_config['spreadsheet_id']
    
    result = sheet.values().get(
        spreadsheetId=spreadsheet_id,
        range=errata_range
    ).execute()
    
    values = result.get('values', [])
    if not values or len(values) < 16:  # Skip header rows
        return []
    
    # Parse errata (typically rows 15-16 in the sheet, adjust as needed)
    errata = []
    for i in range(15, min(17, len(values))):  # Rows 15-16
        row = values[i]
        if len(row) >= 4:
            errata.append({
                'date': row[0],
                'what': row[1],
                'error': row[2],
                'fix': row[3]
            })
    
    return errata


def generate_properties_html(version=None, output_dir=None):
    """
    Generate properties HTML page for specified version
    
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
    print(f"✓ Loaded {len(properties)} property categories")
    
    print("Loading structures...")
    
    # Build backrefs first from raw properties data
    service = build('sheets', 'v4', credentials=credentials)
    sheet = service.spreadsheets()
    properties_range = version_config['google_sheet_tabs']['properties']
    result = sheet.values().get(
        spreadsheetId=version_config['spreadsheet_id'],
        range=properties_range
    ).execute()
    properties_raw = result.get('values', [])
    backrefs = build_backrefs(properties_raw, version_config)
    
    structures = load_structures_data(version_config, credentials, backrefs)
    print(f"✓ Loaded {len(structures)} structures")
    
    print("Loading errata...")
    errata = load_errata_data(version_config, credentials)
    if errata:
        print(f"✓ Loaded {len(errata)} errata entries")
    
    # Setup Jinja2
    templates_dir = os.path.join(os.path.dirname(__file__), 'templates', 'html')
    env = Environment(
        loader=FileSystemLoader(templates_dir),
        autoescape=select_autoescape(['html'])
    )
    template = env.get_template('properties-page.html')
    
    # Render template
    print("Rendering template...")
    html = template.render(
        version=version,
        approval_date=version_config['approval_date'],
        revision_date=version_config['revision_date'],
        copyright_year=version_config['copyright_year'],
        header_appendix=version_config['header_appendix'],
        properties=properties,
        structures=structures,
        errata=errata
    )
    
    # Write output
    if output_dir is None:
        output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'specification')
    
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, f'IPTC-VideoMetadataHub-props-Rec_{version}.html')
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"✓ Generated: {output_file}")
    return output_file


def main():
    parser = argparse.ArgumentParser(
        description='Generate VMHub Properties HTML page from Google Sheets data'
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
        output_file = generate_properties_html(args.version, args.output_dir)
        print(f"\n✓ Success! Generated: {output_file}")
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == '__main__':
    exit(main())

