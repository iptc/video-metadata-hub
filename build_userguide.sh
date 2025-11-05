#!/bin/bash
# Build VMHub User Guide Artifacts
#
# Brendan Quinn, IPTC 2025 (created with the help of Cursor)
#
# Usage: ./build_userguide.sh [version]
#   version: Optional VMHub version (e.g., 1.7). Uses default if not specified.
#
# Run from repository root

set -e  # Exit on error

# Get the directory where this script is located (should be repo root)
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Activate virtual environment if it exists
if [ -f "$SCRIPT_DIR/venv/bin/activate" ]; then
    source "$SCRIPT_DIR/venv/bin/activate"
fi

# Change to the tools directory
cd "$SCRIPT_DIR/tools"

# Get version from argument or use default
VERSION=$1

# Color output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "========================================="
echo "VMHub User Guide Artifact Generator"
echo "========================================="
echo ""

# Check prerequisites
echo "Checking prerequisites..."
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}✗ Python 3 is required but not found${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Python 3 found${NC}"

# Verify we're in the right place
if [ ! -f "lib/version_loader.py" ]; then
    echo -e "${RED}✗ Cannot find tools/lib/version_loader.py${NC}"
    echo -e "${RED}  This script should be in the repository root${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Found tools directory${NC}"
echo ""

# Determine version to use
if [ -z "$VERSION" ]; then
    VERSION_ARG=""
    echo "Using default version from configuration"
else
    VERSION_ARG="--version $VERSION"
    echo "Using version: $VERSION"
fi
echo ""

# Generate properties include
echo "Generating properties include..."
python3 generate_userguide_properties.py $VERSION_ARG
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Properties include generated${NC}"
else
    echo -e "${RED}✗ Failed to generate properties include${NC}"
    exit 1
fi
echo ""

# Generate structures include
echo "Generating structures include..."
python3 generate_userguide_structures.py $VERSION_ARG
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Structures include generated${NC}"
else
    echo -e "${RED}✗ Failed to generate structures include${NC}"
    exit 1
fi
echo ""

# Generate examples includes
echo "Generating examples includes..."
python3 generate_userguide_examples.py $VERSION_ARG
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Examples includes generated${NC}"
else
    echo -e "${RED}✗ Failed to generate examples includes${NC}"
    exit 1
fi
echo ""

# Generate HTML from AsciiDoc
echo "Generating HTML from AsciiDoc..."
cd "$SCRIPT_DIR/video-metadata-guidelines"
if [ -f "asciidoctor-to-html.sh" ]; then
    ./asciidoctor-to-html.sh
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ User guide HTML generated${NC}"
    else
        echo -e "${RED}✗ Failed to generate user guide HTML${NC}"
        exit 1
    fi
else
    echo -e "${RED}✗ asciidoctor-to-html.sh not found${NC}"
    exit 1
fi

echo ""
echo "========================================="
echo -e "${GREEN}✓ All user guide artifacts generated successfully!${NC}"
echo "========================================="


