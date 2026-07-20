"""Per-component narratives for the Full Laboratory Tour (#43).

Offline. Every registered component has a story in chronological process order; the embedded README
model-map snapshot (role / physics / stage) matches the LIVE README verbatim; the espresso-implications
notes exist and are framed as general/caveated, never as validated predictions.
"""
import puckworks
from puckworks.product import lab_component_stories as S


def test_stories_verify_clean_and_snapshot_matches_readme():
    assert S.verify_component_stories() == []


def test_cameron_is_the_first_deep_dive_component():
    ordered = S.ordered_component_ids()
    assert ordered[0] == "cameron2020.extraction_bdf"          # the whole-shot lens leads the tour
    assert ordered.count("cameron2020.extraction_bdf") == 1


def test_every_registered_component_appears_exactly_once_hero_then_chronological():
    ordered = S.ordered_component_ids()
    assert set(ordered) == {c.name for c in puckworks.components()}
    assert len(ordered) == len(set(ordered)) == 25
    # after the hero prefix, the remainder is in chronological process-stage order
    heroes = [c for c in S.HERO_COMPONENT_IDS]
    assert ordered[:len(heroes)] == heroes
    rest = ordered[len(heroes):]
    idx = [S.PROCESS_ORDER.index(S.component_story(cid).process_stage) for cid in rest]
    assert idx == sorted(idx)


def test_each_story_has_role_physics_and_two_layperson_notes():
    for cid in S.ordered_component_ids():
        st = S.component_story(cid)
        assert st.role and st.physics                      # from the README snapshot
        assert st.what_it_computes and st.espresso_implications
        assert st.process_stage in S.PROCESS_ORDER


def test_espresso_notes_are_caveated_not_overclaimed():
    # a standing disclaimer frames the whole section, and no note claims a validated cup prediction
    assert "not validated predictions" in S.STANDING_DISCLAIMER.lower()
    joined = " ".join(S.component_story(cid).espresso_implications.lower()
                      for cid in S.ordered_component_ids())
    for forbidden in ("proves your", "guaranteed", "will taste exactly", "validated prediction of your"):
        assert forbidden not in joined


def test_snapshot_binds_to_readme_and_drift_would_fail(monkeypatch):
    # if a snapshot role/physics no longer matched the live README, verify would flag it
    import copy
    bad = copy.deepcopy(S._README_MODEL_MAP)
    bad["cameron2020.extraction_bdf"] = {**bad["cameron2020.extraction_bdf"], "role": "WRONG ROLE"}
    monkeypatch.setattr(S, "_README_MODEL_MAP", bad)
    problems = S.verify_component_stories()
    assert any("cameron2020.extraction_bdf" in p and "role" in p for p in problems)


def test_a_new_registered_component_without_a_story_fails(monkeypatch):
    class _C:
        name = "newpaper2027.model"
    real = list(puckworks.components())
    monkeypatch.setattr(puckworks, "components", lambda: real + [_C()])
    assert any("newpaper2027.model" in p for p in S.verify_component_stories())
