'use strict';

class VMHubGenerator extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            output: '',
            outputformat: 'json',
            qcodeuri: 'qcodes',
            qcodeVisible: false,
            genre: '',
            medtop: [],
            language: 'en',
            title: '',
            description: '',
            keywords: '',
            supplier: '',
            identifier: '',
            creator: '',
            copyrightowner: '',
            copyrightnotice: '',
            creditline: '',
            usageterms: '',
            slugline: '',
            locationcreated: '',
            locationshown: '',
            altid_name: '',
            altid_value: '',
            ednote: '',
            digitalsourcetytpe: '',
            datamining: ''
        };
        this.handleInputChange = this.handleInputChange.bind(this);
        this.handleSubmit = this.handleSubmit.bind(this);
    }
    componentDidMount() {
        $('[data-toggle="tooltip"]').tooltip();
        this.refreshOutput();
    }
    componentDidUpdate() {
        $('[ata-toggle="tooltip"]').tooltip();
    }
    refreshOutput() {    
        var output;
        if (this.state.outputformat == 'json') {
            this.state.qcodeVisible = false;
            output = this.getVMHubJSONOutput();
        } else if (this.state.outputformat == 'exiftoolxmp') {
            this.state.qcodeVisible = false;
            output = this.getVMHubExiftoolOutput();
        } else if (this.state.outputformat == 'c2patool') {
            this.state.qcodeVisible = false;
            output = this.getVMHubc2patoolOutput();
        } else if (this.state.outputformat == 'newsmlg2') {
            this.state.qcodeVisible = true;
            output = this.getVMHubNewsMLG2Output();
        }
        this.setState({output: output});
    }
    getVMHubJSONOutput() {
        var jsonObj = {};
        var lang = this.state.language;

        if (lang) {
            jsonObj['language'] = lang;
        }
        if (this.state.dateCreated) {
            jsonObj['dateCreated'] = this.state.dateCreated;
        }
        if (this.state.dateReleased) {
            jsonObj['dateReleased'] = this.state.dateReleased;
        }
        if (this.state.title) {
            jsonObj['title'] = {};
            jsonObj['title'][lang] = this.state.title;
        }
        if (this.state.description) {
            jsonObj['description'] = {};
            jsonObj['description'][lang] = this.state.description;
        }
        if (this.state.keywords) {
            var keywords = this.state.keywords.split(',');
            jsonObj['keywords'] = keywords;
        }
        if (this.state.supplier) {
            jsonObj['supplier'] = {}
            jsonObj['supplier'][lang] = this.state.supplier;
        }
        if (this.state.genre) {
            var genreitems = [];
            genreitems.push({
                'cvId': 'http://cv.iptc.org/newscodes/genre/',
                'cvTermId': this.state.genre
            });
            jsonObj['genres'] = genreitems;
        }
        if (this.state.medtop.length > 0) {
            var mediatopics = [];
            for (var elem of this.state.medtop) {
                mediatopics.push({
                    'cvId': 'http://cv.iptc.org/newscodes/mediatopic/',
                    'cvTermId': elem[0],
                    'cvTermName': elem[1]
                });
            }
            jsonObj['aboutCvTerms'] = mediatopics;
        }
        if (this.state.copyrightowner) {
            jsonObj['copyrightOwners'] = [];
            var copyrightownerName = {};
            copyrightownerName[lang] = this.state.copyrightowner;
            var copyrightowner = { 'name': copyrightownerName };
            jsonObj['copyrightOwners'].push(copyrightowner);
        }
        if (this.state.copyrightnotice) {
            jsonObj['copyrightnotice'] = {};
            jsonObj['copyrightnotice'][lang] = this.state.copyrightnotice;
        }
        if (this.state.locationcreated) {
            jsonObj['locationsCreated'] = [];
            var locationCreatedName = {};
            locationCreatedName[lang] = this.state.locationcreated;
            var locationCreated = { 'name': locationCreatedName };
            jsonObj['locationsCreated'].push(locationCreated);
        }
        if (this.state.locationshown) {
            jsonObj['locationsShown'] = [];
            var locationShownName = {};
            locationShownName[lang] = this.state.locationshown;
            var locationShown = { 'name': locationShownName };
            jsonObj['locationsShown'].push(locationShown);
        }
        if (this.state.digitalsourcetype) {
            jsonObj['digitalsourcetype'] =
                'http://cv.iptc.org/newscodes/digitalsourcetype/' +
                this.state.digitalsourcetype;
        }
        if (this.state.datamining) {
            jsonObj['datamining'] =
                'http://ns.useplus.org/ldf/vocab/' +
                this.state.datamining;
        }
 
        return JSON.stringify(jsonObj, null, '\t');
    }

    getVMHubExiftoolOutput() {
        var exiftoolObj = {};
        var lang = this.state.language;

        if (lang) {
            exiftoolObj['XMP-dc:Language'] = lang;
        }
        if (this.state.dateCreated) {
            exiftoolObj['XMP-photoshop:DateCreated'] = this.state.dateCreated;
        }
        if (this.state.dateReleased) {
            exiftoolObj['XMP-xmpDM:ReleaseDate'] = this.state.dateReleased;
        }
        if (this.state.title) {
            exiftoolObj['XMP-dc:Title'] = this.state.title;
        }
        if (this.state.description) {
            exiftoolObj['XMP-dc:Description'] = this.state.description;
        }
        if (this.state.keywords) {
            var keywords = this.state.keywords.split(',');
            exiftoolObj['XMP-dc:Subject'] = keywords;
        }
        if (this.state.supplier) {
            exiftoolObj['XMP-plus:ImageSupplier'] = []
            var supplieritems = [];
            supplieritems.push({
                'ImageSupplierName': this.state.supplier
            });
            exiftoolObj['XMP-plus:ImageSupplier'] = supplieritems;
        }
        if (this.state.genre) {
            var genreitems = [];
            genreitems.push({
                'cvId': 'http://cv.iptc.org/newscodes/genre/',
                'cvTermId': this.state.genre
            });
            exiftoolObj['XMP-iptcExt:Genre'] = genreitems;
        }
        if (this.state.medtop.length > 0) {
            var mediatopics = [];
            for (var elem of this.state.medtop) {
                mediatopics.push({
                    'cvId': 'http://cv.iptc.org/newscodes/mediatopic/',
                    'cvTermId': elem[0],
                    'cvTermName': elem[1]
                });
            }
            exiftoolObj['XMP-iptcExt:AboutCvTerm'] = mediatopics;
        }
        if (this.state.copyrightowner) {
            var copyrightOwners = [];
            copyrightOwners.push({
                "CopyrightOwnerName": this.state.copyrightowner
            });
            exiftoolObj['XMP-plus:CopyrightOwner'] = copyrightOwners;
        }
        if (this.state.copyrightnotice) {
            exiftoolObj['XMP-dc:Rights'] = this.state.copyrightnotice;
        }
        if (this.state.locationcreated) {
            exiftoolObj['XMP-iptcExt:LocationCreated'] = [];
            var locationCreated = {
                'LocationName': this.state.locationcreated
            };
            exiftoolObj['XMP-iptcExt:LocationCreated'].push(locationCreated);
        }
        if (this.state.locationshown) {
            exiftoolObj['XMP-iptcExt:LocationShown'] = [];
            var locationShown = {
                'LocationName': this.state.locationshown
            };
            exiftoolObj['XMP-iptcExt:LocationShown'].push(locationShown);
        }
        if (this.state.digitalsourcetype) {
            exiftoolObj['XMP-iptcExt:DigitalSourceType'] =
                'http://cv.iptc.org/newscodes/digitalsourcetype/' +
                this.state.digitalsourcetype;
        }
        if (this.state.datamining) {
            exiftoolObj['XMP-plus:DataMining'] =
                'http://ns.useplus.org/ldf/vocab/' +
                this.state.datamining;
        }
        return JSON.stringify(exiftoolObj, null, '\t');
    }

    getVMHubc2patoolOutput() {
        var c2patoolObj = {
            "@context" : {
              "Iptc4xmpCore": "http://iptc.org/std/Iptc4xmpCore/1.0/xmlns/",
              "Iptc4xmpExt": "http://iptc.org/std/Iptc4xmpExt/2008-02-29/",
              "dc" : "http://purl.org/dc/elements/1.1/",
              "photoshop" : "http://ns.adobe.com/photoshop/1.0/",
              "plus" : "http://ns.useplus.org/ldf/xmp/1.0/",
              "xmp" : "http://ns.adobe.com/xap/1.0/",
              "xmpDM" : "http://ns.adobe.com/xmp/1.0/DynamicMedia/",
              "xmpRights" : "http://ns.adobe.com/xap/1.0/rights/"
            }
        };
        var lang = this.state.language;

        if (lang) {
            c2patoolObj['dc:language'] = lang;
        }
        if (this.state.dateCreated) {
            c2patoolObj['photoshop:DateCreated'] = this.state.dateCreated;
        }
        if (this.state.dateReleased) {
            c2patoolObj['xmpDM:releaseDate'] = this.state.dateReleased;
        }
        if (this.state.title) {
            c2patoolObj['dc:title'] = this.state.title;
        }
        if (this.state.description) {
            c2patoolObj['dc:description'] = this.state.description;
        }
        if (this.state.keywords) {
            var keywords = this.state.keywords.split(',');
            c2patoolObj['dc:subject'] = keywords;
        }
        if (this.state.supplier) {
            c2patoolObj['plus:ImageSupplier'] = []
            var supplieritems = [];
            supplieritems.push({
                'plus:ImageSupplierName': this.state.supplier
            });
            c2patoolObj['plus:ImageSupplier'] = supplieritems;
        }
        if (this.state.genre) {
            var genreitems = [];
            genreitems.push({
                'Iptc4xmpExt:CvId': 'http://cv.iptc.org/newscodes/genre/',
                'Iptc4xmpExt:CvTermId': this.state.genre
            });
            c2patoolObj['Iptc4xmpExt:Genre'] = genreitems;
        }
        if (this.state.medtop.length > 0) {
            var mediatopics = [];
            for (var elem of this.state.medtop) {
                mediatopics.push({
                    'Iptc4xmpExt:CvId': 'http://cv.iptc.org/newscodes/mediatopic/',
                    'Iptc4xmpExt:CvTermId': elem[0],
                    'Iptc4xmpExt:CvTermName': elem[1]
                });
            }
            c2patoolObj['Iptc4xmpExt:AboutCvTerm'] = mediatopics;
        }
        if (this.state.copyrightowner) {
            var copyrightOwners = [];
            copyrightOwners.push({
                "plus:CopyrightOwnerName": this.state.copyrightowner
            });
            c2patoolObj['plus:CopyrightOwner'] = copyrightOwners;
        }
        if (this.state.copyrightnotice) {
            c2patoolObj['dc:rights'] = this.state.copyrightnotice;
        }
        if (this.state.locationcreated) {
            c2patoolObj['Iptc4xmpExt:LocationCreated'] = [];
            var locationCreated = {
                'Iptc4xmpExt:LocationName': this.state.locationcreated
            };
            c2patoolObj['Iptc4xmpExt:LocationCreated'].push(locationCreated);
        }
        if (this.state.locationshown) {
            c2patoolObj['Iptc4xmpExt:LocationShown'] = [];
            var locationShown = {
                'Iptc4xmpExt:LocationName': this.state.locationshown
            };
            c2patoolObj['Iptc4xmpExt:LocationShown'].push(locationShown);
        }
        if (this.state.digitalsourcetype) {
            c2patoolObj['Iptc4xmpExt:DigitalSourceType'] = 
                'http://cv.iptc.org/newscodes/digitalsourcetype/' +
                this.state.digitalsourcetype;
        }
        if (this.state.datamining) {
            c2patoolObj['plus:DataMining'] = 
                'http://ns.useplus.org/ldf/vocab/' +
                this.state.datamining;
        }

        var data = c2patoolObj;
        var assertionObj = {
            "alg": "es256",
            "private_key": "es256_private.key",
            "sign_cert": "es256_certs.pem",
            "ta_url": "http://timestamp.digicert.com",
            "claim_generator": "IPTC Video Metadata Hub Generator with c2patool",
            "title": "Video signed with c2patool",
            "assertions": [
              {
                "label": "stds.iptc",
                data
              }
            ]
        }
        return JSON.stringify(assertionObj, null, '\t');
     }

     getVMHubNewsMLG2Output() {
        var lang = this.state.language;
        var xmlDoc = document.implementation.createDocument(
            'http://iptc.org/std/nar/2006-10-01/', 'newsItem', null
        );
        var newsItem = xmlDoc.documentElement;
        var todaysDate = new Date().toISOString().slice(0, 10);
        var slugline = this.state.slugline;
        var slugforguid;
        if (slugline) {
            slugforguid = slugline.toUpperCase();
        } else {
            slugforguid = "SLUGLINE";
        }
        slugforguid = this.state.identifier || "IDENTIFIER";
        newsItem.setAttribute('guid', 'urn:newsml:testnewsprovider.com:'+todaysDate+':'+slugforguid);
        newsItem.setAttribute('version', '1');
        newsItem.setAttribute('standard', 'NewsML-G2');
        newsItem.setAttribute('standardversion', '2.29');
        newsItem.setAttribute('conformance', 'power');

        /* catalogRef - only needed in qcode mode from NewsML-G2 2.30 */
        var catalogRef = document.createElementNS('http://iptc.org/std/nar/2006-10-01/', 'catalogRef');
        catalogRef.setAttribute('href', 'http://www.iptc.org/std/catalog/catalog.IPTC-G2-Standards_36.xml');
        xmlDoc.documentElement.appendChild(catalogRef);

        /* rightsInfo */
        if (this.state.copyrightowner != '') {
            var rightsInfoElem = document.createElementNS('http://iptc.org/std/nar/2006-10-01/', 'rightsInfo');
            if (this.state.copyrightowner) {
                /* rightsInfo/CopyrightHolder/@uri (for the VMD Id) + /name (for the VMD name) */
                var copyrightHolderElem = document.createElementNS('http://iptc.org/std/nar/2006-10-01/', 'copyrightHolder');
                var copyrightHolderNameElem = document.createElementNS('http://iptc.org/std/nar/2006-10-01/', 'name');
                copyrightHolderNameElem.innerHTML = this.state.copyrightowner;
                copyrightHolderElem.appendChild(copyrightHolderNameElem);
                rightsInfoElem.appendChild(copyrightHolderElem);
            }
            if (this.state.copyrightnotice) {
                /* 	VMD <--> NMLG2: rightsInfo/copyrightNotice */
                var copyrightNoticeElem = document.createElementNS('http://iptc.org/std/nar/2006-10-01/', 'copyrightNotice');
                copyrightNoticeElem.innerHTML = this.state.copyrightnotice;
                rightsInfoElem.appendChild(copyrightNoticeElem);
            }
            xmlDoc.documentElement.appendChild(rightsInfoElem);
        }

        /* itemMeta */
        var itemMetaElem = document.createElementNS('http://iptc.org/std/nar/2006-10-01/', 'itemMeta');
        /* itemMeta/itemClass is required for NewsML-G2 - use hard-coded ninat:video for VMHub */
        var itemClassElem = document.createElementNS('http://iptc.org/std/nar/2006-10-01/', 'itemClass');
        if (this.state.qcodeuri == 'qcodes') {
            itemClassElem.setAttribute('qcode', 'ninat:video');
        } else {
            itemClassElem.setAttribute('uri', 'http://cv.iptc.org/newscodes/ninature/video');
        }
        itemMetaElem.appendChild(itemClassElem);
        /* itemMeta/provider is required for NewsML-G2 - use default or contents of supplier field */
        var providerElem = document.createElementNS('http://iptc.org/std/nar/2006-10-01/', 'provider');
        var providerNameElem = document.createElementNS('http://iptc.org/std/nar/2006-10-01/', 'name');
        providerNameElem.innerHTML = this.state.supplier || "supplier";
        providerElem.appendChild(providerNameElem);
        itemMetaElem.appendChild(providerElem);
        var dateISOString = new Date().toISOString();
        var versionCreatedElem = document.createElementNS('http://iptc.org/std/nar/2006-10-01/', 'versionCreated');
        versionCreatedElem.innerHTML = dateISOString;
        itemMetaElem.appendChild(versionCreatedElem);
        var firstCreatedElem = document.createElementNS('http://iptc.org/std/nar/2006-10-01/', 'firstCreated');
        firstCreatedElem.innerHTML = dateISOString;
        itemMetaElem.appendChild(firstCreatedElem);
        var generatorElem = document.createElementNS('http://iptc.org/std/nar/2006-10-01/', 'generator');
        generatorElem.innerHTML = 'IPTC Video Metadata Hub Generator v1.1';
        itemMetaElem.appendChild(generatorElem);
        if (this.state.ednote !== '') {
            var edNoteElem = document.createElementNS('http://iptc.org/std/nar/2006-10-01/', 'edNote');
            edNoteElem.innerHTML = this.state.ednote;
            itemMetaElem.appendChild(edNoteElem);
        }
        if (this.state.title) {
            var titleElem = document.createElementNS('http://iptc.org/std/nar/2006-10-01/', 'title');
            titleElem.innerHTML = this.state.title;
            itemMetaElem.appendChild(titleElem);
        }
        xmlDoc.documentElement.appendChild(itemMetaElem);

        /* contentMeta */
        if (this.state.dateCreated != '' || this.state.dateReleased != '' || this.state.language !== '' || this.state.genre !== '' || this.state.medtop.length != 0 || this.state.description != '' || this.state.creator != '' || this.state.creditline != '' || this.state.keywords != '' || this.state.identifier != '' || this.state.locationshown != '') {
            var contentMetaElem = document.createElementNS('http://iptc.org/std/nar/2006-10-01/', 'contentMeta');
            if (this.state.dateCreated) {
                var contentCreatedElem = document.createElementNS('http://iptc.org/std/nar/2006-10-01/', 'contentCreated');
                contentCreatedElem.innerHTML = this.state.dateCreated;
                contentMetaElem.appendChild(contentCreatedElem);
            }
            if (this.state.locationcreated) {
                /* VMD <--> NMLG2: contentMeta/located */
                var locatedElem = document.createElementNS('http://iptc.org/std/nar/2006-10-01/', 'located');
                var locatedNameElem = document.createElementNS('http://iptc.org/std/nar/2006-10-01/', 'name');
                locatedNameElem.innerHTML = this.state.locationcreated;
                locatedElem.appendChild(locatedNameElem);
                contentMetaElem.appendChild(locatedElem);
            }
            if (this.state.supplier) {
                /* contentMeta/infoSource[@role="isrol:contentSource"]/name */
                var infoSourceElem = document.createElementNS('http://iptc.org/std/nar/2006-10-01/', 'infoSource');
                if (this.state.qcodeuri == 'qcodes') {
                    infoSourceElem.setAttribute('role', 'cpprole:contentSource');
                } else {
                    infoSourceElem.setAttribute('roleuri', 'https://cv.iptc.org/newscodes/contentprodpartyrole/contentSource');
                }
                var infoSourceNameElem = document.createElementNS('http://iptc.org/std/nar/2006-10-01/', 'name');
                infoSourceNameElem.innerHTML = this.state.supplier;
                infoSourceElem.appendChild(infoSourceNameElem);
                contentMetaElem.appendChild(infoSourceElem);
            }
            if (this.state.creator) {
                /* VMD <--> NMLG2: contentMeta/creator[@role="..."] */
                var creatorElem = document.createElementNS('http://iptc.org/std/nar/2006-10-01/', 'creator');
                var creatorNameElem = document.createElementNS('http://iptc.org/std/nar/2006-10-01/', 'name');
                creatorElem.appendChild(creatorNameElem);
                creatorNameElem.innerHTML = this.state.creator;
                contentMetaElem.appendChild(creatorElem);
            }
            if (this.state.identifier) {
                /* VMD <--> NMLG2: contentMeta/altId[@role="altidrole:vmhVideoId"] */
                var altIdElem = document.createElementNS('http://iptc.org/std/nar/2006-10-01/', 'altId');
                /* this isn't actually a valid newscode... should we change it? */
                if (this.state.qcodeuri == 'qcodes') {
                    altIdElem.setAttribute('role', 'altidrole:vmhVideoId');
                } else {
                    altIdElem.setAttribute('roleuri', 'http://example.org/altidrole/vmhVideoId');
                }
                altIdElem.innerHTML = this.state.identifier;
                contentMetaElem.appendChild(altIdElem);
            }
            if (this.state.language) {
                var languageElem = document.createElementNS('http://iptc.org/std/nar/2006-10-01/', 'language');
                languageElem.setAttribute('tag', this.state.language);
                contentMetaElem.appendChild(languageElem);
            }
            if (this.state.genre) {
                var genreElem = document.createElementNS('http://iptc.org/std/nar/2006-10-01/', 'genre');
                if (this.state.qcodeuri == 'qcodes') {
                    genreElem.setAttribute('qcode', 'genre:'+this.state.genre);
                } else {
                    genreElem.setAttribute('uri', 'http://cv.iptc.org/genre/'+this.state.genre);
                }
                contentMetaElem.appendChild(genreElem);
            }
            if (this.state.medtop) {
                for (var elem of this.state.medtop) {
                    var subjectElem = document.createElementNS('http://iptc.org/std/nar/2006-10-01/', 'subject');
                    if (this.state.qcodeuri == 'qcodes') {
                        subjectElem.setAttribute('qcode', 'medtop:'+elem[0]);
                    } else {
                        subjectElem.setAttribute('uri', 'http://cv.iptc.org/medtop/'+elem[0]); }
                    var subjectNameElem = document.createElementNS('http://iptc.org/std/nar/2006-10-01/', 'name');
                    subjectNameElem.innerHTML = elem[1];
                    subjectElem.appendChild(subjectNameElem);
                    contentMetaElem.appendChild(subjectElem);
                }
            }
            if (this.state.locationshown) {
                /* VMD <--> NMLG2: contentMeta/subject[@type="cpnat:POI"] */
                var subjectElem = document.createElementNS('http://iptc.org/std/nar/2006-10-01/', 'subject');
                if (this.state.qcodeuri == 'qcodes') {
                    subjectElem.setAttribute('type', 'cpnat:poi');
                } else {
                    subjectElem.setAttribute('typeuri', 'https://cv.iptc.org/newscodes/cpnature/poi');
                }
                var subjectNameElem = document.createElementNS('http://iptc.org/std/nar/2006-10-01/', 'name');
                subjectNameElem.innerHTML = this.state.locationshown;
                subjectElem.appendChild(subjectNameElem);
                contentMetaElem.appendChild(subjectElem);
            }
            if (this.state.description) {
                var descriptionElem = document.createElementNS('http://iptc.org/std/nar/2006-10-01/', 'description');
                descriptionElem.innerHTML = this.state.description;
                contentMetaElem.appendChild(descriptionElem);
            }
            if (this.state.creditline) {
                var creditlineElem = document.createElementNS('http://iptc.org/std/nar/2006-10-01/', 'creditline');
                creditlineElem.innerHTML = this.state.creditline;
                contentMetaElem.appendChild(creditlineElem);
            }
            if (this.state.keywords) {
                for (const keyword of this.state.keywords.split(',')) {
                    var keywordElem = document.createElementNS('http://iptc.org/std/nar/2006-10-01/', 'keyword');
                    keywordElem.innerHTML = keyword;
                    contentMetaElem.appendChild(keywordElem);
                }
            }
            if (this.state.dateReleased) {
                var dateReleasedElem = document.createElementNS('http://iptc.org/std/nar/2006-10-01/', 'contentMetaExtProperty');
                dateReleasedElem.setAttribute('rel', 'entityprop:dateReleased');
                dateReleasedElem.setAttribute('value', this.state.dateReleased);
                contentMetaElem.appendChild(dateReleasedElem);
            }
            xmlDoc.documentElement.appendChild(contentMetaElem);
        }
/*
        if (lang) {
            jsonObj['language'] = lang;
        }
        if (this.state.dateCreated) {
            jsonObj['dateCreated'] = this.state.dateCreated;
        }
        if (this.state.dateReleased) {
            jsonObj['dateReleased'] = this.state.dateReleased;
        }
        if (this.state.title) {
            jsonObj['title'] = {};
            jsonObj['title'][lang] = this.state.title;
        }
        if (this.state.description) {
            jsonObj['description'] = {};
            jsonObj['description'][lang] = this.state.description;
        }
        if (this.state.keywords) {
            var keywords = this.state.keywords.split(',');
            jsonObj['keywords'] = keywords;
        }
        if (this.state.supplier) {
            jsonObj['supplier'] = {}
            jsonObj['supplier'][lang] = this.state.supplier;
        }
        if (this.state.genre) {
            var genreitems = [];
            genreitems.push({
                'cvId': 'http://cv.iptc.org/newscodes/genre/',
                'cvTermId': this.state.genre
            });
            jsonObj['genres'] = genreitems;
        }
        if (this.state.medtop.length > 0) {
            var mediatopics = [];
            for (var value of this.state.medtop) {
                mediatopics.push({
                    'cvId': 'http://cv.iptc.org/newscodes/mediatopic/',
                    'cvTermId': value
                });
            }
            jsonObj['aboutCvTerms'] = mediatopics;
        }
        if (this.state.copyrightowner) {
            jsonObj['copyrightOwners'] = [];
            var copyrightownerName = {};
            copyrightownerName[lang] = this.state.copyrightowner;
            var copyrightowner = { 'name': copyrightownerName };
            jsonObj['copyrightOwners'].push(copyrightowner);
        }
        if (this.state.copyrightnotice) {
            jsonObj['copyrightnotice'] = {};
            jsonObj['copyrightnotice'][lang] = this.state.copyrightnotice;
        }
        if (this.state.locationcreated) {
            jsonObj['locationsCreated'] = [];
            var locationCreatedName = {};
            locationCreatedName[lang] = this.state.locationcreated;
            var locationCreated = { 'name': locationCreatedName };
            jsonObj['locationsCreated'].push(locationCreated);
        }
        if (this.state.locationshown) {
            jsonObj['locationsShown'] = [];
            var locationShownName = {};
            locationShownName[lang] = this.state.locationshown;
            var locationShown = { 'name': locationShownName };
            jsonObj['locationsShown'].push(locationShown);
        }
*/ 
        /* turn XML object into string */
        var serializer = new XMLSerializer();
        var xmlString = serializer.serializeToString(xmlDoc);
        xmlString = this.xmlpretty(xmlString, 1);
        const xmlDecl = '<?xml version="1.0" encoding="UTF-8"?>'
        var xmlDocAsString =  xmlDecl + '\n' + xmlString.toString();
        return xmlDocAsString;
    }
    handleSubmit(event) {
        /* there's no submit button but just in case some automatic feature tries to submit the form... */
        event.preventDefault();
    }
    handleInputChange(event) {
        const target = event.target;
        const value = target.type === 'checkbox' ? target.checked
            : target.type === 'select-multiple' ? [...target.selectedOptions].map(o => [ o.value, o.text ])
            : target.value;
        const name = target.name;
        // if (name == 'newsmlg2') {
        //     $('#qcodeSelector').toggle('d-none');
        // }
        // setState is asynchronous so we update the output after completion using the callback
        this.setState({
            [name]: value
        }, this.refreshOutput);
    }
    copyToClipboard = (e) => {
        this.textArea.select();
        document.execCommand('copy');
        // This is just personal preference.
        // I prefer to not show the whole text area selected.
        e.target.focus();
        this.setState({ copySuccess: 'Copied!' });
        e.preventDefault();
    };
    // used by xmlpretty below
    createShiftArr(step) {
        var space = '    ';
        if ( isNaN(parseInt(step)) ) {  // argument is string
            space = step;
        } else { // argument is integer
            switch(step) {
                case 1: space = '  '; break;
                case 2: space = '    '; break;
                case 3: space = '      '; break;
                case 4: space = '        '; break;
                case 5: space = '          '; break;
                case 6: space = '            '; break;
                case 7: space = '              '; break;
                case 8: space = '                '; break;
                case 9: space = '                  '; break;
                case 10: space = '                    '; break;
                case 11: space = '                      '; break;
                case 12: space = '                        '; break;
            }
        }

        var shift = ['\n']; // array of shifts
        for(var ix=0;ix<100;ix++){
            shift.push(shift[ix]+space);
        }
        return shift;
    }
    xmlpretty(text,step) {
        var shift = this.createShiftArr(step);
        var ar = text.replace(/>\s{0,}</g,"><")
                     .replace(/</g,"~::~<")
                     .replace(/\s*xmlns\:/g,"~::~xmlns:")
                     .replace(/\s*xmlns\=/g,"~::~xmlns=")
                     .split('~::~'),
            len = ar.length,
            inComment = false,
            deep = 0,
            str = '',
            ix = 0,
            shift = step ? this.createShiftArr(step) : shift;

        for(ix=0;ix<len;ix++) {
            // start comment or <![CDATA[...]]> or <!DOCTYPE //
            if(ar[ix].search(/<!/) > -1) {
                str += shift[deep]+ar[ix];
                inComment = true;
                // end comment  or <![CDATA[...]]> //
                if(ar[ix].search(/-->/) > -1 || ar[ix].search(/\]>/) > -1 || ar[ix].search(/!DOCTYPE/) > -1 ) {
                    inComment = false;
                }
            } else
            // end comment  or <![CDATA[...]]> //
            if(ar[ix].search(/-->/) > -1 || ar[ix].search(/\]>/) > -1) {
                str += ar[ix];
                inComment = false;
            } else
            // <elm></elm> //
            if( /^<\w/.exec(ar[ix-1]) && /^<\/\w/.exec(ar[ix]) &&
                /^<[\w:\-\.\,]+/.exec(ar[ix-1]) == /^<\/[\w:\-\.\,]+/.exec(ar[ix])[0].replace('/','')) {
                str += ar[ix];
                if(!inComment) deep--;
            } else
             // <elm> //
            if(ar[ix].search(/<\w/) > -1 && ar[ix].search(/<\//) == -1 && ar[ix].search(/\/>/) == -1 ) {
                str = !inComment ? str += shift[deep++]+ar[ix] : str += ar[ix];
            } else
             // <elm>...</elm> //
            if(ar[ix].search(/<\w/) > -1 && ar[ix].search(/<\//) > -1) {
                str = !inComment ? str += shift[deep]+ar[ix] : str += ar[ix];
            } else
            // </elm> //
            if(ar[ix].search(/<\//) > -1) {
                str = !inComment ? str += shift[--deep]+ar[ix] : str += ar[ix];
            } else
            // <elm/> //
            if(ar[ix].search(/\/>/) > -1 ) {
                str = !inComment ? str += shift[deep]+ar[ix] : str += ar[ix];
            } else
            // <? xml ... ?> //
            if(ar[ix].search(/<\?/) > -1) {
                str += shift[deep]+ar[ix];
            } else
            // xmlns //
            if( ar[ix].search(/xmlns\:/) > -1  || ar[ix].search(/xmlns\=/) > -1) {
                str += shift[deep]+ar[ix];
            }

            else {
                str += ar[ix];
            }
        }

        return  (str[0] == '\n') ? str.slice(1) : str;
    }

    render() {
        var outputtext = "View the generated Video Metadata Hub data";
        return (
<form name="indata" method="post" onSubmit={this.handleSubmit}>
    <div className="row">
        <div className="col">
            <legend>Enter video metadata</legend>
            <div className="form-row">
                <div className="col form-group">
                    <label htmlFor="dateCreated">Date created</label>
                    <input className="form-control form-control-sm" type="date" id="dateCreated" name="dateCreated" size="10" title="Date Created" value={this.state.dateCreated} onChange={this.handleInputChange}  tabIndex="1" />
                </div>
                <div className="col form-group">
                    <label htmlFor="dateReleased">Date released</label>
                    <input className="form-control form-control-sm" type="date" id="dateReleased" name="dateReleased" size="10" title="Date Released" value={this.state.dateReleased} onChange={this.handleInputChange}  tabIndex="2" />
                </div>
                <div className="col form-group">
                    <label htmlFor="language">Language <i className="fas fa-info-circle" data-toggle="tooltip" data-placement="top" title='Language of both content and metadata items, for the sake of example' /></label>
                    <select className="form-control form-control-sm" id="language" name="language" size="1" width="3" value={this.state.language} onChange={this.handleInputChange} tabIndex="3">
                        <option value="af">Afrikaans</option>
                        <option value="sq">Albanian</option>
                        <option value="ar">Arabic</option>
                        <option value="hy">Armenian</option>
                        <option value="eu">Basque</option>
                        <option value="bn">Bengali</option>
                        <option value="bg">Bulgarian</option>
                        <option value="ca">Catalan</option>
                        <option value="km">Cambodian</option>
                        <option value="zh">Chinese (Mandarin)</option>
                        <option value="hr">Croatian</option>
                        <option value="cs">Czech</option>
                        <option value="da">Danish</option>
                        <option value="nl">Dutch</option>
                        <option value="en">English</option>
                        <option value="et">Estonian</option>
                        <option value="fj">Fijian</option>
                        <option value="fi">Finnish</option>
                        <option value="fr">French</option>
                        <option value="ka">Georgian</option>
                        <option value="de">German</option>
                        <option value="el">Greek</option>
                        <option value="gu">Gujarati</option>
                        <option value="he">Hebrew</option>
                        <option value="hi">Hindi</option>
                        <option value="hu">Hungarian</option>
                        <option value="is">Icelandic</option>
                        <option value="id">Indonesian</option>
                        <option value="ga">Irish</option>
                        <option value="it">Italian</option>
                        <option value="ja">Japanese</option>
                        <option value="jw">Javanese</option>
                        <option value="ko">Korean</option>
                        <option value="la">Latin</option>
                        <option value="lv">Latvian</option>
                        <option value="lt">Lithuanian</option>
                        <option value="mk">Macedonian</option>
                        <option value="ms">Malay</option>
                        <option value="ml">Malayalam</option>
                        <option value="mt">Maltese</option>
                        <option value="mi">Maori</option>
                        <option value="mr">Marathi</option>
                        <option value="mn">Mongolian</option>
                        <option value="ne">Nepali</option>
                        <option value="no">Norwegian</option>
                        <option value="fa">Persian</option>
                        <option value="pl">Polish</option>
                        <option value="pt">Portuguese</option>
                        <option value="pa">Punjabi</option>
                        <option value="qu">Quechua</option>
                        <option value="ro">Romanian</option>
                        <option value="ru">Russian</option>
                        <option value="sm">Samoan</option>
                        <option value="sr">Serbian</option>
                        <option value="sk">Slovak</option>
                        <option value="sl">Slovenian</option>
                        <option value="es">Spanish</option>
                        <option value="sw">Swahili</option>
                        <option value="sv">Swedish</option>
                        <option value="ta">Tamil</option>
                        <option value="tt">Tatar</option>
                        <option value="te">Telugu</option>
                        <option value="th">Thai</option>
                        <option value="bo">Tibetan</option>
                        <option value="to">Tonga</option>
                        <option value="tr">Turkish</option>
                        <option value="uk">Ukranian</option>
                        <option value="ur">Urdu</option>
                        <option value="uz">Uzbek</option>
                        <option value="vi">Vietnamese</option>
                        <option value="cy">Welsh</option>
                        <option value="xh">Xhosa</option>
                    </select>
                </div>
                <div className="col form-group">
                    <label htmlFor="genre">Genre <i className="fas fa-info-circle" data-toggle="tooltip" data-placement="top" title='Values are taken from https://cv.iptc.org/newscodes/genre' /></label>
                    <div className="col-sm-10">
                        <select className="form-control form-control-sm" id="genre" name="genre" size="1" width="3" value={this.state.genre} onChange={this.handleInputChange} tabIndex="4">
                            <option value=""> (None) </option>
                            <option value="Actuality"> Actuality </option>
                            <option value="Advice"> Advice </option>
                            <option value="Advisory"> Advisory </option>
                            <option value="Almanac"> Almanac </option>
                            <option value="Analysis"> Analysis </option>
                            <option value="Archive_material"> Archive material </option>
                            <option value="Background"> Background </option>
                            <option value="Biography"> Biography </option>
                            <option value="Birth_Announcement"> Birth Announcement </option>
                            <option value="Current"> Current </option>
                            <option value="Curtain_Raiser"> Curtain Raiser </option>
                            <option value="Daybook"> Daybook </option>
                            <option value="Exclusive"> Exclusive </option>
                            <option value="Feature"> Feature </option>
                            <option value="Fixture"> Fixture </option>
                            <option value="Forecast"> Forecast </option>
                            <option value="From_the_Scene"> From the Scene </option>
                            <option value="History"> History </option>
                            <option value="Horoscope"> Horoscope </option>
                            <option value="Interview"> Interview </option>
                            <option value="Listing_of_facts"> Listing of facts </option>
                            <option value="Music"> Music </option>
                            <option value="Obituary"> Obituary </option>
                            <option value="Opinion"> Opinion </option>
                            <option value="Polls_and_Surveys"> Polls and Surveys </option>
                            <option value="Press_Release"> Press Release </option>
                            <option value="Press-Digest"> Press-Digest </option>
                            <option value="Profile"> Profile </option>
                            <option value="Program"> Program </option>
                            <option value="Question_and_Answer_Session"> Question and Answer Session </option>
                            <option value="Quote"> Quote </option>
                            <option value="Raw_Sound"> Raw Sound </option>
                            <option value="Response_to_a_Question"> Response to a Question </option>
                            <option value="Results_Listings_and_Statistics"> Results Listings and Statistics </option>
                            <option value="Retrospective"> Retrospective </option>
                            <option value="Review"> Review </option>
                            <option value="Scener"> Scener </option>
                            <option value="Side_bar_and_supporting_information"> Side bar and supporting information </option>
                            <option value="Special_Report"> Special Report </option>
                            <option value="Summary"> Summary </option>
                            <option value="Synopsis"> Synopsis </option>
                            <option value="Text_only"> Text only </option>
                            <option value="Transcript_and_Verbatim"> Transcript and Verbatim </option>
                            <option value="Update"> Update </option>
                            <option value="Voicer"> Voicer </option>
                            <option value="Wrap"> Wrap </option>
                            <option value="Wrapup"> Wrapup </option>
                        </select>
                    </div>
                </div>
                </div>
                <div className="form-row">
                    <label className="col-sm-2 col-form-label" htmlFor="title">Title</label>
                    <div className="col-sm-10">
                        <input className="form-control form-control-sm" type="text" id="title" name="title" size="40" title="Title" value={this.state.title} onChange={this.handleInputChange}  tabIndex="5" />
                    </div>
                </div>
                <div className="form-row">
                    <label className="col-sm-2 col-form-label" htmlFor="description">Description</label>
                    <div className="col-sm-10">
                        <textarea className="form-control form-control-sm" id="description" name="description" rows="5" wrap="virtual" cols="60" value={this.state.description} onChange={this.handleInputChange} tabIndex="6"></textarea>
                    </div>
                </div>
                <div className="form-row">
                    <label className="col-sm-2 col-form-label" htmlFor="keywords">Keywords</label>
                    <div className="col-sm-10">
                        <input className="form-control form-control-sm" type="text" id="keywords" name="keywords" size="40" title="Keywords" value={this.state.keywords} onChange={this.handleInputChange} tabIndex="7" />
                    </div>
                </div>
                <div className="form-row">
                    <label className="col-sm-2 col-form-label" htmlFor="creator">Creator</label>
                    <div className="col-sm-10">
                        <input className="form-control form-control-sm" type="text" id="creator" name="creator" size="40" title="Creator" value={this.state.creator} onChange={this.handleInputChange} tabIndex="8" />
                    </div>
                </div>
                <div className="form-row">
                    <label className="col-sm-2 col-form-label" htmlFor="creditline">Credit Line</label>
                    <div className="col-sm-10">
                        <input className="form-control form-control-sm" type="text" id="creditline" name="creditline" size="40" title="Credit line" value={this.state.creditline} onChange={this.handleInputChange} tabIndex="9" />
                    </div>
                </div>
                <div className="form-row">
                    <label className="col-sm-2 col-form-label" htmlFor="supplier">Supplier</label>
                    <div className="col-sm-4">
                        <input className="form-control form-control-sm" type="text" id="supplier" name="supplier" size="25" title="Supplier of information" value={this.state.supplier} onChange={this.handleInputChange} tabIndex="10" />
                    </div>
                    <label className="col-sm-2 col-form-label" htmlFor="profile">Identifier</label>
                    <div className="col-sm-4">
                        <input className="form-control form-control-sm" type="text" id="identifier" name="identifier" size="25" title="Identifier" value={this.state.identifier} onChange={this.handleInputChange} tabIndex="11" />
                    </div>
                </div>
                <div className="form-row">
                    <label className="col-sm-3 col-form-label" htmlFor="copyrightowner">Copyright Owner</label>
                    <div className="col-sm-9">
                        <input className="form-control form-control-sm" type="text" id="copyrightowner" name="copyrightowner" size="25" title="Copyright owner for this item." value={this.state.copyrightowner} onChange={this.handleInputChange} tabIndex="12" />
                    </div>
                </div>
                <div className="form-row">
                    <label className="col-sm-3 col-form-label" htmlFor="copyrightnotice">Copyright Notice</label>
                    <div className="col-sm-9"> <input className="form-control form-control-sm" type="text" id="copyrightnotice" name="copyrightnotice" size="25" title="Copyright notice for this item." value={this.state.copyrightnotice} onChange={this.handleInputChange} tabIndex="13" />
                    </div>
                </div>
                <div className="form-row">
                    <label className="col-sm-3 col-form-label" htmlFor="digitalsourcetype">Data Mining</label>
                    <div className="col-sm-9">
                        <select className="form-control form-control-sm" id="datamining" name="datamining" size="1" value={this.state.datamining} onChange={this.handleInputChange} tabIndex="14">
                            <option value=""> (None) </option>
                            <option value="DMI-UNSPECIFIED">Unspecified - no prohibition defined</option>
                            <option value="DMI-ALLOWED">Allowed</option>
                            <option value="DMI-PROHIBITED-AIMLTRAINING">Prohibited for AI/ML training</option>
                            <option value="DMI-PROHIBITED-GENAIMLTRAINING">Prohibited for Generative AI/ML training</option>
                            <option value="DMI-PROHIBITED-EXCEPTSEARCHENGINEINDEXING">Prohibited except for search engine indexing</option>
                            <option value="DMI-PROHIBITED">Prohibited</option>
                            <option value="DMI-PROHIBITED-SEECONSTRAINT">Prohibited, see Other Constraints property</option>
                            <option value="DMI-PROHIBITED-SEEEMBEDDEDRIGHTSEXPR">Prohibited, see Embedded Encoded Rights Expression property</option>
                            <option value="DMI-PROHIBITED-SEELINKEDRIGHTSEXPR">Prohibited, see Linked Encoded Rights Expression property</option>
                        </select>
                    </div>
                </div>
                <div className="form-row">
                    <label className="col-sm-3 col-form-label" htmlFor="medtop">IPTC Media Topic(s)</label>
                    <div className="col-sm-9">
                        <select className="form-control form-control-sm" id="medtop" name="medtop" size="5" width="25" multiple={true} title="Select the applicable codes." value={this.state.medtop.map(s=>s[0])} onChange={this.handleInputChange} tabIndex="14">
                            <option value="01000000">Arts, culture, entertainment and media</option>
                            <option value="02000000">Crime, law and justice</option>
                            <option value="03000000">Disaster and accident</option>
                            <option value="04000000">Economy, business and finance</option>
                            <option value="05000000">Education</option>
                            <option value="06000000">Environmental issues</option>
                            <option value="07000000">Health</option>
                            <option value="08000000">Human interest</option>
                            <option value="09000000">Labour</option>
                            <option value="10000000">Lifestyle and leisure</option>
                            <option value="11000000">Politics</option>
                            <option value="12000000">Religion and belief</option>
                            <option value="13000000">Science and technology</option>
                            <option value="14000000">Social issues</option>
                            <option value="15000000">Sport</option>
                            <option value="16000000">Unrest, conflict and war</option>
                            <option value="17000000">Weather</option>
                        </select>
                    </div>
                </div>
                <div className="form-row">
                    <label className="col-sm-3 col-form-label" htmlFor="locationcreated">Location Shot</label>
                    <div className="col-sm-9">
                        <input className="form-control form-control-sm" type="text" id="locationcreated" name="locationcreated" size="40" title="Location Shot" value={this.state.locationcreated} onChange={this.handleInputChange} tabIndex="15"/>
                    </div>
                </div>
                <div className="form-row">
                    <label className="col-sm-3 col-form-label" htmlFor="locationshown">Location Shown</label>
                    <div className="col-sm-9">
                        <input className="form-control form-control-sm" type="text" id="locationshown" name="locationshown" size="40" title="Location Shown" value={this.state.locationshown} onChange={this.handleInputChange} tabIndex="16"/>
                    </div>
                </div>
                <div className="form-row">
                    <label className="col-sm-3 col-form-label" htmlFor="digitalsourcetype">Digital Source Type</label>
                    <div className="col-sm-9">
                        <select className="form-control form-control-sm" id="digitalsourcetype" name="digitalsourcetype" size="1" value={this.state.digitalsourcetype} onChange={this.handleInputChange} tabIndex="17">
                            <option value=""> (None) </option>
                            <option value="digitalCapture">Original digital capture sampled from real life</option>
                            <option value="negativeFilm">Digitised from a negative on film</option>
                            <option value="positiveFilm">Digitised from a positive on film</option>
                            <option value="print">Digitised from a print on non-transparent medium</option>
                            <option value="minorHumanEdits">Original media with minor human edits</option>
                            <option value="compositeCapture">Composite of captured elements</option>
                            <option value="algorithmicallyEnhanced">Algorithmically-enhanced media</option>
                            <option value="dataDrivenMedia">Data-driven media</option>
                            <option value="digitalArt">Digital art</option>
                            <option value="virtualRecording">Virtual recording</option>
                            <option value="compositeSynthetic">Composite including synthetic elements</option>
                            <option value="trainedAlgorithmicMedia">Trained algorithmic media</option>
                            <option value="algorithmicMedia">Pure algorithmic media</option>
                        </select>
                    </div>
                </div>
        </div>
        <div className="col">
            <div className="outputbox">
                <div className="form-row">
                    <legend>{outputtext}</legend>
                    <div className="col-sm-4">
                        Choose output format:
                    </div>
                    <div className="col-sm-5">
                        <select className="form-control" id="outputformat" name="outputformat" onChange={this.handleInputChange} tabIndex="18">
                            <option value="json">JSON</option>
                            <option value="exiftoolxmp">JSON XMP (for Exiftool)</option>
                            <option value="c2patool">C2PA assertion (for c2patool)</option>
                            <option value="newsmlg2">NewsML-G2</option>
                        </select>
                    </div>
                    <div className="col-sm-3">
                        <a href="#" className="form-control btn btn-light" onClick={this.copyToClipboard}>Copy to clipboard <i className="fas fa-copy" /></a>
                    </div>
                </div>
                <div className={this.state.qcodeVisible ? "form-row" : "form-row d-none"} id="qcodeSelector">
                    <div className="col-sm-6">
                        Choose controlled value display format:
                    </div>
                    <div className="col-sm-5">
                        <div className="form-check form-check-inline">
                            <input className="form-check-input" type="radio" defaultChecked name="qcodeuri" id="qcodes" value="qcodes" title="QCodes" onChange={this.handleInputChange} tabIndex="23" />&nbsp;
                            <label className="form-check-label" htmlFor="qcodes">QCodes</label>
                        </div>
                        <div className="form-check form-check-inline">
                            <input className="form-check-input" type="radio" name="qcodeuri" id="uris" value="uris" title="URIs" onChange={this.handleInputChange} tabIndex="24" />&nbsp;
                            <label className="form-check-label" htmlFor="uris">URIs</label>
                        </div>
                    </div>
                </div>
                <div className={this.state.outputformat == "exiftoolxmp" || this.state.outputformat == "c2patool" ? "form-row" : "form-row d-none"}>
                    <div className={this.state.outputformat == "exiftoolxmp" ? "col-sm-12" : "d-none"}>
                        Save this JSON block to a file and add it to your video using the exiftool command:<br/>
                        <code>exiftool -v -XMP:all= -j=&lt;JSON file&gt; &lt;videofile&gt;</code>
                    </div>
                    <div className={this.state.outputformat == "c2patool" ? "col-sm-12" : "d-none"}>
                        Save this JSON-LD block to a file and add it to your video using the &nbsp;
                        <a href="https://opensource.contentauthenticity.org/docs/c2patool">c2patool</a> command:<br/>
                        <code>c2patool &lt;input video file&gt; -m iptc-vmhub-assertion.json -o &lt;output video file&gt;</code>
                    </div>
                </div>
                <textarea className="form-control" name="output" style={{'height': '100%', 'fontSize': '12px'}} rows="40" tabIndex="25" value={this.state.output} ref={(textarea) => this.textArea = textarea} readOnly tabIndex="19"></textarea>
            </div>
        </div>
    </div>
</form>
        )
    }
}

const domContainer = document.querySelector('#reactcontainer');
ReactDOM.render(<VMHubGenerator/>, domContainer);
