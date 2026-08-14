#!/usr/bin/env python3
"""
ExifTool tag spec parser for VMHub.

Column U ("ExifTool tag") in the PropertiesRec / Structures tabs uses a
documentation/shape syntax, not literal ExifTool tag strings:

    XMP-ns:Tag                          plain scalar
    XMP-ns:Tag/type/                    scalar with a type hint (date-time,
                                        integer, decimal, ...); the type
                                        hint is informational only
    XMP-ns:Tag//array                   list of scalars (empty struct slot)
    XMP-ns:Tag/StructType               single structure of that type
    XMP-ns:Tag/StructType/array         list of structures of that type
    tag1,tag2                           two parallel ExifTool tags both
                                        receiving the same example value
    XMP-ns:Tag#                         the # is genuine ExifTool raw-mode
                                        syntax; kept verbatim
    NA                                  no XMP mapping exists; skip
    ?                                   mapping unknown; skip

This module parses those strings into a TagSpec and converts an example
cell value (from the Examples tab) into the Python value ExifTool's
`-json=` input expects.

Cell value conventions for structured properties (mix mode):
- For scalar/array-of-scalar specs: plain string, comma-separated list for
  arrays.
- For single-struct specs: either a plain string (goes into the struct's
  default "name" sub-field, see STRUCT_NAME_FIELD) or "Field1=v1; Field2=v2"
  key=value form.
- For array-of-struct specs: same, with "|" separating struct instances,
  e.g. "Name=NASA; Role=Producer | Name=ESA; Role=Co-producer".
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple


# Treated as "no mapping" - silently skipped.
NA_MARKERS = {"NA", "N/A", "-", ""}
# Treated as "unknown/TBD" - skipped with a different category in the summary.
UNKNOWN_MARKERS = {"?", "TBD", "tbd"}

# Default sub-field used when a struct-typed cell contains a plain scalar
# instead of "Field=value" syntax. Keyed by the IPTC struct-type label from
# column U. These are the field names ExifTool's *iptcExt* tables use; PLUS
# and other namespaces flatten differently and need per-tag overrides below.
STRUCT_NAME_FIELD: Dict[str, Optional[str]] = {
    "Entity": "Name",
    "EntityWRole": "Name",
    "LocationDetails": "LocationName",
    "PersonDetails": "PersonName",
    "CvTermDetails": "CvTermName",
    "Device": "Manufacturer",
    # Structs with no obvious single-field default - require key=value form
    "FrameSize": None,
}

# Per-parent-tag overrides for cases where ExifTool's struct field name
# does NOT match the struct-type default above. The PLUS namespace
# notoriously prefixes every field with the parent tag's local name.
# Keyed by full ExifTool tag string (matches the first element produced by
# parse_column_u, before any trailing '#').
STRUCT_FIELD_OVERRIDES: Dict[str, str] = {
    # PLUS namespace prefixes every struct field with the parent tag's
    # local name.
    "XMP-plus:CopyrightOwner":     "CopyrightOwnerName",
    "XMP-plus:Licensor":           "LicensorName",
    "XMP-plus:ImageCreator":       "ImageCreatorName",
    "XMP-plus:ImageSupplier":      "ImageSupplierName",

    # IPTC Extension struct types. Unlike PLUS these use bare field
    # names (Name / Link / etc.), not prefixed with the parent tag.
    "XMP-iptcExt:Episode":          "Name",
    "XMP-iptcExt:Season":           "Name",
    "XMP-iptcExt:Series":           "Name",
    "XMP-iptcExt:PublicationEvent": "Name",
    "XMP-iptcExt:DopesheetLink":    "Link",
    # ArtworkOrObject, LinkedEncRightsExpr, RegistryId (RegistryEntryDetails),
    # TemporalCoverage, VideoFrameSize: no single-field default that makes
    # sense; cells for these must use "Field=value" syntax.
}


def default_struct_field(tag: str, struct_type: Optional[str]) -> Optional[str]:
    """Return the default sub-field for a struct-typed value going into `tag`.
    None means 'no sensible default - cell must use Field=value syntax'."""
    if tag in STRUCT_FIELD_OVERRIDES:
        return STRUCT_FIELD_OVERRIDES[tag]
    if struct_type is None:
        return None
    return STRUCT_NAME_FIELD.get(struct_type)


class SkipReason:
    NA = "na"               # column U is NA / blank
    UNKNOWN = "unknown"     # column U is ?
    MALFORMED = "malformed" # couldn't parse column U
    NO_VALUE = "no_value"   # example cell empty
    STRUCT_NEEDS_KV = "struct_needs_kv"  # struct with no default name field
    EXIFTOOL_UNSUPPORTED = "exiftool_unsupported"  # tag valid in IPTC spec but ExifTool can't write it


# Tags that IPTC defines but ExifTool does not (yet) implement. Skipped
# silently and reported in the run summary. Re-check periodically against
# newer ExifTool releases; remove entries here as upstream support lands.
EXIFTOOL_UNSUPPORTED_TAGS: set = set()


# Tags that the IPTC sheet annotates as scalars in column U but that
# ExifTool defines as XMP structures. When the parsed spec lacks a
# struct_type but the tag appears here, treat the value as a single
# struct, using the configured sub-field name.
FORCED_STRUCT_TAGS: Dict[str, str] = {
    # Both are XMP Entity structs in ExifTool's iptcExt table; the bare
    # 'Name' field is what ExifTool expects, not the prefixed form.
    "XMP-iptcExt:MetadataAuthority":  "Name",
    "XMP-iptcExt:MetadataLastEditor": "Name",
}


# Tags where the IPTC sheet annotates a struct type but ExifTool exposes
# ONLY the flattened scalar name(s). For these, we emit as a plain scalar
# regardless of the sheet's struct annotation. If the cell uses "Field=value"
# form, the value part is extracted and the field name discarded.
FLATTEN_TO_SCALAR_TAGS: set = {
    # ExifTool models this as Snapshot/Link (parent tag "Snapshot", not
    # "SnapshotLink"), only reachable via the flat SnapshotLink name.
    "XMP-iptcExt:SnapshotLink",
}


@dataclass
class TagSpec:
    raw: str
    tags: List[str] = field(default_factory=list)  # one entry, or >1 for parallel
    struct_type: Optional[str] = None
    is_array: bool = False
    is_na: bool = False
    is_unknown: bool = False
    is_malformed: bool = False

    @property
    def skippable_reason(self) -> Optional[str]:
        if self.is_na:
            return SkipReason.NA
        if self.is_unknown:
            return SkipReason.UNKNOWN
        if self.is_malformed:
            return SkipReason.MALFORMED
        return None


def _parse_single(s: str) -> TagSpec:
    """Parse a single (non-comma-split) column U entry."""
    spec = TagSpec(raw=s)
    s = s.strip()
    if s in NA_MARKERS:
        spec.is_na = True
        return spec
    if s in UNKNOWN_MARKERS:
        spec.is_unknown = True
        return spec

    parts = s.split("/")
    # parts[0] is the ExifTool tag (may carry trailing #); parts[1] is the
    # struct type (or empty / a type-hint word); parts[2] is "array" or empty.
    tag = parts[0].strip()
    if not tag or ":" not in tag.replace("XMP-", "X:") and not tag.startswith("XMP-"):
        # Very weak sanity check - must look vaguely like a namespaced tag.
        spec.is_malformed = True
        return spec

    spec.tags = [tag]

    # Anything beyond parts[0] tells us about struct/array shape.
    struct_or_type = parts[1].strip() if len(parts) > 1 else ""
    array_marker = parts[2].strip() if len(parts) > 2 else ""

    # The middle slot is either a struct type name (CapitalCased), a scalar
    # type hint (date-time, integer, decimal, ...), or empty. Heuristic:
    # if it appears in STRUCT_NAME_FIELD we treat it as a struct; otherwise
    # it's a type hint we ignore.
    if struct_or_type:
        if struct_or_type in STRUCT_NAME_FIELD or struct_or_type[:1].isupper():
            # Treat as struct type. (Capitalised words we haven't seen
            # before will fall back to the "no default name field" path.)
            spec.struct_type = struct_or_type

    spec.is_array = (array_marker.lower() == "array")
    return spec


def parse_column_u(s: str) -> TagSpec:
    """Parse a column U cell value into a TagSpec."""
    if s is None:
        return TagSpec(raw="", is_na=True)
    s = s.strip()

    # Parallel-tag form: "tag1,tag2" - parse each side, then merge.
    if "," in s and all("XMP-" in part or part.strip() in NA_MARKERS
                       for part in s.split(",")):
        specs = [_parse_single(part) for part in s.split(",")]
        merged = TagSpec(raw=s)
        merged.tags = [t for sp in specs for t in sp.tags if not sp.is_na and not sp.is_unknown]
        # Struct/array attributes taken from the first non-skip spec.
        for sp in specs:
            if not (sp.is_na or sp.is_unknown or sp.is_malformed):
                merged.struct_type = sp.struct_type
                merged.is_array = sp.is_array
                break
        if not merged.tags:
            merged.is_na = all(sp.is_na for sp in specs)
            merged.is_unknown = any(sp.is_unknown for sp in specs)
            merged.is_malformed = not merged.is_na and not merged.is_unknown
        return merged

    return _parse_single(s)


# ---- cell value -> python ----

def _split_struct_instances(cell: str) -> List[str]:
    # "|" between struct instances. A single instance has no "|".
    return [chunk.strip() for chunk in cell.split("|") if chunk.strip()]


def _parse_kv(chunk: str) -> Optional[Dict[str, str]]:
    """Parse 'Field1=v1; Field2=v2' (or comma-separated) into a dict.
    Returns None if no '=' present (caller can treat as plain scalar).
    """
    if "=" not in chunk:
        return None
    # Prefer ';' separator, fall back to ',' if ';' absent.
    sep = ";" if ";" in chunk else ","
    out: Dict[str, str] = {}
    for piece in chunk.split(sep):
        piece = piece.strip()
        if not piece:
            continue
        if "=" not in piece:
            continue
        k, _, v = piece.partition("=")
        out[k.strip()] = v.strip()
    return out or None


def _scalar_or_list(cell: str) -> Any:
    """Comma-separated -> list; otherwise scalar string."""
    if "," in cell and not cell.startswith("{"):
        return [v.strip() for v in cell.split(",")]
    return cell


def example_value_to_python(spec: TagSpec, cell: str) -> Tuple[Any, Optional[str]]:
    """
    Convert an Examples cell into a Python value matching `spec`.

    Returns (value, skip_reason). When skip_reason is not None, value is
    undefined and the caller should drop this property.
    """
    if cell is None or cell.strip() == "":
        return None, SkipReason.NO_VALUE

    cell = cell.strip()

    # Parallel-tag specs (e.g. OrganisationInImageName,OrganisationInImageCode)
    # are *not* structs at the XMP serialisation level - each tag holds its
    # own scalar bag. Force scalar treatment regardless of struct annotation.
    single_tag = spec.tags[0] if len(spec.tags) == 1 else None

    # Tags whose sheet annotation says struct but ExifTool only exposes a
    # flat scalar form: strip any "Field=" prefix and emit as scalar.
    if single_tag in FLATTEN_TO_SCALAR_TAGS:
        stripped = cell.split("=", 1)[1].strip() if "=" in cell else cell
        return _scalar_or_list(stripped), None

    treat_as_struct = (
        single_tag is not None
        and (spec.struct_type is not None or single_tag in FORCED_STRUCT_TAGS)
    )

    if not treat_as_struct:
        value = _scalar_or_list(cell)
        if spec.is_array and not isinstance(value, list):
            value = [value]
        return value, None

    # Struct-typed tag. Build one dict per instance.
    tag = single_tag
    name_field = FORCED_STRUCT_TAGS.get(tag) or default_struct_field(tag, spec.struct_type)

    instances_raw = _split_struct_instances(cell)
    instances: List[Dict[str, str]] = []
    for chunk in instances_raw:
        kv = _parse_kv(chunk)
        if kv is not None:
            instances.append(kv)
        elif name_field is not None:
            instances.append({name_field: chunk})
        else:
            # Plain scalar but no default sub-field configured for this
            # struct type - can't safely guess where the value goes.
            return None, SkipReason.STRUCT_NEEDS_KV

    if spec.is_array:
        return instances, None
    # Single-struct spec: take the first instance only.
    return instances[0] if instances else None, (
        None if instances else SkipReason.NO_VALUE
    )


# ---- skip summary ----

@dataclass
class SkipStats:
    by_reason: Dict[str, List[str]] = field(default_factory=dict)

    def record(self, reason: str, property_name: str) -> None:
        self.by_reason.setdefault(reason, []).append(property_name)

    def render(self) -> str:
        if not self.by_reason:
            return "  (no properties skipped)"
        labels = {
            SkipReason.NA: "no XMP mapping (NA)",
            SkipReason.UNKNOWN: "mapping unknown (?)",
            SkipReason.MALFORMED: "malformed column U",
            SkipReason.NO_VALUE: "no example value in cell",
            SkipReason.STRUCT_NEEDS_KV:
                "struct type has no default 'name' sub-field "
                "(use Field=value syntax)",
            SkipReason.EXIFTOOL_UNSUPPORTED:
                "tag is valid in the IPTC spec but ExifTool cannot write it",
        }
        lines = []
        for reason, props in sorted(self.by_reason.items()):
            label = labels.get(reason, reason)
            lines.append(f"  {len(props)} skipped: {label}")
            for name in props:
                lines.append(f"      - {name}")
        return "\n".join(lines)


if __name__ == "__main__":
    # Quick self-test against the patterns observed in PropertiesRec 1.7.
    samples = [
        "XMP-iptcExt:Headline",
        "XMP-photoshop:DateCreated/date-time",
        "XMP-iptcExt:CopyrightYear/integer/",
        "XMP-dc:Subject//array",
        "XMP-iptcExt:Creator/EntityWRole/array",
        "XMP-iptcExt:RecDevice/Device",
        "XMP-plus:CopyrightOwner/EntityWRole/array",
        "XMP-iptcExt:OrganisationInImageName/Entity/array,"
        "XMP-iptcExt:OrganisationInImageCode/Entity/array",
        "XMP-xmpDM:AudioChannelType#",
        "NA",
        "?",
        "",
    ]
    for s in samples:
        spec = parse_column_u(s)
        print(f"  {s!r:80s}  -> tags={spec.tags} struct={spec.struct_type} "
              f"array={spec.is_array} na={spec.is_na} unk={spec.is_unknown} "
              f"mal={spec.is_malformed}")
