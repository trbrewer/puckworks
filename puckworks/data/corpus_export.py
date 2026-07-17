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
from pathlib import Path

from puckworks.lib import visualizer_harvest as _vh

EXPORT_SPEC_VERSION = 1

# The fields a sanctioned export is REQUESTED to carry (documented in SANCTIONED_EXPORT_SPEC.md);
# the importer tolerates missing optional fields but REQUIRES a non-null export_cutoff.
REQUIRED_EXPORT_MANIFEST_FIELDS = ("export_cutoff",)

# A PUBLICATION-profile manifest must additionally carry a full governance record before any
# publication freeze may pass. Names align with SANCTIONED_EXPORT_SPEC.md.
PUBLICATION_REQUIRED_FIELDS = (
    "export_spec_version", "source_name", "source_authority", "export_created_at", "export_cutoff",
    "source_schema_version", "record_count", "archive_or_export_sha256", "stable_record_id_semantics",
    "record_version_semantics", "user_linkage_semantics", "privacy_transform", "rights_basis",
    "raw_redistribution_status", "aggregate_publication_status", "retention_policy",
    "deletion_or_correction_policy", "contact_record",
)
_REDIST_VOCAB = {"prohibited", "permitted"}
_AGG_VOCAB = {"permitted", "prohibited"}


class ExportManifestError(ValueError):
    """Raised when a sanctioned-export manifest fails profile validation."""


def _is_sha256(v) -> bool:
    return isinstance(v, str) and len(v) == 64 and all(c in "0123456789abcdef" for c in v.lower())


def validate_export_manifest(manifest, *, profile="rehearsal", n_records=None):
    """Validate a sanctioned-export manifest under a profile.

    ``rehearsal`` requires only enough identity to test import behaviour (a non-null integer
    ``export_cutoff``) and marks its output non-publication. ``publication`` **fails closed** unless
    the full governance record is present and internally consistent — missing rights, checksum,
    aggregate-publication permission, or the immutable cutoff all raise :class:`ExportManifestError`.
    Returns a classification dict; never returns silently on a publication gap.
    """
    if profile not in ("rehearsal", "publication"):
        raise ValueError("profile must be 'rehearsal' or 'publication'")
    if not isinstance(manifest, dict):
        raise ExportManifestError("export manifest must be a mapping")
    problems = []
    cutoff = _vh._as_int(manifest.get("export_cutoff"), default=None)
    if cutoff is None:
        problems.append("export_cutoff must be a non-null integer (distinguishes an export from a feed)")
    if profile == "publication":
        for f in PUBLICATION_REQUIRED_FIELDS:
            if manifest.get(f) in (None, "", []):
                problems.append("missing required publication field %r" % f)
        if manifest.get("archive_or_export_sha256") is not None and not _is_sha256(manifest["archive_or_export_sha256"]):
            problems.append("archive_or_export_sha256 must be a full lowercase SHA-256")
        rc = _vh._as_int(manifest.get("record_count"), default=None)
        if manifest.get("record_count") is not None and rc is None:
            problems.append("record_count must be an integer")
        if rc is not None and n_records is not None and rc != n_records:
            problems.append("record_count %r != actual %r" % (rc, n_records))
        rr = manifest.get("raw_redistribution_status")
        if rr is not None and rr not in _REDIST_VOCAB:
            problems.append("raw_redistribution_status must be one of %s" % sorted(_REDIST_VOCAB))
        ap = manifest.get("aggregate_publication_status")
        if ap is not None and ap not in _AGG_VOCAB:
            problems.append("aggregate_publication_status must be one of %s" % sorted(_AGG_VOCAB))
        if ap == "prohibited":
            problems.append("aggregate_publication_status is prohibited: publication is not permitted")
    if problems:
        raise ExportManifestError("; ".join(problems))
    return {
        "profile": profile,
        "export_cutoff": cutoff,
        "publication_qualified": profile == "publication",
        "classification": "publication-source" if profile == "publication" else "rehearsal-source",
    }


def import_sanctioned_export(records, export_manifest, dst_dir, salt="import"):
    """Import a sanctioned export into a NEW empty store. Returns a summary dict. Writes shards,
    index, Bronze lineage, and a ``source_export_manifest.json`` (the coherence evidence that
    lets a publication freeze pass). Refuses a non-empty target and an export without a cutoff."""
    dst = Path(dst_dir)
    if dst.exists() and any(dst.iterdir()):
        raise FileExistsError("import target must be a NEW empty store: %s" % dst)
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

    man = dict(export_manifest)
    man.update({
        "export_spec_version": EXPORT_SPEC_VERSION,
        "export_cutoff": cutoff,
        "n_export_records": len(list(records)) if hasattr(records, "__len__") else None,
        "n_imported": len(tidy),
        "n_quarantined": len(quarantined),
        "n_excluded_after_cutoff": len(excluded),
        "importer_version": _vh._HARVEST_VERSION,
        "normalizer_schema_version": _vh._NORMALIZE_SCHEMA_VERSION,
        "bronze_schema_version": _vh._BRONZE_SCHEMA_VERSION,
    })
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
    manifest = {
        # legacy/spec-v1 fields (kept for continuity)
        "export_cutoff": cutoff,
        "source": "visualizer.coffee sanctioned export (synthetic fixture)",
        "export_created_at": cutoff,          # deterministic; a real export stamps wall-clock
        "license": "per Miha permission 2026-07-14; attribution + collective user credit",
        "privacy": "salted one-way user hash; free-text/PII dropped on import",
        # publication-profile governance record (synthetic-but-complete)
        "export_spec_version": EXPORT_SPEC_VERSION,
        "source_name": "visualizer.coffee",
        "source_authority": "Miha (visualizer.coffee maintainer) — synthetic fixture stand-in",
        "source_schema_version": 1,
        "record_count": len(records),
        "archive_or_export_sha256": "0" * 64,   # synthetic placeholder; a real export carries the real digest
        "stable_record_id_semantics": "opaque per-shot id; stable across the export",
        "record_version_semantics": "integer updated_at as the monotone version key",
        "user_linkage_semantics": "salted one-way per-user token; no reversible identity",
        "privacy_transform": "PII/free-text dropped on import; salted user hash",
        "rights_basis": "synthetic fixture; a real export must carry the authorised research-use basis",
        "raw_redistribution_status": "prohibited",
        "aggregate_publication_status": "permitted",
        "retention_policy": "synthetic; local-only; not retained beyond the rehearsal",
        "deletion_or_correction_policy": "synthetic; deletions/corrections re-exported by the source",
        "contact_record": "synthetic fixture; a real export records the authorising contact",
    }
    return records, manifest
