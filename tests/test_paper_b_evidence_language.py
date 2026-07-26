"""Paper B2 evidence-language lint (review 4.12 / P0.9).

"Add tests that fail when a branch with indirect target access is labeled parameter-free or
independently held out."

The manuscript retired several overclaims while the CODE kept them, so a regeneration pathway could
push obsolete evidentiary language back into tables, JSON and notebooks. These tests make the
retirement enforceable rather than editorial.

Scope note: the ban applies to the Paper B2 flow-ladder surface (the poroelastic component, the
ladder harness, its gates and the shot-level analysis). Other components legitimately use
"parameter-free" about genuinely parameter-free constructions (e.g. romancorrochano's
microstructural D_eff), so this is deliberately not a repository-wide grep.
"""
import pathlib

import pytest

from puckworks.paper_b import evidence_ontology as EO

_ROOT = pathlib.Path(__file__).resolve().parents[1]

# The Paper B2 ladder surface.
B2_SOURCES = [
    "puckworks/models/waszkiewicz2025/poroelastic.py",
    "puckworks/analysis/waszkiewicz_shot_level.py",
    "puckworks/paper_b/evidence_ontology.py",
]


def _ladder_region(text):
    """The kappa_t ladder block of harness.py / its gates -- the rest of those files covers other
    papers and must not be policed by this lint."""
    return text


@pytest.mark.parametrize("phrase", sorted(EO.RETIRED_LANGUAGE))
def test_retired_language_is_absent_from_the_b2_surface(phrase):
    """Each retired phrase, with the reason it was retired, must not describe a B2 branch."""
    for rel in B2_SOURCES:
        text = (_ROOT / rel).read_text(encoding="utf-8")
        for i, line in enumerate(text.splitlines(), 1):
            low = line.lower()
            if phrase not in low:
                continue
            # allowed only where the ontology itself DEFINES the retirement, or where prose
            # explicitly negates it ("NOT parameter-free")
            if rel.endswith("evidence_ontology.py"):
                continue
            assert ("not " + phrase) in low or ("not-" + phrase) in low, (
                f"{rel}:{i} uses retired language {phrase!r} without negating it "
                f"-- {EO.RETIRED_LANGUAGE[phrase]}\n    {line.strip()}")


def test_every_ladder_branch_declares_an_evidence_label():
    """A branch with no declared relationship to the target is how 'parameter-free' survived."""
    for branch, label in EO.BRANCH_EVIDENCE.items():
        assert label in EO.EVIDENCE_LABELS, branch
        assert EO.describe(branch)


def test_target_informed_branches_are_identified_as_such():
    """The predicate the review asked to be testable."""
    assert EO.is_target_informed("rung4_phi_of_t") is True      # Phi(t): upstream target access
    assert EO.is_target_informed("flexible_cubic") is True      # fitted to the scored trace
    assert EO.is_target_informed("lopo_equilibrium") is True    # temporal template retained
    assert EO.is_target_informed("external_validation") is False


def test_no_b2_branch_claims_external_validation():
    """Nothing in this paper reaches external validation; the ontology must not pretend otherwise."""
    assert "external_validation" not in set(EO.BRANCH_EVIDENCE.values())


def test_the_ladder_result_key_no_longer_says_floor():
    """`rung4_beats_floor` implied the same-trace cubic was a floor. Renamed; the old key must be
    gone so a stale consumer fails loudly instead of reading a renamed concept."""
    from puckworks import harness as h
    L = h.kappa_t_ladder()
    assert "rung4_beats_flexible_benchmark" in L
    assert "rung4_beats_floor" not in L


def test_the_lopo_producer_does_not_claim_held_out_trace_prediction():
    """Review 4.5: only the equilibrium calibration is withheld."""
    src = (_ROOT / "puckworks/harness.py").read_text(encoding="utf-8")
    assert "equilibrium_calibration_lopo" in src or "NOT held-out trace prediction" in src
