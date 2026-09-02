#!/usr/bin/env python3
"""
Sign the generated VMHub example videos with C2PA provenance using the
local IPTC signing service.

Reads examples/IPTC-VMHub-RefVideo-Rec<ver>-<usecase>.mp4 (already
embedded with XMP metadata by generate_example_videos.py) plus its
sidecar .json (used to populate the C2PA manifest's small metadata
subset), sends both to the signer, and writes the signed copy to
examples/c2pa/IPTC-VMHub-RefVideo-Rec<ver>-<usecase>-c2pa.mp4.

The signing service is a local dev tool - see lib/c2pa_signer.py for the
protocol details.
"""

import argparse
import json
import os
import sys

from lib.version_loader import get_version_config, list_available_versions
from lib.use_cases import load_use_cases
from lib.c2pa_signer import (
    DEFAULT_BASE_URL, check_signer_status, sidecar_to_c2pa_metadata, sign_file,
)


def sign_example(use_case: dict, version_clean: str, examples_dir: str,
                 out_dir: str, base_url: str) -> str:
    """Sign one use case. Returns the output path."""
    ext = os.path.splitext(use_case["source_file"])[1] or ".mp4"
    stem = f"IPTC-VMHub-RefVideo-Rec{version_clean}-{use_case['name']}"
    input_media = os.path.join(examples_dir, stem + ext)
    sidecar_path = os.path.join(examples_dir, stem + ".json")
    output_media = os.path.join(out_dir, stem + "-c2pa" + ext)

    if not os.path.exists(input_media):
        raise FileNotFoundError(
            f"input media missing: {input_media}\n"
            f"  Run ./build_examples.sh first to produce the ExifTool-embedded MP4."
        )
    if not os.path.exists(sidecar_path):
        raise FileNotFoundError(f"sidecar JSON missing: {sidecar_path}")

    sidecar = json.load(open(sidecar_path))[0]
    metadata = sidecar_to_c2pa_metadata(sidecar)

    print(f"  input:    {os.path.relpath(input_media)}")
    print(f"  output:   {os.path.relpath(output_media)}")
    print(f"  metadata: {json.dumps(metadata, ensure_ascii=False)}")

    sign_file(input_media, output_media, metadata, base_url=base_url)
    return output_media


def main() -> int:
    parser = argparse.ArgumentParser(
        description="C2PA-sign the generated VMHub example videos."
    )
    parser.add_argument(
        "--version",
        help=f"VMHub version (available: {', '.join(list_available_versions())})",
    )
    parser.add_argument(
        "--use-case",
        help="Sign only this use case (default: all use cases).",
    )
    parser.add_argument(
        "--base-url", default=DEFAULT_BASE_URL,
        help=f"Signer base URL (default: {DEFAULT_BASE_URL}).",
    )
    parser.add_argument(
        "--skip-status-check", action="store_true",
        help="Skip the /status/aws preflight (rarely useful).",
    )
    args = parser.parse_args()

    # Preflight
    if not args.skip_status_check:
        ok, msg = check_signer_status(args.base_url)
        print(f"C2PA signer status: {msg}")
        if not ok:
            print(f"✗ Signer at {args.base_url} is not healthy.")
            print("  If the AWS session behind it has expired, ask Brendan to")
            print("  renew it. Otherwise start the signer service first.")
            return 2
    print()

    version_config = get_version_config(args.version)
    version_clean = version_config["version"].replace(".", "")

    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    examples_dir = os.path.join(repo_root, "examples")
    out_dir = os.path.join(examples_dir, "c2pa")

    use_cases = load_use_cases()
    if args.use_case:
        use_cases = [uc for uc in use_cases if uc["name"] == args.use_case]
        if not use_cases:
            print(f"✗ Unknown use case: {args.use_case}")
            return 1

    failures = []
    for uc in use_cases:
        print(f"---- {uc['name']} ----")
        try:
            out = sign_example(uc, version_clean, examples_dir, out_dir,
                               args.base_url)
            print(f"  ✓ signed: {os.path.relpath(out)}")
        except Exception as e:
            print(f"  ✗ failed: {e}")
            failures.append((uc["name"], str(e)))
        print()

    if failures:
        print("=" * 50)
        print(f"✗ {len(failures)} use case(s) failed:")
        for name, err in failures:
            print(f"  - {name}: {err}")
        return 1

    print("=" * 50)
    print(f"✓ Signed {len(use_cases)} example(s) into {os.path.relpath(out_dir)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
