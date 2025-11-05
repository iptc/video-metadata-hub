#!/usr/bin/env python3
"""
VMHub Data Loading Library

Version-aware data loading from Google Sheets using version-specific configurations
"""

import re
from typing import Dict, List, Optional
from googleapiclient.discovery import build

from .constants import CATEGORY_MAPPING


def text_to_anchor(text: str) -> str:
    """
    Convert text to an anchor-safe format
    
    Args:
        text: Input text
        
    Returns:
        Anchor-safe string
    """
    anchor = re.sub(r'\s', '-', text)
    anchor = re.sub(r'[\(\),]', '', anchor)
    return anchor


def process_structure_links(text: str) -> str:
    """
    Convert structure references to AsciiDoc links
    
    Args:
        text: Text potentially containing "XYZ Structure" references
        
    Returns:
        Text with structure references converted to links
    """
    if not text or ('structure' not in text.lower() and 'Structure' not in text):
        return text
    
    # Convert "Name Structure" to "<<Name Structure>>"
    # 3 is count to re.sub, means evaluate this regex up to 3 times.
    text = re.sub(r'(([a-z\/\-A-Z\ ]+?) [sS]tructure)', r'<<\2 Structure>>', text, 3)
    
    # Fix "<<A Structure>><< or B Structure>>" to "<<A Structure>> or <<B Structure>>"
    text = re.sub(r'<< or ', ' or <<', text)
    
    return text


def load_properties_data(version_config: Dict, credentials) -> List[Dict]:
    """
    Load properties data from Google Sheets
    
    Args:
        version_config: Version-specific configuration dict
        credentials: Google API credentials
        
    Returns:
        List of property dictionaries organized by category
    """
    service = build('sheets', 'v4', credentials=credentials)
    sheet = service.spreadsheets()
    
    # Get properties range from config
    properties_range = version_config['google_sheet_tabs']['properties']
    spreadsheet_id = version_config['spreadsheet_id']
    
    result = sheet.values().get(
        spreadsheetId=spreadsheet_id,
        range=properties_range
    ).execute()
    
    values = result.get('values', [])
    if not values:
        return []
    
    # Get column indices from config
    cols = version_config['column_indices']
    
    category_id = ''
    properties = []
    property_category = {}
    
    for row in values:
        # Check if we've hit the end of properties
        if len(row) > 0 and row[0] == 'Property Structures (PS)':
            break
        
        if len(row) <= cols['property_name']:
            continue
        
        # Check for new category
        if row[cols['category']] != category_id:
            category_id = row[cols['category']]
            if property_category:
                properties.append(property_category)
            property_category = {
                'id': category_id,
                'name': CATEGORY_MAPPING.get(category_id, category_id),
                'properties': []
            }
        
        # Build property data
        prop_data = {
            'anchor': text_to_anchor(row[cols['property_name']]),
            'name': row[cols['property_name']],
            'definition': row[cols['definition']] if len(row) > cols['definition'] else '',
            'type_cardinality': row[cols['type_cardinality']] if len(row) > cols['type_cardinality'] else '',
            'type_cardinality_with_link': process_structure_links(
                row[cols['type_cardinality']] if len(row) > cols['type_cardinality'] else ''
            )
        }
        
        # Optional fields
        if len(row) > cols['user_notes'] and row[cols['user_notes']]:
            prop_data['note'] = row[cols['user_notes']]
        
        if len(row) > cols['change_notes'] and row[cols['change_notes']]:
            prop_data['history'] = row[cols['change_notes']]
        
        # Core sort order (only in v1.7+)
        if cols['core_sort_order'] is not None and len(row) > cols['core_sort_order']:
            prop_data['sort_order'] = row[cols['core_sort_order']]
        
        # XMP properties
        if len(row) > cols['xmp_prop'] and row[cols['xmp_prop']]:
            prop_data['xmp_id'] = row[cols['xmp_prop']]
        if len(row) > cols['xmp_type'] and row[cols['xmp_type']]:
            prop_data['xmp_type'] = row[cols['xmp_type']]
        
        # JSON/PVMD properties
        if len(row) > cols['json_prop'] and row[cols['json_prop']]:
            prop_data['json_schema_id'] = row[cols['json_prop']]
        if len(row) > cols['json_type'] and row[cols['json_type']]:
            prop_data['json_schema_type'] = row[cols['json_type']]
        
        # New/modified flags
        if len(row) > cols['property_name_modified_flag'] and row[cols['property_name_modified_flag']] == 'n':
            prop_data['is_new'] = True
        
        property_category['properties'].append(prop_data)
    
    # Add the last category
    if category_id and property_category:
        properties.append(property_category)
    
    return properties


def build_backrefs(properties_values: List[List], version_config: Dict) -> Dict[str, List[str]]:
    """
    Build back-references from structures to properties that use them
    
    Args:
        properties_values: Raw property values from Google Sheets
        version_config: Version configuration
        
    Returns:
        Dict mapping structure names to lists of property references
    """
    cols = version_config['column_indices']
    backrefs = {}
    
    for row in properties_values:
        if len(row) < cols['type_cardinality'] + 1:
            continue
        
        type_card = row[cols['type_cardinality']]
        if 'structure' in type_card.lower():
            matches = re.findall(r'[a-z\/\-A-Z\ ]+? [sS]tructure', type_card)
            for match in matches:
                refname = row[cols['property_name']]
                reflink = text_to_anchor(refname)
                backrefs.setdefault(match.lower(), []).append(f'<<{reflink},{refname}>>')
    
    return backrefs


def load_structures_data(version_config: Dict, credentials, backrefs: Optional[Dict] = None) -> List[Dict]:
    """
    Load structures data from Google Sheets
    
    Args:
        version_config: Version-specific configuration dict
        credentials: Google API credentials
        backrefs: Optional back-references dict from build_backrefs()
        
    Returns:
        List of structure dictionaries
    """
    service = build('sheets', 'v4', credentials=credentials)
    sheet = service.spreadsheets()
    
    # Get structures range from config
    structures_range = version_config['google_sheet_tabs']['structures']
    spreadsheet_id = version_config['spreadsheet_id']
    
    result = sheet.values().get(
        spreadsheetId=spreadsheet_id,
        range=structures_range
    ).execute()
    
    values = result.get('values', [])
    if not values:
        return []
    
    cols = version_config['column_indices']
    structures = []
    structure_data = {'properties': []}
    structure_name = ''
    
    for row in values:
        if len(row) < 3:
            continue
        
        # Check if this is a new structure
        if row[0]:
            if structure_name != '':
                structures.append(structure_data)
                structure_data = {'properties': []}
            
            structure_name = row[0]
            if structure_name.startswith('PS '):
                structure_name = structure_name.replace('PS ', '')
            
            structure_data['name'] = structure_name + " Structure"
            structure_data['anchor'] = text_to_anchor(structure_name)
            
            # Add back-references if available
            if backrefs and structure_name.lower() + " structure" in backrefs:
                structure_data['used_in'] = backrefs[structure_name.lower() + " structure"]
            
            continue
        
        # Property within a structure
        if len(row) > cols['property_name']:
            structure_prop = {
                'anchor': text_to_anchor(row[cols['property_name']]),
                'name': row[cols['property_name']],
                'definition': row[cols['definition']] if len(row) > cols['definition'] else '',
                'type_cardinality': row[cols['type_cardinality']] if len(row) > cols['type_cardinality'] else ''
            }
            
            if len(row) > cols['user_notes'] and row[cols['user_notes']]:
                structure_prop['note'] = row[cols['user_notes']]
            
            if len(row) > cols['change_notes'] and row[cols['change_notes']]:
                structure_prop['history'] = row[cols['change_notes']]
            
            if len(row) > cols['xmp_prop'] and row[cols['xmp_prop']]:
                structure_prop['xmp_id'] = row[cols['xmp_prop']]
            if len(row) > cols['xmp_type'] and row[cols['xmp_type']]:
                structure_prop['xmp_type'] = row[cols['xmp_type']]
            
            if len(row) > cols['json_prop'] and row[cols['json_prop']]:
                structure_prop['json_schema_name'] = row[cols['json_prop']]
            if len(row) > cols['json_type'] and row[cols['json_type']]:
                structure_prop['json_schema_type'] = row[cols['json_type']]
            
            structure_data['properties'].append(structure_prop)
    
    # Add the last structure
    if structure_name:
        structures.append(structure_data)
    
    return structures


def filter_core_properties(properties: List[Dict], version_config: Dict) -> List[Dict]:
    """
    Filter properties to only include core properties
    
    Args:
        properties: List of property category dicts
        version_config: Version configuration
        
    Returns:
        Filtered list containing only core properties
    """
    if not version_config['features'].get('has_core_sort_column', False):
        raise ValueError(
            f"Version {version_config['version']} does not support core property filtering"
        )
    
    core_properties = []
    
    for category in properties:
        core_category = {
            'id': category['id'],
            'name': category['name'],
            'properties': []
        }
        
        for prop in category['properties']:
            sort_order = prop.get('sort_order', '')
            if sort_order and sort_order.startswith('core'):
                core_category['properties'].append(prop)
        
        if core_category['properties']:
            core_properties.append(core_category)
    
    return core_properties


def load_mappings_data(version_config: Dict, credentials) -> List[List]:
    """
    Load mappings data from Google Sheets
    
    Args:
        version_config: Version-specific configuration dict
        credentials: Google API credentials
        
    Returns:
        Raw mapping values from Google Sheets
    """
    service = build('sheets', 'v4', credentials=credentials)
    sheet = service.spreadsheets()
    
    mappings_range = version_config['google_sheet_tabs']['mappings']
    spreadsheet_id = version_config['spreadsheet_id']
    
    result = sheet.values().get(
        spreadsheetId=spreadsheet_id,
        range=mappings_range
    ).execute()
    
    return result.get('values', [])


def load_examples_data(version_config: Dict, credentials, range_name: str) -> List[List]:
    """
    Load examples data from Google Sheets
    
    Args:
        version_config: Version-specific configuration dict
        credentials: Google API credentials
        range_name: Specific range to load (allows loading different example columns)
        
    Returns:
        Raw example values from Google Sheets
    """
    service = build('sheets', 'v4', credentials=credentials)
    sheet = service.spreadsheets()
    
    spreadsheet_id = version_config['spreadsheet_id']
    
    result = sheet.values().get(
        spreadsheetId=spreadsheet_id,
        range=range_name
    ).execute()
    
    return result.get('values', [])


def build_examples_table(values: List[List], version_config: Dict, example_column: int,
                        notes_column: int, linkid: str) -> List[Dict]:
    """
    Build examples table data from Google Sheets values

    Args:
        values: Raw values from Google Sheets
        version_config: Version configuration
        example_column: Column index containing example values
        notes_column: Column index containing notes
        linkid: Link ID prefix for anchors

    Returns:
        List of category dicts with example properties
    """
    cols = version_config['column_indices']
    category_id = ''
    exampleprops = []
    property_category = {}

    for row in values:
        if len(row) <= cols['property_name']:
            continue

        # Check for new category
        if row[cols['category']] != category_id:
            category_id = row[cols['category']]
            if property_category:
                exampleprops.append(property_category)
            property_category = {
                'id': category_id,
                'name': CATEGORY_MAPPING.get(category_id, category_id),
                'properties': []
            }

        # Get example value
        example_data = row[example_column] if len(row) > example_column else ''
        if not example_data:
            continue  # Skip properties with no example

        prop_data = {
            'anchor': linkid + 'example' + text_to_anchor(row[cols['property_name']]),
            'name': row[cols['property_name']],
            'example_value': example_data
        }

        # Add notes if present
        if len(row) > notes_column and row[notes_column]:
            prop_data['notes'] = row[notes_column]

        property_category['properties'].append(prop_data)

    # Add last category
    if category_id and property_category:
        exampleprops.append(property_category)

    return exampleprops


if __name__ == '__main__':
    # Test data loading
    from .version_loader import get_version_config
    from .credentials import get_credentials
    
    try:
        print("Loading version configuration...")
        config = get_version_config()
        print(f"✓ Using version {config['version']}")
        
        print("\nAuthenticating with Google Sheets...")
        creds = get_credentials()
        print("✓ Authenticated")
        
        print("\nLoading properties...")
        properties = load_properties_data(config, creds)
        print(f"✓ Loaded {len(properties)} property categories")
        for cat in properties:
            print(f"  - {cat['name']}: {len(cat['properties'])} properties")
        
        print("\nLoading structures...")
        structures = load_structures_data(config, creds)
        print(f"✓ Loaded {len(structures)} structures")
        
        if config['features'].get('has_core_sort_column'):
            print("\nFiltering core properties...")
            core_props = filter_core_properties(properties, config)
            total_core = sum(len(cat['properties']) for cat in core_props)
            print(f"✓ Found {total_core} core properties")
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()

