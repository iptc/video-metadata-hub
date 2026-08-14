#!/usr/bin/env python3
"""
Version Configuration Loader

Loads and validates version configurations from vmhub_configuration.json
"""

import json
import os
from typing import Dict, List, Optional


def get_config_path() -> str:
    """Get the path to vmhub_configuration.json"""
    # Go up two levels from this file to reach the repository root
    current_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.dirname(os.path.dirname(current_dir))
    return os.path.join(repo_root, 'vmhub_configuration.json')


def load_versions_config() -> Dict:
    """
    Load the complete versions configuration from vmhub_configuration.json
    
    Returns:
        Dict containing the full configuration including all versions
        
    Raises:
        FileNotFoundError: If configuration file doesn't exist
        json.JSONDecodeError: If configuration file is not valid JSON
    """
    config_path = get_config_path()
    
    if not os.path.exists(config_path):
        raise FileNotFoundError(
            f"Configuration file not found: {config_path}\n"
            f"Please create vmhub_configuration.json in the repository root."
        )
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    # Validate basic structure
    if 'versions' not in config:
        raise ValueError("Configuration must contain a 'versions' key")
    if 'default_version' not in config:
        raise ValueError("Configuration must contain a 'default_version' key")
    if 'spreadsheet_id' not in config:
        raise ValueError("Configuration must contain a 'spreadsheet_id' key")
    
    return config


def get_version_config(version: Optional[str] = None) -> Dict:
    """
    Get configuration for a specific version
    
    Args:
        version: Version string (e.g., "1.7"). If None, uses default_version from config
        
    Returns:
        Dict containing configuration for the specified version
        
    Raises:
        ValueError: If specified version is not found in configuration
    """
    config = load_versions_config()
    
    if version is None:
        version = config['default_version']
    
    if version not in config['versions']:
        available = ', '.join(config['versions'].keys())
        raise ValueError(
            f"Version '{version}' not found in configuration.\n"
            f"Available versions: {available}"
        )
    
    # Return version config with spreadsheet_id included for convenience
    version_config = config['versions'][version].copy()
    version_config['spreadsheet_id'] = config['spreadsheet_id']
    
    return version_config


def list_available_versions() -> List[str]:
    """
    Get list of all configured versions
    
    Returns:
        List of version strings
    """
    config = load_versions_config()
    return sorted(config['versions'].keys())


def get_default_version() -> str:
    """
    Get the default version from configuration
    
    Returns:
        Default version string
    """
    config = load_versions_config()
    return config['default_version']


def validate_version_config(version_config: Dict) -> List[str]:
    """
    Validate a version configuration for completeness
    
    Args:
        version_config: Version configuration dictionary
        
    Returns:
        List of validation errors (empty list if valid)
    """
    errors = []
    
    required_keys = [
        'version', 'approval_date', 'revision_date', 'copyright_year',
        'google_sheet_tabs', 'column_indices', 'row_ranges', 'features'
    ]
    
    for key in required_keys:
        if key not in version_config:
            errors.append(f"Missing required key: {key}")
    
    if 'google_sheet_tabs' in version_config:
        required_tabs = ['properties', 'structures', 'mappings', 'examples']
        for tab in required_tabs:
            if tab not in version_config['google_sheet_tabs']:
                errors.append(f"Missing required tab: google_sheet_tabs.{tab}")
    
    if 'column_indices' in version_config:
        required_cols = ['category', 'property_name', 'definition', 'type_cardinality']
        for col in required_cols:
            if col not in version_config['column_indices']:
                errors.append(f"Missing required column index: column_indices.{col}")
    
    return errors


if __name__ == '__main__':
    # Test the configuration loader
    try:
        print("Loading configuration...")
        config = load_versions_config()
        print(f"✓ Configuration loaded successfully")
        print(f"  Default version: {config['default_version']}")
        print(f"  Spreadsheet ID: {config['spreadsheet_id']}")
        print(f"  Available versions: {', '.join(list_available_versions())}")
        
        print("\nValidating default version...")
        default_config = get_version_config()
        errors = validate_version_config(default_config)
        if errors:
            print(f"✗ Validation errors:")
            for error in errors:
                print(f"  - {error}")
        else:
            print(f"✓ Version {default_config['version']} configuration is valid")
            
    except Exception as e:
        print(f"✗ Error: {e}")

