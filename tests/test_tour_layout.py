"""Structural layout + typography tests for the tour's educational figures (#43, ROADMAP §8).

These render each figure with the Agg backend, draw the canvas, and inspect Text bounding boxes — the
collisions the presentation pass fixed (badge over title, footer over x-labels, clipped annotations,
5.2 pt footer) cannot silently return. Not pixel snapshots: structural checks + a human visual review.
"""
import pytest

pytest.importorskip("matplotlib")
import io  # noqa: E402

import matplotlib  # noqa: E402

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from puckworks.product import lab_tour_insights as I  # noqa: E402
from puckworks.viz import registry as R  # noqa: E402
from puckworks.viz import tour_insight_draw as D  # noqa: E402
from puckworks.viz.tour_style import MIN_VISIBLE_FS  # noqa: E402

_SCEN = {"preset_id": "pv19_named", "overrides": {"pressure_bar": 9.0}, "domain_policy": "warn"}

# (spec_id, draw_name, needs_scenario) flattened from the insight registry
_ALL = [(sid, draw, kw is not I._none)
        for insights in I._INSIGHTS.values()
        for (sid, _h, _q, draw, kw) in insights]
_CHEAP = [t for t in _ALL if not t[2]]          # the 5 reused draws (no Cameron simulation)
_CAMERON = [t for t in _ALL if t[2]]            # the 3 Cameron sweeps (heavier)


def _build(spec_id, draw_name, needs_scenario, presentation="notebook"):
    spec = R.viz_by_id(spec_id)
    data = (I._run_producer(spec, I._cam_kwargs(_SCEN)) if needs_scenario
            else R.producer_data(spec))
    fig, nar = getattr(D, draw_name)(data, presentation=presentation,
                                     ceiling=spec.fidelity_ceiling, title=spec.title)
    R.stamp_fig(fig, spec)
    fig.canvas.draw()
    return fig, spec, nar


# ── bounding-box helpers ──────────────────────────────────────────────────────────────────
def _rend(fig):
    return fig.canvas.get_renderer()


def _ext(t, fig):
    return t.get_window_extent(_rend(fig))


def _overlap_area(b1, b2):
    x0, x1 = max(b1.x0, b2.x0), min(b1.x1, b2.x1)
    y0, y1 = max(b1.y0, b2.y0), min(b1.y1, b2.y1)
    return max(0.0, x1 - x0) * max(0.0, y1 - y0)


def _visible_texts(fig):
    out = list(fig.texts)
    for sf in getattr(fig, "subfigs", []):
        out += list(sf.texts)
        for lg in getattr(sf, "legends", []):
            out += lg.get_texts()
    for lg in getattr(fig, "legends", []):
        out += lg.get_texts()
    for ax in fig.axes:
        out += [ax.title, ax.xaxis.label, ax.yaxis.label, ax.xaxis.offsetText, ax.yaxis.offsetText]
        out += list(ax.texts) + list(ax.get_xticklabels()) + list(ax.get_yticklabels())
        lg = ax.get_legend()
        if lg:
            out += lg.get_texts()
    return [t for t in out if t is not None and t.get_visible() and t.get_text().strip()]


def _band_texts(fig, which):
    return [t for t in fig._tour_layout[which].texts if t.get_text().strip()]


def _plot_axes(fig):
    # every real Axes belongs to the plot band (header/footer bands carry no Axes)
    return list(fig.axes)


def _check_no_band_over_axes(fig):
    axes = _plot_axes(fig)
    for band in ("header", "footer"):
        for t in _band_texts(fig, band):
            tb = _ext(t, fig)
            for ax in axes:
                assert _overlap_area(tb, ax.get_window_extent(_rend(fig))) < 2.0, \
                    f"{band} text {t.get_text()[:30]!r} overlaps a plot Axes"
                for lbl in (ax.xaxis.label, ax.yaxis.label):
                    if lbl.get_text().strip():
                        assert _overlap_area(tb, _ext(lbl, fig)) < 2.0, \
                            f"{band} text overlaps axis label {lbl.get_text()!r}"


def _clip_texts(fig):
    # the clip check targets authored text (annotations, titles, axis labels, band + legend text) — NOT
    # matplotlib's auto tick-label objects, some of which exist for out-of-view ticks and are never drawn.
    out = list(fig.texts)
    for sf in getattr(fig, "subfigs", []):
        out += list(sf.texts)
        for lg in getattr(sf, "legends", []):
            out += lg.get_texts()
    for ax in fig.axes:
        out += [ax.title, ax.xaxis.label, ax.yaxis.label] + list(ax.texts)
        lg = ax.get_legend()
        if lg:
            out += lg.get_texts()
    return [t for t in out if t is not None and t.get_visible() and t.get_text().strip()]


def _check_nothing_clipped(fig):
    fb = fig.bbox
    for t in _clip_texts(fig):
        tb = _ext(t, fig)
        assert tb.x0 >= fb.x0 - 1 and tb.x1 <= fb.x1 + 1 and tb.y0 >= fb.y0 - 1 and tb.y1 <= fb.y1 + 1, \
            f"text clipped outside canvas: {t.get_text()[:40]!r}"


def _check_min_font(fig):
    for t in _visible_texts(fig):
        assert t.get_fontsize() >= MIN_VISIBLE_FS - 1e-6, \
            f"tour text below {MIN_VISIBLE_FS} pt: {t.get_text()[:30]!r} @ {t.get_fontsize()}"


def _generic_checks(fig, spec, nar):
    _check_no_band_over_axes(fig)
    _check_nothing_clipped(fig)
    _check_min_font(fig)
    # badge + a Scope footer are embedded in the graphic
    assert any(spec.badge.replace("_", " ") in t.get_text() for t in _band_texts(fig, "header"))
    assert any("Scope:" in t.get_text() for t in _band_texts(fig, "footer"))
    # notebook presentation must NOT repeat the surrounding question inside the figure
    q = next(q for insights in I._INSIGHTS.values() for (sid, _h, q, _d, _k) in insights if sid == spec.id)
    assert all(q not in t.get_text() for t in _visible_texts(fig))
    # a non-empty PNG still renders
    b = io.BytesIO(); fig.savefig(b, format="png"); assert b.getbuffer().nbytes > 2000


@pytest.mark.parametrize("spec_id,draw_name,needs", _CHEAP)
def test_layout_cheap_figures(spec_id, draw_name, needs):
    fig, spec, nar = _build(spec_id, draw_name, needs)
    _generic_checks(fig, spec, nar)
    plt.close(fig)


@pytest.mark.slow
@pytest.mark.parametrize("spec_id,draw_name,needs", _CAMERON)
def test_layout_cameron_figures(spec_id, draw_name, needs):
    fig, spec, nar = _build(spec_id, draw_name, needs)
    _generic_checks(fig, spec, nar)
    plt.close(fig)


def test_stamp_is_idempotent():
    spec = R.viz_by_id("wetting_front_sweep")
    fig, _ = D.figure_wetting_front(R.producer_data(spec), ceiling=spec.fidelity_ceiling)
    R.stamp_fig(fig, spec); R.stamp_fig(fig, spec)          # twice
    fig.canvas.draw()
    badges = [t for t in _band_texts(fig, "header") if spec.badge.replace("_", " ") in t.get_text()]
    footers = [t for t in _band_texts(fig, "footer") if "Scope:" in t.get_text()]
    assert len(badges) == 1 and len(footers) == 1
    plt.close(fig)


def test_standalone_has_a_title_notebook_does_not():
    spec = R.viz_by_id("wetting_front_sweep")
    data = R.producer_data(spec)
    fs, _ = D.figure_wetting_front(data, presentation="standalone", ceiling=spec.fidelity_ceiling,
                                   title=spec.title)
    fs.canvas.draw()
    assert any(spec.title in t.get_text() for t in _band_texts(fs, "header"))
    fn, _ = D.figure_wetting_front(data, presentation="notebook", ceiling=spec.fidelity_ceiling,
                                   title=spec.title)
    fn.canvas.draw()
    assert all(spec.title not in t.get_text() for t in _band_texts(fn, "header"))
    plt.close(fs); plt.close(fn)


@pytest.mark.slow
def test_pressure_sweep_has_one_shared_x_label_and_reference_key():
    fig, spec, _ = _build("cameron_pressure_sweep", "figure_cameron_pressure_sweep", True)
    plot = fig._tour_layout["plot"]
    assert plot._supxlabel is not None and plot._supxlabel.get_text() == "Pressure (bar)"
    assert all(not ax.get_xlabel() for ax in fig.axes)      # no repeated per-panel x labels
    handles = fig._tour_layout["header"].legends
    labels = [t.get_text() for lg in handles for t in lg.get_texts()]
    assert any("selected pressure" in s for s in labels)    # the red star is explained once
    plt.close(fig)


def test_wetting_front_window_makes_the_event_visible():
    spec = R.viz_by_id("wetting_front_sweep")
    data = R.producer_data(spec)
    fig, _ = D.figure_wetting_front(data, ceiling=spec.fidelity_ceiling)
    ax = fig.axes[0]
    ts = data["t_saturate_s"]
    xmax = ax.get_xlim()[1]
    assert xmax < 5.0 and ts < xmax                          # zoomed to the event, not the 100 s trace
    plt.close(fig)


def test_lb_profile_uses_a_readable_scale_not_six_decimal_ticks():
    spec = R.viz_by_id("puck_flow_field")
    fig, _ = D.figure_stokes_profile(R.producer_data(spec), ceiling=spec.fidelity_ceiling)
    fig.canvas.draw()
    ax = fig.axes[0]
    xticks = [t.get_text() for t in ax.get_xticklabels() if t.get_text().strip()]
    assert not any("0.0000" in s for s in xticks)            # no row of six-decimal near-zeros
    ylabels = [t.get_text() for t in ax.get_yticklabels()]
    assert "centre" in ylabels and "lower wall" in ylabels   # walls/centre labelled
    plt.close(fig)


def test_pack_figure_hides_lattice_ticks():
    spec = R.viz_by_id("grain_pack_3d")
    fig, _ = D.figure_pack_slice(R.producer_data(spec), ceiling=spec.fidelity_ceiling)
    fig.canvas.draw()
    # the two imshow panels expose no numeric lattice ticks (colorbar axis may keep its scale)
    imshow_axes = [ax for ax in fig.axes if ax.images and not ax.get_label().startswith("<colorbar")]
    for ax in imshow_axes:
        assert not [t.get_text() for t in ax.get_xticklabels() if t.get_text().strip()]
        assert not [t.get_text() for t in ax.get_yticklabels() if t.get_text().strip()]
    plt.close(fig)
