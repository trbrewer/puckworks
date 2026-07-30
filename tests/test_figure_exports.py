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


# ── embedded figure numbers (Paper 1 third review, cross-cutting figure issue) ────────────────
def test_paper_a_figures_carry_no_embedded_figure_number():
    """The caption map renumbers producer figures for presentation -- `fig4_transfer` becomes
    Figure 3, `fig3_holdouts` becomes Figure S1 -- so an embedded "Fig 4" inside the image would
    contradict its own caption once uploaded. Numbering is the caption system's job.
    """
    import re
    from pathlib import Path

    src = (Path(__file__).resolve().parents[1] / "puckworks" / "figures_paper_a.py"
           ).read_text(encoding="utf-8")
    offenders = re.findall(r'(?:suptitle|set_title)\(\s*"(Fig(?:ure)?\s*\d+[^"]*)"', src)
    assert not offenders, f"figure titles embed a number: {offenders}"


def test_paper_a_caption_map_records_the_no_embedded_number_policy():
    from pathlib import Path
    caps = (Path(__file__).resolve().parents[1] / "docs" / "figures" / "PAPER_A_FIGURE_MAP_INTERNAL.md"
            ).read_text(encoding="utf-8")
    assert "no embedded figure number" in caps.lower()


def test_figure2_caption_scope_matches_its_producer():
    """A main figure's caption must not claim more data than the producer plots.

    Fourth review P0-8: Figure 2's caption said the model was evaluated at nine optimal-grind
    conditions "for each coffee variety (18 condition means per solute)", while the producer loads
    only `identifiability_panel("Arabica", ...)` for both panels. The caption doubled the apparent
    sample scope, and nothing checked it. This test reads the varieties out of the producer source
    and requires the caption to name exactly those.
    """
    import re
    from pathlib import Path

    root = Path(__file__).resolve().parents[1]
    src = (root / "puckworks" / "figures_paper_a.py").read_text(encoding="utf-8")
    panels = re.findall(r'\("panel_(\w+)",\s*lambda:\s*ab\.identifiability_panel\(\s*"(\w+)"',
                        src)
    assert panels, "could not locate the Figure 2 identifiability panels in the producer"
    varieties = {v for _solute, v in panels}

    caps = (root / "docs" / "figures" / "PAPER_A_FIGURE_MAP_INTERNAL.md").read_text(encoding="utf-8")
    cap = re.search(r"(?ms)^### Figure 2 \(.*?\)\s*\n+(.*?)(?=\n### )", caps).group(1)

    for v in varieties:
        assert v in cap, f"Figure 2 plots {v} panels but the caption never names {v}"
    for other in {"Arabica", "Robusta"} - varieties:
        # Naming a variety the figure does not plot is exactly the defect: it is allowed only where
        # the caption explicitly says that variety is reported elsewhere.
        for m in re.finditer(other, cap):
            window = cap[max(0, m.start() - 160):m.end() + 160]
            assert "Supplementary" in window or "not plotted" in window, (
                f"Figure 2 caption mentions {other}, which it does not plot, without saying where "
                f"it is actually reported")

    n_expected = 9 * len(varieties)
    stated = re.search(r"\((\w+|\d+) condition means per solute\)", cap)
    assert stated, "Figure 2 caption does not state its condition-mean count"
    words = {"nine": 9, "eighteen": 18, "twenty-seven": 27}
    got = words.get(stated.group(1), None)
    got = got if got is not None else int(stated.group(1))
    assert got == n_expected, (
        f"Figure 2 caption claims {got} condition means per solute but the producer plots "
        f"{len(varieties)} variety/varieties x 9 conditions = {n_expected}")
