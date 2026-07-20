"""Offline, fast tests for the viz layer (ROADMAP §8).

The honesty contract made executable: every VizSpec binds to a producer, carries a
valid badge + evidence word + a non-empty fidelity ceiling, every source is
labelled, and the generated gallery reproduces the hand-authored acceptance seed
(modulo the sanctioned Note-1 composite divergences). NOT wired into
run_all_gates; no 3D / LB / video is rendered here.
"""
import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
# the hand-authored acceptance seed is preserved as a permanent fixture; GALLERY.md
# is the machine-generated live gallery (which must reproduce the seed).
SEED = ROOT / "docs/figures/viz/GALLERY_SEED.md"


def test_viz_imports_without_viz3d():
    """The package imports on the core install; the heavy [viz3d] dep (pyvista) is
    NEVER imported at load (lazy-import contract)."""
    import puckworks.viz          # noqa: F401
    import puckworks.viz.producers  # noqa: F401
    import puckworks.viz.registry   # noqa: F401
    assert "pyvista" not in sys.modules


def test_every_vizspec_passes_the_honesty_contract():
    from puckworks.viz import validate_all, VIZZES
    assert len(VIZZES) >= 9
    assert validate_all() == []


def test_producers_are_named_functions_not_hardcoded():
    """Anti-fabrication: every spec's producer resolves to a real callable (numbers
    recompute from a named function, never hand-typed)."""
    import importlib
    from puckworks.viz import VIZZES
    for v in VIZZES:
        fn = getattr(importlib.import_module(v.producer.module), v.producer.function)
        assert callable(fn), v.id


def test_fidelity_ceiling_covers_every_source():
    """No unlabelled source: every component a VizSpec references has a ceiling."""
    from puckworks.viz import VIZZES, FIDELITY_CEILINGS
    for v in VIZZES:
        for c in v.components:
            assert c in FIDELITY_CEILINGS, f"{v.id}: '{c}' has no fidelity ceiling"


def test_a_visual_with_no_producer_or_ceiling_is_rejected():
    """The gate must FAIL a fabricated visual (empty producer / empty ceiling)."""
    from puckworks.viz.spec import VizSpec
    from puckworks.public.schema import Producer
    bad = VizSpec(id="bad", title="x", class_=1,
                  producer=Producer(module="", function="", result_map={}),
                  badge="OBSERVED", evidence_strength="reference",
                  fidelity_ceiling="", render_fn="m:f", components=["nope"], caption="")
    errs = bad.validate()
    assert any("no Producer" in e for e in errs)
    assert any("empty fidelity_ceiling" in e for e in errs)
    assert any("nope" in e for e in errs)


def test_class1_render_is_stamped(tmp_path):
    """A tiny class-1 render returns a non-empty image and the badge is stamped INTO
    the figure (drawn, not just captioned)."""
    pytest.importorskip("matplotlib")
    from puckworks.viz import viz_by_id, render_spec, stamp_fig
    spec = viz_by_id("process_schematic")
    out = render_spec(spec, outdir=str(tmp_path))
    thumb = Path(out["thumb"])
    assert thumb.exists() and thumb.stat().st_size > 1000
    # the stamp writes the badge text onto the figure canvas — search ALL Text artists (the badge may
    # live in a reserved header subfigure for tour figures, or in fig.texts for the ordinary stamp)
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    def all_text(fig):
        out = list(fig.texts)
        for sf in getattr(fig, "subfigs", []):
            out += all_text(sf)
        for ax in fig.axes:
            out += list(ax.texts) + [ax.title, ax.xaxis.label, ax.yaxis.label]
        return out

    fig = plt.figure()
    stamp_fig(fig, spec, commit="deadbeefcafe")
    assert any(spec.badge in t.get_text() for t in all_text(fig))
    plt.close(fig)


# --- the acceptance test: generated gallery reproduces the seed --------------
def _parse(path):
    rows = {}
    for ln in open(path, encoding="utf-8"):
        if ln.startswith("| ") and "|---" not in ln and " id " not in ln:
            c = [x.strip() for x in ln.strip().strip("|").split("|")]
            if len(c) >= 8:
                rid = re.sub(r"\*.*", "", c[0]).strip()
                rows[rid] = {"badge": c[2], "ev": c[3], "ceil": c[5]}
    return rows


def _norm(s):
    return (re.sub(r"\s+", " ", s).replace("–", "-").replace("“", '"')
            .replace("”", '"').replace("'", '"').strip().lower())


# The ONLY sanctioned generated-vs-seed divergences (seed Note 1 + closed vocab):
_SANCTIONED = {
    ("process_schematic", "badge"),   # composite -> strictest lens badge
    ("hidden_puck_movie", "badge"),   # composite -> strictest lens badge
    ("hidden_puck_movie", "ev"),      # 'per-lens (unchanged)' -> closed-vocab floor
}


def test_generated_gallery_reproduces_seed(tmp_path):
    from puckworks.viz.registry import write_gallery
    gen = _parse(write_gallery(str(tmp_path / "gen.md")))
    seed = _parse(SEED)
    assert set(gen) == set(seed), "id set differs from the seed"
    divergences = set()
    for rid in seed:
        for f in ("badge", "ev", "ceil"):
            if _norm(seed[rid][f]) != _norm(gen[rid][f]):
                divergences.add((rid, f))
    # ceilings must be verbatim (no ceiling divergence allowed); badge/ev divergences
    # must be EXACTLY the sanctioned Note-1 set — nothing silently reconciled or added
    assert not any(f == "ceil" for _, f in divergences), \
        f"ceiling drift vs seed: {[d for d in divergences if d[1]=='ceil']}"
    assert divergences == _SANCTIONED, (
        f"unexpected badge/evidence divergences: {divergences ^ _SANCTIONED}")
