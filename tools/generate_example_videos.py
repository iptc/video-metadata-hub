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
from typing import Dict

from lib.version_loader import get_version_config, list_available_versions
from lib.credentials import get_credentials
from lib.vmhub_data import load_properties_data


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


def create_full_example_metadata(properties, version):
    """
    Create comprehensive example metadata from properties data
    
    Note: This is a simplified version. A complete implementation would
    include example values for all properties based on their data types.
    """
    metadata = create_minimal_example_metadata(version)
    
    # Add more properties based on the loaded data
    # This is a placeholder - full implementation would parse each property
    # and create appropriate example values
    
    return metadata


def generate_example_videos(version=None, output_dir=None, create_full=False):
    """
    Generate example video files for specified version
    
    Args:
        version: Version string (e.g., "1.7"). If None, uses default
        output_dir: Output directory. If None, uses ../examples/
        create_full: If True, creates full example. If False, creates minimal example
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
    
    # Create metadata
    if create_full:
        print("Loading properties for full example...")
        credentials = get_credentials()
        properties = load_properties_data(version_config, credentials)
        metadata = create_full_example_metadata(properties, version)
        example_type = "full"
    else:
        metadata = create_minimal_example_metadata(version)
        example_type = "minimal"
    
    # Find or create source video
    source_video = os.path.join(output_dir, 'simple-video.mp4')
    if not os.path.exists(source_video):
        print(f"✗ Source video not found: {source_video}")
        print("  Please provide a source video file as examples/simple-video.mp4")
        return None
    
    # Generate metadata JSON file for ExifTool
    version_clean = version.replace('.', '')
    metadata_file = os.path.join(output_dir, f'IPTC-VMHub-RefVideo-Rec{version_clean}-{example_type}.json')
    
    # ExifTool expects an array with metadata object
    exiftool_data = [metadata]
    
    with open(metadata_file, 'w', encoding='utf-8') as f:
        json.dump(exiftool_data, f, indent=2)
    
    print(f"✓ Created metadata file: {metadata_file}")
    
    # Create output video
    output_video = os.path.join(output_dir, f'IPTC-VMHub-RefVideo-Rec{version_clean}-{example_type}.mp4')
    
    # Copy source video to output
    shutil.copy2(source_video, output_video)
    
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
        '--full',
        action='store_true',
        help='Create full example with all properties (default: minimal example)'
    )
    
    args = parser.parse_args()
    
    try:
        output_file = generate_example_videos(args.version, args.output_dir, args.full)
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

