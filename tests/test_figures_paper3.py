"""Paper 3 figures (review MC12).

The seven figures were specifications. These tests hold the three properties that make them
reviewable rather than merely present: every figure renders from producers, every data-bearing
figure exports its source data, and every figure has a text alternative.

Rendering is exercised into a temp directory so the committed artifacts are never touched by a
test run.
"""
import csv
import pathlib

import pytest

import puckworks.models  # noqa: F401  (registers components)
from puckworks import registry as R

pytest.importorskip("matplotlib", reason="figures need the [figures] extra")
from puckworks import figures_paper3 as F  # noqa: E402

_ROOT = pathlib.Path(__file__).resolve().parents[1]
_COMMITTED = _ROOT / "docs/figures/paper3"


def test_every_figure_renders(tmp_path):
    """A figure that raises is not a figure. Renders all seven into a scratch directory."""
    for fn in F.FIGURES:
        out = fn(outdir=str(tmp_path))
        assert pathlib.Path(out).exists(), fn.__name__


def test_committed_figures_exist_in_raster_and_vector():
    """MC12 asks for both. The saver emits SVG and PDF siblings alongside the PNG."""
    assert _COMMITTED.exists(), "figures have never been rendered into the repo"
    for fn in F.FIGURES:
        stem = fn.__name__
        assert (_COMMITTED / (stem + ".png")).exists(), stem
        assert (_COMMITTED / (stem + ".svg")).exists(), stem
        assert (_COMMITTED / (stem + ".pdf")).exists(), stem


def test_every_figure_has_alt_text():
    """The accessibility statement promised text alternatives; nothing emitted any until now."""
    stems = {fn.__name__ for fn in F.FIGURES}
    assert set(F.ALT_TEXT) == stems, set(F.ALT_TEXT) ^ stems
    for stem, alt in F.ALT_TEXT.items():
        assert len(alt.split()) >= 30, f"{stem}: alt text is too thin to substitute for the figure"


def test_alt_text_file_is_current():
    path = _COMMITTED / "ALT_TEXT.md"
    assert path.exists()
    text = path.read_text(encoding="utf-8")
    for stem, alt in F.ALT_TEXT.items():
        assert stem in text and alt[:60] in text, stem


def test_source_data_exports_and_is_non_empty(tmp_path):
    paths = F.export_source_data(outdir=str(tmp_path))
    assert len(paths) >= 4
    for p in paths:
        with open(p, newline="", encoding="utf-8") as fh:
            rows = list(csv.reader(fh))
        assert len(rows) >= 2, f"{p} has a header but no data"


def test_source_data_matches_the_live_registry(tmp_path):
    """The stage/role CSV must equal the registry, not a snapshot of it."""
    F.export_source_data(outdir=str(tmp_path))
    path = tmp_path / "source_data" / "fig2_stage_role_counts.csv"
    with path.open(newline="", encoding="utf-8") as fh:
        rows = {r["stage"]: (int(r["runtime"]), int(r["calibration"]))
                for r in csv.DictReader(fh)}
    for stage, (rt, cal) in rows.items():
        assert rt == sum(1 for c in R.components()
                         if c.stage == stage and c.execution_role == "runtime")
        assert cal == sum(1 for c in R.components()
                          if c.stage == stage and c.execution_role == "calibration")


def test_ladder_source_data_matches_the_producer(tmp_path):
    from puckworks import harness as h
    F.export_source_data(outdir=str(tmp_path))
    path = tmp_path / "source_data" / "fig4_ladder.csv"
    with path.open(newline="", encoding="utf-8") as fh:
        rows = {r["rung"]: float(r["rmse_g_per_s"]) for r in csv.DictReader(fh)}
    L = h.kappa_t_ladder()
    assert rows["best in-window constant"] == L["rung1_const_kappa"]
    assert rows["empirical Phi(t)"] == L["rung4_phi_of_t"]


def test_composition_source_data_matches_the_producer(tmp_path):
    from puckworks.models.brewer2026 import coupled_kappa_t as ck
    F.export_source_data(outdir=str(tmp_path))
    path = tmp_path / "source_data" / "fig5_composition.csv"
    with path.open(newline="", encoding="utf-8") as fh:
        rows = {r["branch"]: float(r["rmse_g_per_s"]) for r in csv.DictReader(fh)}
    assert rows["composite_with_swelling"] == ck.composition_residual()["rmse"]
    assert rows["extraction_only"] == float(ck.degeneracy_rmse())


def test_the_manuscript_references_generated_figures_not_specifications():
    text = (_ROOT / "docs/PAPER_3_PUCKWORKS_DRAFT.md").read_text(encoding="utf-8")
    assert "## Figure specifications and draft captions" not in text
    assert "python -m puckworks.figures_paper3" in text
    for fn in F.FIGURES:
        assert fn.__name__ in text, fn.__name__


def test_the_module_imports_without_matplotlib_at_top_level():
    """Repository rule: optional extras are imported lazily, so the package works without them."""
    src = (_ROOT / "puckworks/figures_paper3.py").read_text(encoding="utf-8")
    head = src.split("def ")[0]
    assert "import matplotlib" not in head and "from matplotlib" not in head
