"""Figure 1's dependency graph and Figure S3's layout, asserted rather than eyeballed.

Round-8 P1-5 and P2-2. Both defects survived every existing figure test because those tests check
that an image FILE exists and is non-trivial. An exported PNG can exist, be the right size, and
still draw the wrong scientific graph or clip its own panel titles.

  * P1-5: Figure 1's caption promises arrows show actual data/parameter dependency, but the figure
    drew recalibration -> LOCO -> cross-grind holdout in series. The cross-grind benchmark does not
    consume the LOCO output: LOCO refits on 8 of 9 optimal-grind conditions per fold, while the
    transfer benchmark fits all 9 once and freezes that calibration. They are parallel siblings.
  * P2-2: Supplementary Figure S3's two panel titles overran the central margin and clipped each
    other at publication width.

The graph is tested as data, before any rendering; the layout is tested on laid-out artist extents.
"""
from __future__ import annotations

import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

CAPTIONS = REPO / "docs" / "figures" / "PAPER_A_CAPTIONS.md"


# ── Figure 1: dependency semantics ─────────────────────────────────────────────────────────
def _fig1():
    from puckworks import figures_paper_a as F
    return F


def test_fig1_declares_every_edge_between_declared_nodes():
    F = _fig1()
    for a, b in F.FIG1_EDGES:
        assert a in F.FIG1_NODES, f"edge source {a!r} is not a declared node"
        assert b in F.FIG1_NODES, f"edge target {b!r} is not a declared node"


def test_fig1_has_no_loco_to_cf_dependency():
    """The round-8 P1-5 defect, stated directly."""
    F = _fig1()
    assert ("loco", "cf_transfer") not in F.FIG1_EDGES
    assert "cf_transfer" not in F._fig1_ancestors("loco")
    assert "loco" not in F._fig1_ancestors("cf_transfer"), (
        "the cross-grind holdout must not descend from the LOCO analysis: it uses a different "
        "calibration instance (9/9 fit once and frozen, not 8/9 per fold)")


def test_fig1_loco_and_cf_are_parallel_children_of_the_recalibration():
    F = _fig1()
    assert ("angeloni_recal", "loco") in F.FIG1_EDGES
    assert ("angeloni_recal", "cf_transfer") in F.FIG1_EDGES
    assert F._fig1_ancestors("loco") == F._fig1_ancestors("cf_transfer")


def test_fig1_external_branch_does_not_inherit_angeloni_validation():
    F = _fig1()
    ancestors = F._fig1_ancestors("external")
    for forbidden in ("angeloni_recal", "loco", "cf_transfer"):
        assert forbidden not in ancestors, (
            f"the external trajectory must not descend from {forbidden!r}; it freezes the source "
            "kinetics and profiles its own level")


@pytest.mark.parametrize("edge", [
    ("loco", "cf_transfer"), ("cf_transfer", "loco"), ("angeloni_recal", "external")])
def test_fig1_forbidden_edges_are_declared_and_absent(edge):
    F = _fig1()
    assert edge in F.FIG1_FORBIDDEN_EDGES
    assert edge not in F.FIG1_EDGES


def test_fig1_graph_is_acyclic():
    F = _fig1()
    for node in F.FIG1_NODES:
        assert node not in F._fig1_ancestors(node), f"{node!r} is its own ancestor"


def test_fig1_reintroducing_the_forbidden_edge_would_be_caught():
    """Mutation: with the bad edge present, the parallelism assertion must fail."""
    F = _fig1()
    mutated = tuple(F.FIG1_EDGES) + (("loco", "cf_transfer"),)
    assert "loco" in F._fig1_ancestors("cf_transfer", edges=mutated)


def test_fig1_labels_state_both_calibration_scopes():
    """A reader must be able to see WHY the branches differ, not just that they do."""
    F = _fig1()
    assert "8 of 9" in F.FIG1_NODES["loco"]["label"]
    assert "9" in F.FIG1_NODES["cf_transfer"]["label"]
    assert "freeze" in F.FIG1_NODES["cf_transfer"]["label"].lower()


def test_fig1_caption_states_the_branches_are_parallel():
    text = CAPTIONS.read_text()
    lowered = text.lower()
    assert "parallel" in lowered
    assert "does not consume" in lowered or "does **not** consume" in lowered, (
        "the Figure 1 caption must say the cross-grind holdout does not use the LOCO output")


# ── Figure S3: rendered layout ──────────────────────────────────────────────────────────────
def _render_s3(tmp_path):
    pytest.importorskip("matplotlib")
    from puckworks import figures_paper_a as F
    try:
        return F.fig7_per_group_diagnostics(outdir=str(tmp_path), return_fig=True)
    except FileNotFoundError as exc:                       # results bundle absent on a lean lane
        pytest.skip(f"figure results bundle unavailable: {exc}")


def test_s3_panel_titles_do_not_overlap(tmp_path):
    _path, fig = _render_s3(tmp_path)
    fig.canvas.draw()
    r = fig.canvas.get_renderer()
    boxes = [ax.title.get_window_extent(r) for ax in fig.axes if ax.get_title()]
    assert len(boxes) >= 2, "expected two titled panels"
    boxes.sort(key=lambda b: b.x0)
    for left, right in zip(boxes, boxes[1:]):
        assert left.x1 <= right.x0, (
            "Supplementary Figure S3's panel titles overlap across the central margin "
            f"({left.x1:.1f} > {right.x0:.1f}); shorten them and move detail to the caption")


def test_s3_suptitle_does_not_overlap_the_panel_titles(tmp_path):
    _path, fig = _render_s3(tmp_path)
    fig.canvas.draw()
    r = fig.canvas.get_renderer()
    sup = fig._suptitle.get_window_extent(r)
    for ax in fig.axes:
        if not ax.get_title():
            continue
        assert ax.title.get_window_extent(r).y1 <= sup.y0, "the suptitle collides with a panel title"


def test_s3_titles_stay_inside_the_canvas(tmp_path):
    _path, fig = _render_s3(tmp_path)
    fig.canvas.draw()
    r = fig.canvas.get_renderer()
    w, h = fig.canvas.get_width_height()
    for ax in fig.axes:
        if not ax.get_title():
            continue
        b = ax.title.get_window_extent(r)
        assert b.x0 >= -1 and b.x1 <= w + 1 and b.y0 >= -1 and b.y1 <= h + 1, "a title is clipped"


def test_s3_titles_are_short_enough_to_survive_a_narrower_column(tmp_path):
    """Guards the actual failure mode: titles that fit only at review width."""
    from puckworks import figures_paper_a as F
    for title in F.FIG_S3_PANEL_TITLES:
        assert len(title) <= 46, (
            f"panel title {title!r} is {len(title)} characters; it will collide again at journal "
            "width — put the detail in the caption")


def test_s3_caption_carries_the_detail_removed_from_the_titles():
    """Shortening the titles must not lose the scientific content."""
    text = CAPTIONS.read_text().lower()
    for needed in ("not** a temporal trajectory", "nine", "40 g"):
        assert needed.lower() in text, f"the S3 caption no longer states {needed!r}"
