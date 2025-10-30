#!/usr/bin/env python3
"""
Constant values for updating Video Metadata Hub specs

For IPTC internal use
"""

import os

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/sheets.googleapis.com-python-quickstart.json
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
CLIENT_SECRET_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'client_secret.json')
APPLICATION_NAME = 'Video Metadata Hub Documentation Generator'

# Constant values
StdVersion = "1.7"
HeaderAppendix = "" # "- DRAFT -"   # could be " - D-R-A-F-T - "
IPTCApprovalDate = "16 October 2025"
IPTCRevisionDate = "16 October 2025"
CopyrightYear = "2025"
SpreadsheetId = '1TgfvHcsbGvJqmF0iUUnaL-RAdd1lbentmb2LhcM8SDk'
PropertiesRangeName = 'PropertiesRec 1.7!A3:W'
MappingsRangeName = 'MappingsRec 1.7!A4:T'
ErrataRangeName = 'PropErrata!A3:E'

# these numbers are relative to the range name given in PropertiesRangeName
FIRST_PROPERTY_ROW = 0
LAST_PROPERTY_ROW = 104
FIRST_STRUCTURE_ROW = 106
LAST_STRUCTURE_ROW = 246

MAPPINGS_FIRST_PROPERTY_ROW = 2
MAPPINGS_LAST_PROPERTY_ROW = 215

# prefix for JSON Schema shared definitions
JSONSCHEMA_REF_PREFIX = 'https://www.iptc.org/std/phovidmd/iptc-phovidmdshared-schema.json'
