#!/usr/bin/env python3
"""
Version-Independent Constants

Constants that apply across all VMHub versions
"""

# Google Sheets API
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

# Category mappings from Google Sheet category IDs to display names
CATEGORY_MAPPING = {
    'administrative': 'Administrative fields',
    'describing a/v content': 'Fields describing audio/visual content',
    'rights': 'Rights fields',
    'technical': 'Technical fields',
    'tool': 'Time marker'
}

# Mapping standards configuration
# Each mapping includes the display names and column indices in the mappings sheet
MAPPINGS = [
    {
        'shortheading': 'DPP AS-11',
        'heading': 'DPP AS-11',
        'mappingsheetcolumn': 7,
        'filenameid': 'DPP-AS-11'
    },
    {
        'shortheading': 'MovieLabs MDDF',
        'heading': 'MovieLabs MDDF',
        'mappingsheetcolumn': 8,
        'filenameid': 'MDDF'
    },
    {
        'shortheading': 'Apple Quicktime',
        'heading': 'Apple Quicktime',
        'mappingsheetcolumn': 9,
        'filenameid': 'AppleQT'
    },
    {
        'shortheading': 'MPEG 7',
        'heading': 'MPEG 7',
        'mappingsheetcolumn': 11,
        'filenameid': 'MPEG7'
    },
    {
        # New column M in MappingsRec 1.7 (work in progress).
        'shortheading': 'ninjs',
        'heading': 'ninjs',
        'mappingsheetcolumn': 12,
        'filenameid': 'ninjs'
    },
    {
        'shortheading': 'NewsML-G2',
        'heading': 'NewsML-G2',
        'mappingsheetcolumn': 13,
        'filenameid': 'NewsML-G2'
    },
    {
        'shortheading': 'PB Core 2.1',
        'heading': 'PB Core 2.1',
        'mappingsheetcolumn': 14,
        'filenameid': 'PBCore21'
    },
    {
        'shortheading': 'Schema.org',
        'heading': 'Schema.org',
        'mappingsheetcolumn': 15,
        'filenameid': 'SchemaOrg'
    },
    {
        'shortheading': 'Sony Cameras',
        'heading': 'Sony XDCAM & Planning',
        'mappingsheetcolumn': 16,
        'filenameid': 'SonyXDCAM'
    },
    {
        'shortheading': 'Panasonic Cameras',
        'heading': 'Panasonic/SMPTE P2',
        'mappingsheetcolumn': 17,
        'filenameid': 'SMPTEP2'
    },
    {
        'shortheading': 'Canon Cameras',
        'heading': 'Canon VideoClip XML',
        'mappingsheetcolumn': 18,
        'filenameid': 'CanonVClip'
    },
    {
        'shortheading': 'exiftool',
        'heading': 'exiftool field id',
        'mappingsheetcolumn': 19,
        'filenameid': 'exiftool'
    },
    {
        'shortheading': 'EIDR Data Fields 2.0',
        'heading': ' EIDR Data Fields 2.0',
        'mappingsheetcolumn': 20,
        'filenameid': 'EIDR'
    }
]

# JSON Schema reference prefix for shared definitions
JSONSCHEMA_REF_PREFIX = 'https://www.iptc.org/std/phovidmd/iptc-phovidmdshared-schema.json'

