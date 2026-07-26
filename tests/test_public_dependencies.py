"""Public-claim dependency identity and scoped evidence (Paper 3 review, step 0 + P0-4 option b).

Before this, `PublicClaim.components` was a flat list of free text: of the 13 dependency edges
across the five public claims, only 2 resolved to a registry component id. The rest were prose
labels that conflated components, producer functions and datasets, so an output could not carry the
evidence relations of its dependencies -- the dependencies were not identified.

These tests hold the fix: every dependency must RESOLVE, and component dependencies must bring
their scoped evidence with them.
"""
import csv
import importlib
import pathlib

import pytest

import puckworks.models  # noqa: F401  (registers components)
from puckworks import registry as R
from puckworks.public import schema as PS
from puckworks.public.claims import PUBLIC_CLAIMS

_ROOT = pathlib.Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def manifest_ids():
    path = _ROOT / "puckworks/data/MANIFEST.csv"
    with path.open(newline="", encoding="utf-8") as fh:
        return {row["dataset_id"] for row in csv.DictReader(fh) if row.get("dataset_id")}


def _deps():
    return [(c.claim_id, d) for c in PUBLIC_CLAIMS for d in c.dependencies]


def test_every_claim_declares_dependencies():
    for c in PUBLIC_CLAIMS:
        assert c.dependencies, f"{c.claim_id} declares no dependencies"


def test_no_claim_validates_with_an_unresolvable_dependency():
    assert [e for c in PUBLIC_CLAIMS for e in c.validate()] == []


def test_component_dependencies_resolve_to_the_live_registry():
    ids = {c.name for c in R.components()}
    bad = [(cid, d.ref) for cid, d in _deps() if d.kind == "component" and d.ref not in ids]
    assert not bad, f"component dependencies not in the registry: {bad}"


def test_dataset_dependencies_resolve_to_the_manifest(manifest_ids):
    bad = [(cid, d.ref) for cid, d in _deps()
           if d.kind == "dataset" and d.ref not in manifest_ids]
    assert not bad, f"dataset dependencies not in MANIFEST.csv: {bad}"


def test_producer_dependencies_are_importable():
    bad = []
    for cid, d in _deps():
        if d.kind != "producer":
            continue
        mod, _, fn = d.ref.rpartition(".")
        try:
            assert callable(getattr(importlib.import_module(mod), fn))
        except Exception as exc:                       # noqa: BLE001
            bad.append((cid, d.ref, type(exc).__name__))
    assert not bad, f"producer dependencies not importable: {bad}"


def test_every_dependency_records_what_it_contributes():
    """A resolvable identifier with no role is still not a provenance record."""
    for cid, d in _deps():
        assert len(d.role.split()) >= 4, (cid, d.ref, d.role)


# --- scoped evidence (option b) ---------------------------------------------------------------
def test_component_dependencies_carry_scoped_evidence():
    """The point of the change: a component dependency brings its evidence records with it."""
    comps = [(cid, d) for cid, d in _deps() if d.kind == "component"]
    assert comps, "no component dependencies at all -- this guard would be vacuous"
    for cid, d in comps:
        assert d.evidence, f"{cid}: component {d.ref} carries no evidence records"
        for e in d.evidence:
            assert e.scope.strip() and e.scope != "(scope not recorded)", (cid, d.ref)
            assert e.gate, (cid, d.ref)


def test_producers_and_datasets_carry_no_evidence_relation():
    """A producer computes a value and a dataset supplies one; neither is a comparison against
    reality, so neither may carry an evidence relation."""
    for cid, d in _deps():
        if d.kind in ("producer", "dataset"):
            assert not d.evidence, f"{cid}: {d.kind} {d.ref} carries an evidence relation"


def test_the_evidence_profile_is_richer_than_the_single_label():
    """The scope-laundering fix, made checkable: at least one claim's profile spans more than one
    relation, which a single evidence_strength cannot express."""
    spans = {c.claim_id: {r["relation"] for r in c.evidence_profile()} for c in PUBLIC_CLAIMS}
    multi = {k: sorted(v) for k, v in spans.items() if len(v) > 1}
    assert multi, f"no claim has a multi-relation profile: {spans}"


def test_components_is_derived_and_deprecated_not_authoritative():
    """`components` survives for published artifacts, but the identified list is the real one."""
    for c in PUBLIC_CLAIMS:
        assert len(c.component_refs()) <= len(c.dependencies)
    src = (_ROOT / "puckworks/public/schema.py").read_text(encoding="utf-8")
    assert "DEPRECATED free-text list; use `dependencies`" in src


# --- relation / outcome separation ------------------------------------------------------------
def test_no_claim_uses_a_compound_relation_outcome_label():
    """'negative validation' fused a relation and an outcome. PV-03 previously carried it."""
    for c in PUBLIC_CLAIMS:
        assert c.evidence_strength not in PS.LEGACY_COMPOUND_RELATIONS, c.claim_id
        assert c.outcome in PS.PUBLIC_OUTCOMES, c.claim_id


def test_the_negative_result_is_still_reported_as_negative():
    """Decomposing the label must not quietly lose the negative finding."""
    negatives = [c.claim_id for c in PUBLIC_CLAIMS if c.outcome == "negative"]
    assert "PV-03" in negatives, negatives


def test_the_compound_label_is_rejected_if_reintroduced():
    """Non-vacuity: prove validate() catches the compound coming back."""
    import dataclasses as dc
    c = dc.replace(PUBLIC_CLAIMS[0], evidence_strength="negative validation")
    assert any("compound" in e for e in c.validate()), c.validate()


# --- the generated artifact had no freshness guard at all -------------------------------------
def test_the_generated_claims_artifact_is_current():
    """`docs/public/generated/claims.json` is a committed export that NOTHING checked. It was
    silently stale (missing `dependencies`, `outcome` and `evidence_profile`) until this test was
    added -- the same drift class the papers are about, in the papers' own repository."""
    import json

    path = _ROOT / "docs/public/generated/claims.json"
    assert path.exists(), path
    committed = json.loads(path.read_text(encoding="utf-8"))
    live = [c.to_dict() for c in PUBLIC_CLAIMS]
    assert len(committed) == len(live)

    def _strip(d):
        # commit stamps move on every export and are not part of the claim content; the JSON
        # round-trip also turns tuples into lists, so normalise both sides through JSON rather
        # than comparing Python containers of different types
        return json.loads(json.dumps(
            {k: v for k, v in d.items()
             if k not in ("source_commit", "generated_from_commit",
                          "last_verified_against_commit")}, default=str))

    for c, l in zip(sorted(committed, key=lambda x: x["claim_id"]),
                    sorted(live, key=lambda x: x["claim_id"])):
        assert _strip(c) == _strip(l), (
            f"{c['claim_id']}: docs/public/generated/claims.json is stale -- "
            f"run `python -c 'from puckworks.public import export as E; E.export()'`")


def test_the_generated_artifact_carries_the_new_fields():
    import json
    d = json.loads((_ROOT / "docs/public/generated/claims.json").read_text(encoding="utf-8"))
    for c in d:
        assert "dependencies" in c and c["dependencies"], c["claim_id"]
        assert "outcome" in c, c["claim_id"]
        assert "evidence_profile" in c, c["claim_id"]
