#!/bin/bash
# Build VMHub Specification Artifacts
#
# Brendan Quinn, IPTC 2025 (created with the help of Cursor)
#
# Usage: ./build_spec.sh [version]
#   version: Optional VMHub version (e.g., 1.7). Uses default if not specified.
#
# Run from repository root

set -e  # Exit on error

# Get the directory where this script is located (should be repo root)
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Change to the tools directory
cd "$SCRIPT_DIR/tools"

# Get version from argument or use default
VERSION=$1

# Color output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "========================================="
echo "VMHub Specification Artifact Generator"
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

# Generate properties HTML
echo "Generating properties HTML..."
python3 generate_properties_html.py $VERSION_ARG
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Properties HTML generated${NC}"
else
    echo -e "${RED}✗ Failed to generate properties HTML${NC}"
    exit 1
fi
echo ""

# Generate mappings HTML
echo "Generating mappings HTML..."
python3 generate_mappings_html.py $VERSION_ARG
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Mappings HTML generated${NC}"
else
    echo -e "${RED}✗ Failed to generate mappings HTML${NC}"
    exit 1
fi
echo ""

# Generate JSON Schema
echo "Generating JSON Schema..."
python3 generate_json_schema.py $VERSION_ARG
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ JSON Schema generated${NC}"
else
    echo -e "${RED}✗ Failed to generate JSON Schema${NC}"
    exit 1
fi
echo ""

echo "========================================="
echo -e "${GREEN}✓ All spec artifacts generated successfully!${NC}"
echo "========================================="

