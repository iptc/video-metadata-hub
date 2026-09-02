#!/bin/bash
# Build C2PA-signed copies of the VMHub example videos.
#
# Sends each examples/IPTC-VMHub-RefVideo-Rec<ver>-<usecase>.mp4 to the
# local IPTC C2PA signing service and writes the signed copy to
# examples/c2pa/IPTC-VMHub-RefVideo-Rec<ver>-<usecase>-c2pa.mp4.
#
# The signing service is a local dev tool that depends on an AWS session
# for its KMS-hosted certificates. If it isn't running or its AWS session
# has expired this script exits with a warning but code 0, so build_all.sh
# can carry on and produce the rest of the artifacts.
#
# Usage: ./build_c2pa.sh [version]

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

if [ -f "$SCRIPT_DIR/venv/bin/activate" ]; then
    source "$SCRIPT_DIR/venv/bin/activate"
fi

cd "$SCRIPT_DIR/tools"

VERSION=$1
BASE_URL="${VMHUB_C2PA_SIGNER_URL:-http://localhost:5001}"

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "========================================="
echo "VMHub C2PA Signer"
echo "========================================="
echo ""
echo "Signer URL: $BASE_URL"
echo ""

# Preflight: if the signer isn't healthy, warn and exit 0 so a full
# build can still finish. The user can run ./build_c2pa.sh manually
# once the signer is back.
if ! python3 -c "
import sys
from lib.c2pa_signer import check_signer_status
ok, msg = check_signer_status('$BASE_URL')
print(msg)
sys.exit(0 if ok else 1)
"; then
    echo ""
    echo -e "${YELLOW}⚠ C2PA signer not available - skipping C2PA build.${NC}"
    echo "  Start the local signer (and check its AWS session) then run"
    echo "  ./build_c2pa.sh manually."
    exit 0
fi
echo ""

if [ -z "$VERSION" ]; then
    VERSION_ARG=""
else
    VERSION_ARG="--version $VERSION"
fi

if python3 sign_c2pa_examples.py $VERSION_ARG --base-url "$BASE_URL" --skip-status-check; then
    echo ""
    echo -e "${GREEN}✓ C2PA signing complete.${NC}"
else
    echo ""
    echo -e "${RED}✗ One or more use cases failed to sign.${NC}"
    exit 1
fi
