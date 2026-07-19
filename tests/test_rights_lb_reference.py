"""Bounded rights review for the first-party LB channel code-verification component (issue #70).

`brewer2026.lb_reference` is a first-party, in-repo D3Q19 TRT lattice-Boltzmann kernel whose verification
case is generated synthetically in code and compared to the ANALYTIC plane-Poiseuille solution (no
third-party dataset is bundled). This affirmative review clears exactly that path — code CLEAR, data
NOT_APPLICABLE (synthetic input), output CLEAR — and NOTHING else. These tests prove the record is
explicit (not the NOT_REVIEWED default), that its use-specific decisions match its states, that unrelated
components (Cameron, the three source-data native runners, the rest of the brewer2026 family, Grudeva) are
untouched, and that the record is NOT a family-, author-, model-, or namespace-wide clearance.
"""
import puckworks
from puckworks import rights

LB = "brewer2026.lb_reference"


def test_lb_reference_has_an_explicit_record_not_the_default():
    r = rights.rights_record(LB)
    # explicit (reviewed) — a reviewed determination must cite evidence + a date (enforced in __post_init__)
    assert r.review_date == "2026-07-19" and r.source and r.decision_issue == "#70"
    assert LB in rights._RECORDS                              # a real record, not the NOT_REVIEWED fallback
    # not a silent default
    assert (r.code_rights_state, r.data_rights_state, r.output_redistribution_state) != (
        "NOT_REVIEWED", "NOT_REVIEWED", "NOT_REVIEWED")


def test_lb_reference_code_data_output_states_are_separate():
    r = rights.rights_record(LB)
    assert r.code_rights_state == "CLEAR"
    assert r.data_rights_state == "NOT_APPLICABLE"           # synthetic generated input; no dataset
    assert r.output_redistribution_state == "CLEAR"
    # NOT_APPLICABLE requires a documented reason (enforced), and the note bounds the scope to the LB path
    assert r.rights_note and "code-verification" in r.rights_note.lower()


def test_lb_reference_local_execution_allowed():
    d = rights.may_execute_locally(LB)
    assert d.allowed and d.severity == "clear" and d.governing_field == "code_rights_state"


def test_lb_reference_public_batch_execution_allowed_under_its_code_result():
    d = rights.may_execute_in_public_batch(LB)
    # allowed ONLY because code_rights_state is affirmative (CLEAR); NOT_REVIEWED would not clear it
    assert d.allowed and d.severity == "clear"
    assert d.governing_state == rights.rights_record(LB).code_rights_state == "CLEAR"


def test_lb_reference_output_publication_allowed_under_its_output_result():
    d = rights.may_publish_outputs(LB)
    assert d.allowed and d.severity == "clear"
    assert d.governing_state == rights.rights_record(LB).output_redistribution_state == "CLEAR"


def test_lb_reference_data_inclusion_is_explicitly_not_applicable():
    d = rights.may_include_data_in_release(LB)
    # NOT_APPLICABLE is not a block: it ships (there is nothing to redistribute) but is reported distinctly
    assert d.allowed and d.severity == "not_applicable"
    assert d.governing_state == "NOT_APPLICABLE"


def test_unrelated_records_are_unchanged():
    # the only affirmatively/blocked reviewed records today are exactly LB (this review) and Grudeva (#73)
    reviewed = {r.component_id for r in rights.all_rights()
                if any(s != "NOT_REVIEWED" for s in
                       (r.code_rights_state, r.data_rights_state, r.output_redistribution_state))}
    assert reviewed == {LB, "grudeva2025.reduced"}


def test_grudeva_remains_blocked():
    g = rights.rights_record("grudeva2025.reduced")
    assert g.code_rights_state == "RIGHTS_BLOCKED" and g.output_redistribution_state == "RIGHTS_BLOCKED"
    assert rights.blocked_components() == ["grudeva2025.reduced"]
    assert not rights.may_execute_in_public_batch("grudeva2025.reduced").allowed


def test_cameron_and_the_source_data_native_runners_remain_unreviewed():
    for cid in ("cameron2020.extraction_bdf", "waszkiewicz2025.poroelastic",
                "wadsworth2026.permeability", "foster2025.infiltration"):
        r = rights.rights_record(cid)
        assert r.code_rights_state == "NOT_REVIEWED"
        # not cleared for public/outward use — a visible gap, never "clear"
        assert not rights.may_execute_in_public_batch(cid).allowed
        assert not rights.may_publish_outputs(cid).allowed


def test_review_is_not_a_family_author_model_or_namespace_wide_clearance():
    # every OTHER brewer2026.* component stays NOT_REVIEWED — the affirmative record is per-component
    others = [c.name for c in puckworks.components()
              if c.name.startswith("brewer2026.") and c.name != LB]
    assert others                                            # sanity: there ARE sibling components
    for cid in others:
        assert rights.rights_record(cid).code_rights_state == "NOT_REVIEWED"


def test_unknown_component_still_fails_to_the_not_reviewed_default():
    r = rights.rights_record("not.a.real.component")
    assert (r.code_rights_state, r.data_rights_state, r.output_redistribution_state) == (
        "NOT_REVIEWED", "NOT_REVIEWED", "NOT_REVIEWED")
    assert not rights.may_execute_in_public_batch("not.a.real.component").allowed


def test_record_set_is_clean_and_every_component_has_exactly_one_record():
    assert rights.validate_records() == []
    ids = [r.component_id for r in rights.all_rights()]
    assert ids == sorted(ids) and len(ids) == len(set(ids))
    assert set(ids) == {c.name for c in puckworks.components()}
