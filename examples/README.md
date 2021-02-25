= Video Metadata Hub example files

This folder contains sample video files with IPTC Video Metadata Hub properties
embedded using various formats.

== Creating the XMP examples using exiftool

* The JSON file `IPTC-VMHub0102-All4exiftool.json` contains
all metadata properties of the Video Metadata Hub 1.2 using the ExifTool names.
Note that these names don't all match the VM Hub names - see the
[exiftool mappings reference](https://iptc.org/std/videometadatahub/recommendation/IPTC-VideoMetadataHub-mapping-exiftool-Rec_1.3.html) for the exact names used.

* This is the command line for embedding it into the video file example1.mp4:

    exiftool -v --XMP:all= -j=IPTC-VMHub0102-All4exiftool.json example1.mp4

* The command line arguments:

 -v             makes the output less verbose (actually it is the same as -v0)
 --XMP:all=     deletes all currently existing XMP metadata of the video file
 -j=...         names the JSON file with the metadata last term: the file name
                of the video file

== How to check the embedded metadata – as XMP document

    exiftool -xmp -b example1.mp4 > example1.xmp.xml

example1.xmp.xml holds the extracted XMP packet.

== How to check the embedded metadata – as ExifTool JSON document

    exiftool -j -G1 -struct example1.mp4 -w -out.json

To explain the command line arguments:

 -j             set JSON as output format
 -G1            sets the type of naming, see below
 -struct        defines that the output should not be a flat list of properties
                but structured properties should be structured in the output
 ... video file name ...
 -w             write output to a file with the file name ...
  -out.json     use the original base file name and append -out.json to it.
 
== A note on the ExifTool types of property names

In exiftool, property names can be grouped. The argument -G sets how the groups
are used:

 -G (same as -G0)   the data format and the property name without a namespace are used.
                    The Creator property in XMP is named XMP:Creator

 -G1                the data format and the property name with its namespace are
                    used. The Creator property in XMP is named
                    `XMP-iptcExt:Creator`
 
We prefer to use G1 as it avoids the overlapping of the same property name in
different namespaces. If G1 isn't set and an overlapping name is found, Exiftool
creates an alternative name which is not the original one anymore, which can be
confusing.  – see the `IPTC-VMHub0102-All4exiftool.json`
file.

The resulting file, created using the `-G1` option, is saved in this folder as
`IPTC-VMHub-TestVideo-rec0102-exiftool.json`.
 
General note: all subproperties inside a structure don’t have data format and
namespace, this is inherited from the main property.
