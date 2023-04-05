#!/usr/bin/env python3
"""
Python script for retrieving IPTC Video Metadata Hub mapping data from a Google sheet
The retrieved data are transformed in HTML as saved as HTML page.

For IPTC-internal use
Creator: Michael Steidl
History:
    2016-11-25 mws: project started, download and HTML output ok
    2020-06-15 BQ: Updated and checked into GitHub
    2022-09-29 BQ: Many updates to make changes less painful and remove repetitive code. Still more refactoring needed, but it works.
"""

from __future__ import print_function
import pickle
import os
import sys

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

from lxml import etree as ET

from constants import *

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
        'shortheading': 'NewsML-G2',
        'heading': 'NewsML-G2',
        'mappingsheetcolumn': 12,
        'filenameid': 'NewsML-G2'
    },
    {
        'shortheading': 'PB Core 2.1',
        'heading': 'PB Core 2.1',
        'mappingsheetcolumn': 13,
        'filenameid': 'PBCore21'
    },
    {
        'shortheading': 'Schema.org',
        'heading': 'Schema.org',
        'mappingsheetcolumn': 14,
        'filenameid': 'SchemaOrg'
    },
    {
        'shortheading': 'Sony Cameras',
        'heading': 'Sony XDCAM & Planning',
        'mappingsheetcolumn': 15,
        'filenameid': 'SonyXDCAM'
    },
    {
        'shortheading': 'Panasonic Cameras',
        'heading': 'Panasonic/SMPTE P2',
        'mappingsheetcolumn': 16,
        'filenameid': 'SMPTEP2'
    },
    {
        'shortheading': 'Canon Cameras',
        'heading': 'Canon VideoClip XML',
        'mappingsheetcolumn': 17,
        'filenameid': 'CanonVClip'
    },
    {
        'shortheading': 'exiftool',
        'heading': 'exiftool field id',
        'mappingsheetcolumn': 18,
        'filenameid': 'exiftool'
    },
    {
        'shortheading': 'EIDR Data Fields 2.0',
        'heading': ' EIDR Data Fields 2.0',
        'mappingsheetcolumn': 19,
        'filenameid': 'EIDR'
    }
]

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

def createSpecificMapping(valuesProp, headingtext1, headingtext2, findmoreaturl, mapIdx, filename):
    # create the HTML document
    xroot = ET.Element('html')
    head = ET.SubElement(xroot, 'head')
    title = ET.SubElement(head, 'title')
    title.text = 'Video Metadata Hub Mapping'
    metachset = ET.SubElement(head, 'meta', {'http-equiv': "Content-Type", 'content': "text/html; charset=utf-8"})
    csslink1 = ET.SubElement(head, 'link', {'type': 'text/css', 'rel': 'stylesheet', 'href': 'iptcspecs1.css'})

    body = ET.SubElement(xroot, 'body')
    pageheader = ET.SubElement(body, 'h1', {'class':'pageheader'})
    iptcanc = ET.SubElement(pageheader, 'a', {'href':'https://iptc.org'})
    iptcimg = ET.SubElement(iptcanc, 'img', {'src':'https://iptc.org/download/resources/logos/iptc-gr_70x70.jpg', 'align':'left', 'border':'0'})
    pageheader.text = headingtext1
    seeotherdoc1 = ET.SubElement(body, 'p', {'class':'note1'})
    seeotherdoc1.text = 'Return to '
    seeotherdoc1link1 = ET.SubElement(seeotherdoc1, 'a', {'href':'IPTC-VideoMetadataHub-mapping-Rec_'+StdVersion+'.html'})
    seeotherdoc1link1.text = 'all recommended mappings of the Video Metadata Hub.'

    seeotherdoc2 = ET.SubElement(body, 'p', {'class':'note1'})
    seeotherdoc2.text = 'See the '
    seeotherdoc1link2 = ET.SubElement(seeotherdoc2, 'a', {'href':'IPTC-VideoMetadataHub-props-Rec_'+StdVersion+'.html'})
    seeotherdoc1link2.text = 'specification of Video Metadata Hub properties'

    docdate = ET.SubElement(body, 'p', {'class':'note1'})
    docdate.text = 'Mapping recommended on ' + IPTCApprovalDate + '. Document revision as of ' + IPTCRevisionDate + '.'

    copyrightnotice = ET.fromstring('<p class="smallnote1">Copyright © ' + CopyrightYear + ', <a href="https://iptc.org">IPTC</a> - all rights reserved. Published under the Creative Commons Attribution 4.0 license <a href="http://creativecommons.org/licenses/by/4.0/">http://creativecommons.org/licenses/by/4.0/</a></p>')
    body.append(copyrightnotice)

    mappedstdnote = ET.SubElement(body, 'p', {'class':'note1'})
    mappedstdnote.text = 'In this table the columns with a blue header are defined by the Video Metadata Hub, the column with the green header is defined by ' + headingtext2
    propnote1 = ET.fromstring('<p class="note1">Note on the column headers:<br />EBUcore: based on the EBU Core Metadata Standard.<br />XMP: based on the ISO XMP standard.<br />PVMD: a specification of JSON properties for Photo and Video MetaData by IPTC (aka phovidmd).</p>')
    body.append(propnote1)


    if not valuesProp:
        print('No Property data found.')
    else:
        table = ET.SubElement(body, 'table', {'class':'spec1 vmhmapping'})
        thead = ET.SubElement(table, 'thead')
        throw = ET.SubElement(thead, 'tr')
        thcol1 = ET.SubElement(throw, 'th', {'class':'hdrcol1'})
        thcol1.text = 'Property Group'
        thcol2 = ET.SubElement(throw, 'th', {'class':'hdrcol2'})
        thcol2.text = 'Property Name'
        thcol3 = ET.SubElement(throw, 'th', {'class':'hdrcol3'})
        thcol3.text = 'Definition / Semantics'
        """
        thcol4 = ET.SubElement(throw, 'th', {'class':'hdrcol4'})
        thcol4.text = 'Basic Type/Cardinality'
        """
        thcol5 = ET.SubElement(throw, 'th', {'class':'hdrcol5'})
        thcol5.text = 'EBUcore'
        thcol6 = ET.SubElement(throw, 'th', {'class':'hdrcol6'})
        thcol6.text = 'XMP'
        thcol7 = ET.SubElement(throw, 'th', {'class':'hdrcol7'})
        thcol7.text = 'PVMD JSON'
        thcol8 = ET.SubElement(throw, 'th', {'class':'hdrcolNoniptc'})
        thcol8.text = headingtext2

        # second row with "find more at ..." links
        throw = ET.SubElement(thead, 'tr')
        thcol1 = ET.SubElement(throw, 'td', {'class':'hdrcol1'})
        thcol1.text = ' '
        thcol2 = ET.SubElement(throw, 'td', {'class':'hdrcol2'})
        thcol2.text = ' '
        thcol3 = ET.SubElement(throw, 'td', {'class':'hdrcol3'})
        thcol3.text = ' '
        """
        thcol4 = ET.SubElement(throw, 'td', {'class':'hdrcol4'})
        thcol4.text = ''
        """
        moreatlink = valuesProp[0][4]
        colcode = ET.fromstring(
            '<td class="hdrcolIptc"><a href="' + moreatlink + '" target="_blank">Find more about it at ...</a></td>')
        throw.append(colcode)
        moreatlink = valuesProp[0][5]
        colcode = ET.fromstring(
            '<td class="hdrcolIptc"><a href="' + moreatlink + '" target="_blank">Find more about it at ...</a></td>')
        throw.append(colcode)
        moreatlink = valuesProp[0][6]
        colcode = ET.fromstring(
            '<td class="hdrcolIptc"><a href="' + moreatlink + '" target="_blank">Find more about it at ...</a></td>')
        throw.append(colcode)

        moreatlink = valuesProp[0][mapIdx]
        if moreatlink != '':
            colcode = ET.fromstring(
                '<td class="hdrcolNoniptc"><a href="' + moreatlink + '" target="_blank">Find more about it at ...</a></td>')
            throw.append(colcode)
        else:
            colcode = ET.fromstring(
                '<td class="hdrcolNoniptc"> </td>')
            throw.append(colcode)

        tbody = ET.SubElement(table, 'tbody')

        for rowcounter in range(2, 210):
            xrow = ET.SubElement(tbody, 'tr')
            teststr = valuesProp[rowcounter][0]
            if teststr == 'Property Structures (PS)':
                xrow.set('style', 'background-color: #009999;')
            if teststr.find('PS', 0) == 0:
                xrow.set('style', 'background-color: #00cccc;')
            xcell1 = ET.SubElement(xrow, 'td', { 'class': 'bgdcolIptc'})

            try:
                valstr = valuesProp[rowcounter][0]
            except:
                valstr = ' '
            xcell1.text = valstr

            xcell2 = ET.SubElement(xrow, 'td', { 'class': 'bgdcolIptc'})
            try:
                valstr = valuesProp[rowcounter][1]
            except:
                valstr = ' '
            xcell2.text = valstr

            xcell3 = ET.SubElement(xrow, 'td', { 'class': 'bgdcolIptc'})
            try:
                valstr = valuesProp[rowcounter][2]
            except:
                valstr = ' '
            xcell3.text = valstr
            """
            xcell4 = ET.SubElement(xrow, 'td', { 'class': 'bgdcolIptc'})
            try:
                valstr = valuesProp[rowcounter][3]
            except:
                valstr = ' '
            xcell4.text = valstr
            """
            xcell5 = ET.SubElement(xrow, 'td', { 'class': 'bgdcolIptc'})
            try:
                valstr = valuesProp[rowcounter][4]
            except:
                valstr = ' '
            xcell5.text = valstr

            xcell6 = ET.SubElement(xrow, 'td', { 'class': 'bgdcolIptc'})
            try:
                valstr = valuesProp[rowcounter][5]
            except:
                valstr = ' '
            xcell6.text = valstr

            xcell7 = ET.SubElement(xrow, 'td', { 'class': 'bgdcolIptc'})
            try:
                valstr = valuesProp[rowcounter][6]
            except:
                valstr = ' '
            xcell7.text = valstr

            xcell8 = ET.SubElement(xrow, 'td', { 'class': 'bgdcolNoniptc'})
            try:
                valstr = valuesProp[rowcounter][mapIdx]
            except:
                valstr = ' '
            xcell8.text = valstr

    with open(filename, 'w') as file:
        file.write(ET.tostring(xroot, pretty_print=True).decode())

def main():
    credentials = get_credentials()
    service = build('sheets', 'v4', credentials=credentials)

    result1 = service.spreadsheets().values().get(
        spreadsheetId=SpreadsheetId, range=MappingsRangeName).execute()
    valuesProp = result1.get('values', [])

    # create the main mapping HTML document
    xroot = ET.Element('html')
    head = ET.SubElement(xroot, 'head')
    title = ET.SubElement(head, 'title')
    title.text = 'Video Metadata Hub Mapping'
    metachset = ET.SubElement(head, 'meta', {'http-equiv': "Content-Type", 'content': "text/html; charset=utf-8"})
    csslink1 = ET.SubElement(head, 'link', {'type': 'text/css', 'rel': 'stylesheet', 'href': 'iptcspecs1.css'})

    body = ET.SubElement(xroot, 'body')
    pageheader = ET.SubElement(body, 'h1', {'class':'pageheader'})
    iptcanc = ET.SubElement(pageheader, 'a', {'href':'https://iptc.org'})
    iptcimg = ET.SubElement(iptcanc, 'img', {'src':'https://iptc.org/download/resources/logos/iptc-gr_70x70.jpg', 'align':'left', 'border':'0'})
    pageheader.text = 'IPTC Video Metadata Hub - Recommendation '+ StdVersion +' / all Mappings' + HeaderAppendix
    seeotherdoc1 = ET.SubElement(body, 'p', {'class':'note1'})
    seeotherdoc1.text = 'See the '
    seeotherdoc1link1 = ET.SubElement(seeotherdoc1, 'a', {'href':'IPTC-VideoMetadataHub-props-Rec_'+StdVersion+'.html'})
    seeotherdoc1link1.text = 'specification of Video Metadata Hub properties'
    docdate = ET.SubElement(body, 'p', {'class':'note1'})
    docdate.text = 'Mapping recommended on ' + IPTCApprovalDate + '. Document revision as of ' + IPTCRevisionDate + '.'
    copyrightnotice = ET.fromstring('<p class="smallnote1">Copyright © '+ CopyrightYear + ', <a href="https://iptc.org">IPTC</a> - all rights reserved. Published under the Creative Commons Attribution 4.0 license <a href="http://creativecommons.org/licenses/by/4.0/">http://creativecommons.org/licenses/by/4.0/</a></p>')
    body.append(copyrightnotice)
    mappedstdnote = ET.SubElement(body, 'p', {'class':'note1'})
    mappedstdnote.text = 'In this table the columns with a blue header are defined by the Video Metadata Hub, the columns with the green or amber headers are defined by other standards or tools.'
    propnote1 = ET.fromstring('<p class="note1">Note on the column headers:<br />EBUcore: based on the EBU Core Metadata Standard.<br />XMP: based on the ISO XMP standard.<br />PVMD: a specification of JSON properties for Photo and Video MetaData by IPTC (aka phovidmd).</p>')
    body.append(propnote1)
    docnote1 = ET.SubElement(body, 'p', {'class':'smallnote1'})
    docnote1.text = 'The header of mappings to other standards provides a link to a table including only this mapping (better for printing)'

    if not valuesProp:
        print('No Property data found.')
    else:
        table = ET.SubElement(body, 'table', {'class':'spec1 vmhmapping'})
        thead = ET.SubElement(table, 'thead')
        throw = ET.SubElement(thead, 'tr')
        thcol1 = ET.SubElement(throw, 'th', {'class':'hdrcol1'})
        thcol1.text = 'Property Group'
        thcol2 = ET.SubElement(throw, 'th', {'class':'hdrcol2'})
        thcol2.text = 'Property Name'
        thcol3 = ET.SubElement(throw, 'th', {'class':'hdrcol3'})
        thcol3.text = 'Definition / Semantics'
        """
        thcol4 = ET.SubElement(throw, 'th', {'class':'hdrcol4'})
        thcol4.text = 'Basic Type/Cardinality'
        """
        thcol5 = ET.SubElement(throw, 'th', {'class':'hdrcol5'})
        thcol5.text = 'EBUcore'
        thcol6 = ET.SubElement(throw, 'th', {'class':'hdrcol6'})
        thcol6.text = 'XMP'
        thcol7 = ET.SubElement(throw, 'th', {'class':'hdrcol7'})
        thcol7.text = 'IPTC PVMD JSON'

        for mapping in MAPPINGS:
            heading = mapping['heading']
            filename = 'IPTC-VideoMetadataHub-mapping-'+mapping['filenameid']+'-Rec_'+StdVersion+'.html'
            thcol = ET.SubElement(throw, 'th', {'class':'hdrcolNoniptc'})
            thcollink = ET.SubElement(thcol,'a', {'href': filename })
            thcollink.text = heading

        # second row with "find more at ..." links
        throw = ET.SubElement(thead, 'tr')
        thcol1 = ET.SubElement(throw, 'td', {'class':'hdrcol1'})
        thcol1.text = ' '
        thcol2 = ET.SubElement(throw, 'td', {'class':'hdrcol2'})
        thcol2.text = ' '
        thcol3 = ET.SubElement(throw, 'td', {'class':'hdrcol3'})
        thcol3.text = ' '
        """
        thcol4 = ET.SubElement(throw, 'td', {'class':'hdrcol4'})
        thcol4.text = ''
        """
        moreatlink = valuesProp[0][4]
        colcode = ET.fromstring(
            '<td class="hdrcolIptc"><a href="' + moreatlink + '" target="_blank">Find more about it at ...</a></td>')
        throw.append(colcode)
        moreatlink = valuesProp[0][5]
        colcode = ET.fromstring(
            '<td class="hdrcolIptc"><a href="' + moreatlink + '" target="_blank">Find more about it at ...</a></td>')
        throw.append(colcode)
        moreatlink = valuesProp[0][6]
        colcode = ET.fromstring(
            '<td class="hdrcolIptc"><a href="' + moreatlink + '" target="_blank">Find more about it at ...</a></td>')
        throw.append(colcode)

        for mapping in MAPPINGS:
            col = mapping['mappingsheetcolumn']
            moreatlink = valuesProp[0][col]
            if moreatlink != '':
                colcode = ET.fromstring(
                    '<td class="hdrcolNoniptc"><a href="' + moreatlink + '" target="_blank">Find more about it at ...</a></td>')
                throw.append(colcode)
            else:
                colcode = ET.fromstring(
                    '<td class="hdrcolNoniptc"> </td>')
                throw.append(colcode)

        tbody = ET.SubElement(table, 'tbody')
        for rowcounter in range(2, 210):
            xrow = ET.SubElement(tbody, 'tr')
            teststr = valuesProp[rowcounter][0]
            if teststr == 'Property Structures (PS)':
                xrow.set('style', 'background-color: #009999;')
            if teststr.find('PS', 0) == 0:
                xrow.set('style', 'background-color: #00cccc;')
            xcell1 = ET.SubElement(xrow, 'td', {'class':'bgdcolIptc'})

            try:
                valstr = valuesProp[rowcounter][0]
            except:
                valstr = ' '
            xcell1.text = valstr

            xcell2 = ET.SubElement(xrow, 'td', {'class':'bgdcolIptc'})
            try:
                valstr = valuesProp[rowcounter][1]
            except:
                valstr = ' '
            xcell2.text = valstr

            xcell3 = ET.SubElement(xrow, 'td', {'class':'bgdcolIptc'})
            try:
                valstr = valuesProp[rowcounter][2]
            except:
                valstr = ' '
            xcell3.text = valstr
            """
            xcell4 = ET.SubElement(xrow, 'td', {'class':'bgdcolIptc'})
            try:
                valstr = valuesProp[rowcounter][4]
            except:
                valstr = ' '
            xcell4.text = valstr
            """
            xcell5 = ET.SubElement(xrow, 'td', {'class':'bgdcolIptc'})
            try:
                valstr = valuesProp[rowcounter][4]
            except:
                valstr = ' '
            xcell5.text = valstr

            xcell6 = ET.SubElement(xrow, 'td', {'class':'bgdcolIptc'})
            try:
                valstr = valuesProp[rowcounter][5]
            except:
                valstr = ' '
            xcell6.text = valstr

            xcell7 = ET.SubElement(xrow, 'td', {'class':'bgdcolIptc'})
            try:
                valstr = valuesProp[rowcounter][6]
            except:
                valstr = ' '
            xcell7.text = valstr

            for mapping in MAPPINGS:
                col = mapping['mappingsheetcolumn']
                mappingcell = ET.SubElement(xrow, 'td', {'class':'bgdcolIptc'})
                try:
                    mappingcell.text = valuesProp[rowcounter][col]
                except:
                    mappingcell.text = ' '

    filename = "IPTC-VideoMetadataHub-mapping-Rec_"+StdVersion+".html"
    with open(filename, 'w') as file:
        print("Creating "+filename)
        file.write(ET.tostring(xroot, pretty_print=True).decode())

    for mapping in MAPPINGS:
        htmlheading = 'IPTC Video Metadata Hub - Recommendation ' + StdVersion + HeaderAppendix + '/ Mapping VMHub - '+mapping['shortheading']
        column = mapping['mappingsheetcolumn']
        moreatlink = valuesProp[1][column]
        filename = 'IPTC-VideoMetadataHub-mapping-'+mapping['filenameid']+'-Rec_'+StdVersion+'.html'
        print("Creating "+filename)
        createSpecificMapping(valuesProp, htmlheading, mapping['heading'], moreatlink, column, filename)

if __name__ == '__main__':
    main()
