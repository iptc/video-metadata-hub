#!/usr/bin/env python3
"""
Generate User Guide Examples Includes

Generates multiple example AsciiDoc files for different use cases
"""

import argparse
import os
from jinja2 import Environment, FileSystemLoader, select_autoescape

from lib.version_loader import get_version_config, list_available_versions
from lib.credentials import get_credentials
from lib.vmhub_data import load_examples_data, build_examples_table
from lib.use_cases import load_use_cases, get_examples_base_url


def generate_userguide_examples(version=None, output_dir=None):
    """
    Generate user guide example AsciiDoc includes for all use cases
    
    Args:
        version: Version string (e.g., "1.7"). If None, uses default
        output_dir: Output directory. If None, uses default location
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
    
    # Setup Jinja2
    templates_dir = os.path.join(os.path.dirname(__file__), 'templates', 'userguide_includes')
    env = Environment(
        loader=FileSystemLoader(templates_dir),
        autoescape=select_autoescape()
    )
    template = env.get_template('examples.adoc')
    
    # Determine output directory
    if output_dir is None:
        base_dir = os.path.dirname(os.path.dirname(__file__))
        output_dir = os.path.join(base_dir, 'user-guide', '_includes')
    
    os.makedirs(output_dir, exist_ok=True)
    
    generated_files = []

    base_url = get_examples_base_url()
    version_clean = version.replace('.', '')

    # Generate each use case example file
    for use_case in load_use_cases():
        print(f"\nGenerating {use_case['name']} example...")

        # Load examples data for this use case
        values = load_examples_data(version_config, credentials, use_case['range'])

        # Build examples table
        linkid = f"{use_case['name']}-example"
        exampleprops = build_examples_table(
            values,
            version_config,
            use_case['example_column'],
            use_case['notes_column'],
            linkid
        )

        # Download link for the published example file. Filename mirrors
        # the convention used by generate_example_videos.py:
        #   IPTC-VMHub-RefVideo-Rec<ver_clean>-<use_case>.<ext>
        source_ext = os.path.splitext(use_case['source_file'])[1] or '.mp4'
        download_filename = (
            f"IPTC-VMHub-RefVideo-Rec{version_clean}-{use_case['name']}{source_ext}"
        )
        download_url = base_url + download_filename

        # Render template (now self-contained: heading, credit, thumbnail,
        # download link, then the property table)
        output = template.render(
            use_case=use_case,
            exampleprops=exampleprops,
            download_url=download_url,
            download_filename=download_filename,
        )

        # Write output
        output_file = os.path.join(output_dir, f"{use_case['name']}-example.adoc")
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(output)

        print(f"✓ Generated: {output_file}")
        generated_files.append(output_file)

    return generated_files


def main():
    parser = argparse.ArgumentParser(
        description='Generate user guide example AsciiDoc includes from Google Sheets data'
    )
    parser.add_argument(
        '--version',
        help=f'VMHub version to generate (available: {", ".join(list_available_versions())})'
    )
    parser.add_argument(
        '--output-dir',
        help='Output directory (default: ../user-guide/_includes/)'
    )
    
    args = parser.parse_args()
    
    try:
        output_files = generate_userguide_examples(args.version, args.output_dir)
        print(f"\n✓ Success! Generated {len(output_files)} example files")
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == '__main__':
    exit(main())



