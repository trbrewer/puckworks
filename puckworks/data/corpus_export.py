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
        "export_cutoff": cutoff,
        "source": "visualizer.coffee sanctioned export (synthetic fixture)",
        "export_created_at": cutoff,          # deterministic; a real export stamps wall-clock
        "license": "per Miha permission 2026-07-14; attribution + collective user credit",
        "privacy": "salted one-way user hash; free-text/PII dropped on import",
    }
    return records, manifest
