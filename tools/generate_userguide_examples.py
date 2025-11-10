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


# Example use cases with their column configurations
EXAMPLE_USE_CASES = [
    {
        'name': 'enterprise-advertising-production',
        'range': 'Examples!A3:M99',
        'example_column': 11,
        'notes_column': 12
    },
    {
        'name': 'glam',
        'range': 'Examples!A3:P99',
        'example_column': 14,
        'notes_column': 15
    },
    {
        'name': 'stock',
        'range': 'Examples!A3:S99',
        'example_column': 17,
        'notes_column': 18
    },
    {
        'name': 'long-form-production',
        'range': 'Examples!A3:V99',
        'example_column': 20,
        'notes_column': 21
    },
    {
        'name': 'broadcast-media-management',
        'range': 'Examples!A3:Y99',
        'example_column': 23,
        'notes_column': 24
    },
    {
        'name': 'news-agency',
        'range': 'Examples!A3:AB99',
        'example_column': 26,
        'notes_column': 27
    }
]


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
        output_dir = os.path.join(base_dir, 'video-metadata-guidelines', '_includes')
    
    os.makedirs(output_dir, exist_ok=True)
    
    generated_files = []
    
    # Generate each use case example file
    for use_case in EXAMPLE_USE_CASES:
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
        
        # Render template
        output = template.render(exampleprops=exampleprops)
        
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
        help='Output directory (default: ../video-metadata-guidelines/_includes/)'
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



