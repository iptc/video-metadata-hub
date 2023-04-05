#!/usr/bin/env python3
"""
Constant values for updating Video Metadata Hub specs

For IPTC internal use
"""

import os

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/sheets.googleapis.com-python-quickstart.json
SCOPES = [ 'https://www.googleapis.com/auth/spreadsheets.readonly' ]
CLIENT_SECRET_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'client_secret.json')
APPLICATION_NAME = 'Video Metadata Hub Documentation Generator'

# Constant values
StdVersion = "1.4"
HeaderAppendix = "" # "- DRAFT -"   # could be " - D-R-A-F-T - "
IPTCApprovalDate = "19 Oct 2022"
IPTCRevisionDate = "19 Oct 2022"
CopyrightYear = "2022"
SpreadsheetId = '1TgfvHcsbGvJqmF0iUUnaL-RAdd1lbentmb2LhcM8SDk'
PropertiesRangeName = 'PropertiesRec 1.4!A3:W'
MappingsRangeName = 'MappingsRec 1.4!A4:T'
ErrataRangeName = 'PropErrata!A3:E'

# these numbers are relative to the range name given in PropertiesRangeName
FIRST_PROPERTY_ROW = 0
LAST_PROPERTY_ROW = 97
FIRST_STRUCTURE_ROW = 100
LAST_STRUCTURE_ROW = 233

# prefix for JSON Schema shared definitions
JSONSCHEMA_REF_PREFIX = 'https://www.iptc.org/std/phovidmd/iptc-phovidmdshared-schema.json'
