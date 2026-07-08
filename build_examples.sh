#!/bin/bash
# Build VMHub Example Media Files
#
# Generates one example media file per use case defined in
# example_use_cases.json, embedding metadata from the Google Sheet using
# ExifTool. The source media for each use case is configured in
# example_use_cases.json (source_file field).
#
# Usage: ./build_examples.sh [version]
#   version: Optional VMHub version (e.g., 1.7). Uses default if not specified.
#
# Requires:
#   - exiftool on PATH
#   - source media files present in examples/ (named by source_file in config)
#   - Google Sheets credentials in tools/

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

if [ -f "$SCRIPT_DIR/venv/bin/activate" ]; then
    source "$SCRIPT_DIR/venv/bin/activate"
fi

cd "$SCRIPT_DIR/tools"

VERSION=$1

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "========================================="
echo "VMHub Example Media Generator"
echo "========================================="
echo ""

# Check prerequisites
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}✗ Python 3 is required but not found${NC}"
    exit 1
fi

if ! command -v exiftool &> /dev/null; then
    echo -e "${RED}✗ ExifTool is required but not found on PATH${NC}"
    echo "  Install from: https://exiftool.org/"
    exit 1
fi
echo -e "${GREEN}✓ ExifTool found${NC}"

if [ ! -f "lib/use_cases.py" ]; then
    echo -e "${RED}✗ Cannot find tools/lib/use_cases.py${NC}"
    exit 1
fi

if [ -z "$VERSION" ]; then
    VERSION_ARG=""
    echo "Using default version from configuration"
else
    VERSION_ARG="--version $VERSION"
    echo "Using version: $VERSION"
fi
echo ""

# Enumerate use case names from example_use_cases.json
USE_CASES=$(python3 -c "from lib.use_cases import list_use_case_names; print(' '.join(list_use_case_names()))")
if [ -z "$USE_CASES" ]; then
    echo -e "${RED}✗ No use cases found in example_use_cases.json${NC}"
    exit 1
fi

echo "Use cases to generate:"
for uc in $USE_CASES; do
    echo "  - $uc"
done
echo ""

FAILED=()
for uc in $USE_CASES; do
    echo -e "${YELLOW}---- $uc ----${NC}"
    if python3 generate_example_videos.py $VERSION_ARG --use-case "$uc"; then
        echo -e "${GREEN}✓ $uc generated${NC}"
    else
        echo -e "${RED}✗ $uc failed${NC}"
        FAILED+=("$uc")
    fi
    echo ""
done

if [ ${#FAILED[@]} -ne 0 ]; then
    echo "========================================="
    echo -e "${RED}✗ Failed use cases: ${FAILED[*]}${NC}"
    echo "========================================="
    exit 1
fi

echo "========================================="
echo -e "${GREEN}✓ All example media files generated successfully!${NC}"
echo "========================================="
