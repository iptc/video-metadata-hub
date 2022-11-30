#!/usr/bin/env python3
"""
Python script for retrieving IPTC Video Metadata Hub properties data from a Google sheet
and creating a JSON Schema file.

For IPTC-internal use
Creator: Michael Steidl
History:
    2017-03-15 mws: existing JSON script adapted to create JSON-LD
    2020-06-15 BQ: updated and added to GitHub repo
"""

from __future__ import print_function
import httplib2
import os
import pickle
import sys

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

import xml.etree.ElementTree as ET

import json
import collections

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

    spreadsheetId = '1TgfvHcsbGvJqmF0iUUnaL-RAdd1lbentmb2LhcM8SDk'
    rangeName = 'Properties 1.4 DRAFT!A3:W'
    result1 = service.spreadsheets().values().get(
        spreadsheetId=spreadsheetId, range=rangeName).execute()
    valuesProp = result1.get('values', [])

    # create properties
    jsonprops = {}
    for rowcounter in range(0, 85):
        try:
            valstr = valuesProp[rowcounter][13]
        except:
            valstr = ' '
        xmpid = valstr.strip('\n')
        try:
            valstr = valuesProp[rowcounter][15]
        except:
            valstr = ' '
        propnamejson = valstr.strip('\n')

        jsonprops[propnamejson] = xmpid

    jsonpropsordered = collections.OrderedDict(sorted(jsonprops.items()))

    # finally: write the JSON Schema snippets
    filename = "VMH-JSON-LD-contextMapping.json"
    with open(filename, "w") as outf:
        print("Creating "+filename)
        json.dump(jsonpropsordered, outf)


if __name__ == '__main__':
    main()
