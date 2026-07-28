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
                          "last_verified_against_commit", "payload_sha256")}, default=str))

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


# ── unscoped component dependencies must fail closed (Paper 3 fourth review P0-3) ─────────────
def _unscoped_claim():
    """A minimal component-dependent claim with NO evidence selections."""
    import dataclasses

    from puckworks.public.claims import PUBLIC_CLAIMS

    proto = PUBLIC_CLAIMS[0]
    dep = next(d for c in PUBLIC_CLAIMS for d in c.dependencies if d.kind == "component")
    return dataclasses.replace(proto, claim_id="TEST-unscoped", dependencies=(dep,),
                               evidence_selections=()), dep


def test_a_component_dependent_claim_with_no_selection_fails_validation():
    """The review's counterexample, pinned.

    `validate()` only ran the load-bearing-coverage check inside `if self.evidence_selections`, so
    the single case where inheritance actually happened -- a claim with NO selections -- skipped it
    entirely. Such a claim validated cleanly and exposed its component's whole evidence inventory.
    """
    claim, dep = _unscoped_claim()
    errs = claim.validate()
    assert any("load-bearing but no evidence is selected" in e for e in errs), (
        f"an unscoped component dependency validated cleanly; errors were {errs}")
    assert any(dep.ref in e for e in errs)


def test_evidence_profile_never_falls_back_to_the_inventory():
    """`evidence_profile()` means SELECTED evidence, always.

    It returned the full inventory whenever selections were empty -- under a field name that a
    consumer reads as "this claim's support". An unscoped claim must have an EMPTY profile, not an
    inherited one, even though its inventory is non-empty.
    """
    claim, _dep = _unscoped_claim()
    assert claim.evidence_inventory(), "the fixture must have inventory for this test to mean anything"
    assert claim.evidence_profile() == (), (
        "evidence_profile() inherited the component inventory for an unscoped claim")
    assert claim.evidence_profile() == claim.selected_evidence()


def test_context_only_roles_are_the_only_exemption_and_must_be_declared():
    """A dependency may skip selection only by explicitly declaring itself non-licensing."""
    import dataclasses

    from puckworks.public import schema as S

    claim, dep = _unscoped_claim()
    assert S.CONTEXT_ONLY_ROLES, "there must be an explicit, enumerable exemption"
    for role in S.CONTEXT_ONLY_ROLES:
        assert role not in S.LICENSING_ROLES, (
            f"{role!r} is both a licensing role and a context-only exemption")
        exempt = dataclasses.replace(claim, dependencies=(dataclasses.replace(dep, role=role),))
        assert not any("load-bearing but no evidence is selected" in e
                       for e in exempt.validate()), (
            f"declaring role={role!r} did not exempt the dependency")


def test_every_shipped_claim_still_validates_under_the_stricter_rule():
    from puckworks.public.claims import PUBLIC_CLAIMS

    bad = [(c.claim_id, e) for c in PUBLIC_CLAIMS for e in c.validate()]
    assert not bad, bad


# ── persistent commit provenance (Paper 3 fourth review P0-8) ─────────────────────────────────
def test_generation_commit_survives_a_fresh_process_when_the_payload_is_unchanged():
    """`generated_from_commit` must be read back from the artifact, not reset to HEAD every run.

    It was stamped only `if c.generated_from_commit is None` -- but claims are rebuilt from source
    in every fresh process, where it is always `None`. "Immutable" therefore held only inside one
    Python object's lifetime, and each export silently re-dated the generation commit.

    Driven end to end: export at a pretend old commit, then re-export at a new one and require the
    generation commit to be preserved while the verification commit moves.
    """
    import json
    import tempfile
    from pathlib import Path

    from puckworks.public import export as E

    with tempfile.TemporaryDirectory() as td:
        real = E._source_commit
        try:
            E._source_commit = lambda: "aaaaaaaaaaaa"
            E.export(out_dir=td)
            first = json.loads((Path(td) / "claims.json").read_text())
            E._source_commit = lambda: "bbbbbbbbbbbb"
            E.export(out_dir=td)
            second = json.loads((Path(td) / "claims.json").read_text())
        finally:
            E._source_commit = real

    rows1 = {r["claim_id"]: r for r in (first["claims"] if isinstance(first, dict) else first)}
    rows2 = {r["claim_id"]: r for r in (second["claims"] if isinstance(second, dict) else second)}
    assert rows1 and rows1.keys() == rows2.keys()
    for cid, r2 in rows2.items():
        assert r2["payload_sha256"] == rows1[cid]["payload_sha256"], "payload changed unexpectedly"
        assert r2["generated_from_commit"] == "aaaaaaaaaaaa", (
            f"{cid}: generation commit was reset to HEAD by a fresh process")
        assert r2["last_verified_against_commit"] == "bbbbbbbbbbbb", (
            f"{cid}: verification commit did not advance")


def test_a_changed_payload_starts_a_new_generation():
    """Carrying the generation commit forward is conditional on payload identity, not automatic."""
    import json
    import tempfile
    from pathlib import Path

    from puckworks.public import export as E

    with tempfile.TemporaryDirectory() as td:
        real = E._source_commit
        try:
            E._source_commit = lambda: "aaaaaaaaaaaa"
            E.export(out_dir=td)
            path = Path(td) / "claims.json"
            data = json.loads(path.read_text())
            rows = data["claims"] if isinstance(data, dict) else data
            # Perturb the stored payload hash: the next export must treat it as a new generation.
            rows[0]["payload_sha256"] = "0" * 64
            path.write_text(json.dumps(data))
            E._source_commit = lambda: "bbbbbbbbbbbb"
            E.export(out_dir=td)
            after = json.loads(path.read_text())
        finally:
            E._source_commit = real

    changed = (after["claims"] if isinstance(after, dict) else after)[0]
    assert changed["generated_from_commit"] == "bbbbbbbbbbbb", (
        "a payload whose recorded hash did not match kept its old generation commit")


def test_the_payload_hash_ignores_provenance_stamps():
    """Re-verifying at a new commit must not change the hash, or nothing could ever be carried."""
    import dataclasses

    from puckworks.public import export as E
    from puckworks.public.claims import PUBLIC_CLAIMS

    c = PUBLIC_CLAIMS[0]
    restamped = dataclasses.replace(c, generated_from_commit="x" * 12,
                                    last_verified_against_commit="y" * 12,
                                    source_commit="z" * 12)
    assert E.payload_hash(c) == E.payload_hash(restamped)

    moved = dataclasses.replace(c, headline=c.headline + " (edited)")
    assert E.payload_hash(c) != E.payload_hash(moved), "the hash ignores the claim's own content"


# ── the public relation must be supported by the selection (Paper 3 fourth review P0-4) ───────
def test_authoring_a_stronger_relation_than_the_selection_supports_fails():
    """The review's counterexample: `independent` authored over a `code_verification` selection.

    `validate()` checked vocabulary membership only, so any term in the list passed regardless of
    what the claim actually selected.
    """
    import dataclasses

    from puckworks.public.claims import PUBLIC_CLAIMS

    # A claim whose selection genuinely caps the relation.
    base = next(c for c in PUBLIC_CLAIMS
                if any(s.role_in_claim == "produces_reported_value"
                       for s in c.evidence_selections))
    from puckworks.public import schema as S
    cap = S.strongest_supported_relation(base)
    assert cap, "fixture must have a capping selection"

    stronger = [r for r in S._PUBLIC_RELATION_ORDER
                if S._PUBLIC_RELATION_ORDER.index(r) > S._PUBLIC_RELATION_ORDER.index(cap)]
    assert stronger, "fixture's cap is already the strongest relation"
    over = dataclasses.replace(base, claim_id="TEST-over", evidence_strength=stronger[-1])
    assert any("stronger than the selected licensing evidence supports" in e
               for e in over.validate()), (
        f"authoring {stronger[-1]!r} over a {cap!r} selection validated cleanly")

    # Stating the supported relation, or anything weaker, is fine.
    ok = dataclasses.replace(base, claim_id="TEST-ok", evidence_strength=cap)
    assert not any("stronger than the selected" in e for e in ok.validate())


def test_same_campaign_holdout_is_not_published_as_independent():
    """The lossy public mapping collapsed a real evaluation-design distinction.

    `controlled_independent` and `within_campaign_held_out` both mapped to `independent`, which
    reverses the manuscript's own argument at the presentation layer.
    """
    from puckworks.public import schema as S

    assert S.REGISTRY_TO_PUBLIC["controlled_independent"] == "independent"
    assert S.REGISTRY_TO_PUBLIC["within_campaign_held_out"] != "independent"
    assert "same campaign" in S.REGISTRY_TO_PUBLIC["within_campaign_held_out"]
    assert S.REGISTRY_TO_PUBLIC["source_curve_reproduction"] != \
        S.REGISTRY_TO_PUBLIC["post_fit_reconstruction"]

    # And the ordering must rank independence above same-campaign holdout, or the cap is wrong.
    order = S._PUBLIC_RELATION_ORDER
    assert order.index("independent") > order.index("held out within the same campaign")
    assert (order.index("held out within the same campaign")
            > order.index("same campaign, not held out"))


def test_a_context_only_comparator_does_not_cap_a_measured_claim():
    """A model that supplies only a comparator must not drag a measurement down to its tier.

    PV-01 reports a measured TDS fraction and names a model solely as the timescale it is read
    against. Capping on every selection regardless of role would have downgraded it to the
    comparator's `verification` tier — a false correction.
    """
    from puckworks.public import schema as S
    from puckworks.public.claims import PUBLIC_CLAIMS

    c = next(x for x in PUBLIC_CLAIMS if x.claim_id == "PV-01")
    assert all(s.role_in_claim == "comparator_context" for s in c.evidence_selections)
    assert S.strongest_supported_relation(c) is None
    assert not any("stronger than the selected" in e for e in c.validate())
    # The comparator's evidence is still visible in the detail record, just not load-bearing.
    assert "verification" in S.relation_summary(c)[0]
