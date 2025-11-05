#!/bin/bash
# Build All VMHub Artifacts
#
# Brendan Quinn, IPTC 2025 (created with the help of Cursor)
#
# Usage: ./build_all.sh [version]
#   version: Optional VMHub version (e.g., 1.7). Uses default if not specified.
#
# Generates both specification and user guide artifacts

set -e  # Exit on error

# Get version from argument or use default
VERSION=$1

# Color output
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "========================================="
echo "VMHub Complete Artifact Generator"
echo "========================================="
echo ""

if [ -z "$VERSION" ]; then
    echo "Generating artifacts for default version"
else
    echo "Generating artifacts for version: $VERSION"
fi
echo ""

# Build specification artifacts
echo -e "${BLUE}==== Building Specification Artifacts ====${NC}"
./build_spec.sh $VERSION
if [ $? -ne 0 ]; then
    echo -e "${RED}✗ Specification build failed${NC}"
    exit 1
fi
echo ""

# Build user guide artifacts
echo -e "${BLUE}==== Building User Guide Artifacts ====${NC}"
./build_userguide.sh $VERSION
if [ $? -ne 0 ]; then
    echo -e "${RED}✗ User guide build failed${NC}"
    exit 1
fi
echo ""

echo "========================================="
echo -e "${GREEN}✓ ALL ARTIFACTS GENERATED SUCCESSFULLY!${NC}"
echo "========================================="
echo ""
echo "Generated artifacts:"
echo "  - Specification: specification/"
echo "  - User Guide: video-metadata-guidelines/index.html"
echo ""


