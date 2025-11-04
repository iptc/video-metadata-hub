#!/usr/bin/env python3

"""
Python script for retrieving IPTC Photo Metadata properties data
from the Google sheet IPTC PMD Working Document
The retrieved data are transformed into an object/dict which can be saved as YAML or JSON document.
As multiple files are created they are finally collated to a single iptc-pmd-techreference file.

Creator: Michael Steidl (mwsteidl@newsit.biz) for IPTC Photo Metadata Working Group (iptc.org)
Adapted by Brendan Quinn(mdirector@iptc.org) for IPTC Video Metadata Hub
History:
    2024 BQ: converted from Photo Metadata to Video Metadata Hub
    2021-09-28 v05 mws: format in JSON data type column changed
    2021-07-15 v04 mws: rename techref property 'label' to 'name'
    2021-06-02 v03 mws: rename the output file to ...techreference...
    2021-05-21 mws: etdetailsmode allows to slim down the details of the output
    2021-04-23 mws: round of updates closed:
                    * content of IPTC PMD Working Document extended = columns added
                    * ... sub-properties of an IPTC PMD property added
                    * After creating the YAML files for the top level properties of the file:
                      Their content is collated to a final iptc-pmd-techguide_v2019.1--.yml file
    2021-04-17 mws: file buildPmdInvestigationRefdoc03.py copied to *:_v01.py
"""
# from __future__ import print_function
from datetime import datetime, timezone
from typing import Optional
import yaml
import json

from googleapiclient.discovery import build

TECHREF_FN = 'iptc-vmhub-techreference_2024.1_0--'

from constants import *
from credentials import get_credentials

# ************************************
# CONSTANTS of the Working Document
#
# column index of specific columns in the sheet (updated 2021-04-13, sort order cols inserted)
COLGSORTORDER = 10 # global sort order
#COLSSO = 2  # special sort order
#COLIPDMSCHEMA = 3  # IPTC PMD Schema: IPTC Core or IPTC Extension
#COLSIGNAL01 = 7  # internal processing signal for using/rendering
#COLPMDUSERGUIDEREF = 5  # reference link inside the IPTC PMD User Guide
COLVMHPROPNAME = 3  # IPTC VMHub Property Name
COLVMHPROPLABEL = 3  # IPTC VMHub Property, recommended label (same as prop name for VMH)
COLVMHPROPDEF = 5  # IPTC VMHub Property, semantic definition (not used, yet)
#COLIIMNAME = 27  # IIM data set name
#COLIIMMAXB = 28  # IIM string - maximum bytes
COLXMPTAG = 13
#COLXMPNS = 29  # XMP Namespace alias
#COLXMPID = 30  # XMP identifier (local to the namespace!)
COLJSONID = 18  # IPTC VMHub JSON ID
COLJSONDT = 20  # JSON Data Type
#COLMAPHIST = 50  # Mapping History Note
#COLEXIFTAG = 51  # mapped Exif Tag
#COLSCHORG = 53  # mapped schema.org property
COLETTNAMES = 22  # ExifTool Tag names
#COLETEXIFTNAMES = 56  # ExifTool Tag name of a mapped Exif Tag
SPREADSHEET_ID = '1TgfvHcsbGvJqmF0iUUnaL-RAdd1lbentmb2LhcM8SDk'
SPREADSHEET_SHEET_RANGE = 'PropertiesRec 1.5 with sort order!A:W'
VMHUB_PROPS_START = 3 # row in spreadsheet where prop definitions begin, relative to spreadsheet range above
VMHUB_PROPS_END = 102 # row in spreadsheet where prop definitions end, relative to spreadsheet range above
VMHUB_STRUCTS_START = 104 # row in spreadsheet where prop structures begin, relative to spreadsheet range above
VMHUB_STRUCTS_END = 237 # row in spreadsheet where prop structures end, relative to spreadsheet range above
# PMD: SPREADSHEET_ID = '1WZLI0OZzfDuGohZIsqfjSiTm31F-e9g5IG4ctvCIsLY'
# PMD: SPREADSHEET_SHEET_RANGE = 'IPTC-PMD-worksheet!A4:BE'

# *********************
# HELPER FUNCTIONS
#


def write_outputfile(outbox: dict, output_fp: str, outputformat: str):
    """ Serializes a dict to a YAML and/or JSON file

    :param outbox: the dict holding the to-be-serialized data
    :param output_fp: file path of the output file - WITHOUT an extension!
    :param outputformat: 'YAML' or 'JSON' or both separated by a space
    :return: nothing
    """
    if 'YAML' in outputformat.upper():
        with open(output_fp + '.yml', "w", encoding='utf-8') as outf:
            try:
                yaml.dump(outbox, outf, sort_keys=False)
            except yaml.YAMLError as exc:
                print('ERROR in writing YAML to file: ' + str(exc))
    if 'JSON' in outputformat.upper():
        with open(output_fp + '.json', "w", encoding='utf-8') as outf:
            json.dump(outbox, outf)


def decode_ipmd_datatype(datatype: str, rowno: int) -> Optional[dict]:
    """Decodes the format of an IPTC PMD/JSON data type: {data type id}/{data format}/occurrences

    :param datatype: IPTC PMD/JSON data type as string
    :param rowno: number of the row in the reference document
    :return: decoded data type as dict. If the datatype cannot be decoded: None
    """
    decodeddt = {
        'core': 'NONE',
        'refstruct': '',
        'format': '',
        'occurrence': 'single'
    }
    if datatype == '' or datatype == 'NA':
        return None
    usedatatype: str = datatype
    if '|' in datatype:  # use only the first data type in a |-separated sequence of data types
        datatypes: list = datatype.split('|')
        usedatatype = datatypes[0]
    dtparts: list[str] = usedatatype.split('/')
    if len(dtparts) < 3:
        print('ERROR: less than 2 / in row ' + str(rowno) + ' - value: ' + usedatatype)
    decodeddt['core'] = dtparts[0]
    # if dtparts[0][:2].istitle():  # if the data type start with upper case = an object, no plain value
    if dtparts[0].lower() == 'object':
        decodeddt['core'] = 'struct'
        decodeddt['refstruct'] = dtparts[1]  # 0 -> 1
    else:
        if len(dtparts) > 1:
            if dtparts[1] != '':
                decodeddt['format'] = dtparts[1]
    if len(dtparts) > 2:
        if dtparts[2].lower() == 'array':
            decodeddt['occurrence'] = 'multi'
    return decodeddt


def get_lines_fromtextfile(text_fp: str, firstlineno: int, lastlineno: int) -> list[str]:
    """Reads lines from a text file and returns them in a defined range

    :param text_fp: file path of the text file
    :param firstlineno: number of the first line to return - first line in the file = lineno 1
    :param lastlineno: number of the last line to return, could exceed line count of file
    :return: list of strings
    """
    resultlines: list = []
    with open(text_fp, encoding='utf-8') as textfile:
        alllines: list = textfile.readlines()
        lctr: int = 0
        for line in alllines:
            lctr += 1
            if lctr < firstlineno:
                continue
            if lctr > lastlineno:
                continue
            resultlines.append(line)
    return resultlines


def read_googledeveloperkey() -> str:
    """Read Google Developer Key from a local file

    :return: the Google Developer Key
    """
    devkey: str = ''
    with open('GoogleDeveloperKey.json', mode='r', encoding='utf-8') as devkeyfile:
        googledev_data: dict = json.load(devkeyfile)
        if 'developerKey' in googledev_data:
            devkey = googledev_data['developerKey']
    return devkey


# *************************************
# WRITE REFERENCE DOCUMENT FUNCTIONS
#

def write_refdoc4et(sheetrows: list, from_row: int, to_row: int, output_fn: str,
                    groupname: str, etdetailsmode: str, outputformat: str = 'YAML'):
    """Writes a reference document for ExifTool tags, using YAML or/and JSON format

    :param sheetrows: a list of a set of data for each row
    :param from_row: lower limit of the range of rows
    :param to_row: upper limit of the range of rows
    :param output_fn: name of the output file
    :param groupname: name of the top level key in the output file
    :param outputformat: values 'YAML' or/and 'JSON', if both: comma separated
    :return: nothing
    """
    etdetailslevel: int = 0  # Rule: a higher value supports more details, the minimal level = 1
    # check the etdetailsmode:
    if etdetailsmode != 'full':
        if etdetailsmode != 'mid':
            if etdetailsmode != 'min':
                print('ERROR in write_refdoc4et: the used argument of etdetailsmode is invalid: ' + etdetailsmode)
                return
            else:
                etdetailslevel = 1
        else:
            etdetailslevel = 5
    else:
        etdetailslevel = 9

    # set the output filepath, extension is NOT included yet!
    output_fp: str = os.path.join('.', 'output', output_fn)
    # create output dict
    outbox: dict = {}
    ts: str = datetime.now(timezone.utc).isoformat()
    outbox['release_timestamp'] = ts[:19] + '+00:00'
    outgroup: dict = {}

    valstr: str = ''
    for rowcounter in range(from_row, to_row):  # iterate across a range of rows
        #if sheetrows[rowcounter][COLSIGNAL01] == "x":
        #    continue   # skip rows x-ed out
        try:
            valstr = sheetrows[rowcounter][COLETTNAMES]  # exiftool tag names
        except IndexError:
            valstr = ' '
        etnamesstr: str = valstr.strip()
        if etnamesstr == '':
            continue
        # get the optional ExifTool tag for a mapped Exif Tag
        #try:
        #    valstr = sheetrows[rowcounter][COLETEXIFTNAMES]  # ExifTool tag of a mapped Exif Tag
        #except IndexError:
        #    valstr = ' '
        #etexiftag: str = valstr.strip()

        # get more details of the PMD property
        try:
            valstr = sheetrows[rowcounter][COLGSO]  # Global sort order
        except IndexError:
            valstr = ' '
        globalsortorder: str = valstr.strip()
        #try:
        #    valstr = sheetrows[rowcounter][COLPMDUSERGUIDEREF]  # PMD user guide topic
        #except IndexError:
        #    valstr = ' '
        #proptopic: str = valstr.strip()
        try:
            valstr = sheetrows[rowcounter][COLVMHPROPNAME]  # PMD prop name
        except IndexError:
            valstr = ' '
        propname: str = valstr.strip()
        if propname.find('structure') > -1:
            continue   # skip header of a structure
        try:
            valstr = sheetrows[rowcounter][COLVMHPROPLABEL]  # PMD prop label
        except IndexError:
            valstr = ' '
        proplabel: str = valstr.strip()
        #try:
        #    valstr = sheetrows[rowcounter][COLIIMNAME]  # PMD IIM Name
        #except IndexError:
        #    valstr = ' '
        #propiimname: str = valstr.strip()
        try:
            valstr = sheetrows[rowcounter][COLXMPTAG]  # VMHub prop XMP Tag
        except IndexError:
            valstr = ' '
        (propxmpns, propxmpid) = valstr.split(':')
        #try:
        #    valstr = sheetrows[rowcounter][COLXMPID]  # PMD prop XMP id
        #except IndexError:
        #    valstr = ' '
        #propxmpid: str = valstr.strip()
        try:
            valstr = sheetrows[rowcounter][COLJSONID]  # PMD prop JSON id
        except IndexError:
            valstr = ' '
        propjsonid: str = valstr.strip()
        try:
            valstr = sheetrows[rowcounter][COLJSONDT]  # PMD prop DataType
        except IndexError:
            valstr = ' '
        propjsondt: str = valstr.strip()
        sepidx: int = propjsondt.find('|')  # check for alternative data types, use the first one
        if sepidx > -1:
            propjsondt = propjsondt[:sepidx]
        slashidx: int = propjsondt.find('/')  # get the string before the first slash
        if slashidx > -1:
            propdt = propjsondt[:slashidx]
        else:
            propdt = propjsondt
        """
        Exif part not relevant for VMHub
        try:
            valstr = sheetrows[rowcounter][COLEXIFTAG]  # (mapped) Exif Tag
        except IndexError:
            valstr = ' '
        tempstr: str = valstr.strip()
        tempstrparts: list = tempstr.split('/')
        if len(tempstrparts) > 1:
            exifid: str = tempstrparts[1]
        else:
            exifid: str = ''
        # start with Exif Tag
        if etexiftag != '':
            if etexiftag == 'ExifIFD:DateTimeOriginal+ExifIFD:TimeZoneOffset':
                etexiftags: list = etexiftag.split('+')
                etexiftag_inuse = etexiftags[0]
                outprop: dict = {}
                if (groupname == 'et_topnoprefix') or (groupname == 'et_instructure'):
                    nameparts: list = etexiftag_inuse.split(':')
                    propid: str = nameparts[1]
                else:
                    propid: str = etexiftag_inuse.replace(':', '_')
                fullname: str = propname + 'DateTimeOriginal (Exif)|Exif Tag Id 36867'
                outprop['ipmdid'] = propjsonid
                if etdetailslevel > 1:
                    outprop['name'] = fullname
                    sortorder: str = globalsortorder + 'z'
                    outprop['sortorder'] = sortorder
                    outprop['ipmddatatype'] = propdt
                    if groupname == 'et_topwithprefix':
                        outputcode: str = 'exif,' + proptopic
                        outprop['output'] = outputcode
                outgroup[propid] = outprop
                etexiftag_inuse = etexiftags[1]
                outprop: dict = {}
                if (groupname == 'et_topnoprefix') or (groupname == 'et_instructure'):
                    nameparts: list = etexiftag_inuse.split(':')
                    propid: str = nameparts[1]
                else:
                    propid: str = etexiftag_inuse.replace(':', '_')
                fullname: str = propname + 'TimeZoneOffset (Exif)|Exif Tag Id 36881'
                outprop['ipmdid'] = propjsonid
                if etdetailslevel > 1:
                    outprop['name'] = fullname
                    sortorder: str = globalsortorder + 'z'
                    outprop['sortorder'] = sortorder
                    outprop['ipmddatatype'] = propdt
                    if groupname == 'et_topwithprefix':
                        outputcode: str = 'exif,' + proptopic
                        outprop['output'] = outputcode
                outgroup[propid] = outprop
            elif etexiftag == 'IFD0:ImageDescription|ExifIFD:UserComment':
                etexiftags: list = etexiftag.split('|')
                etexiftag_inuse = etexiftags[0]
                outprop: dict = {}
                if (groupname == 'et_topnoprefix') or (groupname == 'et_instructure'):
                    nameparts: list = etexiftag_inuse.split(':')
                    propid: str = nameparts[1]
                else:
                    propid: str = etexiftag_inuse.replace(':', '_')
                fullname: str = propname + 'ImageDescription (Exif)|Exif Tag Id 270'
                outprop['ipmdid'] = propjsonid
                if etdetailslevel > 1:
                    outprop['name'] = fullname
                    sortorder: str = globalsortorder + 'z'
                    outprop['sortorder'] = sortorder
                    outprop['ipmddatatype'] = propdt
                    if groupname == 'et_topwithprefix':
                        outputcode: str = 'exif,' + proptopic
                        outprop['output'] = outputcode
                outgroup[propid] = outprop
                etexiftag_inuse = etexiftags[1]
                outprop: dict = {}
                if (groupname == 'et_topnoprefix') or (groupname == 'et_instructure'):
                    nameparts: list = etexiftag_inuse.split(':')
                    propid: str = nameparts[1]
                else:
                    propid: str = etexiftag_inuse.replace(':', '_')
                fullname: str = propname + 'UserComment (Exif)|Exif Tag Id 37510'
                outprop['ipmdid'] = propjsonid
                if etdetailslevel > 1:
                    outprop['name'] = fullname
                    sortorder: str = globalsortorder + 'z'
                    outprop['sortorder'] = sortorder
                    outprop['ipmddatatype'] = propdt
                    if groupname == 'et_topwithprefix':
                        outputcode: str = 'exif,' + proptopic
                        outprop['output'] = outputcode
                outgroup[propid] = outprop
            else:
                outprop: dict = {}
                if (groupname == 'et_topnoprefix') or (groupname == 'et_instructure'):
                    nameparts: list = etexiftag.split(':')
                    if len(nameparts) > 1:
                        propid: str = nameparts[1]
                    else:
                        propid: str = ''
                else:
                    propid: str = etexiftag.replace(':', '_')
                fullname: str = propname + ' (Exif)|Exif Tag Id ' + exifid
                outprop['ipmdid'] = propjsonid
                if etdetailslevel > 1:
                    outprop['name'] = fullname
                    sortorder: str = globalsortorder + 'z'
                    outprop['sortorder'] = sortorder
                    outprop['ipmddatatype'] = propdt
                    if groupname == 'et_topwithprefix':
                        outputcode: str = 'exif,' + proptopic
                        outprop['output'] = outputcode
                if propid != '':
                    outgroup[propid] = outprop
        """

        # next: IIM and XMP tags
        etnameslist: list = etnamesstr.split(',')
        # reverse list as the XMP tag is always the first one, for the topnoprefix output it should be the last one
        rev_etnameslist: list = list(reversed(etnameslist))
        for etname in rev_etnameslist:
            slashidx: int = etname.find('/')
            etnameadj: str = etname
            if slashidx > -1:
                etnameadj = etname[:slashidx]
            if etnameadj.find(':') > -1:   # ET tags with prefix
                if etnameadj[:4] == 'IPTC':
                    if 'IPTC:DateCreated+IPTC:TimeCreated' in etnameadj:
                        # Handmade split of the IIM properties Date Created and Time Created
                        outprop: dict = {}  # for Date Created
                        if (groupname == 'et_topnoprefix') or (groupname == 'et_instructure'):
                            propid: str = 'DateCreated'
                        else:
                            propid: str = 'IPTC_DateCreated'
                        fullname = 'Date Created (IIM)|IIM 2:55 Date Created'
                        outprop['ipmdid'] = propjsonid
                        if etdetailslevel > 1:
                            outprop['name'] = fullname
                            sortorder: str = globalsortorder + 'id'
                            outprop['sortorder'] = sortorder
                            outprop['ipmddatatype'] = propdt
                            if groupname != 'et_instructure':
                                specidx: str = '#' + propname.lower().replace(' ', '-').replace('(', '').replace(')',
                                                                                                                 '')
                                outprop['specidx'] = specidx
                            if groupname == 'et_topwithprefix':
                                outputcode: str = 'iim,' + proptopic
                                outprop['output'] = outputcode
                        outgroup[propid] = outprop

                        outprop: dict = {}  # for Time Created
                        if (groupname == 'et_topnoprefix') or (groupname == 'et_instructure'):
                            propid: str = 'TimeCreated'
                        else:
                            propid: str = 'IPTC_TimeCreated'
                        fullname = 'Time Created (IIM)|IIM 2:60 Time Created'
                        outprop['ipmdid'] = propjsonid
                        if etdetailslevel > 1:
                            outprop['name'] = fullname
                            sortorder: str = globalsortorder + 'it'
                            outprop['sortorder'] = sortorder
                            if groupname != 'et_instructure':
                                specidx: str = '#' + propname.lower().replace(' ', '-').replace('(', '').replace(')', '')
                                outprop['specidx'] = specidx
                            if groupname == 'et_topwithprefix':
                                outputcode: str = 'iim,' + proptopic
                                outprop['output'] = outputcode
                        outgroup[propid] = outprop
                    else:  # a 'simple' tag
                        outprop: dict = {}
                        if (groupname == 'et_topnoprefix') or (groupname == 'et_instructure'):
                            propid: str = etnameadj[5:]
                        else:
                            propid: str = etnameadj.replace(':', '_')
                        fullname: str = propname + " (IIM)|IIM " + propiimname
                        outprop['ipmdid'] = propjsonid
                        if etdetailslevel > 1:
                            outprop['name'] = fullname
                            sortorder: str = globalsortorder + 'i'
                            outprop['sortorder'] = sortorder
                            if groupname != 'et_instructure':
                                specidx: str = '#' + propname.lower().replace(' ', '-').replace('(', '').replace(')', '')
                                outprop['specidx'] = specidx
                            if groupname == 'et_topwithprefix':
                                outputcode: str = 'iim,' + proptopic
                                outprop['output'] = outputcode
                        outgroup[propid] = outprop
                if etnameadj[:3] == 'XMP':
                    outprop: dict = {}
                    if (groupname == 'et_topnoprefix') or (groupname == 'et_instructure'):
                        colonidx: int = etnameadj.index(':')
                        propid: str = etnameadj[colonidx + 1:]
                    else:
                        propid: str = etnameadj.replace(':', '_')
                    fullname: str = propname + " (XMP)|XMP " + propxmpns + ':' + propxmpid
                    outprop['ipmdid'] = propjsonid
                    if etdetailslevel > 1:
                        outprop['name'] = fullname
                        if groupname != 'et_instructure':
                            sortorder: str = globalsortorder + 'x'
                            outprop['sortorder'] = sortorder
                            specidx: str = '#' + propname.lower().replace(' ', '-').replace('(', '').replace(')', '')
                            outprop['specidx'] = specidx
                        if groupname == 'et_topwithprefix':
                            outputcode: str = 'xmp,' + proptopic
                            outprop['output'] = outputcode
                    outgroup[propid] = outprop
            else:  # Typically this is a property in a structure
                outprop: dict = {}
                propid: str = etnameadj
                if propid == '{any}':
                    continue
                fullname: str = propname + " (XMP)|XMP " + propxmpns + ':' + propxmpid
                outprop['ipmdid'] = propjsonid
                if etdetailslevel > 1:
                    outprop['name'] = fullname
                    if groupname != 'et_instructure':
                        sortorder: str = globalsortorder + 'x'
                        outprop['sortorder'] = sortorder
                        specidx: str = '#' + propname.lower().replace(' ', '-').replace('(', '').replace(')', '')
                        outprop['specidx'] = specidx
                    if groupname == 'et_topwithprefix':
                        outputcode: str = 'xmp,' + proptopic
                        outprop['output'] = outputcode
                outgroup[propid] = outprop
        # end of etnameslist
    # end of rows loop
    outbox[groupname] = outgroup
    # write the output files
    write_outputfile(outbox, output_fp, outputformat)


def write_refdoc4ipmd_top(sheetrows: list, from_row: int, to_row: int,
                          output_fn: str, groupname: str, outputformat: str = 'YAML'):
    """Writes a reference document about the top level properties defined by IPTC PMD Standard

    :param sheetrows: a list of a set of data for each row
    :param from_row: lower limit of the range of rows
    :param to_row: upper limit of the range of rows
    :param output_fn: name of the output file
    :param groupname: name of the top level key in the YAML file
    :param outputformat: 'JSON' or/and 'YAML', if both: comma separated
    :return: nothing
    """
    # set the output filepath, extension is NOT included yet!
    output_fp: str = ".\\output\\" + output_fn
    # create output dict
    outbox: dict = {}
    ts: str = datetime.now(timezone.utc).isoformat()
    outbox['release_timestamp'] = ts[:19] + '+00:00'
    outgroup: dict = {}

    # process the data from the sheet
    for rowcounter in range(from_row, to_row):  # iterate across a range of rows
        valstr: str = ''
        #if sheetrows[rowcounter][COLSIGNAL01] == "x":
        #    continue   # skip rows x-ed out
        try:
            valstr = sheetrows[rowcounter][COLETTNAMES]  # exiftool tag names
        except IndexError:
            valstr = ' '
        etnamesstr: str = valstr.strip()
        # get the ExifTool tag of an optional mapped Exif Tag
        #try:
        #    valstr = sheetrows[rowcounter][COLETEXIFTNAMES]  # ExifTool tag of a mapped Exif Tag
        #except IndexError:
        #    valstr = ' '
        #etexiftag: str = valstr.strip()

        # get more details of the PMD property
        try:
            valstr = sheetrows[rowcounter][COLGSORTORDER]  # Global sort order
        except IndexError:
            valstr = ''
        globalsortorder: str = valstr.strip()
        #try:
        #    valstr = sheetrows[rowcounter][COLIPDMSCHEMA]  # IPTC PMD Schema
        #except IndexError:
        #    valstr = ' '
        #ipmdschema: str = valstr.strip()
        #if 'IptcExt' in ipmdschema:
        #    ipmdschema = 'IptcExt'
        #try:
        #    valstr = sheetrows[rowcounter][COLPMDUSERGUIDEREF]  # PMD user guide topic
        #except IndexError:
        #    valstr = ' '
        #proptopic: str = valstr.strip()
        try:
            valstr = sheetrows[rowcounter][COLVMHPROPNAME]  # PMD prop name
        except IndexError:
            valstr = ' '
        propname: str = valstr.strip()
        if propname.find('structure') > -1:
            continue   # skip header of a structure
        try:
            valstr = sheetrows[rowcounter][COLVMHPROPLABEL]  # PMD prop label
        except IndexError:
            valstr = ' '
        proplabel: str = valstr.strip()
        #try:
        #    valstr = sheetrows[rowcounter][COLIIMNAME]  # PMD IIM Name
        #except IndexError:
        #    valstr = ' '
        #propiimname: str = valstr.strip()
        #propiimmaxb: int = 0
        #try:
        #    tempstr = sheetrows[rowcounter][COLIIMMAXB]  # PMD IIM string, max bytes
        #except IndexError:
        #    tempstr = ''
        #if tempstr != '':
        #    try:
        #        propiimmaxb: int = int(tempstr.strip())
        #    except ValueError:
        #        propiimmaxb: int = 0
        try:
            valstr = sheetrows[rowcounter][COLXMPTAG]  # VMHub prop XMP Tag
        except IndexError:
            valstr = ''
        if valstr:
            (propxmpns, propxmpid) = valstr.split(':')
        try:
            valstr = sheetrows[rowcounter][COLJSONID]  # PMD prop JSON id
        except IndexError:
            valstr = ' '
        propjsonid: str = valstr.strip()
        try:
            valstr = sheetrows[rowcounter][COLJSONDT]  # PMD prop DataType
        except IndexError:
            valstr = ' '
        propjsondt: str = valstr.strip()
        decodedpropdt: dict = decode_ipmd_datatype(propjsondt, rowcounter)
        """
        try:
            valstr = sheetrows[rowcounter][COLEXIFTAG]  # (mapped) Exif Tag
        except IndexError:
            valstr = ' '
        tempstr: str = valstr.strip()
        tempstrparts: list = tempstr.split('/')
        if len(tempstrparts) > 1:
            exifid: str = tempstrparts[1]
        else:
            exifid: str = ''
        try:
            valstr = sheetrows[rowcounter][COLSCHORG]  # (mapped) schema.org property identifier (URL)
        except IndexError:
            valstr = ' '
        schemaorgid: str = valstr.strip()
        """

        outprop: dict = {}
        outprop['name'] = propname
        # outprop['ipmdschema'] = ipmdschema
        outprop['sortorder'] = globalsortorder
        # outprop['ugtopic'] = proptopic
        # outprop['specidx'] = '#' + propname.lower().replace(' ', '-').replace('(', '').replace(')', '')
        if decodedpropdt is not None:
            outprop['datatype'] = decodedpropdt['core']
            if decodedpropdt['core'] == 'struct':
                outprop['dataformat'] = decodedpropdt['refstruct']
            else:
                if decodedpropdt['format'] != '':
                    outprop['dataformat'] = decodedpropdt['format']
            outprop['propoccurrence'] = decodedpropdt['occurrence']
        else:
            print('WARNING: data type of <' + propjsonid + '> cannot be decoded - check the Google sheet!')
            continue
        outprop['isrequired'] = '0'  # hardwired value for IPTC PMD TechReference
        """
        if propiimname != '':
            iimds: str = ''
            iimname: str = ''
            spaceidx: int = propiimname.find(' ')
            if spaceidx > -1:
                iimds = propiimname[:spaceidx]
                iimname = propiimname[spaceidx + 1:]
                outprop['IIMid'] = iimds
                outprop['IIMname'] = iimname
                if propiimmaxb != 0:
                    outprop['IIMmaxbytes'] = propiimmaxb
            else:
                outprop['IIMname'] = propiimname
        outprop['XMPid'] = propxmpns + ':' + propxmpid
        if exifid != '':
            outprop['EXIFid'] = exifid
        if schemaorgid != '':
            outprop['SCHEMAid'] = schemaorgid
        """
        etnameslist: list = etnamesstr.split(',')
        for etname in etnameslist:
            slashidx: int = etname.find('/')
            etnameadj: str = etname
            if slashidx > -1:
                etnameadj = etname[:slashidx]
            if etnameadj.find(':') > -1:  # ET tags with prefix
                if etnameadj[:4] == 'IPTC':
                    outprop['etIIM'] = etnameadj
                if etnameadj[:3] == 'XMP':
                    outprop['etXMP'] = etnameadj
            else:
                outprop['etTag'] = etnameadj
        """
        if etexiftag != '':
            outprop['etEXIF'] = etexiftag
        """
        outgroup[propjsonid] = outprop

    outbox[groupname] = outgroup
    # Write output file(s)
    write_outputfile(outbox, output_fp, outputformat)


def write_refdoc4ipmd_struct(sheetrows: list, from_row: int, to_row: int,
                             output_fn: str, groupname: str, outputformat: str = 'YAML',
                             withAltLang: bool = False):
    """Writes a reference document about the structures defined by IPTC PMD Standard

    :param sheetrows: a list of a set of data for each row
    :param from_row: lower limit of the range of rows
    :param to_row: upper limit of the range of rows
    :param output_fn: name of the output file
    :param groupname: name of the top level key in the YAML file
    :param outputformat: one out of 'JSON', 'YAML'
    :param withAltLang:
    :return: nothing
    """
    # set the output filepath, extension is NOT included yet!
    output_fp: str = ".\\output\\" + output_fn
    # create output dict
    outbox: dict = {}
    ts: str = datetime.now(timezone.utc).isoformat()
    outbox['release_timestamp'] = ts[:19] + '+00:00'
    outgroup: dict = {}

    # process the data from the sheet
    valstr: str = ''
    structbox: dict = {}
    structboxname: str = ''
    instruct: bool = False
    for rowcounter in range(from_row, to_row):  # iterate across a range of rows
        #if sheetrows[rowcounter][COLSIGNAL01] == "x":
        #    continue   # skip rows x-ed out
        try:
            valstr = sheetrows[rowcounter][COLETTNAMES]  # exiftool tag names
        except IndexError:
            valstr = ' '
        etnamesstr: str = valstr.strip()
        # get the ExifTool tag of an optional mapped Exif Tag
        #try:
        #    valstr = sheetrows[rowcounter][COLETEXIFTNAMES]  # ExifTool tag of a mapped Exif Tag
        #except IndexError:
        #    valstr = ' '
        #etexiftag: str = valstr.strip()

        if not instruct:
            structbox: dict = {}
            structboxname: str = ''

        # get more details of the PMD property
        try:
            valstr = sheetrows[rowcounter][COLGSORTORDER]  # Global sort order
        except IndexError:
            valstr = ' '
        globalsortorder: str = valstr.strip()
        #try:
        #    valstr = sheetrows[rowcounter][COLIPDMSCHEMA]  # IPTC PMD Schema
        #except IndexError:
        #    valstr = ' '
        #ipmdschema: str = valstr.strip()
        #if 'IptcExt' in ipmdschema:
        #    ipmdschema = 'IptcExt'
        #try:
        #    valstr = sheetrows[rowcounter][COLPMDUSERGUIDEREF]  # PMD user guide topic
        #except IndexError:
        #    valstr = ' '
        #proptopic: str = valstr.strip()
        try:
            valstr = sheetrows[rowcounter][COLVMHPROPNAME]  # PMD prop name
        except IndexError:
            valstr = ' '
        propname: str = valstr.strip()
        try:
            valstr = sheetrows[rowcounter][COLVMHPROPLABEL]  # PMD prop label
        except IndexError:
            valstr = ' '
        proplabel: str = valstr.strip()
        try:
            valstr = sheetrows[rowcounter][COLXMPTAG]  # VMHub prop XMP Tag
        except IndexError:
            valstr = ''
        if valstr:
            (propxmpns, propxmpid) = valstr.split(':')
        try:
            valstr = sheetrows[rowcounter][COLJSONID]  # PMD prop JSON id
        except IndexError:
            valstr = ' '
        propjsonid: str = valstr.strip()
        if propjsonid == 'any':  # 'any' is used for "any IPMD property may occur here"
            propjsonid = '$anypmdproperty'
        try:
            valstr = sheetrows[rowcounter][COLJSONDT]  # PMD prop DataType
        except IndexError:
            valstr = ' '
        propjsondt: str = valstr.strip()
        decodedpropdt: dict = decode_ipmd_datatype(propjsondt, rowcounter)
        """
        try:
            valstr = sheetrows[rowcounter][COLEXIFTAG]  # (mapped) Exif Tag
        except IndexError:
            valstr = ' '
        tempstr: str = valstr.strip()
        tempstrparts: list = tempstr.split('/')
        if len(tempstrparts) > 1:
            exifid: str = tempstrparts[1]
        else:
            exifid: str = ''
        try:
            valstr = sheetrows[rowcounter][COLSCHORG]  # (mapped) schema.org property identifier (URL)
        except IndexError:
            valstr = ' '
        schemaorgid: str = valstr.strip()
        """

        setinstructtrue: bool = False
        if propjsondt == 'object//':
            # there may be a filled structbox: write it to the group
            if any(structbox.values()):
                if structboxname != '':
                    outgroup[structboxname] = structbox
            structbox = {}
            structboxname = propjsonid
            instruct = False
            setinstructtrue = True
        if instruct:
            outprop: dict = {}
            outprop['name'] = propname
            #outprop['ipmdschema'] = ipmdschema
            outprop['sortorder'] = globalsortorder
            #outprop['specidx'] = '#' + propname.lower().replace(' ', '-').replace('(', '').replace(')', '')
            if decodedpropdt is not None:
                outprop['datatype'] = decodedpropdt['core']
                if decodedpropdt['core'] == 'struct':
                    outprop['dataformat'] = decodedpropdt['refstruct']
                else:
                    if decodedpropdt['format'] != '':
                        outprop['dataformat'] = decodedpropdt['format']
                outprop['propoccurrence'] = decodedpropdt['occurrence']
            else:
                print('ERROR: data type of <' + propjsonid + '> in struct <' + structboxname
                      + '> cannot be decoded - check the Google sheet!')
                continue
            outprop['isrequired'] = '0'  # hardwired value for IPTC PMD TechReference
            outprop['XMPid'] = propxmpns + ':' + propxmpid
            if propjsonid == '$anypmdproperty':
                outprop['XMPid'] = ''
            if exifid != '':
                outprop['EXIFid'] = exifid
            if schemaorgid != '':
                outprop['SCHEMAid'] = schemaorgid
            etnameslist: list = etnamesstr.split(',')
            for etname in etnameslist:
                slashidx: int = etname.find('/')
                etnameadj: str = etname
                if slashidx > -1:
                    etnameadj = etname[:slashidx]
                if etnameadj.find(':') > -1:  # ET tags with prefix
                    if etnameadj[:4] == 'IPTC':
                        outprop['etIIM'] = etnameadj
                    if etnameadj[:3] == 'XMP':
                        outprop['etXMP'] = etnameadj
                else:
                    outprop['etTag'] = etnameadj
                    if propjsonid == '$anypmdproperty':
                        outprop['etTag'] = ''
            if etexiftag != '':
                outprop['etEXIF'] = etexiftag
            structbox[propjsonid] = outprop
        if setinstructtrue:
            instruct = True
    if withAltLang:
        outgroup[structboxname] = structbox
        structbox = {}
        structbox['Note'] = 'A special structure covering variants of a text in different languages.'
        structbox['BCP47langid_1'] = 'Text in the human language corresponding to the BCP 47 language id'
        structbox['BCP47langid_toMany'] = 'Text in the human language corresponding to the BCP 47 language id'
        outgroup['AltLang'] = structbox
    outbox[groupname] = outgroup
    # Write output file(s)
    write_outputfile(outbox, output_fp, outputformat)


def build_techreference():
    """Retrieves data from the IPTC PMD Working Document Google sheet,
    transforms them and writes them to the iptc-pmd-techreference.... output file

    :return: nothing
    """
    print('***** Building the iptc-pmd-techreference document STARTED')
    """
    Michael's old code
    # using a Google Developer Key
    developerkey: str = read_googledeveloperkey()
    if developerkey == '':
        print('Google Developer Key is not available - processing aborted')
        return
    service = build('sheets', 'v4', developerKey=developerkey)
    sheet = service.spreadsheets()  # call Sheets API

    # access a Google sheet document IPTC Photo Metadata Working Document
    spreadsheet_id: str = SPREADSHEET_ID
    # ... and inside of it a specific sheet and a range of cells
    rangeinsheet: str = SPREADSHEET_SHEET_RANGE
    result1: dict = sheet.values().get(
        spreadsheetId=spreadsheet_id, range=rangeinsheet).execute()
    END michael's old code
    """
    credentials = get_credentials()
    service = build('sheets', 'v4', credentials=credentials)

    result1 = service.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID, range=SPREADSHEET_SHEET_RANGE).execute()

    rows: list = result1.get('values', [])


    # IPTC Video Metadata Hub data
    out_fn = 'vmhub_props'
    print(f'** Create file {out_fn}')
    write_refdoc4ipmd_top(rows, VMHUB_PROPS_START, VMHUB_PROPS_END, out_fn, 'vmhub_props', 'YAML')

    out_fn = 'vmhub_structs'
    print(f'** Create file {out_fn}')
    write_refdoc4ipmd_struct(rows, VMHUB_STRUCTS_START, VMHUB_STRUCTS_END, out_fn, 'vmhub_structs', 'YAML')  # 65, 158

    """
    out_fn = 'vmhub_struct2'
    print(f'** Create file {out_fn}')
    write_refdoc4ipmd_struct(rows, 166, 190, out_fn, 'ipmd_struct', 'YAML', withAltLang=True)
    """

    # ExifTool data
    ETDETAILSMODE = 'min'  # Enum: 'full', 'mid', 'min'
    out_fn = 'et_topwithprefix'
    print(f'** Create file {out_fn}')
    write_refdoc4et(rows, 0, 63, out_fn, 'et_topwithprefix', ETDETAILSMODE)

    out_fn = 'et_topnoprefix'
    print(f'** Create file {out_fn}')
    write_refdoc4et(rows, 0, 63, out_fn, 'et_topnoprefix', ETDETAILSMODE)

    out_fn = 'et_instructure1'
    print(f'** Create file {out_fn}')
    write_refdoc4et(rows, 67, 161, out_fn, 'et_instructure', ETDETAILSMODE)

    out_fn = 'et_instructure2'
    print(f'** Create file {out_fn}')
    write_refdoc4et(rows, 166, 190, out_fn, 'et_instructure', ETDETAILSMODE)

    # collate the YAML parts to a single file
    alllines: list = []
    basicoutput_dir: str = ".\\output\\"
    templates_dir: str = ".\\templates\\"
    # header with introduction
    getlines_fp = templates_dir + 'iptc-pmd-techreference_head-template1.yml'
    somelines = get_lines_fromtextfile(getlines_fp, 1, 999)
    alllines += somelines
    # the YAML files
    getlines_fp = basicoutput_dir + 'ipmd_top.yml'
    somelines = get_lines_fromtextfile(getlines_fp, 1, 999)
    alllines += somelines
    getlines_fp = basicoutput_dir + 'ipmd_struct1.yml'
    somelines = get_lines_fromtextfile(getlines_fp, 2, 999)
    alllines += somelines
    getlines_fp = basicoutput_dir + 'ipmd_struct2.yml'
    somelines = get_lines_fromtextfile(getlines_fp, 3, 999)
    alllines += somelines
    getlines_fp = basicoutput_dir + 'et_topwithprefix.yml'
    somelines = get_lines_fromtextfile(getlines_fp, 2, 999)
    alllines += somelines
    getlines_fp = templates_dir + 'et_topwithprefix_fixedvalues.yml'
    somelines = get_lines_fromtextfile(getlines_fp, 1, 999)
    alllines += somelines
    getlines_fp = basicoutput_dir + 'et_topnoprefix.yml'
    somelines = get_lines_fromtextfile(getlines_fp, 2, 999)
    alllines += somelines
    getlines_fp = basicoutput_dir + 'et_instructure1.yml'
    somelines = get_lines_fromtextfile(getlines_fp, 2, 999)
    alllines += somelines
    getlines_fp = basicoutput_dir + 'et_instructure2.yml'
    somelines = get_lines_fromtextfile(getlines_fp, 3, 999)
    alllines += somelines
    # write the final reference file
    yaml_output_fp: str = basicoutput_dir + TECHREF_FN + '.yml'
    with open(yaml_output_fp, 'w', encoding='utf-8') as outf:
        outf.writelines(alllines)
    json_output_fp: str = basicoutput_dir + TECHREF_FN + '.json'
    with open(yaml_output_fp, 'r', encoding='utf-8') as yamlf:
        techref_yaml: dict = yaml.load(yamlf, Loader=yaml.FullLoader)
        with open(json_output_fp, 'w', encoding='utf-8') as jsonf:
            json.dump(techref_yaml, jsonf, indent=4)


    print('***** Building the iptc-pmd-techreference document ENDED')

if __name__ == '__main__':
    build_techreference()
