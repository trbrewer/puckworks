"""WP1.7 / PR3 — the sanctioned-export contract + a deterministic importer.

The moving public window is not a coherent dataset (WP1.5). A *sanctioned export* is a
point-in-time dump of the source database that carries an ``export_cutoff`` and per-record
version identity. This module (a) defines the versioned export contract, (b) imports an export
into a NEW empty store that ``corpus_freeze.freeze_rehearse`` can accept as publication-ready,
and (c) provides a synthetic export fixture exercising the adversarial cases the plan lists
(revisions, equal-timestamp conflicts, missing channels, source-family differences, quarantine
cases, records around the cutoff).

The importer is deterministic (no wall-clock/random), quarantines un-normalizable records
instead of crashing, and drops post-cutoff records (they violate the export's coherence claim).
See ``docs/analysis/SANCTIONED_EXPORT_SPEC.md`` for the requested export schema.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

from puckworks.lib import visualizer_harvest as _vh

EXPORT_SPEC_VERSION = 1

# The fields a sanctioned export is REQUESTED to carry (documented in SANCTIONED_EXPORT_SPEC.md);
# the importer tolerates missing optional fields but REQUIRES a non-null export_cutoff.
REQUIRED_EXPORT_MANIFEST_FIELDS = ("export_cutoff",)

# A PUBLICATION-profile manifest must carry a full governance record before any publication freeze
# may pass. Names align with SANCTIONED_EXPORT_SPEC.md. Strict (no coercion, exact v1 field set).
_PUB_INT_FIELDS = ("export_spec_version", "export_cutoff", "source_schema_version", "record_count")
_PUB_STR_FIELDS = (
    "source_name", "source_authority", "stable_record_id_semantics", "record_version_semantics",
    "user_linkage_semantics", "privacy_transform", "rights_basis", "retention_policy",
    "deletion_or_correction_policy", "contact_record",
)
PUBLICATION_REQUIRED_FIELDS = tuple(
    list(_PUB_INT_FIELDS) + list(_PUB_STR_FIELDS)
    + ["export_created_at", "archive_or_export_sha256", "raw_redistribution_status",
       "aggregate_publication_status", "source_kind"]
)
# exact publication v1 field set; legacy spec-v1 fields are tolerated but never substitute a
# publication field, and any other field must use the documented "x_" extension namespace.
_LEGACY_FIELDS = {"source", "license", "privacy"}
# "importer" is an importer-owned metadata block (nested), never a source-manifest substitute.
_PUBLICATION_V1_FIELDS = set(PUBLICATION_REQUIRED_FIELDS) | _LEGACY_FIELDS | {"importer"}
_REDIST_VOCAB = {"prohibited", "permitted"}
_AGG_VOCAB = {"permitted", "prohibited"}
SOURCE_KIND_VOCAB = {"real_export", "synthetic_test_fixture"}
_RFC3339 = re.compile(r"^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2})(?:\.\d+)?(Z|[+-]\d{2}:\d{2})$")


class ExportManifestError(ValueError):
    """Raised when a sanctioned-export manifest fails profile validation."""


def _is_lower_sha256(v) -> bool:
    return isinstance(v, str) and len(v) == 64 and all(c in "0123456789abcdef" for c in v)


def _strict_int(v) -> bool:
    return isinstance(v, int) and not isinstance(v, bool)


def _valid_rfc3339(v) -> bool:
    if not isinstance(v, str):
        return False
    m = _RFC3339.match(v)
    if not m:
        return False
    try:
        from datetime import datetime
        datetime(*(int(m.group(i)) for i in range(1, 7)))
    except ValueError:
        return False
    off = m.group(7)
    return off == "Z" or (int(off[1:3]) <= 23 and int(off[4:6]) <= 59)


def validate_export_manifest(manifest, *, profile="rehearsal", n_records=None):
    """Validate a sanctioned-export manifest under a profile (strict; no coercion).

    ``rehearsal`` requires only a non-null integer ``export_cutoff`` and marks output non-publication.
    ``publication`` **fails closed** unless the full governance record is present, strictly typed, and
    internally consistent — strict integers; ``export_spec_version == EXPORT_SPEC_VERSION``; RFC 3339
    ``export_created_at``; a full **lowercase** SHA-256; nonempty governance strings; exact v1 field
    set (unknown fields require the ``x_`` extension namespace); ``aggregate_publication_status ==
    permitted``; and ``source_kind == real_export`` (a synthetic fixture can never qualify).
    """
    if profile not in ("rehearsal", "publication"):
        raise ValueError("profile must be 'rehearsal' or 'publication'")
    if not isinstance(manifest, dict):
        raise ExportManifestError("export manifest must be a mapping")
    problems = []
    if not _strict_int(manifest.get("export_cutoff")):
        problems.append("export_cutoff must be a non-null integer (distinguishes an export from a feed)")
    if profile == "publication":
        for f in PUBLICATION_REQUIRED_FIELDS:
            if manifest.get(f) in (None, "", []):
                problems.append("missing required publication field %r" % f)
        for f in _PUB_INT_FIELDS:
            if f in manifest and not _strict_int(manifest[f]):
                problems.append("%s must be a strict integer (not bool/str/float)" % f)
        if _strict_int(manifest.get("export_spec_version")) and manifest["export_spec_version"] != EXPORT_SPEC_VERSION:
            problems.append("export_spec_version must be %d" % EXPORT_SPEC_VERSION)
        if _strict_int(manifest.get("record_count")) and manifest["record_count"] < 0:
            problems.append("record_count must be non-negative")
        for f in _PUB_STR_FIELDS:
            v = manifest.get(f)
            if v is not None and not (isinstance(v, str) and v.strip()):
                problems.append("%s must be a non-empty string" % f)
        if manifest.get("export_created_at") is not None and not _valid_rfc3339(manifest["export_created_at"]):
            problems.append("export_created_at must be an RFC 3339 timestamp with an explicit offset")
        if manifest.get("archive_or_export_sha256") is not None and not _is_lower_sha256(manifest["archive_or_export_sha256"]):
            problems.append("archive_or_export_sha256 must be a full lowercase SHA-256")
        rc = manifest.get("record_count")
        if _strict_int(rc) and n_records is not None and rc != n_records:
            problems.append("record_count %r != actual %r" % (rc, n_records))
        rr = manifest.get("raw_redistribution_status")
        if rr is not None and rr not in _REDIST_VOCAB:
            problems.append("raw_redistribution_status must be one of %s" % sorted(_REDIST_VOCAB))
        ap = manifest.get("aggregate_publication_status")
        if ap is not None and ap not in _AGG_VOCAB:
            problems.append("aggregate_publication_status must be one of %s" % sorted(_AGG_VOCAB))
        if ap != "permitted":
            problems.append("publication requires aggregate_publication_status == permitted")
        sk = manifest.get("source_kind")
        if sk is not None and sk not in SOURCE_KIND_VOCAB:
            problems.append("source_kind must be one of %s" % sorted(SOURCE_KIND_VOCAB))
        if sk != "real_export":
            problems.append("publication requires source_kind == real_export (synthetic cannot qualify)")
        unknown = set(manifest) - _PUBLICATION_V1_FIELDS - {k for k in manifest if str(k).startswith("x_")}
        if unknown:
            problems.append("unknown publication field(s) (use the x_ extension namespace): %s" % sorted(unknown))
    if problems:
        raise ExportManifestError("; ".join(problems))
    return {
        "profile": profile,
        "export_cutoff": manifest["export_cutoff"],
        "publication_qualified": profile == "publication",
        "source_kind": manifest.get("source_kind"),
        "classification": "publication-source" if profile == "publication" else "rehearsal-source",
    }


def import_sanctioned_export(records, export_manifest, dst_dir, salt="import"):
    """Import a sanctioned export into a NEW empty store. Returns a summary dict. Writes shards,
    index, Bronze lineage, and a ``source_export_manifest.json`` (the coherence evidence that
    lets a publication freeze pass). Refuses a non-empty target and an export without a cutoff."""
    dst = Path(dst_dir)
    if dst.exists() and any(dst.iterdir()):
        raise FileExistsError("import target must be a NEW empty store: %s" % dst)
    records = list(records)   # materialize the immutable input ONCE (no generator re-consumption)
    for f in REQUIRED_EXPORT_MANIFEST_FIELDS:
        if export_manifest.get(f) is None:
            raise ValueError("sanctioned export manifest missing required field %r" % f)
    cutoff = _vh._as_int(export_manifest.get("export_cutoff"), default=None)
    if cutoff is None:
        raise ValueError("export_cutoff must be an integer")

    cfg = _vh.HarvestConfig(out_dir=str(dst), salt=salt, store_bronze=True)
    tidy, index_rows, bronze, quarantined, excluded = [], [], [], [], []
    for raw in records:
        u = _vh._as_int((raw or {}).get("updated_at") if isinstance(raw, dict) else None,
                        default=None)
        if u is not None and u > cutoff:
            excluded.append({"id": (raw or {}).get("id"), "updated_at": u,
                             "reason": "after_export_cutoff"})
            continue
        try:
            t = _vh.normalize_shot(raw, cfg)
        except Exception as exc:                       # un-normalizable -> resolve by quarantine
            sid = (raw or {}).get("id") if isinstance(raw, dict) else None
            quarantined.append({"id": sid, "reason": "normalize_error:%s" % type(exc).__name__})
            continue
        tidy.append(t)
        index_rows.append(_vh._index_row(t))
        bronze.append(_vh._bronze_record(cfg, raw, t))

    sz = cfg.shard_size
    for i in range(0, len(tidy), sz):
        idx = i // sz
        _vh._write_shard(cfg, idx, tidy[i:i + sz])
        _vh._write_bronze_shard(cfg, idx, bronze[i:i + sz])
    if index_rows:
        _vh._append_index(cfg, index_rows)

    # Preserve the SOURCE manifest verbatim; record importer-owned facts under a nested "importer"
    # key (so the strict publication field-set is not polluted). Record accounting: the source
    # record_count must equal the materialized input, and imported+quarantined+excluded must too.
    man = dict(export_manifest)
    accounting_ok = (len(records) == len(tidy) + len(quarantined) + len(excluded))
    man["importer"] = {
        "n_export_records": len(records),
        "n_imported": len(tidy),
        "n_quarantined": len(quarantined),
        "n_excluded_after_cutoff": len(excluded),
        "accounting_ok": accounting_ok,
        "source_record_count_matches_input": (export_manifest.get("record_count") == len(records)),
        "importer_version": _vh._HARVEST_VERSION,
        "normalizer_schema_version": _vh._NORMALIZE_SCHEMA_VERSION,
        "bronze_schema_version": _vh._BRONZE_SCHEMA_VERSION,
    }
    (dst / "source_export_manifest.json").write_text(
        json.dumps(man, indent=2, sort_keys=True), encoding="utf-8")
    # quarantine/exclusions are RESOLVED (dropped from the store) but logged for audit
    if quarantined:
        (dst / "import_quarantine.json").write_text(
            json.dumps(quarantined, indent=2, sort_keys=True), encoding="utf-8")
    if excluded:
        (dst / "import_exclusions.json").write_text(
            json.dumps(excluded, indent=2, sort_keys=True), encoding="utf-8")
    return {"n_imported": len(tidy), "n_quarantined": len(quarantined),
            "n_excluded_after_cutoff": len(excluded), "export_cutoff": cutoff}


def synthetic_export(cutoff=1000):
    """A deterministic synthetic export exercising the adversarial cases (WP1.7). Returns
    ``(records, export_manifest)``. Includes: a normal shot; a REVISION (two updated_at for one
    id); an equal-timestamp CONFLICT (same id+updated_at, differing content); a pressure-only
    shot (missing flow channel); a second source family; a post-cutoff record (excluded); and an
    un-normalizable record (quarantined)."""
    tf = [0.0, 1.0, 2.0]

    def shot(sid, u, pressure=None, flow=None, source="app", user="u1"):
        data = {}
        if pressure is not None:
            data["espresso_pressure"] = pressure
            data["espresso_pressure_goal"] = pressure
        if flow is not None:
            data["espresso_flow"] = flow
        return {"id": sid, "user_id": user, "updated_at": u, "integration_source": source,
                "timeframe": tf, "data": data}

    records = [
        shot("normal1", 100, [6.0, 9.0, 9.0], [1.0, 2.0, 2.0]),
        shot("rev1", 120, [3.0, 3.0, 3.0]),                    # revision v1
        shot("rev1", 220, [3.0, 6.0, 9.0]),                    # revision v2 (later updated_at)
        shot("conflict1", 300, [1.0, 1.0, 1.0]),               # equal-ts conflict A
        shot("conflict1", 300, [9.0, 9.0, 9.0]),               # equal-ts conflict B (differs)
        shot("presonly", 150, [6.0, 9.0, 9.0]),                # missing flow channel
        shot("srcB", 130, [6.0, 8.0, 8.0], [1.0, 1.5, 1.5], source="de1app", user="u2"),
        shot("postcutoff", cutoff + 500, [6.0, 9.0, 9.0]),     # after cutoff -> excluded
        {"id": "bad1", "user_id": "u3", "updated_at": 140, "timeframe": tf, "data": "nope"},  # quarantined
    ]
    manifest = _governance_record(len(records), cutoff, source_kind="synthetic_test_fixture")
    manifest.update({  # legacy spec-v1 fields (kept for continuity; never a publication substitute)
        "source": "visualizer.coffee sanctioned export (synthetic fixture)",
        "license": "per Miha permission 2026-07-14; attribution + collective user credit",
        "privacy": "salted one-way user hash; free-text/PII dropped on import",
    })
    return records, manifest


def _governance_record(record_count, cutoff, *, source_kind, archive_sha256="0" * 64):
    """A complete publication-profile governance record. ``source_kind`` decides whether it can ever
    qualify for publication (``real_export``) or is a synthetic/test stand-in that never can."""
    return {
        "export_spec_version": EXPORT_SPEC_VERSION,
        "source_name": "visualizer.coffee",
        "source_authority": "visualizer.coffee maintainer" if source_kind == "real_export"
                            else "synthetic fixture stand-in",
        "export_created_at": "2026-07-17T00:00:00Z",   # deterministic; a real export stamps wall-clock
        "export_cutoff": cutoff,
        "source_schema_version": 1,
        "record_count": record_count,
        "archive_or_export_sha256": archive_sha256,
        "stable_record_id_semantics": "opaque per-shot id; stable across the export",
        "record_version_semantics": "integer updated_at as the monotone version key",
        "user_linkage_semantics": "salted one-way per-user token; no reversible identity",
        "privacy_transform": "PII/free-text dropped on import; salted user hash",
        "rights_basis": "authorised research use" if source_kind == "real_export"
                        else "synthetic fixture; not a rights grant",
        "raw_redistribution_status": "prohibited",
        "aggregate_publication_status": "permitted",
        "retention_policy": "per the source governance record",
        "deletion_or_correction_policy": "deletions/corrections re-exported by the source",
        "contact_record": "recorded authorising contact",
        "source_kind": source_kind,
    }
