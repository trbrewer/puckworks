"""Paper 2 figure module — the set that review item 4.7 left owed.

The manuscript carried four figure specifications and four "Figure N near here" placeholders, and
no `figures_paper_b*` module existed. These tests hold the new module to the standard the other two
paper figure modules meet, and pin the three real defects found while building it:

* `flow_minimum()` returns `(Q_min, t)` — value FIRST. Unpacking it as `(t, Q)` put the marker at
  the top of the axes and printed a wrong annotation.
* The calibration-drift panel referenced the median of the leave-one-out fits rather than the
  all-pressure fit, which put a point outside the ±2.83 % bound the panel's own title states.
* The Foster reconstruction was drawn past the interval the model covers, so an extrapolation sat
  beside published data and read as disagreement.
"""
import csv
import os

import pytest

matplotlib = pytest.importorskip("matplotlib", reason="figures need the [figures] extra")

from puckworks import figures_paper_b2 as F  # noqa: E402


@pytest.fixture(scope="module")
def bundle():
    return F._bundle()


def test_every_specified_figure_is_rendered(tmp_path):
    paths = F.render_all(outdir=str(tmp_path))
    assert len(paths) == len(F.FIGURES) == 5
    for stem in ("fig1_machine_nonuniqueness", "fig2_null_first_ladder", "fig3_cross_pressure",
                 "fig4_residual_structure", "fig5_perturbation_matrix"):
        for ext in (".png", ".svg", ".pdf"):
            assert os.path.exists(os.path.join(tmp_path, stem + ext)), stem + ext


def test_every_figure_has_alt_text():
    stems = [f.__name__ for f in F.FIGURES]
    assert set(F.ALT_TEXT) == set(stems), set(F.ALT_TEXT) ^ set(stems)
    for stem, alt in F.ALT_TEXT.items():
        assert len(alt) > 200, f"{stem} alt text is a stub"
        # each must describe the PANELS, not just name the figure, or it is not an alternative
        assert alt.lower().count("panel") >= 2 or "matrix" in alt.lower(), stem


def test_figures_render_from_the_bundle_the_claims_are_checked_against(bundle):
    """The point of rendering from `paper_b_results.json`: a figure cannot disagree with a claim
    that was verified against the same object."""
    from puckworks.paper_b2 import build as B
    assert os.path.samefile(F.BUNDLE, B._BUNDLE), (F.BUNDLE, B._BUNDLE)
    ok, failures, _ = B.verify(write_manifest=False)
    assert ok, failures


def test_predictions_are_recovered_not_recomputed(bundle):
    """measured - residual, so the plotted curves ARE the ones the diagnostics were computed from.
    Recomputing would give curves that merely ought to agree."""
    import numpy as np
    t, measured, preds = F._diagnostic_grid(bundle)
    rd = bundle["shot_level"]["residuals_1s"]["branches"]
    assert len(t) == len(measured) == bundle["shot_level"]["residuals_1s"]["n_points_at_resolution"]
    for key, *_ in F.BRANCHES:
        resid = np.asarray(rd[key]["residual_vs_time_g_per_s"], dtype=float)
        assert np.allclose(measured - preds[key], resid, atol=1e-9), key


def test_the_two_constant_branches_leave_identical_centred_diagnostics(bundle):
    """Not a bug and the figure says so: a constant level and the static branch differ by an
    offset, so after centring every diagnostic coincides. Without this the overplotted curve reads
    as a missing one."""
    import numpy as np
    rd = bundle["shot_level"]["residuals_1s"]["branches"]
    assert np.allclose(rd["rung1_const"]["acf_by_lag"], rd["rung3_static"]["acf_by_lag"], atol=1e-9)
    assert (rd["rung1_const"]["spectrum"]["peak_bin_period_s"]
            == rd["rung3_static"]["spectrum"]["peak_bin_period_s"])


def test_the_foster_flow_minimum_is_unpacked_in_the_right_order():
    """REAL DEFECT. `flow_minimum()` returns (Q_min/Q_m, t_exp) -- value first. The gate is the
    reference: Q_min 0.181 at t 1.99. Unpacking it as (t, Q) drew the marker at the top of panel b
    and annotated 'minimum 1.99 at 0.18 s'."""
    from puckworks.models.foster2025 import machine_mode as fm
    from puckworks.validation import gates
    q_min, t_min = fm.flow_minimum()
    g = gates.gate_foster_fig15_flowmin()
    assert q_min == pytest.approx(g["Q_min"], abs=1e-3)
    assert t_min == pytest.approx(g["t_min"], abs=1e-2)
    assert q_min < t_min, "the (value, time) order this figure relies on has changed"


def test_the_reconstruction_is_drawn_only_where_the_model_is_defined():
    """The published Fig-15 series runs to 10 s; the model covers [t_p, t_s]. Drawing beyond it put
    an extrapolation beside published data."""
    from puckworks.models.foster2025 import machine_mode as fm
    from puckworks.validation.gates import gates_data
    r = fm.solve()
    hi = r["t_s"] + r["p"].t_shift
    published_max = max(row["t_s"] for row in gates_data().foster_fig15_flow())
    assert hi < published_max, (
        "the model now spans the whole published series -- the shaded 'outside the modelled "
        "interval' band in fig 1b is no longer meaningful")

    src = __import__("inspect").getsource(F.fig1_machine_nonuniqueness)
    assert 'r["t_s"]' in src and "axvspan" in src, "the window restriction is gone"


def test_calibration_drift_is_plotted_against_the_all_pressure_fit(bundle):
    """REAL DEFECT. Referencing the median of the leave-one-out fits put a point at -3.0 %, outside
    the ±2.83 % bound the panel's own title states. `max_calibration_drift` is measured against the
    all-pressure fit, so the panel must use that reference or it contradicts itself."""
    import numpy as np
    lo = bundle["loco"]
    pdom = bundle["shot_level"]["pressure_domains"]
    pressures = sorted(lo["per_pressure"], key=float)
    pc = np.array([lo["per_pressure"][p]["P_c"] for p in pressures], dtype=float)
    qc = np.array([lo["per_pressure"][p]["Q_c"] for p in pressures], dtype=float)
    rp = float(pdom["fitted_equilibrium_P_c_bar"])
    rq = float(pdom["fitted_equilibrium_Q_c_g_per_s"])
    worst = max(float(np.max(np.abs(pc - rp) / rp)), float(np.max(np.abs(qc - rq) / rq)))
    bound = lo["max_calibration_drift"]
    assert worst <= bound + 5e-4, (worst, bound)

    # ...and the median reference really would have violated it, so this test is not vacuous.
    worst_median = float(np.max(np.abs(qc - np.median(qc)) / np.median(qc)))
    assert worst_median > bound, (
        "the median reference no longer violates the bound -- re-check that this guard still "
        "discriminates")


def test_the_best_branch_count_is_derived_not_asserted(bundle):
    """Panel 3a's title states how many times the best branch changes. The manuscript says three."""
    cp = bundle["cross_pressure"]
    pressures = sorted(cp["per_pressure"], key=float)
    best = [min(("static", "phi", "rc3b"), key=lambda k: cp["per_pressure"][p][k])
            for p in pressures]
    changes = sum(1 for i in range(1, len(best)) if best[i] != best[i - 1])
    assert changes == 3, changes
    text = open("docs/PAPER_B2_TEMPORAL_DRAFT.md", encoding="utf-8").read()
    assert "changes three times" in text


def test_source_data_is_exported_for_every_data_bearing_figure(tmp_path):
    written = F.export_source_data(outdir=str(tmp_path))
    names = {os.path.basename(p) for p in written}
    for expected in ("fig2_predictions_and_residuals.csv", "fig2_ladder_rmse.csv",
                     "fig2_block_intervals.csv", "fig3_per_pressure.csv",
                     "fig3_nominal_vs_recorded.csv", "fig4_residual_structure.csv",
                     "fig4_acf_by_lag.csv", "fig5_perturbation_matrix.csv"):
        assert expected in names, expected
    for path in written:
        with open(path, encoding="utf-8") as fh:
            rows = list(csv.reader(fh))
        assert len(rows) > 1, path


def test_exported_source_data_matches_the_bundle(tmp_path, bundle):
    """A CSV that drifted from the bundle would let a reviewer 're-plot' a different figure."""
    F.export_source_data(outdir=str(tmp_path))
    with open(os.path.join(tmp_path, "source_data", "fig4_residual_structure.csv"),
              encoding="utf-8") as fh:
        rows = {r["branch"]: r for r in csv.DictReader(fh)}
    rd = bundle["shot_level"]["residuals_1s"]["branches"]
    for key, *_ in F.BRANCHES:
        assert float(rows[key]["power_in_slowest_quarter"]) == pytest.approx(
            rd[key]["spectrum"]["power_in_slowest_quarter"], abs=1e-9)
        assert float(rows[key]["lag1_acf"]) == pytest.approx(
            rd[key]["lag1_autocorrelation"], abs=1e-9)


def test_the_perturbation_matrix_is_declared_and_says_so():
    """It is not computed and no data from those protocols exists. The figure must not read as a
    result."""
    assert "declared" in F.ALT_TEXT["fig5_perturbation_matrix"].lower()
    src = __import__("inspect").getsource(F.fig5_perturbation_matrix)
    assert "DECLARED, not measured" in src
    assert "NO data from any of these protocols" in src
    assert len(F.PREDICTIONS) == len(F.MECHANISMS) * len(F.PERTURBATIONS)


def test_the_matrix_vocabulary_matches_the_manuscript_table():
    """Figure 5 transcribes Table 4. If the table's rows or columns change, the figure is stale."""
    text = open("docs/PAPER_B2_TEMPORAL_DRAFT.md", encoding="utf-8").read()
    table = text.split("**Table 4.")[1].split("###")[0]
    for token in ("Machine/headspace", "Dissolution-linked opening", "Fines migration",
                  "Compaction and elastic recovery", "Particle swelling"):
        assert token in table, token
    for token in ("Pressure step upward", "Flow reversal", "Rebrew of spent puck",
                  "Depth-resolved end state"):
        assert token in table, token
    assert len(F.MECHANISMS) == 5 and len(F.PERTURBATIONS) == 5


def test_alt_text_file_is_written(tmp_path):
    path = F.write_alt_text(outdir=str(tmp_path))
    body = open(path, encoding="utf-8").read()
    for stem in F.ALT_TEXT:
        assert stem in body


def test_the_module_imports_without_matplotlib(monkeypatch):
    """CLAUDE.md's optional-dependency rule: importing must not require the [figures] extra."""
    src = open("puckworks/figures_paper_b2.py", encoding="utf-8").read()
    head = src.split("def ")[0]
    assert "import matplotlib" not in head, "matplotlib is imported at module top"
    assert "_plt()" in src


def test_the_manuscript_no_longer_says_the_figure_set_is_unbuilt():
    text = open("docs/PAPER_B2_TEMPORAL_DRAFT.md", encoding="utf-8").read()
    assert "not yet built" not in text, (
        "the manuscript still says the figure set does not exist")
