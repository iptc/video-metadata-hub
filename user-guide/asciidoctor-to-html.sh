#!/bin/sh
echo "Converting file... IPTC-VideoMetadata-UserGuide.adoc"
asciidoctor -b html5 -o index.html IPTC-VideoMetadata-UserGuide.adoc
echo "Done."
