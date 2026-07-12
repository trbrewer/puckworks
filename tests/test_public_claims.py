"""Structural guardrails for the public-claim registry (PV-00 §5.5).

These are FAST integrity checks on the public layer — NOT physics gates and NOT in
run_all_gates(). They fail when a public claim would violate a PUBLIC_VALUE.md §3
guardrail: a number without a unit, a missing/invalid evidence-strength tag, a
missing badge, a dataset id absent from the manifest, a hard-coded number (no
Producer), or a grinder-dial comparison with no non-portability warning. Fast
Producers are regenerated and checked against their snapshots (the staleness
guard); slow Producers are skipped here.
"""
import csv
import os

import pytest

from puckworks.public import PUBLIC_CLAIMS, BADGES, EVIDENCE_STRENGTHS
from puckworks.public.export import regenerate

_MANIFEST = os.path.join(os.path.dirname(__file__), "..", "puckworks", "data",
                         "MANIFEST.csv")


def _manifest_ids():
    with open(_MANIFEST) as f:
        return {row[0].strip() for row in csv.reader(f) if row}


ALL = pytest.mark.parametrize("c", PUBLIC_CLAIMS, ids=[c.claim_id for c in PUBLIC_CLAIMS])


@ALL
def test_claim_passes_structural_guardrails(c):
    """(1) unit, (2) strength tag, (3) badge, (5) no hard-coded number,
    (6) dial-portability — all enforced by PublicClaim.validate()."""
    errs = c.validate()
    assert errs == [], "; ".join(errs)


@ALL
def test_badge_and_strength_in_vocabulary(c):
    assert c.badge in BADGES
    assert c.evidence_strength in EVIDENCE_STRENGTHS


@ALL
def test_every_number_has_a_unit(c):
    for k in c.numeric_result:
        assert c.units.get(k), f"{c.claim_id}: '{k}' missing unit"


@ALL
def test_every_number_is_producer_generated(c):
    # a public number with no Producer path is a hard-coded number -> forbidden
    for k in c.numeric_result:
        assert k in c.producer.result_map, f"{c.claim_id}: '{k}' hard-coded"


@ALL
def test_dataset_ids_exist_in_manifest(c):
    ids = _manifest_ids()
    for did in c.dataset_manifest_ids:
        assert did in ids, f"{c.claim_id}: dataset '{did}' not in MANIFEST.csv"


def test_claim_ids_unique():
    ids = [c.claim_id for c in PUBLIC_CLAIMS]
    assert len(ids) == len(set(ids))


def test_fast_producers_regenerate_matching_snapshots():
    """Regenerate every FAST claim number from its Producer; a snapshot that no
    longer matches the live harness result is drift the card must be refreshed for
    (this is the guard that a revised scientific result invalidates a stale card)."""
    _, drift = regenerate(run_slow=False)
    assert drift == [], f"stale public snapshots: {drift}"
