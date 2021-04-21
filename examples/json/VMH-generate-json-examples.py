#!/usr/bin/env python3
"""
Python script for retrieving IPTC Video Metadata Hub properties data from a Google sheet
to generate JSON example files for use cases.

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


SCOPES = [ 'https://www.googleapis.com/auth/spreadsheets.readonly' ]
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
    examplesRangeName = 'Examples!A3:AB'
    examplesRange = service.spreadsheets().values().get(
        spreadsheetId=spreadsheetId, range=examplesRangeName).execute()
    examplesValues = examplesRange.get('values', [])
    propertiesRangeName = 'PropertiesRec!A3:U'
    propertiesRange = service.spreadsheets().values().get(
        spreadsheetId=spreadsheetId, range=propertiesRangeName).execute()
    propertiesValues = propertiesRange.get('values', [])
    

    # create properties
    jsonprops = {}
    examples_config = [
        {
            'name': 'Enterprise advertising production', # could grab this from sheet?
            'slug': 'eaprod',
            'column_number': 11
        },
        {
            'name': 'Galleries, Libraries, Archives and Museums',
            'slug': 'glam',
            'column_number': 14
        },
        {
            'name': 'Stock Footage',
            'slug': 'stock',
            'column_number': 17
        },
        {
            'name': 'Long-form Production',
            'slug': 'lfprod',
            'column_number': 20
        },
        {
            'name': 'Broadcast Media Management',
            'slug': 'broadcast',
            'column_number': 23
        },
        {
            'name': 'News Agency',
            'slug': 'newsagency',
            'column_number': 26
        }
    ]        
   
    examples_hash = {} 

    for rowcounter in range(0, 90):
        json_param_name = propertiesValues[rowcounter][18].strip()
        json_param_type = propertiesValues[rowcounter][20].strip()
        for example in examples_config:
            slug = example['slug']
            column = example['column_number']
            if len(examplesValues[rowcounter]) < column+1:
                # google truncates rows when there are no values
                continue
            value = examplesValues[rowcounter][column]
            if value:
                # change output to match required json type
                if json_param_type == 'boolean//':
                    value = bool(value)
                elif json_param_type == 'number//':
                    value = float(value)
                elif json_param_type == 'AltLang':
                    value = { 'en': value }
                elif json_param_type == 'string//array':
                    value = [ value ]
                elif json_param_type == 'string/uri/array':
                    value = [ value ]
                elif json_param_type in ['Entity//', 'Entity']:
                    value = { 'name': { 'en': value } }
                elif json_param_type == 'EntityWRole//array':
                    value = [ { 'name': { 'en': value } } ]
                elif json_param_type == 'PublicationEvent//array':
                    value = [ value ]
                elif json_param_type == 'FrameSize':
                    width, height = value.split('x')
                    value = {
                        'widthPixels': int(width),
                        'heightPixels': int(height)
                    }
                elif json_param_type == 'EpisodeSeason':
                    value = { 'name': { 'en': value } }
                elif value.startswith('{'):
                    value = json.loads(value)
                if slug not in examples_hash:
                    examples_hash[slug] = {}
                examples_hash[slug][json_param_name] = value

    # finally: write the JSON Schema snippets
    for slug in examples_hash:
        # jsonpropsordered = collections.OrderedDict(sorted(examples_hash[slug].items()))
        # jsonpropsordered = sorted(examples_hash[slug].items())
        with open("VMH-JSON-Examples-"+slug+".json", "w") as outf:
            output_json = [
                {
                    "photoVideoMetadataIPTC": examples_hash[slug]
                }
            ]
            json.dump(output_json, outf, indent=4)


if __name__ == '__main__':
    main()
