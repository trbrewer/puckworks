"""WP1 / PR2 — a VERIFIED publication-freeze lifecycle for the visualizer corpus.

A publication freeze must be an immutable, independently verifiable artifact — NOT a
classification string a caller can assign to an ordinary moving store. This module replaces
"``classification == 'publication-freeze'``" checks with a three-stage lifecycle whose only
route to publication status is a passing verification:

    freeze_rehearse(source)      -> FreezeCandidate   (read-only readiness + blockers)
    freeze_materialize(src, dst) -> materialized snapshot dir (canonical records + audit)
    freeze_verify(dst[, source]) -> PublicationReceipt (independent recompute + immutability)

Rules enforced here (WP1.2/1.5):
- The current EXPLORATORY moving public window (no coherent export cutoff) is REJECTED by the
  publication gate — it can be materialized only as ``current-state``.
- Materialization refuses to overwrite an existing snapshot and fails if the source mutates
  during the operation.
- A publication bundle requires a verified PublicationReceipt, not a label
  (see ``corpus_bundle.build_bundle``).
"""
from __future__ import annotations

import gzip
import hashlib
import json
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

from puckworks.lib import visualizer_harvest as _vh
from puckworks.data.visualizer_store import CorpusSnapshot

PUBLICATION = "publication-freeze"


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class FreezeCandidate:
    """Read-only readiness report over a specific source state. ``ready_for_publication`` is
    True only when ``blockers`` is empty; it can NEVER be forced by a caller."""
    source_dir: str
    ready_for_publication: bool
    blockers: tuple
    has_export_cutoff: bool
    reconcile_ok: bool
    integrity: dict
    n_quarantined: int
    source_aggregate_sha256: str


@dataclass(frozen=True)
class PublicationReceipt:
    """Result of an independent verification pass. ``qualifies_for_publication`` is True only
    when the materialized snapshot both verified AND was materialized as a publication-freeze."""
    snapshot_dir: str
    snapshot_id: str
    classification: str
    verified: bool
    problems: tuple
    manifest_sha256: str
    receipt_sha256: str

    @property
    def qualifies_for_publication(self) -> bool:
        return bool(self.verified and self.classification == PUBLICATION)


# ---------------------------------------------------------------------------------------------
# source-state hashing (immutability + coherence)
# ---------------------------------------------------------------------------------------------

def _source_files(source_dir: Path):
    """Deterministically ordered list of the source's identity-bearing files.

    Includes the data shards/index AND the governance/audit files that justify publication status, so
    a change to rights basis, aggregate-publication permission, contact, retention, quarantine, or
    exclusions changes the source aggregate digest.
    """
    pats = ("shard_*.jsonl.gz", "bronze_*.jsonl.gz")
    files = []
    for pat in pats:
        files.extend(sorted(source_dir.glob(pat)))
    for name in ("_index.csv", "source_export_manifest.json", "import_quarantine.json",
                 "import_exclusions.json"):
        f = source_dir / name
        if f.exists():
            files.append(f)
    return files


def _source_state(source_dir: Path) -> dict:
    """Per-file hashes + an order-independent aggregate digest of the source store."""
    per_file = {p.name: _vh._sha256_file(p) for p in _source_files(source_dir)}
    agg = _sha256_text(json.dumps(per_file, sort_keys=True))
    return {"files": per_file, "aggregate_sha256": agg}


def _export_manifest(source_dir: Path):
    """The sanctioned-export descriptor, if present. A coherent export carries a non-null
    ``export_cutoff``; a moving public-window crawl does not (WP1.5)."""
    p = source_dir / "source_export_manifest.json"
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None


# ---------------------------------------------------------------------------------------------
# stage A — rehearse (read-only)
# ---------------------------------------------------------------------------------------------

def freeze_rehearse(source_dir, as_of=None) -> FreezeCandidate:
    """Read-only readiness/blocker report. NEVER emits a publication-qualified artifact."""
    source_dir = Path(source_dir)
    snap = CorpusSnapshot(source_dir, name="rehearse", classification="current-state",
                          as_of=as_of)
    integ = snap.integrity_stats()
    recon = snap.reconcile()
    exp = _export_manifest(source_dir)
    manifest_present = (source_dir / "source_export_manifest.json").exists()
    manifest_malformed = manifest_present and exp is None
    has_cutoff = bool(exp and exp.get("export_cutoff") is not None)
    # a publication freeze requires a VALIDATED publication-profile source manifest, not merely a
    # non-null cutoff (rights, checksum, aggregate-publication permission, governance record).
    pub_problem = None
    from puckworks.data.corpus_export import ExportManifestError, validate_export_manifest
    try:
        validate_export_manifest(exp or {}, profile="publication")
    except ExportManifestError as _exc:
        pub_problem = str(_exc)

    blockers = []
    if not recon.get("ok"):
        # reconcile.ok already accounts for the store's bronze policy; a genuinely broken
        # store (e.g. a version missing from the index) fails here. A fully bronzeless store
        # is a policy choice, not a coherence failure, so bronze lineage is NOT blanket-blocked.
        blockers.append("reconcile not ok: %r" % ((recon.get("problems") or [])[:3]))
    if recon.get("n_quarantined"):
        blockers.append("unresolved quarantine: %d" % recon["n_quarantined"])
    if integ.get("n_missing_updated_at"):
        blockers.append("records missing updated_at (no time base): %d"
                        % integ["n_missing_updated_at"])
    if manifest_malformed:
        blockers.append("source_export_manifest.json is present but malformed/unreadable")
    if not has_cutoff:
        blockers.append("no coherent export cutoff — source is a moving feed, not an export "
                        "(sanctioned bulk export required for publication; WP1.5/WP7)")
    elif pub_problem is not None:
        blockers.append("export manifest fails the publication profile: %s" % pub_problem)

    return FreezeCandidate(
        source_dir=str(source_dir),
        ready_for_publication=not blockers,
        blockers=tuple(blockers),
        has_export_cutoff=has_cutoff,
        reconcile_ok=bool(recon.get("ok")),
        integrity=integ,
        n_quarantined=int(recon.get("n_quarantined") or 0),
        source_aggregate_sha256=_source_state(source_dir)["aggregate_sha256"],
    )


# ---------------------------------------------------------------------------------------------
# stage B — materialize
# ---------------------------------------------------------------------------------------------

def _conflicts(snap: CorpusSnapshot):
    """Ids whose versions share an updated_at with DIFFERING content (deterministic winner is
    still selected, but the conflict is materialized for audit)."""
    per_id = defaultdict(lambda: defaultdict(set))
    for rec in snap.iter_versions():
        per_id[rec.get("id")][_vh._as_int(rec.get("updated_at"), default=-1)].add(
            rec.get("content_sha256") or "")
    out = []
    for sid, by_ts in per_id.items():
        for ts, hashes in by_ts.items():
            if len(hashes) > 1:
                out.append({"id": sid, "updated_at": ts, "n_distinct_content": len(hashes)})
    return sorted(out, key=lambda r: (str(r["id"]), r["updated_at"]))


def freeze_materialize(source_dir, dst_dir, classification="current-state", as_of=None,
                       name="snapshot") -> dict:
    """Read a FIXED source state and write the canonical one-row-per-logical-record view plus
    audit/provenance to a NEW destination. Refuses to overwrite. For ``publication-freeze`` it
    requires a clean rehearsal (no blockers); otherwise it raises. Fails if the source mutates
    during materialization."""
    source_dir, dst = Path(source_dir), Path(dst_dir)
    if classification not in ("current-state", PUBLICATION):
        raise ValueError("materialize classification must be 'current-state' or %r" % PUBLICATION)
    if dst.exists() and any(dst.iterdir()):
        raise FileExistsError("refusing to overwrite an existing snapshot at %s" % dst)

    if classification == PUBLICATION:
        cand = freeze_rehearse(source_dir, as_of=as_of)
        if not cand.ready_for_publication:
            raise RuntimeError("source is NOT publication-ready; blockers: %s"
                               % "; ".join(cand.blockers))

    pre = _source_state(source_dir)                       # WP1.5 immutability: before
    snap = CorpusSnapshot(source_dir, name=name, classification=classification, as_of=as_of)

    dst.mkdir(parents=True, exist_ok=True)
    # canonical records — one row per logical record
    records = list(snap.latest())
    with gzip.open(dst / "canonical_records.jsonl.gz", "wt", encoding="utf-8") as fh:
        for rec in records:
            fh.write(json.dumps(rec, sort_keys=True, ensure_ascii=False) + "\n")
    # selected-version map + conflicts
    winners = _vh.latest_index_rows(snap._cfg, as_of=as_of)
    svm = sorted(
        ({"id": sid, "updated_at": r.get("updated_at"),
          "content_sha256": r.get("content_sha256") or "",
          "selection_reason": "max_updated_at,last_written_append_seq"}
         for sid, r in winners.items()), key=lambda r: str(r["id"]))
    (dst / "selected_version_map.json").write_text(
        json.dumps(svm, indent=2, sort_keys=True), encoding="utf-8")
    conflicts = _conflicts(snap)
    (dst / "version_conflicts.json").write_text(
        json.dumps(conflicts, indent=2, sort_keys=True), encoding="utf-8")

    post = _source_state(source_dir)                      # WP1.5 immutability: after
    if post["aggregate_sha256"] != pre["aggregate_sha256"]:
        raise RuntimeError("source mutated during materialization — snapshot is not coherent")

    # manifest = the read-view manifest augmented with materialization + immutability provenance
    manifest = snap.manifest()
    materialized = {p.name: _vh._sha256_file(p) for p in sorted(dst.glob("*"))
                    if p.name not in ("snapshot_manifest.json", "verification_receipt.json",
                                      "file_hashes.json", "DATA_CARD.md")}
    manifest.update({
        "classification": classification,
        "n_canonical_records": len(records),
        "n_version_conflicts": len(conflicts),
        "source_state_pre_sha256": pre["aggregate_sha256"],
        "source_state_post_sha256": post["aggregate_sha256"],
        "source_export_manifest": _export_manifest(source_dir),
        "materialized_file_hashes": materialized,
    })
    manifest["snapshot_id"] = _sha256_text(json.dumps(
        {"manifest_sha256": manifest["manifest_sha256"], "materialized": materialized,
         "classification": classification}, sort_keys=True))
    (dst / "snapshot_manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    (dst / "file_hashes.json").write_text(
        json.dumps(materialized, indent=2, sort_keys=True), encoding="utf-8")
    (dst / "DATA_CARD.md").write_text(
        _data_card(manifest, classification), encoding="utf-8")
    return manifest


def _data_card(manifest, classification):
    tag = ("PUBLICATION FREEZE — immutable, verified snapshot" if classification == PUBLICATION
           else "EXPLORATORY — NOT A PUBLICATION SNAPSHOT (moving-window materialization)")
    return (f"# Corpus snapshot — {classification}\n\n**{tag}**\n\n"
            f"- snapshot_id: `{manifest.get('snapshot_id')}`\n"
            f"- canonical records: {manifest.get('n_canonical_records')}\n"
            f"- version conflicts (same-ts, differing content): {manifest.get('n_version_conflicts')}\n"
            f"- source aggregate hash: `{manifest.get('source_state_post_sha256')}`\n"
            f"- reconcile ok: {manifest.get('reconcile_ok')}\n\n"
            "Verify with `corpus_freeze.freeze_verify(<dir>[, source_dir])`.\n")


# ---------------------------------------------------------------------------------------------
# stage C — verify (independent recompute)
# ---------------------------------------------------------------------------------------------

def freeze_verify(dst_dir, source_dir=None) -> PublicationReceipt:
    """Independently recompute hashes/counts and (optionally) confirm the source did not mutate
    since materialization. Writes ``verification_receipt.json`` and returns a receipt whose
    ``qualifies_for_publication`` is True only for a verified publication-freeze."""
    dst = Path(dst_dir)
    manifest = json.loads((dst / "snapshot_manifest.json").read_text(encoding="utf-8"))
    problems = []

    # 1. materialized file hashes match what the manifest recorded
    recorded = manifest.get("materialized_file_hashes") or {}
    for name, h in recorded.items():
        p = dst / name
        if not p.exists():
            problems.append("missing materialized file: %s" % name)
        elif _vh._sha256_file(p) != h:
            problems.append("materialized file mutated: %s" % name)
    # 2. canonical record count matches (guarded: a corrupted file is a problem, not a crash)
    cr = dst / "canonical_records.jsonl.gz"
    if cr.exists():
        try:
            with gzip.open(cr, "rt", encoding="utf-8") as fh:
                n = sum(1 for _ in fh)
            if n != manifest.get("n_canonical_records"):
                problems.append("canonical record count mismatch: %d vs %s"
                                % (n, manifest.get("n_canonical_records")))
        except Exception as exc:
            problems.append("canonical_records unreadable: %s" % exc)
    else:
        problems.append("missing canonical_records.jsonl.gz")
    # 3. immutability: source unchanged since materialization
    if source_dir is not None:
        now = _source_state(Path(source_dir))["aggregate_sha256"]
        if now != manifest.get("source_state_post_sha256"):
            problems.append("source has mutated since materialization")

    verified = not problems
    receipt = {
        "snapshot_id": manifest.get("snapshot_id"),
        "classification": manifest.get("classification"),
        "verified": verified,
        "problems": problems,
        "manifest_sha256": manifest.get("manifest_sha256"),
        "n_canonical_records": manifest.get("n_canonical_records"),
    }
    receipt_sha = _sha256_text(json.dumps(receipt, sort_keys=True))
    receipt["receipt_sha256"] = receipt_sha
    (dst / "verification_receipt.json").write_text(
        json.dumps(receipt, indent=2, sort_keys=True), encoding="utf-8")
    return PublicationReceipt(
        snapshot_dir=str(dst), snapshot_id=manifest.get("snapshot_id"),
        classification=manifest.get("classification") or "", verified=verified,
        problems=tuple(problems), manifest_sha256=manifest.get("manifest_sha256") or "",
        receipt_sha256=receipt_sha)
