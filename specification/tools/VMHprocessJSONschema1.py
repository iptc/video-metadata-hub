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


SCOPES = 'https://www.googleapis.com/auth/spreadsheets.readonly'
CLIENT_SECRET_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'client_secret.json')
APPLICATION_NAME = 'Video Metadata Hub Documentation Generator'

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

    spreadsheetId = '1TgfvHcsbGvJqmF0iUUnaL-RAdd1lbentmb2LhcM8SDk'
    rangeName = 'PropertiesRec!A3:W'
    result1 = service.spreadsheets().values().get(
        spreadsheetId=spreadsheetId, range=rangeName).execute()
    valuesProp = result1.get('values', [])


    # create properties
    jsonprops = {}
    for rowcounter in range(0, 85): #81
        try:
            valstr = valuesProp[rowcounter][0]
        except:
            valstr = ' '
        propgroup = valstr.strip('\n')
        try:
            valstr = valuesProp[rowcounter][2]
        except:
            valstr = ' '
        proptitle = valstr.strip('\n')
        try:
            valstr = valuesProp[rowcounter][4]
        except:
            valstr = ' '
        propdef = valstr.strip('\n')
        try:
            valstr = valuesProp[rowcounter][17]
        except:
            valstr = ' '
        propusedby = valstr.strip('\n')
        try:
            valstr = valuesProp[rowcounter][18]
        except:
            valstr = ' '
        propname = propgroup + '-' + valstr.strip('\n')
        try:
            valstr = valuesProp[rowcounter][20]
        except:
            valstr = ' '
        propparams = valstr.strip('\n')

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
                        arrdetails['$ref'] = '#/definitions/' + refobjectname
                        propdetails['items'] = arrdetails
                else:
                    propdetails['$ref'] = '#/definitions/' + refobjectname
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
    with open("VMH-JSON-Schema-snip-properties.json", "w") as outf:
        json.dump(jsonpropsordered, outf, indent=4)

    # create referenced objects
    jsonrefobjprops = {}
    refobject = {}
    refobjectname1 = ''
    refobjprops = {}

    for rowcounter in range(87, 185):
        try:
            valstr = valuesProp[rowcounter][0]
        except:
            valstr = ' '
        propgroup = valstr.strip('\n')
        try:
            valstr = valuesProp[rowcounter][2]
        except:
            valstr = ' '
        proptitle = valstr.strip('\n')
        try:
            valstr = valuesProp[rowcounter][4]
        except:
            valstr = ' '
        propdef = valstr.strip('\n')
        try:
            valstr = valuesProp[rowcounter][17]
        except:
            valstr = ' '
        propusedby = valstr.strip('\n')
        try:
            valstr = valuesProp[rowcounter][18]
        except:
            valstr = ' '
        propname = propgroup + '-' + valstr.strip('\n')
        try:
            valstr = valuesProp[rowcounter][20]
        except:
            valstr = ' '
        propparams = valstr.strip('\n')

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
            elif params != ['NA']:  # a plain property
                params = propparams.split('/')
                proptype = params[0]
                propformat = params[1]
                moreparams = params[2]
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
    with open("VMH-JSON-Schema-snip-refObjectproperties.json", "w") as outf:
        json.dump(jsonrefobjpropsordered, outf, indent=4)


if __name__ == '__main__':
    main()
