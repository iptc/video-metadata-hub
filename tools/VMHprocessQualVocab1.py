"""
Python script for retrieving IPTC Video Metadata Hub Qualifier Vocabulary data from a Google sheet
The retrieved data are transformed into CSV data

For IPTC-internal use
Creator: Michael Steidl
History:
    2018-01-19 MS: adapted other VMHprocess script
"""

from __future__ import print_function
import httplib2
import os

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

import xml.etree.ElementTree as ET

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

from constants import *

def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'sheets.googleapis.com-python-quickstart.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

def writeConcepts(valuesProp, fromRow, toRow, outputFN, toplevelkeyword):
    # open the output document
    filename = ".\\output\\" + outputFN

    print("Creating "+filename)
    with open(filename, "w", encoding='utf-8') as outf:
        for rowindex in range(fromRow, toRow):
            # outf.write("\n")

            # collect data from a row of the sheet
            try:
                valstr = valuesProp[rowindex][3]
            except:
                valstr = ' '
            cptCode = valstr.strip('\n')

            try:
                valstr = valuesProp[rowindex][1]
            except:
                valstr = ' '
            cptName = valstr.strip('\n')

            try:
                valstr = valuesProp[rowindex][5]
            except:
                valstr = ' '
            cptQcode = valstr.strip('\n')


            # write concept specification
            outstr = "ivqu:" + cptCode
            outstr += "|2016-10-14T12:00:00+00:00|cpnat:abstract||" + cptName
            outstr += "|2018-01-19T12:00:00+00:00|VMH-dev\n"
            outf.write(outstr)


        outf.close()

def writeConceptProperties(valuesProp, fromRow, toRow, outputFN, toplevelkeyword):
    # open the output document
    filename = ".\\output\\" + outputFN

    print("Creating "+filename)
    with open(filename, "w", encoding='utf-8') as outf:
        for rowindex in range(fromRow, toRow):
            # outf.write("\n")

            # collect data from a row of the sheet
            try:
                valstr = valuesProp[rowindex][0]
            except:
                valstr = ' '
            refVmhprop = valstr.strip('\n')

            try:
                valstr = valuesProp[rowindex][1]
            except:
                valstr = ' '
            cptName = valstr.strip('\n')

            try:
                valstr = valuesProp[rowindex][2]
            except:
                valstr = ' '
            cptDefinition = valstr.strip('\n')

            try:
                valstr = valuesProp[rowindex][3]
            except:
                valstr = ' '
            cptCode = valstr.strip('\n')

            try:
                valstr = valuesProp[rowindex][5]
            except:
                valstr = ' '
            cptQcode = valstr.strip('\n')

            # write concept name
            outstr = "http://cv.iptc.org/newscodes/videoqualifier/|" + cptCode
            outstr += "|http://iptc.org/std/nar/2006-10-01/name|||en-GB|text|" + cptName + "|VMH-dev\n"
            outf.write(outstr)

            # write concept definition
            outstr = "http://cv.iptc.org/newscodes/videoqualifier/|" + cptCode
            outstr += "|http://iptc.org/std/nar/2006-10-01/definition|||en-GB|text|" + cptDefinition + "|VMH-dev\n"
            outf.write(outstr)

            # write concept (user) note
            outstr = "http://cv.iptc.org/newscodes/videoqualifier/|" + cptCode
            outstr += "|http://iptc.org/std/nar/2006-10-01/note|||en-GB|text|Use with Video Metadata Hub property: " + refVmhprop + "|VMH-dev\n"
            outf.write(outstr)


        outf.close()

def main():
    """Shows basic usage of the Sheets API.
    Creates a Sheets API service object
    https://docs.google.com/spreadsheets/d/1TgfvHcsbGvJqmF0iUUnaL-RAdd1lbentmb2LhcM8SDk/edit
    = IPTC Video Metadata Working Document
    """
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?'
                    'version=v4')
    service = discovery.build('sheets', 'v4', http=http,
                              discoveryServiceUrl=discoveryUrl)

    spreadsheetId = '1TgfvHcsbGvJqmF0iUUnaL-RAdd1lbentmb2LhcM8SDk'
    rangeName = 'QualifierVocab Rec 1.0!A5:F'
    result1 = service.spreadsheets().values().get(
        spreadsheetId=spreadsheetId, range=rangeName).execute()
    values = result1.get('values', [])

    if not values:
        print('No Property data found.')
        return
    else:
        # create concepts
        writeConcepts(values, 0, 55, "VMH-QualVocab_Concepts.txt", "")
        # create properties
        writeConceptProperties(values, 0, 55, "VMH-QualVocab_CptProps.txt", "")


if __name__ == '__main__':
    main()
