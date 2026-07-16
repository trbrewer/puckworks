from __future__ import annotations

from pathlib import Path

import pytest

# Figure rendering needs the optional [figures] extra (matplotlib). The quick lane installs
# only [dev], so skip cleanly there — these run in slow-science, which installs [figures].
pytest.importorskip("matplotlib")


def test_save_writes_png_svg_pdf(tmp_path: Path) -> None:
    from puckworks.figures import _plt, _save

    plt = _plt()
    fig, ax = plt.subplots()
    ax.plot([0, 1], [0, 1])
    try:
        returned = Path(_save(fig, str(tmp_path), "smoke.png"))
    finally:
        plt.close(fig)

    assert returned == tmp_path / "smoke.png"
    for suffix in (".png", ".svg", ".pdf"):
        path = tmp_path / f"smoke{suffix}"
        assert path.is_file()
        assert path.stat().st_size > 0


def test_vector_outputs_are_byte_reproducible(tmp_path: Path) -> None:
    from puckworks.figures import _plt, _save

    plt = _plt()

    def render(destination: Path) -> None:
        fig, ax = plt.subplots()
        ax.plot([0, 1], [1, 0], label="series")
        ax.legend()
        try:
            _save(fig, str(destination), "stable.png")
        finally:
            plt.close(fig)

    first = tmp_path / "first"
    second = tmp_path / "second"
    render(first)
    render(second)

    assert (first / "stable.svg").read_bytes() == (second / "stable.svg").read_bytes()
    assert (first / "stable.pdf").read_bytes() == (second / "stable.pdf").read_bytes()


def test_paperb_figure_render_is_deterministic(tmp_path: Path) -> None:
    """Reproducibility guard (B6-FIG), render path: fig1 (which consumes the RSM
    residual-bootstrap curve band) must render BYTE-IDENTICALLY on a repeat render, i.e.
    the stochastic step is seeded end-to-end. Catches an unseeded RNG regressing figure
    reproducibility. (PNG bytes remain matplotlib-version-scoped; committed figures are
    regenerated at the pinned release env, whose matplotlib version the reproducibility
    manifest records.)"""
    from puckworks import figures as F

    a = tmp_path / "a"
    b = tmp_path / "b"
    a.mkdir()
    b.mkdir()
    F.fig1_result1(str(a))
    F.fig1_result1(str(b))
    name = "fig1_result1_tds_ey.png"
    assert (a / name).read_bytes() == (b / name).read_bytes(), f"{name} not reproducible"


def test_paperb_bootstrap_analyses_are_deterministic() -> None:
    """Reproducibility guard (B6-FIG), analysis path: both figure-feeding bootstraps --
    the RSM residual bootstrap (`schmieder_rsm_diagnostics`, fig1) and the Result-2
    moving-block resampling (`result2_residual_diagnostics`, fig3/fig6) -- are seeded, so
    two calls return identical interval endpoints. Fast (no rendering); this is the root
    guarantee behind the byte-reproducible figures."""
    from puckworks import harness as h

    d1 = h.schmieder_rsm_diagnostics()
    d2 = h.schmieder_rsm_diagnostics()
    assert d1["curve_band"] == d2["curve_band"]
    assert d1["bootstrap"] == d2["bootstrap"]

    r1 = h.result2_residual_diagnostics()
    r2 = h.result2_residual_diagnostics()
    assert r1["rmse_diff_phi_minus_best_const"] == r2["rmse_diff_phi_minus_best_const"]
    assert r1["rmse_diff_phi_minus_cubic"] == r2["rmse_diff_phi_minus_cubic"]
