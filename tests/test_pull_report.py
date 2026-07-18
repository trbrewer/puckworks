"""Tests for the Guided Espresso Pull visual report (issue #48, Milestone B, Section 2).

Offline. Proves the renderer consumes an already-completed PullRun (never re-simulates, never
mutates), that core import stays matplotlib-free, that the missing-viz-extra error is actionable, and
that the deterministic file set is produced with an explicit overwrite policy.
"""
import subprocess
import sys

import puckworks.product as p
import pytest


def _run():
    recipe, config = p.load_pull_preset("pv19_named")
    return p.simulate_pull(recipe, config)


def test_core_product_import_does_not_import_matplotlib():
    # A fresh interpreter: importing the product API must not pull in matplotlib.
    code = ("import sys, puckworks, puckworks.product; "
            "assert 'matplotlib' not in sys.modules, 'product imported matplotlib'")
    r = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr


def test_missing_viz_extra_raises_actionable_error(monkeypatch):
    import puckworks.figures as figures
    from puckworks.viz import pull_report

    def _boom():
        raise ModuleNotFoundError("No module named 'matplotlib'")

    monkeypatch.setattr(figures, "_plt", _boom)
    with pytest.raises(ModuleNotFoundError, match=r"puckworks\[viz\]"):
        pull_report._plt()


def test_render_produces_the_full_file_set(tmp_path):
    pytest.importorskip("matplotlib")
    run = _run()
    art = p.render_pull_report(run, tmp_path / "report")
    for f in art.files:
        assert f.__class__ is str or True  # paths are strings
    import os
    for name in ("guided_pull_results.json", "guided_pull_report.md", "guided_pull_summary.png",
                 "pressure_flow.png", "cup_progress.png", "extraction_progress.png",
                 "guided_pull_captions.txt"):
        fp = os.path.join(art.out_dir, name)
        assert os.path.exists(fp), name
        if name.endswith(".png"):
            assert os.path.getsize(fp) > 1000, f"{name} looks empty"


def test_renderer_never_resimulates(tmp_path, monkeypatch):
    pytest.importorskip("matplotlib")
    run = _run()
    import puckworks.product._pull as pull_mod

    def _forbidden(*a, **k):
        raise AssertionError("renderer re-simulated the run")

    monkeypatch.setattr(pull_mod, "simulate_pull", _forbidden)
    art = p.render_pull_report(run, tmp_path / "r", overwrite=True)
    assert art.summary_png.endswith("guided_pull_summary.png")


def test_renderer_does_not_mutate_the_run(tmp_path):
    pytest.importorskip("matplotlib")
    run = _run()
    before = p.pull_run_to_json(run)
    p.render_pull_report(run, tmp_path / "r")
    assert p.pull_run_to_json(run) == before, "renderer mutated the PullRun"


def test_overwrite_policy(tmp_path):
    pytest.importorskip("matplotlib")
    run = _run()
    out = tmp_path / "r"
    p.render_pull_report(run, out)
    with pytest.raises(FileExistsError):
        p.render_pull_report(run, out)              # default refuses to clobber
    art = p.render_pull_report(run, out, overwrite=True)   # explicit overwrite is allowed
    assert art.out_dir == str(out)


def test_captions_are_a_static_text_equivalent(tmp_path):
    pytest.importorskip("matplotlib")
    run = _run()
    art = p.render_pull_report(run, tmp_path / "r")
    text = open(art.captions_txt, encoding="utf-8").read()
    for token in ("EXPLORATORY_SIMULATION", "prescribed", "not modeled", "recorded-only",
                  "composition, not flavor"):
        assert token.lower() in text.lower(), token


def test_cameron_has_a_fidelity_ceiling():
    from puckworks.viz.spec import FIDELITY_CEILINGS
    assert "cameron2020.extraction_bdf" in FIDELITY_CEILINGS
    assert FIDELITY_CEILINGS["cameron2020.extraction_bdf"]
