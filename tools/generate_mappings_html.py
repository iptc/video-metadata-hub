#!/usr/bin/env python3
"""
Generate VMHub Mappings HTML Pages

Generates the mappings specification pages from Google Sheets data
"""

import argparse
import os
from jinja2 import Environment, FileSystemLoader, select_autoescape

from lib.version_loader import get_version_config, list_available_versions
from lib.credentials import get_credentials
from lib.vmhub_data import load_mappings_data
from lib.constants import MAPPINGS


def generate_mappings_html(version=None, output_dir=None):
    """
    Generate mappings HTML pages for specified version

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

    # Load mappings data
    print("Loading mappings data...")
    mappings_values = load_mappings_data(version_config, credentials)
    print(f"✓ Loaded mappings data")

    # Setup output directory
    if output_dir is None:
        output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'specification')
    os.makedirs(output_dir, exist_ok=True)

    # Setup Jinja2
    templates_dir = os.path.join(os.path.dirname(__file__), 'templates', 'html')
    env = Environment(
        loader=FileSystemLoader(templates_dir),
        autoescape=select_autoescape(['html'])
    )

    # Get row ranges
    ranges = version_config['row_ranges']
    first_row = ranges.get('mappings_first_property_row', 2)
    last_row = ranges.get('mappings_last_property_row', 215)

    # Generate individual mapping pages
    specific_template = env.get_template('mappings-specific.html')

    for mapping in MAPPINGS:
        print(f"Generating mapping for {mapping['heading']}...")

        # Build mapping rows
        mapping_rows = []
        for rowcounter in range(first_row, min(last_row, len(mappings_values))):
            row = mappings_values[rowcounter]

            # Check if this is a structure header or structure row
            test_str = row[0] if len(row) > 0 else ''
            is_structure_header = (test_str == 'Property Structures (PS)')
            is_structure = (test_str.startswith('PS '))

            mapping_row = {
                'property_group': row[0] if len(row) > 0 else ' ',
                'property_name': row[1] if len(row) > 1 else ' ',
                'definition': row[2] if len(row) > 2 else ' ',
                'ebucore': row[4] if len(row) > 4 else ' ',
                'xmp': row[5] if len(row) > 5 else ' ',
                'pvmd_json': row[6] if len(row) > 6 else ' ',
                'mapping_value': row[mapping['mappingsheetcolumn']] if len(row) > mapping['mappingsheetcolumn'] else ' ',
                'is_structure_header': is_structure_header,
                'is_structure': is_structure
            }
            mapping_rows.append(mapping_row)

        # Get "find more" URL
        mapping_find_more_url = ''
        if len(mappings_values) > 0 and len(mappings_values[0]) > mapping['mappingsheetcolumn']:
            mapping_find_more_url = mappings_values[0][mapping['mappingsheetcolumn']]

        # Render template
        html = specific_template.render(
            version=version,
            approval_date=version_config['approval_date'],
            revision_date=version_config['revision_date'],
            copyright_year=version_config['copyright_year'],
            header_appendix=version_config['header_appendix'],
            mapping_heading=mapping['heading'],
            mapping_find_more_url=mapping_find_more_url,
            find_more_url='',  # Could be populated from mappings_values[0]
            mapping_rows=mapping_rows
        )

        # Write output
        output_file = os.path.join(
            output_dir,
            f"IPTC-VideoMetadataHub-mapping-{mapping['filenameid']}-Rec_{version}.html"
        )

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html)

        print(f"  ✓ {output_file}")

    print(f"\n✓ Generated {len(MAPPINGS)} individual mapping files")

    # Generate main mappings page with all mappings
    print("\nGenerating main mappings page...")
    main_template = env.get_template('mappings.html')

    # Build mapping rows for main page (includes all mapping columns)
    main_mapping_rows = []
    for rowcounter in range(first_row, min(last_row, len(mappings_values))):
        row = mappings_values[rowcounter]

        # Check if this is a structure header or structure row
        test_str = row[0] if len(row) > 0 else ''
        is_structure_header = (test_str == 'Property Structures (PS)')
        is_structure = (test_str.startswith('PS '))

        # Collect all mapping values
        mapping_values = []
        for mapping in MAPPINGS:
            value = row[mapping['mappingsheetcolumn']] if len(row) > mapping['mappingsheetcolumn'] else ' '
            mapping_values.append(value)

        mapping_row = {
            'property_group': row[0] if len(row) > 0 else ' ',
            'property_name': row[1] if len(row) > 1 else ' ',
            'definition': row[2] if len(row) > 2 else ' ',
            'ebucore': row[4] if len(row) > 4 else ' ',
            'xmp': row[5] if len(row) > 5 else ' ',
            'pvmd_json': row[6] if len(row) > 6 else ' ',
            'mapping_values': mapping_values,
            'is_structure_header': is_structure_header,
            'is_structure': is_structure
        }
        main_mapping_rows.append(mapping_row)

    # Build mappings list with find_more URLs
    mappings_with_urls = []
    for mapping in MAPPINGS:
        mapping_with_url = mapping.copy()
        if len(mappings_values) > 0 and len(mappings_values[0]) > mapping['mappingsheetcolumn']:
            mapping_with_url['find_more_url'] = mappings_values[0][mapping['mappingsheetcolumn']]
        else:
            mapping_with_url['find_more_url'] = ''
        mappings_with_urls.append(mapping_with_url)

    # Get find more URLs for core columns
    find_more_urls = {
        'xmp': mappings_values[0][4] if len(mappings_values) > 0 and len(mappings_values[0]) > 4 else '',
        'pvmd_json': mappings_values[0][5] if len(mappings_values) > 0 and len(mappings_values[0]) > 5 else '',
        'ebucore': mappings_values[0][6] if len(mappings_values) > 0 and len(mappings_values[0]) > 6 else '',
    }

    # Render main template
    html = main_template.render(
        version=version,
        approval_date=version_config['approval_date'],
        revision_date=version_config['revision_date'],
        copyright_year=version_config['copyright_year'],
        header_appendix=version_config['header_appendix'],
        mappings=mappings_with_urls,
        mapping_rows=main_mapping_rows,
        find_more_urls=find_more_urls
    )

    # Write main mappings output
    main_output_file = os.path.join(
        output_dir,
        f"IPTC-VideoMetadataHub-mapping-Rec_{version}.html"
    )

    with open(main_output_file, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"  ✓ {main_output_file}")
    print(f"\n✓ Generated main mappings file and {len(MAPPINGS)} individual mapping files")
    return output_dir


def main():
    parser = argparse.ArgumentParser(
        description='Generate VMHub Mappings HTML pages from Google Sheets data'
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
        output_dir = generate_mappings_html(args.version, args.output_dir)
        print(f"\n✓ Success! Generated mapping files in: {output_dir}")
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == '__main__':
    exit(main())

