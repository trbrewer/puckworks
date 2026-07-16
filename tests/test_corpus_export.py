"""WP1.7 / PR3 — a synthetic sanctioned export runs the COMPLETE pipeline end to end:
import -> reconcile -> rehearse -> materialize -> verify -> bundle, exercising revisions,
equal-timestamp conflicts, missing channels, source families, quarantine, and post-cutoff
exclusion.
"""
import json

import pytest

from puckworks.data import corpus_export as ce
from puckworks.data import corpus_freeze as cf
from puckworks.data import visualizer_store as vs
from puckworks.analysis import corpus_bundle


def test_synthetic_export_end_to_end(tmp_path):
    records, manifest = ce.synthetic_export(cutoff=1000)
    store = tmp_path / "store"
    summary = ce.import_sanctioned_export(records, manifest, store)

    # adversarial cases handled: one quarantined (bad data), one excluded (post-cutoff)
    assert summary["n_quarantined"] == 1
    assert summary["n_excluded_after_cutoff"] == 1
    # logical records: normal1, rev1 (1 logical), conflict1 (1 logical), presonly, srcB = 5
    snap = vs.CorpusSnapshot(store, name="imp", classification="current-state")
    ids = {r["id"] for r in snap.latest()}
    assert ids == {"normal1", "rev1", "conflict1", "presonly", "srcB"}
    # the rev1 winner is the later updated_at (220), the conflict winner is last-written (9 bar)
    latest = {r["id"]: r for r in snap.latest()}
    assert latest["rev1"]["hydraulic"]["pressure__Pa"][-1] == pytest.approx(9.0e5)
    assert latest["conflict1"]["hydraulic"]["pressure__Pa"][0] == pytest.approx(9.0e5)

    # a coherent export IS publication-ready (has export_cutoff, reconciles clean)
    cand = cf.freeze_rehearse(store)
    assert cand.reconcile_ok and cand.has_export_cutoff
    assert cand.ready_for_publication is True, cand.blockers

    # materialize -> verify -> a qualifying receipt
    snap_dir = tmp_path / "snap"
    man = cf.freeze_materialize(store, snap_dir, classification="publication-freeze", name="pub")
    assert man["n_canonical_records"] == 5
    # the equal-timestamp conflict is materialized for audit
    conflicts = json.loads((snap_dir / "version_conflicts.json").read_text())
    assert any(c["id"] == "conflict1" for c in conflicts)
    receipt = cf.freeze_verify(snap_dir, source_dir=store)
    assert receipt.qualifies_for_publication is True

    # the verified receipt unlocks a publication bundle
    bundle = corpus_bundle.build_bundle(snap, require_freeze=True, receipt=receipt)
    assert bundle["exploratory"] is False
    assert bundle["publication_receipt_sha256"] == receipt.receipt_sha256


def test_import_requires_cutoff_and_empty_target(tmp_path):
    records, manifest = ce.synthetic_export()
    # missing cutoff -> refused
    with pytest.raises(ValueError, match="export_cutoff"):
        ce.import_sanctioned_export(records, {"source": "x"}, tmp_path / "a")
    # non-empty target -> refused
    store = tmp_path / "b"
    ce.import_sanctioned_export(records, manifest, store)
    with pytest.raises(FileExistsError):
        ce.import_sanctioned_export(records, manifest, store)


def test_import_is_deterministic(tmp_path):
    records, manifest = ce.synthetic_export()
    a = ce.import_sanctioned_export(records, manifest, tmp_path / "a")
    b = ce.import_sanctioned_export(records, manifest, tmp_path / "b")
    assert a == b
    # identical canonical view from two independent imports
    la = {r["id"] for r in vs.CorpusSnapshot(tmp_path / "a").latest()}
    lb = {r["id"] for r in vs.CorpusSnapshot(tmp_path / "b").latest()}
    assert la == lb
