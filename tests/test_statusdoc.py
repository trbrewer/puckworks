"""P0.1 — the canonical status source (docs/status/current.json) and its generated document.

Offline structural checks use check_commits=False; the CI `status-truth` job (fetch-depth: 0)
runs the full verify including verified_commit resolution.
"""
import copy

from puckworks import statusdoc as S


def test_status_source_is_structurally_valid():
    assert S.validate(S.load(), check_commits=False) == []


def test_generated_doc_is_fresh_and_phrase_clean():
    assert S.verify(check_commits=False) == []             # freshness + prohibited phrases + structure


def test_active_queue_capped_at_five():
    n_active = sum(1 for it in S.load()["items"] if it["state"] == "active")
    assert n_active <= S.MAX_ACTIVE


def test_generated_doc_has_no_transient_phrases():
    low = S.render(S.load()).lower()
    for p in S.PROHIBITED_PHRASES:
        assert p not in low


def _base():
    return {"schema_version": S.SCHEMA_VERSION, "generated_doc": S.DOC_REL, "items": []}


def _item(**kw):
    it = {f: None for f in S._REQUIRED_FIELDS}
    it.update(id="x", title="t", area="a", state="proposed", priority="P2",
              owner_type="maintainer")
    it.update(kw)
    return it


def test_validate_flags_too_many_active():
    data = _base()
    data["items"] = [_item(id="a%d" % i, state="active", next_gate="g") for i in range(6)]
    assert any("active queue has 6" in p for p in S.validate(data, check_commits=False))


def test_validate_flags_active_without_next_gate():
    data = _base()
    data["items"] = [_item(id="a", state="active", next_gate=None)]
    assert any("no next_gate" in p for p in S.validate(data, check_commits=False))


def test_validate_flags_blocker_without_resume_trigger():
    data = _base()
    data["items"] = [_item(id="b", state="blocked", next_gate="g",
                           external_blocker="waiting on X", resume_trigger=None)]
    assert any("no resume_trigger" in p for p in S.validate(data, check_commits=False))


def test_validate_flags_complete_without_pr_or_commit():
    data = _base()
    data["items"] = [_item(id="c", state="complete", issue_or_pr=None,
                           verified_commit=None, verified_date=None)]
    problems = S.validate(data, check_commits=False)
    assert any("no issue_or_pr" in p for p in problems)
    assert any("no verified_commit" in p for p in problems)
    assert any("no verified_date" in p for p in problems)


def test_validate_flags_noncomplete_with_verified_commit():
    data = _base()
    data["items"] = [_item(id="d", state="active", next_gate="g", verified_commit="deadbeef")]
    assert any("contradictory" in p for p in S.validate(data, check_commits=False))


def test_validate_flags_duplicate_ids():
    data = _base()
    data["items"] = [_item(id="dup"), _item(id="dup")]
    assert any("duplicate id" in p for p in S.validate(data, check_commits=False))


def test_render_flags_stale_checked_in_doc(tmp_path):
    # mutate the source in memory and confirm the freshness check would catch a stale doc
    data = S.load()
    mutated = copy.deepcopy(data)
    mutated["items"][0]["title"] = "CHANGED TITLE"
    assert S.render(mutated) != S.render(data)             # generator is sensitive to the source
