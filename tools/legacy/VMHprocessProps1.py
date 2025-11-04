#!/usr/bin/env python3
"""
Python script for retrieving IPTC Video Metadata Hub properties data from a Google sheet
The retrieved data are transformed in HTML as saved as HTML page.

For IPTC-internal use
Creator: Michael Steidl
History:
    2016-11-25 mws: project started, download and HTML output ok
    2020-06-15 BQ: Updated and added to GitHub repository
"""

from __future__ import print_function
import httplib2
import os
import pickle
import sys

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from lxml import etree as ET

from constants import *

from credentials import get_credentials


def main():
    credentials = get_credentials()
    service = build('sheets', 'v4', credentials=credentials)

    result1 = service.spreadsheets().values().get(
        spreadsheetId=SpreadsheetId, range=PropertiesRangeName).execute()
    valuesProp = result1.get('values', [])

    result2 = service.spreadsheets().values().get(
        spreadsheetId=SpreadsheetId, range=ErrataRangeName).execute()
    valuesErr = result2.get('values', [])

    # create the HTML document
    xroot = ET.Element('html')
    head = ET.SubElement(xroot, 'head')
    title = ET.SubElement(head, 'title')
    title.text = 'Video Metadata Hub properties'
    metachset = ET.SubElement(head, 'meta', {'http-equiv': "Content-Type", 'content': "text/html; charset=utf-8"})
    csslink1 = ET.SubElement(head, 'link', {'type': 'text/css', 'rel': 'stylesheet', 'href': 'iptcspecs1.css'})

    body = ET.SubElement(xroot, 'body')
    pageheader = ET.SubElement(body, 'h1', {'class':'pageheader'})
    iptcanc = ET.SubElement(pageheader, 'a', {'href':'https://iptc.org'})
    iptcimg = ET.SubElement(iptcanc, 'img', {'src':'https://iptc.org/download/resources/logos/iptc-gr_70x70.jpg', 'align':'left', 'border':'0'})
    pageheader.text = 'IPTC Video Metadata Hub - Recommendation ' + StdVersion + HeaderAppendix + ' / Properties'
    seeotherdoc0 = ET.SubElement(body, 'p', {'class':'smallnote1'})
    seeotherdoc0.text = '.'
    seeotherdoc1 = ET.SubElement(body, 'p', {'class':'note1'})
    seeotherdoc1.text = 'See the '
    seeotherdoc1link1 = ET.SubElement(seeotherdoc1, 'a', {'href':'IPTC-VideoMetadataHub-mapping-Rec_'+StdVersion+'.html'})
    seeotherdoc1link1.text = 'Recommendation of Video Metadata Hub mappings'
    seeotherdoc2 = ET.SubElement(body, 'p', {'class':'note1'})
    seeotherdoc2.text = 'See also: '
    seeotherdoc1link2 = ET.SubElement(seeotherdoc2, 'a', {'href':'/std/videometadatahub/recommendation/iptc-vmhub-schema.json'})
    seeotherdoc1link2.text = 'JSON Schema of the PVMD properties (specified on this page).'
    docdate = ET.SubElement(body, 'p', {'class':'note1'})
    docdate.text = 'Properties approved on ' + IPTCApprovalDate + '. Document revision as of ' + IPTCRevisionDate + '.'
    changenote1 = ET.SubElement(body, 'p', {'class':'note1'})
    changenote1.text = ''

    docnote1 = ET.SubElement(body, 'p', {'class':'note1'})
    docnote1.text = 'Boxes with green background show a new property or Property Structure. Boxes with grey background show a fixed erratum - '
    docnote1link1 = ET.SubElement(docnote1, 'a', {'href':'#errata'})
    docnote1link1.text = 'see a list of errata at the bottom of this page'
    docnote1link1.tail = ' and how they were fixed.'

    copyrightnotice = ET.fromstring('<p class="smallnote1">Copyright © ' + CopyrightYear + ', <a href="https://iptc.org">IPTC</a> - all rights reserved. Published under the Creative Commons Attribution 4.0 license <a href="http://creativecommons.org/licenses/by/4.0/">http://creativecommons.org/licenses/by/4.0/</a></p>')
    body.append(copyrightnotice)

    propnote1 = ET.fromstring('<p class="note1">Note on the ... Property headers:<br />XMP: based on the ISO XMP standard.<br />PVMD: a specification of JSON properties for Photo and Video MetaData by IPTC (aka phovidmd).</p>')
    body.append(propnote1)
    jsonnote1 = ET.SubElement(body, 'p', {'class':'smallnote1'})
    jsonnote1.text = 'Note on the JSON Data Type column. It shows three values separated by /: 1) the JSON datatype (could be an object, with uppercase name), 2) optionally a sub-type defined by JSON Schema, 3) optionally "array" if multiple values are supported. '


    if not valuesProp:
        print('No Property data found.')
    else:
        table = ET.SubElement(body, 'table', {'class':'spec1 vmhprop'})
        thead = ET.SubElement(table, 'thead')
        throw = ET.SubElement(thead, 'tr')
        thcol1 = ET.SubElement(throw, 'th', {'class':'hdrcol1'})
        thcol1.text = 'Property Group'
        thcol2 = ET.SubElement(throw, 'th', {'class':'hdrcol2'})
        thcol2.text = 'Property Name'
        thcol3 = ET.SubElement(throw, 'th', {'class':'hdrcol3'})
        thcol3.text = 'Definition / Semantics'
        thcol4 = ET.SubElement(throw, 'th', {'class':'hdrcol4'})
        thcol4.text = 'User Notes'
        thcol5 = ET.SubElement(throw, 'th', {'class':'hdrcol5'})
        thcol5.text = 'Change Notes'
        thcol6 = ET.SubElement(throw, 'th', {'class':'hdrcol6'})
        thcol6.text = 'Basic Type/Cardinality'
        #thcol7 = ET.SubElement(throw, 'th', {'class':'hdrcol7'})
        #thcol7.text = 'EBUcore Property'
        thcol8 = ET.SubElement(throw, 'th', {'class':'hdrcol8'})
        thcol8.text = 'XMP Property'
        thcol9 = ET.SubElement(throw, 'th', {'class':'hdrcol9'})
        thcol9.text = 'XMP Data Type'
        thcol10 = ET.SubElement(throw, 'th', {'class':'hdrcol10'})
        thcol10.text = 'PVMD JSON Property'
        thcol11 = ET.SubElement(throw, 'th', {'class':'hdrcol11'})
        thcol11.text = 'PVMD JSON Data Type'

        tbody = ET.SubElement(table, 'tbody')
        for rowcounter in range(FIRST_PROPERTY_ROW, LAST_STRUCTURE_ROW):
            xrow = ET.SubElement(tbody, 'tr')

            propisnew = False
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

            # is the property new? (we highlight these in green)
            try:
                valstr = valuesProp[rowcounter][3]
            except:
                valstr = ''
            if valstr == 'n':
                propisnew = True

            try:
                valstr = valuesProp[rowcounter][1]
            except:
                valstr = ''
            if valstr == 'm':
                xcell1.set('class', 'modified')

            xcell2 = ET.SubElement(xrow, 'td', { 'class': 'bgdcolIptc'})
            try:
                valstr = valuesProp[rowcounter][2]
            except:
                valstr = ' '
            xcell2.text = valstr
            try:
                valstr = valuesProp[rowcounter][3]
            except:
                valstr = ''
            if valstr == 'm':
                xcell2.set('class', 'modified')
            if propisnew:
                xcell2.set('class', 'isnew')

            xcell3 = ET.SubElement(xrow, 'td')
            try:
                valstr = valuesProp[rowcounter][4]
            except:
                valstr = ' '
            xcell3.text = valstr
            try:
                valstr = valuesProp[rowcounter][5]
            except:
                valstr = ''
            if valstr == 'm':
                xcell3.set('class', 'modified')
            if propisnew:
                xcell3.set('class', 'isnew')

            xcell4 = ET.SubElement(xrow, 'td')
            try:
                valstr = valuesProp[rowcounter][6]
            except:
                valstr = ' '
            xcell4.text = valstr
            try:
                valstr = valuesProp[rowcounter][7]
            except:
                valstr = ''
            if valstr == 'm':
                xcell4.set('class', 'modified')

            xcell5 = ET.SubElement(xrow, 'td')
            try:
                valstr = valuesProp[rowcounter][10]
            except:
                valstr = ' '
            xcell5.text = valstr
            if propisnew == True:
                xcell5.set('class', 'isnew')

            xcell6 = ET.SubElement(xrow, 'td')
            try:
                valstr = valuesProp[rowcounter][8]
            except:
                valstr = ' '
            xcell6.text = valstr
            try:
                valstr = valuesProp[rowcounter][9]
            except:
                valstr = ''
            if valstr == 'm':
                xcell6.set('class', 'modified')

            #xcell7 = ET.SubElement(xrow, 'td')
            #try:
            #    valstr = valuesProp[rowcounter][11]
            #except:
            #    valstr = ' '
            #xcell7.text = valstr
            #try:
            #    valstr = valuesProp[rowcounter][12]
            #except:
            #    valstr = ''
            #if valstr == 'm':
            #    xcell7.set('class', 'modified')

            xcell8 = ET.SubElement(xrow, 'td')
            try:
                valstr = valuesProp[rowcounter][13]
            except:
                valstr = ' '
            xcell8.text = valstr
            try:
                valstr = valuesProp[rowcounter][14]
            except:
                valstr = ''
            if valstr == 'm':
                xcell8.set('class', 'modified')

            xcell9 = ET.SubElement(xrow, 'td')
            try:
                valstr = valuesProp[rowcounter][15]
            except:
                valstr = ' '
            xcell9.text = valstr
            try:
                valstr = valuesProp[rowcounter][16]
            except:
                valstr = ''
            if valstr == 'm':
                xcell9.set('class', 'modified')

            xcell10 = ET.SubElement(xrow, 'td')
            try:
                valstr = valuesProp[rowcounter][17]
            except:
                valstr = ' '
            xcell10.text = valstr
            try:
                valstr = valuesProp[rowcounter][18]
            except:
                valstr = ''
            if valstr == 'm':
                xcell10.set('class', 'modified')

            xcell11 = ET.SubElement(xrow, 'td')
            try:
                valstr = valuesProp[rowcounter][19]
            except:
                valstr = ' '
            xcell11.text = valstr
            try:
                valstr = valuesProp[rowcounter][20]
            except:
                valstr = ''
            if valstr == 'm':
                xcell11.set('class', 'modified')

    if not valuesErr:
        print('No Errata data found.')
    else:
        errataheader = ET.SubElement(body,'h2', {'id':'errata'})
        errataheader.text = '(Fixed) Errata'
        table = ET.SubElement(body, 'table', {'class':'spec1 vmhproperrata'})
        thead = ET.SubElement(table, 'thead')
        throw = ET.SubElement(thead, 'tr')
        thcol1 = ET.SubElement(throw, 'th', {'class':'hdrcol1'})
        thcol1.text = 'Date'
        thcol2 = ET.SubElement(throw, 'th', {'class':'hdrcol2'})
        thcol2.text = 'What had an error'
        thcol3 = ET.SubElement(throw, 'th', {'class':'hdrcol3'})
        thcol3.text = 'Error'
        thcol4 = ET.SubElement(throw, 'th', {'class':'hdrcol4'})
        thcol4.text = 'How the error was fixed'

        tbody = ET.SubElement(table, 'tbody')
        # rowcounter: subtract 2 from the row numbers of the PropErrata Google sheet
        for rowcounter in range(15, 17):
            xrow = ET.SubElement(tbody, 'tr')
            xcell1 = ET.SubElement(xrow, 'td')
            try:
                valstr = valuesErr[rowcounter][0]
            except:
                valstr = ' '
            xcell1.text = valstr

            xcell2 = ET.SubElement(xrow, 'td')
            try:
                valstr = valuesErr[rowcounter][1]
            except:
                valstr = ' '
            xcell2.text = valstr

            xcell3 = ET.SubElement(xrow, 'td')
            try:
                valstr = valuesErr[rowcounter][2]
            except:
                valstr = ' '
            xcell3.text = valstr

            xcell4 = ET.SubElement(xrow, 'td')
            try:
                valstr = valuesErr[rowcounter][3]
            except:
                valstr = ' '
            xcell4.text = valstr

    filename = "IPTC-VideoMetadataHub-props-Rec_"+StdVersion+".html"
    print("Creating "+filename)
    with open(filename, 'w') as file:
        file.write(ET.tostring(xroot, pretty_print=True).decode())

if __name__ == '__main__':
    main()
