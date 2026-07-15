"""Canonical, deduplicated read interface + freeze contract for the visualizer corpus store.

WP0 / PR1 of the corpus-integrity plan (2026-07-15). Analysis code MUST consume a
``CorpusSnapshot`` — never the raw shard iterator ``visualizer_harvest.iter_store`` — so that
deduplication, version semantics, the measurement dictionary, and freeze status are always
explicit. A snapshot is one of three classifications:

    exploratory-window   : the moving recent-public window; NOT a coherent point-in-time
    current-state        : latest-version-per-id as of read time; still moving
    publication-freeze   : an immutable, manifested, hashed snapshot for paper-grade work

The store primitives (shards, index, content-addressed version keys, latest view,
reconciliation) live in ``puckworks.lib.visualizer_harvest``; this module is the typed,
guard-railed layer on top.
"""

from __future__ import annotations

import hashlib
import json
from collections import defaultdict
from pathlib import Path
from types import SimpleNamespace

from puckworks.lib import visualizer_harvest as _vh

CLASSIFICATIONS = ("exploratory-window", "current-state", "publication-freeze")


# --- P1 minimum measurement dictionary (first tranche) --------------------------------------
# One entry per channel the first analyses touch. `commanded=True` marks a goal/setpoint
# (commanded) channel vs an achieved measurement; `ambiguity` names an unresolved quantity
# kind; `eligibility` names the coarsest analysis tier the channel may enter. A channel whose
# canonical_unit is None is NOT an SI quantity and must never be pooled onto a physical axis.
MEASUREMENT_DICTIONARY = {
    "time__s": {
        "source_field": "timeframe", "quantity_kind": "time",
        "raw_unit": "s", "canonical_unit": "s", "sensor": "clock",
        "commanded": False, "ambiguity": None, "eligibility": "core",
    },
    "pressure__Pa": {
        "source_field": "espresso_pressure", "quantity_kind": "pressure",
        "raw_unit": "bar", "canonical_unit": "Pa", "sensor": "machine_pressure",
        "commanded": False, "ambiguity": None, "eligibility": "pressure_tracking",
    },
    "pressure_goal__Pa": {
        "source_field": "espresso_pressure_goal", "quantity_kind": "pressure",
        "raw_unit": "bar", "canonical_unit": "Pa", "sensor": "machine_setpoint",
        "commanded": True, "ambiguity": None, "eligibility": "pressure_tracking",
    },
    "mass_flow_from_scale__kg_per_s": {
        "source_field": "espresso_flow_weight", "quantity_kind": "mass_flow",
        "raw_unit": "g/s", "canonical_unit": "kg/s", "sensor": "scale_derived",
        "commanded": False, "ambiguity": None, "eligibility": "mass_flow_tracking",
    },
    "flow_reported__native": {
        "source_field": "espresso_flow", "quantity_kind": "flow_UNRESOLVED",
        "raw_unit": "native", "canonical_unit": None, "sensor": "machine_estimate",
        "commanded": False, "ambiguity": "volumetric_or_mass_or_proxy",
        "eligibility": "exploratory_proxy_flow",
    },
    "flow_goal_reported__native": {
        "source_field": "espresso_flow_goal", "quantity_kind": "flow_UNRESOLVED",
        "raw_unit": "native", "canonical_unit": None, "sensor": "machine_setpoint",
        "commanded": True, "ambiguity": "volumetric_or_mass_or_proxy",
        "eligibility": "exploratory_proxy_flow",
    },
    "weight__kg": {
        "source_field": "espresso_weight", "quantity_kind": "cumulative_mass",
        "raw_unit": "g", "canonical_unit": "kg", "sensor": "scale",
        "commanded": False, "ambiguity": None, "eligibility": "weight_tracking",
    },
    "state_change": {
        "source_field": "espresso_state_change", "quantity_kind": "categorical_state",
        "raw_unit": "code", "canonical_unit": "code", "sensor": "machine_state",
        "commanded": False, "ambiguity": None, "eligibility": "metadata",
    },
}


def measurement_dictionary():
    """Return a deep copy of the P1 measurement dictionary (safe to mutate)."""
    return {k: dict(v) for k, v in MEASUREMENT_DICTIONARY.items()}


def is_pooling_safe(channel):
    """True only if `channel` is a resolved SI quantity that may enter a physical-axis
    analysis. Ambiguous / native flow channels return False (P0.4 guardrail)."""
    entry = MEASUREMENT_DICTIONARY.get(channel)
    return bool(entry and entry.get("canonical_unit") and not entry.get("ambiguity"))


def _as_int(x, default=None):
    return _vh._as_int(x, default=default)


class CorpusSnapshot:
    """Canonical read interface over a visualizer store directory. Deduplicates to one
    logical record per shot id (max ``updated_at``, ties → last-written), exposes version
    history separately, and reports revision/conflict/missing-timestamp counts."""

    def __init__(self, out_dir, name="unnamed", classification="exploratory-window",
                 as_of=None):
        if classification not in CLASSIFICATIONS:
            raise ValueError("classification must be one of %r" % (CLASSIFICATIONS,))
        self.out_dir = Path(out_dir)
        self.name = name
        self.classification = classification
        self.as_of = as_of              # optional int cutoff: only versions with updated_at<=as_of
        self._cfg = SimpleNamespace(out_dir=self.out_dir)

    # -- reading -----------------------------------------------------------------------------
    def iter_versions(self):
        """Yield every stored VERSION (append-only history) — for audit/lineage work only."""
        for rec in _vh.iter_store(self._cfg):
            if self.as_of is None or _as_int(rec.get("updated_at"), default=-1) <= self.as_of:
                yield rec

    def latest(self):
        """Yield exactly one logical record per shot id: the latest version (P0.1). When
        ``as_of`` is set, the latest version at or before that cutoff."""
        if self.as_of is None:
            yield from _vh.iter_store_latest(self._cfg)
            return
        # as_of cutoff: recompute the winner per id over the bounded history
        winners = {}       # id -> (updated_at, content_sha256, record)
        for rec in self.iter_versions():
            sid = rec.get("id")
            key = (_as_int(rec.get("updated_at"), default=-1), rec.get("content_sha256") or "")
            prev = winners.get(sid)
            if prev is None or key >= prev[0]:
                winners[sid] = (key, rec)
        for _, rec in winners.values():
            yield rec

    # -- integrity ---------------------------------------------------------------------------
    def integrity_stats(self):
        """Deduplication / version diagnostics computed from the index: logical-record count,
        stored-version count, revisions (ids with >1 distinct version), conflicts (same
        (id, updated_at) with differing content), and records missing updated_at."""
        per_id = defaultdict(list)         # id -> [(updated_at, content_sha256)]
        n_versions = n_missing_updated = 0
        for row in _vh.iter_index_rows(self._cfg):
            sid = row.get("id")
            u_raw = row.get("updated_at")
            u = _as_int(u_raw, default=None)
            if self.as_of is not None and u is not None and u > self.as_of:
                continue
            n_versions += 1
            if u is None:
                n_missing_updated += 1
            per_id[sid].append((u if u is not None else -1, row.get("content_sha256") or ""))
        n_revisions = 0
        n_conflicts = 0
        for versions in per_id.values():
            if len(set(versions)) > 1:
                n_revisions += 1
            by_ts = defaultdict(set)
            for ts, h in versions:
                by_ts[ts].add(h)
            n_conflicts += sum(1 for hashes in by_ts.values() if len(hashes) > 1)
        return {
            "n_logical_records": len(per_id),
            "n_stored_versions": n_versions,
            "n_revisions": n_revisions,
            "n_same_timestamp_conflicts": n_conflicts,
            "n_missing_updated_at": n_missing_updated,
        }

    def reconcile(self):
        """Store integrity report (delegates to the harvester reconciler)."""
        return _vh.reconcile_store(self._cfg)

    # -- manifest ----------------------------------------------------------------------------
    def manifest(self, cutoff=None, collection_start=None, collection_end=None):
        """Build a DETERMINISTIC snapshot manifest (no wall-clock reads): store identity,
        integrity counts, per-shard hashes, and a content digest over the whole manifest. Any
        collection-window fields must be passed in (they come from run manifests, not now())."""
        integ = self.integrity_stats()
        recon = self.reconcile()
        shards = []
        for p in sorted(self.out_dir.glob("shard_*.jsonl.gz")):
            shards.append({"name": p.name, "sha256": _vh._sha256_file(p)})
        index_path = self.out_dir / "_index.csv"
        body = {
            "snapshot_name": self.name,
            "classification": self.classification,
            "as_of": self.as_of,
            "cutoff": cutoff,
            "collection_start": collection_start,
            "collection_end": collection_end,
            "store_schema_version": _vh._NORMALIZE_SCHEMA_VERSION,
            "bronze_schema_version": _vh._BRONZE_SCHEMA_VERSION,
            "harvest_version": _vh._HARVEST_VERSION,
            "harvester_commit": _vh._git_commit(),
            "normalizer_source_sha256": _vh._normalizer_source_sha256(),
            "measurement_dictionary_channels": sorted(MEASUREMENT_DICTIONARY),
            "integrity": integ,
            "reconcile_ok": recon["ok"],
            "reconcile_problems": recon["problems"],
            "n_bronze": recon["n_bronze"],
            "n_norm_without_bronze": recon.get("n_norm_without_bronze"),
            "n_quarantined": recon["n_quarantined"],
            "index_sha256": _vh._sha256_file(index_path) if index_path.exists() else None,
            "shards": shards,
        }
        blob = json.dumps(body, sort_keys=True, ensure_ascii=False)
        body["manifest_sha256"] = hashlib.sha256(blob.encode("utf-8")).hexdigest()
        return body


def freeze_snapshot(out_dir, name, dst_path, classification="publication-freeze",
                    as_of=None, cutoff=None, collection_start=None, collection_end=None):
    """Write a deterministic snapshot manifest JSON to `dst_path` and return it. This is the
    freeze contract: a paper-grade snapshot must be built with classification
    'publication-freeze' AND against a store that no longer mutates. Returns the manifest."""
    snap = CorpusSnapshot(out_dir, name=name, classification=classification, as_of=as_of)
    manifest = snap.manifest(cutoff=cutoff, collection_start=collection_start,
                             collection_end=collection_end)
    dst = Path(dst_path)
    dst.parent.mkdir(parents=True, exist_ok=True)
    with open(dst, "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, sort_keys=True, indent=2)
    return manifest
