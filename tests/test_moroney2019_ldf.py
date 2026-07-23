"""moroney2019 1-D two-grain LDF solver + verification gate.

VERIFICATION only (model-vs-itself + physical plausibility) — the solver reproduces no
experimental result; it checks the transcribed equations and the cooper2021 h_sl erratum.
"""
from puckworks.analysis import moroney2019_ldf as ldf
from puckworks.validation.gates import gate_moroney2019_ldf_verification


def test_solver_conserves_mass_and_has_two_timescales():
    for grind in ("fine", "coarse"):
        r = ldf.solve(grind)
        # solute removed from the grains is carried out of the bed (upwind numerical floor)
        assert 0.92 <= r["budget_closure"] <= 1.0, (grind, r["budget_closure"])
        # physical: exit concentration is non-negative, peaks below the solid inventory, and decays
        assert r["cexit_kgm3"].min() >= -1e-6
        assert 0 < r["cexit_peak"] < r["cs0_kgm3"]
        assert r["cexit_end"] < r["cexit_peak"]
        # two-grain structure: the small population empties before the large one
        assert r["tau_small_s"] < r["tau_large_s"]
    # coarse extracts slower than fine (larger grains)
    assert ldf.solve("coarse")["tau_large_s"] > ldf.solve("fine")["tau_large_s"]


def test_cooper2021_erratum_is_physically_confirmed():
    D_FREE = 2.2e-9        # coffee-in-water molecular diffusivity (card)
    for grind in ("fine", "coarse"):
        r = ldf.solve(grind)
        # corrected intragranular diffusivities are physical (<= free aqueous diffusion)
        assert all(v <= D_FREE for v in r["D_v_corrected"].values()), (grind, r["D_v_corrected"])
        # the uncorrected (reported) large-grain value is unphysical (exceeds free diffusion)
        assert r["D_v_reported"]["large"] > D_FREE, (grind, r["D_v_reported"])


def test_gate_passes():
    assert gate_moroney2019_ldf_verification()["passed"]
