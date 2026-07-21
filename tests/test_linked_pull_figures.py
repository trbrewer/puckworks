"""Result-bound, presentational relay figures (§8, §12, §15.3).

Figures draw ONLY from the completed result's payloads — zero model/producer calls at draw time, no hidden
permeability fallback, correct component ownership, provenance-hashed source stages.
"""
import io

import pytest

pytest.importorskip("matplotlib")
import matplotlib  # noqa: E402

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from puckworks.product.linked_pull import RelayRequest, execute_illustrative_linked_pull  # noqa: E402
from puckworks.product.linked_pull_figures import figures_by_owner, relay_figures  # noqa: E402


@pytest.fixture(scope="module")
def result():
    return execute_illustrative_linked_pull(RelayRequest(mode="fast"))


def test_result_carries_figure_payloads(result):
    ids = {p["figure_id"] for p in result["figure_payloads"]}
    assert {"cameron_shot", "synthetic_pack", "wetting_front"} <= ids
    for p in result["figure_payloads"]:
        assert p["owner_component_ids"] and p["viz_spec_id"] and p["source_stage_hashes"]


def test_figures_render_with_every_model_and_producer_broken(result, monkeypatch):
    # break every scientific entry point the figures could touch; they must still render from the result
    import puckworks.viz.producers as P
    from puckworks.models.brewer2026 import pack_generator as pg
    from puckworks.models.cameron2020 import extraction_bdf as cam
    from puckworks.models.foster2025 import infiltration as inf

    def boom(*a, **k):
        raise AssertionError("a model/producer was called during figure drawing")

    for mod, names in [(P, ["cameron_shot_timeseries", "pack_porosity_slice", "wetting_front"]),
                       (cam, ["simulate_shot", "grind_microstructure", "bed_depth"]),
                       (inf, ["front_from_pressure"]), (pg, ["make_pack", "hetero_field"])]:
        for n in names:
            if hasattr(mod, n):
                monkeypatch.setattr(mod, n, boom)

    figs = relay_figures(result)
    assert len(figs) >= 3
    for f in figs:
        b = io.BytesIO(); f.figure.savefig(b, format="png"); plt.close(f.figure)
        assert b.getbuffer().nbytes > 2000


def test_figure_source_hashes_exist_in_the_result(result):
    stage_hashes = {s["component_id"]: s["content_hash"] for s in result["stages"]}
    for f in relay_figures(result):
        plt.close(f.figure)
        for h in f.source_stage_hashes:
            assert h in stage_hashes.values()


def test_figures_are_owned_by_the_correct_component(result):
    by_owner = figures_by_owner(result)
    for figs in by_owner.values():
        for f in figs:
            plt.close(f.figure)
    assert "cameron2020.extraction_bdf" in by_owner        # the shot figure sits under Cameron
    assert "brewer2026.pack_generator" in by_owner          # the pack figure under the pack generator
    # the Cameron shot figure is NOT shown under unrelated components
    assert all("cameron_shot" not in [f.figure_id for f in by_owner.get(cid, [])]
               for cid in ("wadsworth2026.grindmap", "brewer2026.streamtube"))


def test_no_hidden_permeability_fallback_in_figure_layer():
    import inspect

    from puckworks.product import linked_pull_figures as F
    src = inspect.getsource(F)
    assert "2.0e-13" not in src and "2e-13" not in src
    # the draw path calls no models/producers
    assert "simulate_shot" not in src and "front_from_pressure" not in src and "make_pack" not in src


def test_every_relay_figure_keeps_badge_and_scope(result):
    for f in relay_figures(result):
        plt.close(f.figure)
        assert f.evidence_badge and f.fidelity_ceiling
