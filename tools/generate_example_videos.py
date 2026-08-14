#!/usr/bin/env python3
"""
Generate VMHub Example Video Files

Creates example video files with embedded IPTC Video Metadata Hub properties using ExifTool
"""

import argparse
import json
import os
import subprocess
import shutil
from typing import Dict, List

from lib.version_loader import get_version_config, list_available_versions
from lib.credentials import get_credentials
from lib.vmhub_data import load_properties_data, load_examples_data
from lib.use_cases import load_use_cases, get_use_case, list_use_case_names
from lib.exiftool_tags import (
    parse_column_u, example_value_to_python, SkipStats, SkipReason,
    EXIFTOOL_UNSUPPORTED_TAGS,
)


def create_minimal_example_metadata(version):
    """Create minimal example metadata in ExifTool JSON format"""
    return {
        "XMP-dc:Title": f"IPTC VMHub {version} Example Video",
        "XMP-dc:Description": "Example video demonstrating IPTC Video Metadata Hub properties",
        "XMP-dc:Subject": ["example", "vmhub", f"version{version}"],
        "XMP-dc:Language": "en",
        "XMP-photoshop:DateCreated": "2025-01-01T12:00:00Z",
        "XMP-photoshop:Credit": "IPTC",
        "XMP-dc:Rights": {"en": f"Copyright © 2025 IPTC - VMHub {version} Example"}
    }


def build_property_name_to_column_u(properties: List[Dict]) -> Dict[str, str]:
    """
    Build a mapping from property name -> the raw column U string from
    PropertiesRec. The string is later parsed by lib.exiftool_tags.

    Returns:
        Dict mapping property name to the raw column U value.
    """
    mapping = {}
    for category in properties:
        for prop in category['properties']:
            if 'exiftool_tag' in prop:
                mapping[prop['name']] = prop['exiftool_tag']
    return mapping


def create_full_example_metadata(version_config: Dict, credentials, use_case: Dict, version: str) -> Dict:
    """
    Create comprehensive example metadata from Google Sheets example data
    
    Args:
        version_config: Version configuration dict
        credentials: Google API credentials
        use_case: Use case dict with range and column info
        version: Version string
        
    Returns:
        Dict of metadata in ExifTool JSON format
    """
    # Load properties to get column U (ExifTool tag spec) per property
    print("  Loading property definitions...")
    properties = load_properties_data(version_config, credentials)
    prop_name_to_col_u = build_property_name_to_column_u(properties)

    # Load example data for this use case
    print(f"  Loading example data for {use_case['name']}...")
    values = load_examples_data(version_config, credentials, use_case['range'])

    # Build metadata dict
    metadata = {}
    cols = version_config['column_indices']
    stats = SkipStats()
    unmatched_in_properties = []  # property name appears in Examples but not PropertiesRec

    for row in values:
        if len(row) <= cols['property_name']:
            continue

        property_name = row[cols['property_name']]
        if not property_name:
            continue

        # Get example value
        if len(row) <= use_case['example_column']:
            continue
        example_value = row[use_case['example_column']]

        col_u = prop_name_to_col_u.get(property_name)
        if col_u is None:
            unmatched_in_properties.append(property_name)
            continue

        spec = parse_column_u(col_u)
        if spec.skippable_reason:
            stats.record(spec.skippable_reason, property_name)
            continue

        value, skip_reason = example_value_to_python(spec, example_value)
        if skip_reason:
            stats.record(skip_reason, property_name)
            continue

        # Drop tags ExifTool is known not to implement; otherwise it
        # silently discards them and we'd report a misleading "embedded"
        # count. Re-check the list in lib.exiftool_tags periodically.
        writable_tags = [t for t in spec.tags
                         if t.rstrip('#') not in EXIFTOOL_UNSUPPORTED_TAGS]
        if not writable_tags:
            stats.record(SkipReason.EXIFTOOL_UNSUPPORTED, property_name)
            continue

        for tag in writable_tags:
            metadata[tag] = value

    print(f"  ✓ Generated metadata with {len(metadata)} ExifTool tags")
    print("  Skip summary:")
    print(stats.render())
    if unmatched_in_properties:
        print(f"  ⚠ {len(unmatched_in_properties)} property name(s) in the "
              f"Examples tab have no matching row in PropertiesRec "
              f"(likely renamed - check the sheet):")
        for n in unmatched_in_properties:
            print(f"      - {n!r}")
    return metadata


def generate_example_videos(version=None, output_dir=None, use_case_name=None):
    """
    Generate example video files for specified version and use case
    
    Args:
        version: Version string (e.g., "1.7"). If None, uses default
        output_dir: Output directory. If None, uses ../examples/
        use_case_name: Use case name (e.g., "news-agency"). If None, creates minimal example
    """
    # Check if exiftool is available
    if not shutil.which('exiftool'):
        print("✗ ExifTool is not installed or not in PATH")
        print("  Install from: https://exiftool.org/")
        return None
    
    # Load version configuration
    print(f"Loading configuration for version {version or 'default'}...")
    version_config = get_version_config(version)
    version = version_config['version']
    print(f"✓ Using version {version}")
    
    # Setup output directory
    if output_dir is None:
        output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'examples')
    os.makedirs(output_dir, exist_ok=True)

    # Resolve source media + use case
    if use_case_name:
        use_case = get_use_case(use_case_name)
        if not use_case:
            print(f"✗ Unknown use case: {use_case_name}")
            print(f"  Available use cases: {', '.join(list_use_case_names())}")
            return None

        source_media = os.path.join(output_dir, use_case['source_file'])
        if not os.path.exists(source_media):
            print(f"✗ Source media not found: {source_media}")
            print(f"  Use case '{use_case_name}' is configured to use "
                  f"'{use_case['source_file']}' (see example_use_cases.json)")
            return None

        print(f"Creating example for use case: {use_case_name}")
        print(f"  Source media: {use_case['source_file']}")
        credentials = get_credentials()
        metadata = create_full_example_metadata(version_config, credentials, use_case, version)
        example_type = use_case_name
    else:
        # Minimal example falls back to simple-video.mp4 for backwards compatibility
        source_media = os.path.join(output_dir, 'simple-video.mp4')
        if not os.path.exists(source_media):
            print(f"✗ Source video not found: {source_media}")
            print("  Please provide a source video file as examples/simple-video.mp4")
            return None
        print("Creating minimal example...")
        metadata = create_minimal_example_metadata(version)
        example_type = "minimal"

    # Preserve the source file's extension so audio sources (e.g. .mp3) work too
    source_ext = os.path.splitext(source_media)[1] or '.mp4'

    # Generate metadata JSON file for ExifTool
    version_clean = version.replace('.', '')
    metadata_file = os.path.join(output_dir, f'IPTC-VMHub-RefVideo-Rec{version_clean}-{example_type}.json')

    # ExifTool expects an array with metadata object
    exiftool_data = [metadata]

    with open(metadata_file, 'w', encoding='utf-8') as f:
        json.dump(exiftool_data, f, indent=2)

    print(f"✓ Created metadata file: {metadata_file}")

    # Create output media file (matches source extension)
    output_video = os.path.join(output_dir, f'IPTC-VMHub-RefVideo-Rec{version_clean}-{example_type}{source_ext}')

    # Copy source media to output
    shutil.copy2(source_media, output_video)
    
    # Embed metadata using ExifTool
    print(f"Embedding metadata into video...")
    try:
        cmd = [
            'exiftool',
            '-overwrite_original',
            '-XMP:all=',  # Clear existing XMP
            f'-json={metadata_file}',
            output_video
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✓ Created: {output_video}")
            return output_video
        else:
            print(f"✗ ExifTool error: {result.stderr}")
            return None
            
    except Exception as e:
        print(f"✗ Error running ExifTool: {e}")
        return None


def main():
    parser = argparse.ArgumentParser(
        description='Generate VMHub example video files with embedded metadata'
    )
    parser.add_argument(
        '--version',
        help=f'VMHub version to generate (available: {", ".join(list_available_versions())})'
    )
    parser.add_argument(
        '--output-dir',
        help='Output directory (default: ../examples/)'
    )
    parser.add_argument(
        '--use-case',
        help=f'Use case to generate (available: {", ".join(list_use_case_names())}). If not specified, creates minimal example.'
    )
    
    args = parser.parse_args()
    
    try:
        output_file = generate_example_videos(args.version, args.output_dir, args.use_case)
        if output_file:
            print(f"\n✓ Success! Generated: {output_file}")
        else:
            print("\n✗ Failed to generate example video")
            return 1
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == '__main__':
    exit(main())

