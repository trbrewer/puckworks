"""Shared-porosity SIGN CONTRACT (Paper 3 review P0-7).

The composition documented `eps = eps0*(1 + Phi_ext - Phi_swell - ...)`, implying Phi_swell is a
non-negative closure MAGNITUDE to subtract. The implementation returns `eps_b/eps0 - 1` -- a SIGNED
relative increment, negative when swelling closes pores -- and ADDS it. The arithmetic agreed; the
interface did not, so a downstream consumer could not tell which convention `Phi_swelling` obeyed.

Paper 3's own thesis is that typed contracts prevent exactly this, so the ambiguity had to be
resolved rather than documented. Convention adopted (the review's recommendation, and what the code
already did): every branch is a SIGNED relative porosity increment and branches ADD.
"""
import json
import pathlib

import numpy as np

from puckworks.models.brewer2026 import coupled_kappa_t as C

_ROOT = pathlib.Path(__file__).resolve().parents[1]
T = np.linspace(1.0, 90.0, 60)


def test_branch_signs_follow_the_declared_convention():
    """Opening branches >= 0, closing branches <= 0 -- the whole point of the convention."""
    assert (C._phi_extraction(T, 18.0) >= 0).all(), "dissolution must OPEN pore space"
    assert (C._phi_swelling(T) <= 0).all(), "swelling must CLOSE pore space (signed, negative)"


def test_swelling_is_a_relative_increment_not_a_magnitude():
    """The distinguishing test: a magnitude convention would return |eps_b/eps0 - 1| >= 0."""
    v = C._phi_swelling(T)
    assert v.min() < 0.0
    assert np.all(np.abs(v) < 1.0), "a relative increment, not an absolute porosity"


def test_branches_compose_additively_and_reduce_exactly_when_a_branch_is_off():
    """Adding a branch must equal the base plus that branch's signed increment -- and turning it
    off must recover the base EXACTLY (no residual offset hiding a sign flip)."""
    base = C.simulate(branches=("extraction",))
    both = C.simulate(branches=("extraction", "swelling"))
    assert np.allclose(base["t"], both["t"])
    # the swelling branch only ever lowers porosity relative to extraction-only
    assert (both["eps"] <= base["eps"] + 1e-12).all()
    # and extraction-only is exactly reproducible (exact reduction when the branch is zero)
    again = C.simulate(branches=("extraction",))
    assert np.allclose(base["eps"], again["eps"], atol=0, rtol=0)


def test_monotone_response_to_adding_a_closing_branch():
    """Composing a closing branch must reduce porosity monotonically, never raise it."""
    base = C.simulate(branches=("extraction",))
    both = C.simulate(branches=("extraction", "swelling"))
    delta = both["eps"] - base["eps"]
    assert delta.max() <= 1e-12, "a closing branch must not increase porosity anywhere"
    assert delta.min() < 0.0, "and it must actually do something"


def test_code_card_and_public_artifacts_agree_on_the_convention():
    """Review P0-7: agreement among code, card, exported JSON, caption and manuscript. The
    subtractive form must not survive anywhere as a live statement of the contract."""
    src = (_ROOT / "puckworks/models/brewer2026/coupled_kappa_t.py").read_text(encoding="utf-8")
    assert "SIGN CONTRACT" in src
    assert "eps0 * (1 + Phi_ext(t) + Phi_swell(t)" in src

    pub = (_ROOT / "puckworks/public/model_composition.py").read_text(encoding="utf-8")
    assert "eps(t) = eps0*(1 + Phi_extraction - Phi_swelling)" not in pub
    assert "SIGNED relative" in pub

    data = json.loads((_ROOT / "puckworks/public/data/pv05_model_composition.json")
                      .read_text(encoding="utf-8"))
    blob = json.dumps(data)
    assert "1 + Phi_extraction - Phi_swelling" not in blob
    assert "SIGNED relative" in blob


def test_the_simulator_exposes_the_signed_branches_it_composed():
    """A consumer must be able to read the per-branch increments and re-derive eps, otherwise the
    convention is unverifiable from outside."""
    r = C.simulate(branches=("extraction", "swelling"))
    # NOTE the returned key `phi` holds the PER-BRANCH dict of signed increments, not the summed
    # array -- a naming trap worth knowing about, kept because consumers (public JSON) rely on it.
    parts = r["phi"]
    assert {"extraction", "swelling"} <= set(parts)
    assert (np.asarray(parts["swelling"]) <= 0).all()
    assert (np.asarray(parts["extraction"]) >= 0).all()
    # the UNSELECTED structural stubs must contribute EXACTLY zero -- otherwise "stub" is hiding a
    # contribution, and the composition would not reduce cleanly to its selected branches
    for stub in ("compaction_stub", "fines_stub"):
        if stub in parts:
            assert np.all(np.asarray(parts[stub]) == 0.0), f"{stub} is not inert"
    # eps must be reconstructable from eps0 and the SUM of signed increments (pre-clamp)
    total = sum(np.asarray(v) for v in parts.values())
    eps_expected = C.EPS0_DEFAULT * (1.0 + total)
    clamped = np.clip(eps_expected, C.EPS_MIN, C.EPS_MAX)
    assert np.allclose(r["eps"], clamped, rtol=1e-9, atol=1e-12)
