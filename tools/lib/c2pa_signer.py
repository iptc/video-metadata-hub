#!/usr/bin/env python3
"""
Client for the IPTC C2PA signing service.

The signer runs locally (default http://localhost:5001), takes a media file
plus a small JSON metadata blob, and returns a C2PA-signed copy. Two
certificates live in AWS KMS behind the API: cert_id=1 for the manifest
signature, identity_cert_id=2 for the CAWG identity assertion. Both are
fixed for the VMHub work.

Set VMHUB_C2PA_SIGNER_URL to override the base URL.

The API only carries a small fixed set of metadata fields, so we extract
what we can from the ExifTool sidecar JSON that generate_example_videos.py
already produced. Unknown or empty fields are simply not sent.
"""

import json
import os
import shutil
import urllib.request
from typing import Any, Callable, Dict, List, Optional, Tuple


DEFAULT_BASE_URL = os.environ.get("VMHUB_C2PA_SIGNER_URL", "http://localhost:5001")
CERT_ID = "1"
IDENTITY_CERT_ID = "2"


# ---- status ----

def check_signer_status(base_url: str = DEFAULT_BASE_URL) -> Tuple[bool, str]:
    """Hit /status/aws. Return (ok, human-readable-message)."""
    try:
        with urllib.request.urlopen(f"{base_url}/status/aws", timeout=5) as r:
            data = json.loads(r.read().decode())
    except Exception as e:
        return False, f"could not reach {base_url}/status/aws ({e})"

    checks = data.get("checks") or {}
    tagged = data.get("tagged_keys")
    all_ok = all(v == "ok" for v in checks.values()) if checks else False
    if not all_ok:
        return False, f"AWS checks not all ok: {checks}"
    if tagged != 2:
        return False, f"expected tagged_keys=2, got {tagged}"
    return True, "signer healthy"


# ---- sidecar -> C2PA metadata mapping ----

def _first(v: Any) -> Any:
    """If v is a list, return the first item; else v itself."""
    return v[0] if isinstance(v, list) and v else v


def _as_str(v: Any) -> Optional[str]:
    """Coerce lists/tuples to comma-joined strings, drop empty."""
    if v is None:
        return None
    if isinstance(v, (list, tuple)):
        parts = [str(x) for x in v if x not in (None, "")]
        return ", ".join(parts) if parts else None
    s = str(v).strip()
    return s or None


def _struct_field(v: Any, *field_names: str) -> Optional[str]:
    """Pull one of `field_names` out of a struct or list-of-structs value."""
    item = _first(v)
    if isinstance(item, dict):
        for f in field_names:
            if item.get(f) not in (None, ""):
                return str(item[f])
    return _as_str(item)


# Each entry: (c2pa_field, list of sidecar keys to try, extractor).
# The first sidecar key that yields a non-empty value wins.
_MAPPING: List[Tuple[str, List[str], Callable[[Any], Optional[str]]]] = [
    ("publisher",         ["XMP-plus:CopyrightOwner"],
        lambda v: _struct_field(v, "CopyrightOwnerName", "Name")),
    ("caption",           ["XMP-dc:Description"], _as_str),
    ("alt_text",          ["XMP-iptcCore:AltTextAccessibility"], _as_str),
    ("byline",            ["XMP-iptcExt:Creator", "XMP-dc:creator"],
        lambda v: _struct_field(v, "Name")),
    ("source",            ["XMP-photoshop:Source", "XMP-plus:ImageSupplier"],
        lambda v: _struct_field(v, "ImageSupplierName", "Name")),
    ("creditline",        ["XMP-photoshop:Credit"], _as_str),
    ("copyright_notice",  ["XMP-dc:Rights", "XMP-photoshop:CopyrightNotice"],
        _as_str),
    ("genre",             ["XMP-iptcExt:Genre"],
        lambda v: _struct_field(v, "CvTermName", "Name")),
    ("locationcreated",   ["XMP-iptcExt:LocationCreated"],
        lambda v: _struct_field(v, "LocationName", "Name")),
    ("published_date",    ["XMP-photoshop:DateCreated", "XMP-xmpDM:ReleaseDate"],
        _as_str),
    ("digitalsourcetype", ["XMP-iptcExt:DigitalSourceType"], _as_str),
]


def sidecar_to_c2pa_metadata(sidecar: Dict[str, Any]) -> Dict[str, str]:
    """Extract C2PA-supported fields from an ExifTool sidecar dict."""
    out: Dict[str, str] = {}
    for c2pa_field, keys, extractor in _MAPPING:
        for k in keys:
            if k in sidecar:
                val = extractor(sidecar[k])
                if val:
                    out[c2pa_field] = val
                    break
    return out


# ---- signing one file ----

def _multipart_body(fields: Dict[str, str], file_field: str,
                    file_path: str, boundary: str) -> bytes:
    """Build a multipart/form-data body from string fields + one file field."""
    parts: List[bytes] = []
    for name, value in fields.items():
        parts.append(f"--{boundary}\r\n".encode())
        parts.append(f'Content-Disposition: form-data; name="{name}"\r\n\r\n'
                     .encode())
        parts.append(value.encode("utf-8"))
        parts.append(b"\r\n")

    parts.append(f"--{boundary}\r\n".encode())
    parts.append(
        f'Content-Disposition: form-data; name="{file_field}"; '
        f'filename="{os.path.basename(file_path)}"\r\n'.encode()
    )
    parts.append(b"Content-Type: application/octet-stream\r\n\r\n")
    with open(file_path, "rb") as f:
        parts.append(f.read())
    parts.append(b"\r\n")

    parts.append(f"--{boundary}--\r\n".encode())
    return b"".join(parts)


def sign_file(input_path: str, output_path: str,
              metadata: Dict[str, str],
              base_url: str = DEFAULT_BASE_URL,
              timeout: int = 120) -> None:
    """
    Send `input_path` to the signer with `metadata`; save the signed result
    to `output_path`. Raises on any error (HTTP, network, or a JSON body
    with success != True).
    """
    boundary = "----vmhub-c2pa-" + os.urandom(8).hex()
    fields = {
        "cert_id": CERT_ID,
        "identity_cert_id": IDENTITY_CERT_ID,
        "metadata": json.dumps(metadata, ensure_ascii=False),
    }
    body = _multipart_body(fields, "file", input_path, boundary)

    req = urllib.request.Request(
        f"{base_url}/api/sign",
        data=body,
        method="POST",
        headers={
            "Content-Type": f"multipart/form-data; boundary={boundary}",
            "Content-Length": str(len(body)),
        },
    )

    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            resp = json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        try:
            detail = json.loads(e.read().decode()).get("error", str(e))
        except Exception:
            detail = str(e)
        raise RuntimeError(f"signer HTTP {e.code}: {detail}") from e

    if not resp.get("success"):
        raise RuntimeError(f"signer refused: {resp}")

    download_url = resp.get("download_url")
    if not download_url:
        raise RuntimeError(f"signer response missing download_url: {resp}")

    # Download immediately - signed files are shared-directory + 24h TTL.
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    tmp = output_path + ".part"
    with urllib.request.urlopen(download_url, timeout=timeout) as r_dl, \
         open(tmp, "wb") as f_out:
        shutil.copyfileobj(r_dl, f_out)
    os.replace(tmp, output_path)


if __name__ == "__main__":
    # Quick health + mapping smoke test.
    ok, msg = check_signer_status()
    print(f"signer: {msg}")
    import sys
    if len(sys.argv) > 1:
        sidecar = json.load(open(sys.argv[1]))[0]
        print("Would send this metadata:")
        print(json.dumps(sidecar_to_c2pa_metadata(sidecar), indent=2))
