#!/usr/bin/env python3
"""
Python script for retrieving IPTC Video Metadata Hub properties data from a Google sheet
The retrieved data are transformed in HTML as saved as HTML page.

For IPTC-internal use
Creator: Michael Steidl
History:
    2017-01-19 mws: started, download and JSON output ok
    2020-06-15 BQ: updated, checked into GitHub repo
"""

from __future__ import print_function
import collections
import httplib2
import json
import os
import pickle
import sys

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

import xml.etree.ElementTree as ET

from constants import *

def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """

    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CLIENT_SECRET_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    return creds

def main():
    credentials = get_credentials()
    service = build('sheets', 'v4', credentials=credentials)

    result1 = service.spreadsheets().values().get(
        spreadsheetId=SpreadsheetId, range=PropertiesRangeName).execute()
    valuesProp = result1.get('values', [])

    # create properties
    jsonprops = {}
    for rowcounter in range(FIRST_PROPERTY_ROW - 1, LAST_PROPERTY_ROW):
        try:
            valstr = valuesProp[rowcounter][0]  # Property Group
        except:
            valstr = ' '
        propgroup = valstr.strip('\n')
        try:
            valstr = valuesProp[rowcounter][2]  # Property Name (text)
        except:
            valstr = ' '
        proptitle = valstr.strip('\n')
        try:
            valstr = valuesProp[rowcounter][4]  # Definition (text)
        except:
            valstr = ' '
        propdef = valstr.strip('\n')
        try:
            valstr = valuesProp[rowcounter][17] # JSON property names
        except:
            valstr = ' '
        # propname = propgroup + '-' + valstr.strip('\n')
        propname = valstr.strip('\n')
        try:
            valstr = valuesProp[rowcounter][19] # JSON data type
        except:
            valstr = ' '
        propparams = valstr.strip('\n')
        print("row "+str(rowcounter)+", prop name = "+propname+", prop params = "+propparams)
        
        # propname = valstr.strip('\n')
#        try:
#            valstr = valuesProp[rowcounter][20]
#        except:
#            valstr = ' '
#        propparams = valstr.strip('\n')
        propdetails = {}
        propdetails['title'] = proptitle
        propdetails['description'] = propdef

        arrdetails = {}
        if propparams[0].isupper(): # a referenced structure
            params = propparams.split('/')
            if len(params) > 0:
                refobjectname = params[0]
                if len(params) > 1:
                    if params[1] == 'array':
                        propdetails['type'] = 'array'
                        arrdetails['$ref'] = JSONSCHEMA_REF_PREFIX + '#/definitions/' + refobjectname
                        propdetails['items'] = arrdetails
                else:
                    propdetails['$ref'] = JSONSCHEMA_REF_PREFIX + '#/definitions/' + refobjectname
        else: # a plain property
            params = propparams.split('/')
            proptype = params[0]
            propformat = params[1]
            moreparams = params[2]
            if moreparams.find('enum') > -1:
                propdetails['enum'] = ["dummy1"]
            if moreparams.find('array') > -1:
                propdetails['type'] = 'array'
                arrdetails['type'] = proptype
                if propformat != '':
                    arrdetails['format'] = propformat
                propdetails['items'] = arrdetails
            else:
                propdetails['type'] = proptype
                if propformat != '':
                    propdetails['format'] = propformat
        jsonprops[propname] = propdetails

    jsonpropsordered = collections.OrderedDict(sorted(jsonprops.items()))

    # finally: write the JSON Schema snippets
    filename = "VMH-JSON-Schema-snip-properties.json"
    print("Creating "+filename)
    with open(filename, "w") as outf:
        json.dump(jsonpropsordered, outf, indent=4)

    # create referenced objects
    jsonrefobjprops = {}
    refobject = {}
    refobjectname1 = ''
    refobjprops = {}

    for rowcounter in range(FIRST_STRUCTURE_ROW - 1, LAST_STRUCTURE_ROW - 1):
        try:
            valstr = valuesProp[rowcounter][0]  # prop group
        except:
            valstr = ' '
        propgroup = valstr.strip('\n')
        try:
            valstr = valuesProp[rowcounter][2]  # prop name (human)
        except:
            valstr = ' '
        proptitle = valstr.strip('\n')
        try:
            valstr = valuesProp[rowcounter][4]  # prop definition (human)
        except:
            valstr = ' '
        propdef = valstr.strip('\n')
        try:
            valstr = valuesProp[rowcounter][17] # JSON property name
        except:
            valstr = ' '
        propname = valstr.strip('\n')
        try:
            valstr = valuesProp[rowcounter][19] # JSON schema data type
        except:
            valstr = ' '
        propparams = valstr.strip('\n')
        print("row "+str(rowcounter)+", prop name = "+propname+", prop params = "+propparams)

        if propparams == 'object':
            if refobject:
                refobject['properties'] = refobjprops
                refobject['required'] = mandatoryprops
                jsonrefobjprops[refobjectname1] = refobject
            refobject = {}
            refobjectname1 = propname
            refobject['type'] = 'object'
            refobject['additionalProperties'] = False
            refobjprops = {}
            mandatoryprops = []
        else: # a property of the object above
            propdetails = {}
            propdetails['title'] = proptitle
            propdetails['description'] = propdef

            refobjectname = ''
            if propparams[0].isupper():  # a referenced structure
                params = propparams.split('/')
                if len(params) > 0:
                    refobjectname = params[0]
                    objectcard = 'single'
                    if len(params) > 1:
                        if params[1] == 'array':
                            propdetails['type'] = 'array'
                            arrdetails = {}
                            arrdetails['$ref'] = '#/definitions/' + refobjectname
                            propdetails['items'] = arrdetails
                    else:
                        propdetails['$ref'] = '#/definitions/' + refobjectname
            elif params != 'NA':  # a plain property
                #params = propparams.split('/')
                #if len(params) < 2:
                #    import pdb; pdb.set_trace()
                #proptype = params[0]
                #propformat = params[1]
                #moreparams = params[2]
                try:
                    (proptype, propformat, moreparams) = propparams.split('/')
                except ValueError:
                    raise Exception('JSON type not defined correctly: '+propparams+' in row '+str(rowcounter+1))
                if moreparams.find('MANDATORY') > -1:
                    mandatoryprops.append(propname)
                if moreparams.find('enum') > -1:
                    propdetails['enum'] = ["dummy1"]
                if moreparams.find('array') > -1:
                    propdetails['type'] = 'array'
                    arrdetails = {}
                    arrdetails['type'] = proptype
                    if propformat != '':
                        arrdetails['format'] = propformat
                    propdetails['items'] = arrdetails
                else:
                    propdetails['type'] = proptype
                    if propformat != '':
                        propdetails['format'] = propformat

            refobjprops[propname] = propdetails

        jsonrefobjpropsordered = collections.OrderedDict(sorted(jsonrefobjprops.items()))
    # finally: write the JSON Schema snippet
    filename = "VMH-JSON-Schema-snip-refObjectproperties.json"
    with open(filename, "w") as outf:
        print("Creating "+filename)
        json.dump(jsonrefobjpropsordered, outf, indent=4)


if __name__ == '__main__':
    main()
