#!/usr/bin/env python3
"""
Python script for retrieving IPTC Video Metadata Hub mapping data from a Google sheet
The retrieved data are transformed in HTML as saved as HTML page.

For IPTC-internal use
Creator: Michael Steidl
History:
    2016-11-25 mws: project started, download and HTML output ok
    2020-06-15 BQ: Updated and checked into GitHub
"""

from __future__ import print_function
import pickle
import os
import sys

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

from lxml import etree as ET

SCOPES = 'https://www.googleapis.com/auth/spreadsheets.readonly'
CLIENT_SECRET_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'client_secret.json')
APPLICATION_NAME = 'Video Metadata Hub Documentation Generator'

# Constant values
StdVersion = "1.3"
HeaderAppendix = ""   # could be " - D-R-A-F-T - "
IPTCApprovalDate = "13 May 2020"
IPTCRevisionDate = "13 May 2020"
CopyrightYear = "2020"

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

        for rowcounter in range(2, 186):
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

    spreadsheetId = '1TgfvHcsbGvJqmF0iUUnaL-RAdd1lbentmb2LhcM8SDk'
    rangeName = 'MappingRec 1.3.1 DRAFT!A4:R'
    result1 = service.spreadsheets().values().get(
        spreadsheetId=spreadsheetId, range=rangeName).execute()
    valuesProp = result1.get('values', [])

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
        thcol8 = ET.SubElement(throw, 'th', {'class':'hdrcolNoniptc'})
        thcol8link = ET.SubElement(thcol8,'a', {'href':'IPTC-VideoMetadataHub-mapping-AppleQT-Rec_'+StdVersion+'.html'})
        thcol8link.text = 'Apple Quicktime'
        thcol9 = ET.SubElement(throw, 'th', {'class':'hdrcolNoniptc2'})
        thcol9link = ET.SubElement(thcol9,'a', {'href':'IPTC-VideoMetadataHub-mapping-MPEG7-Rec_'+StdVersion+'.html'})
        thcol9link.text = 'MPEG 7'
        thcol10 = ET.SubElement(throw, 'th', {'class':'hdrcolNoniptc'})
        thcol10link = ET.SubElement(thcol10,'a', {'href':'IPTC-VideoMetadataHub-mapping-NewsMLG2-Rec_'+StdVersion+'.html'})
        thcol10link.text = 'NewsML-G2'
        thcol11 = ET.SubElement(throw, 'th', {'class':'hdrcolNoniptc2'})
        thcol11link = ET.SubElement(thcol11,'a', {'href':'IPTC-VideoMetadataHub-mapping-PBCore21-Rec_'+StdVersion+'.html'})
        thcol11link.text = 'PB Core 2.1'
        thcol12 = ET.SubElement(throw, 'th', {'class':'hdrcolNoniptc'})
        thcol12link = ET.SubElement(thcol12,'a', {'href':'IPTC-VideoMetadataHub-mapping-SchemaOrg-Rec_'+StdVersion+'.html'})
        thcol12link.text = 'Schema.org'
        # new in 2018-03
        thcol13 = ET.SubElement(throw, 'th', {'class':'hdrcolNoniptc2'})
        thcol13link = ET.SubElement(thcol13,'a', {'href':'IPTC-VideoMetadataHub-mapping-SonyXDCAM-Rec_'+StdVersion+'.html'})
        thcol13link.text = 'Sony XDCAM & Planning'
        thcol14 = ET.SubElement(throw, 'th', {'class':'hdrcolNoniptc'})
        thcol14link = ET.SubElement(thcol14,'a', {'href':'IPTC-VideoMetadataHub-mapping-Panasonic-SMPTEP2-Rec_'+StdVersion+'.html'})
        thcol14link.text = 'Panasonic/SMPTE P2'
        thcol15 = ET.SubElement(throw, 'th', {'class':'hdrcolNoniptc2'})
        thcol15link = ET.SubElement(thcol15,'a', {'href':'IPTC-VideoMetadataHub-mapping-CanonVClip-Rec_'+StdVersion+'.html'})
        thcol15link.text = 'Canon VideoClip XML'
        thcol16 = ET.SubElement(throw, 'th', {'class':'hdrcolNoniptc'})
        thcol16link = ET.SubElement(thcol16,'a', {'href':'IPTC-VideoMetadataHub-mapping-exiftool-Rec_'+StdVersion+'.html'})
        thcol16link.text = 'exiftool field ids'
        thcol17 = ET.SubElement(throw, 'th', {'class':'hdrcolNoniptc2'})
        thcol17link = ET.SubElement(thcol17,'a', {'href':'IPTC-VideoMetadataHub-mapping-EIDR-Rec_'+StdVersion+'.html'})
        thcol17link.text = 'EIDR Data Fields 2.0'

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

        moreatlink = valuesProp[0][7]
        if moreatlink != '':
            colcode = ET.fromstring(
                '<td class="hdrcolNoniptc"><a href="' + moreatlink + '" target="_blank">Find more about it at ...</a></td>')
            throw.append(colcode)
        else:
            colcode = ET.fromstring(
                '<td class="hdrcolNoniptc"> </td>')
            throw.append(colcode)
        moreatlink = valuesProp[0][9]
        if moreatlink != '':
            colcode = ET.fromstring(
                '<td class="hdrcolNoniptc2"><a href="' + moreatlink + '" target="_blank">Find more about it at ...</a></td>')
            throw.append(colcode)
        else:
            colcode = ET.fromstring(
                '<td class="hdrcolNoniptc2"> </td>')
            throw.append(colcode)
        moreatlink = valuesProp[0][10]
        if moreatlink != '':
            colcode = ET.fromstring(
                '<td class="hdrcolNoniptc"><a href="' + moreatlink + '" target="_blank">Find more about it at ...</a></td>')
            throw.append(colcode)
        else:
            colcode = ET.fromstring(
                '<td class="hdrcolNoniptc"> </td>')
            throw.append(colcode)
        moreatlink = valuesProp[0][11]
        if moreatlink != '':
            colcode = ET.fromstring(
                '<td class="hdrcolNoniptc2"><a href="' + moreatlink + '" target="_blank">Find more about it at ...</a></td>')
            throw.append(colcode)
        else:
            colcode = ET.fromstring(
                '<td class="hdrcolNoniptc2"> </td>')
            throw.append(colcode)
        moreatlink = valuesProp[0][12]
        if moreatlink != '':
            colcode = ET.fromstring(
                '<td class="hdrcolNoniptc"><a href="' + moreatlink + '" target="_blank">Find more about it at ...</a></td>')
            throw.append(colcode)
        else:
            colcode = ET.fromstring(
                '<td class="hdrcolNoniptc"> </td>')
            throw.append(colcode)
        moreatlink = valuesProp[0][13]
        if moreatlink != '':
            colcode = ET.fromstring(
                '<td class="hdrcolNoniptc2"><a href="' + moreatlink + '" target="_blank">Find more about it at ...</a></td>')
            throw.append(colcode)
        else:
            colcode = ET.fromstring(
                '<td class="hdrcolNoniptc2"> </td>')
            throw.append(colcode)
        moreatlink = valuesProp[0][14]
        if moreatlink != '':
            colcode = ET.fromstring(
                '<td class="hdrcolNoniptc"><a href="' + moreatlink + '" target="_blank">Find more about it at ...</a></td>')
            throw.append(colcode)
        else:
            colcode = ET.fromstring(
                '<td class="hdrcolNoniptc"> </td>')
            throw.append(colcode)
        moreatlink = valuesProp[0][15]
        if moreatlink != '':
            colcode = ET.fromstring(
                '<td class="hdrcolNoniptc2"><a href="' + moreatlink + '" target="_blank">Find more about it at ...</a></td>')
            throw.append(colcode)
        else:
            colcode = ET.fromstring(
                '<td class="hdrcolNoniptc2"> </td>')
            throw.append(colcode)
        moreatlink = valuesProp[0][16]
        if moreatlink != '':
            colcode = ET.fromstring(
                '<td class="hdrcolNoniptc"><a href="' + moreatlink + '" target="_blank">Find more about it at ...</a></td>')
            throw.append(colcode)
        else:
            colcode = ET.fromstring(
                '<td class="hdrcolNoniptc"> </td>')
            throw.append(colcode)
        moreatlink = valuesProp[0][17]
        if moreatlink != '':
            colcode = ET.fromstring(
                '<td class="hdrcolNoniptc2"><a href="' + moreatlink + '" target="_blank">Find more about it at ...</a></td>')
            throw.append(colcode)
        else:
            colcode = ET.fromstring(
                '<td class="hdrcolNoniptc2"> </td>')
            throw.append(colcode)

        tbody = ET.SubElement(table, 'tbody')
        for rowcounter in range(2, 186):
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
                valstr = valuesProp[rowcounter][3]
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

            xcell8 = ET.SubElement(xrow, 'td', {'class':'bgdcolNoniptc'})
            try:
                valstr = valuesProp[rowcounter][7]
            except:
                valstr = ' '
            xcell8.text = valstr

            xcell9 = ET.SubElement(xrow, 'td', {'class':'bgdcolNoniptc2'})
            try:
                valstr = valuesProp[rowcounter][9]
            except:
                valstr = ' '
            xcell9.text = valstr

            xcell10 = ET.SubElement(xrow, 'td', {'class':'bgdcolNoniptc'})
            try:
                valstr = valuesProp[rowcounter][10]
            except:
                valstr = ' '
            xcell10.text = valstr

            xcell11 = ET.SubElement(xrow, 'td', {'class':'bgdcolNoniptc2'})
            try:
                valstr = valuesProp[rowcounter][11]
            except:
                valstr = ' '
            xcell11.text = valstr

            xcell12 = ET.SubElement(xrow, 'td', {'class':'bgdcolNoniptc'})
            try:
                valstr = valuesProp[rowcounter][12]
            except:
                valstr = ' '
            xcell12.text = valstr

            xcell13 = ET.SubElement(xrow, 'td', {'class':'bgdcolNoniptc2'})
            try:
                valstr = valuesProp[rowcounter][13]
            except:
                valstr = ' '
            xcell13.text = valstr

            xcell14 = ET.SubElement(xrow, 'td', {'class':'bgdcolNoniptc'})
            try:
                valstr = valuesProp[rowcounter][14]
            except:
                valstr = ' '
            xcell14.text = valstr

            xcell15 = ET.SubElement(xrow, 'td', {'class':'bgdcolNoniptc2'})
            try:
                valstr = valuesProp[rowcounter][15]
            except:
                valstr = ' '
            xcell15.text = valstr

            xcell16 = ET.SubElement(xrow, 'td', {'class':'bgdcolNoniptc'})
            try:
                valstr = valuesProp[rowcounter][16]
            except:
                valstr = ' '
            xcell16.text = valstr

            xcell17 = ET.SubElement(xrow, 'td', {'class':'bgdcolNoniptc2'})
            try:
                valstr = valuesProp[rowcounter][17]
            except:
                valstr = ' '
            xcell17.text = valstr


    filename = "IPTC-VideoMetadataHub-mapping-Rec_"+StdVersion+".html"
    with open(filename, 'w') as file:
        file.write(ET.tostring(xroot, pretty_print=True).decode())

    moreatlink = valuesProp[0][7]
    createSpecificMapping(valuesProp, 'IPTC Video Metadata Hub - Recommendation ' + StdVersion + HeaderAppendix + '/ Mapping VMHub - Apple Quicktime', 'Apple Quicktime', moreatlink, 7, 'IPTC-VideoMetadataHub-mapping-AppleQT-Rec_'+StdVersion+'.html')
    createSpecificMapping(valuesProp, 'IPTC Video Metadata Hub - Recommendation ' + StdVersion + HeaderAppendix + '/ Mapping VMHub - MPEG 7', 'MPEG 7', moreatlink, 9,'IPTC-VideoMetadataHub-mapping-MPEG7-Rec_'+StdVersion+'.html')
    createSpecificMapping(valuesProp, 'IPTC Video Metadata Hub - Recommendation ' + StdVersion + HeaderAppendix + '/ Mapping VMHub - NewsML-G2', 'NewsML-G2', moreatlink, 10,'IPTC-VideoMetadataHub-mapping-NewsMLG2-Rec_'+StdVersion+'.html')
    createSpecificMapping(valuesProp, 'IPTC Video Metadata Hub - Recommendation ' + StdVersion + HeaderAppendix + '/ Mapping VMHub - PB Core 2.1', 'PB Core 2.1', moreatlink, 11,'IPTC-VideoMetadataHub-mapping-PBCore21-Rec_'+StdVersion+'.html')
    createSpecificMapping(valuesProp, 'IPTC Video Metadata Hub - Recommendation ' + StdVersion + HeaderAppendix + '/ Mapping VMHub - Schema.org', 'Schema.org', moreatlink, 12,'IPTC-VideoMetadataHub-mapping-SchemaOrg-Rec_'+StdVersion+'.html')
    # new in 2018-03
    createSpecificMapping(valuesProp, 'IPTC Video Metadata Hub - Recommendation ' + StdVersion + HeaderAppendix + '/ Mapping VMHub - Sony Cameras ', 'Sony XDCAM & Planning', moreatlink, 13,'IPTC-VideoMetadataHub-mapping-SonyXDCAM-Rec_'+StdVersion+'.html')
    createSpecificMapping(valuesProp, 'IPTC Video Metadata Hub - Recommendation ' + StdVersion + HeaderAppendix + '/ Mapping VMHub - Panasonic Cameras', 'Panasonic/SMPTE P2', moreatlink, 14,'IPTC-VideoMetadataHub-mapping-Panasonic-SMPTEP2-Rec_'+StdVersion+'.html')
    createSpecificMapping(valuesProp, 'IPTC Video Metadata Hub - Recommendation ' + StdVersion + HeaderAppendix + '/ Mapping VMHub - Canon Cameras', 'Canon VideoClip XML', moreatlink, 15,'IPTC-VideoMetadataHub-mapping-CanonVClip-Rec_'+StdVersion+'.html')
    createSpecificMapping(valuesProp, 'IPTC Video Metadata Hub - Recommendation ' + StdVersion + HeaderAppendix + '/ Mapping VMHub - exiftool', 'exiftool field id', moreatlink, 16,'IPTC-VideoMetadataHub-mapping-exiftool-Rec_'+StdVersion+'.html')
    createSpecificMapping(valuesProp, 'IPTC Video Metadata Hub - Recommendation ' + StdVersion + HeaderAppendix + '/ Mapping VMHub - EIDR Data Fields 2.0', 'EIDR Data Fields 2.0', moreatlink, 17,'IPTC-VideoMetadataHub-mapping-EIDR-Rec_'+StdVersion+'.html')

if __name__ == '__main__':
    main()
