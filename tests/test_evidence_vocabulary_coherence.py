"""Cross-schema evidence-vocabulary coherence (Paper 3 review P0-2/P0-3/P0-4).

Three vocabularies describe evidence in this repository -- the component registry, the evidence
graph, and the public claim surface -- and they are NOT the same list. That is defensible (the
public surface is deliberately coarser), but it was implied rather than stated: `public/schema.py`
claimed its vocabulary "rides along UNCHANGED" from the registry, which was false.

These tests make the relationship explicit and enforceable: every registry relation must map to a
public term, no vocabulary may drift without the mapping being updated, and the manuscript must not
describe the evidence model in ways the implementation contradicts.
"""
import json
import pathlib
import re

import pytest

import puckworks.models  # noqa: F401  (registers components)
from puckworks import registry as R
from puckworks.paper3 import evidence_graph as EG
from puckworks.public import schema as PS

_ROOT = pathlib.Path(__file__).resolve().parents[1]
_MANUSCRIPT = (_ROOT / "docs/PAPER_3_PUCKWORKS_DRAFT.md").read_text(encoding="utf-8")


def test_every_registry_relation_maps_to_a_public_term():
    """No registry relation may exist with no public rendering -- that is how a component becomes
    unpresentable, or worse, silently presented under someone else's label."""
    missing = set(R.EVIDENCE_STRENGTHS) - set(PS.REGISTRY_TO_PUBLIC)
    assert not missing, f"registry relations with no public mapping: {sorted(missing)}"


def test_the_mapping_only_targets_real_public_terms():
    bad = {k: v for k, v in PS.REGISTRY_TO_PUBLIC.items() if v not in PS.EVIDENCE_STRENGTHS}
    assert not bad, f"mapping targets terms the public vocabulary does not define: {bad}"


def test_the_mapping_never_upgrades_evidence():
    """A coarser public label must not read STRONGER than the registry relation it renders.
    `independent` is the strongest public term, so only the two genuinely independent registry
    relations may map to it."""
    allowed_independent = {"controlled_independent", "within_campaign_held_out"}
    upgraded = {k for k, v in PS.REGISTRY_TO_PUBLIC.items()
                if v == "independent" and k not in allowed_independent}
    assert not upgraded, f"public label 'independent' would overstate: {sorted(upgraded)}"


def test_negative_validation_is_an_outcome_not_a_relation():
    """P0-2: 'reject negative validation as an evidence relation'. The manuscript already says a
    negative result is a failed OUTCOME on some relation, not a relation of its own. It survives
    only as a documented legacy compound, and must decompose."""
    assert "negative validation" in PS.LEGACY_COMPOUND_RELATIONS
    d = PS.LEGACY_COMPOUND_RELATIONS["negative validation"]
    assert d["relation"] in PS.EVIDENCE_STRENGTHS
    assert d["outcome"] in PS.PUBLIC_OUTCOMES and d["outcome"] == "negative"
    # and it must never become a registry relation
    assert "negative_validation" not in R.EVIDENCE_STRENGTHS
    assert "negative validation" not in R.EVIDENCE_STRENGTHS


def test_evidence_graph_relations_are_disjoint_from_registry_relations_by_design():
    """The graph's `relationship` answers a DIFFERENT question (fit/eval relationship) from the
    registry's `evidence_strength` (comparison relation). Conflating them is the P0-2 failure, so
    pin that they are genuinely different vocabularies rather than accidental near-duplicates."""
    assert set(EG.RELATIONSHIPS) != set(R.EVIDENCE_STRENGTHS)
    assert "code_verification" in EG.RELATIONSHIPS      # the one deliberate overlap
    assert "not_empirical" in EG.RELATIONSHIPS


def test_manuscript_does_not_claim_four_independent_axes():
    """P0-3: the badge is DERIVED from the other three, so 'four independent axes' is inaccurate,
    and 'independent' risks implying statistical independence."""
    assert "four independent axes" not in _MANUSCRIPT
    assert "three separate authored fields" in _MANUSCRIPT
    assert "derived, not authored" in _MANUSCRIPT


def test_manuscript_states_the_rollup_is_a_release_check_not_the_evidence_model():
    """P0-4: the implementation orders relations for a release check while the paper argues they
    are non-ordinal. The paper must acknowledge and bound that, including the scope-laundering
    limitation, rather than leaving the two in apparent contradiction."""
    assert "release heuristic" in _MANUSCRIPT
    assert "launder" in _MANUSCRIPT
    assert "scoped evidence profile" in _MANUSCRIPT


def test_the_rollup_probe_documents_itself_as_a_release_check():
    src = (_ROOT / "puckworks/paper3/evidence_graph.py").read_text(encoding="utf-8")
    assert "CONSERVATIVE RELEASE CHECK -- not the evidence model" in src
    assert "LAUNDER SCOPE" in src


def test_the_public_schema_no_longer_claims_an_unchanged_vocabulary():
    src = (_ROOT / "puckworks/public/schema.py").read_text(encoding="utf-8")
    assert "rides along UNCHANGED into public." not in src
    assert "DELIBERATELY COARSER" in src
    # and the per-field comment must not repeat the same false claim
    assert "(UNCHANGED from source)" not in src
