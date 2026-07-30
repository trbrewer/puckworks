"""Round-10, second review: the observation universe, the geometry authority, and total validators.

An independent second review of the same commit found four things the first review did not, and one
of them is the most interesting kind of defect this repository keeps producing — a *common-mode*
assumption shared by two implementations that were built to be independent.

The oracle and the production corpus manifest both treated "every retained sample record contributes
three named-solute observations" as an axiom. Neither read the source columns those observations are
measured in. The reviewer deleted `CF`, `TR` and `5CQA` from a copy of `bioactives.csv` — every
scored column in the study — and the oracle still certified 44 records and 132 observations without
raising. The grouping algorithms were genuinely independent; their premise was not.

The tests here are organised by finding, and every mutation is one the review reproduced.
"""
from __future__ import annotations

import ast
import copy
import json
import pathlib
import subprocess
import sys
import tempfile

import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from puckworks.paper_a import source_resampling_oracle as ORACLE  # noqa: E402
from puckworks.paper_a import transfer_contract as TC  # noqa: E402
from puckworks.paper_a import transfer_semantics as TS  # noqa: E402

ENDPOINT_JSON = REPO / "docs" / "paper1_resource" / "PAPER_A_ENDPOINT_PROPAGATION.json"


def _endpoint():
    return json.loads(ENDPOINT_JSON.read_text(encoding="utf-8"))


# ── P1-2: the scored observation universe ───────────────────────────────────────────────────
def _source_lines():
    text = ORACLE.SOURCE_CSV.read_text(encoding="utf-8")
    lines = text.splitlines()
    header_index = next(i for i, line in enumerate(lines) if line.startswith("sample,"))
    return lines, header_index, lines[header_index].split(",")


def _mutated_source(mutate) -> pathlib.Path:
    """Write a mutated copy of the source CSV. The committed source is never touched."""
    lines, _index, _header = _source_lines()
    lines = list(lines)
    mutate(lines)
    handle = tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False, encoding="utf-8")
    with handle as fh:
        fh.write("\n".join(lines) + "\n")
    return pathlib.Path(handle.name)


def _drop_column(name: str):
    _lines, index, header = _source_lines()
    position = header.index(name)

    def mutate(lines):
        for i in range(index, len(lines)):
            if not lines[i].strip():
                continue
            cells = lines[i].split(",")
            if len(cells) > position:
                del cells[position]
            lines[i] = ",".join(cells)
    return mutate


def _set_cell(column: str, value: str, sample: str = "A12"):
    _lines, index, header = _source_lines()
    position = header.index(column)

    def mutate(lines):
        for i in range(index + 1, len(lines)):
            if lines[i].startswith(sample + ","):
                cells = lines[i].split(",")
                cells[position] = value
                lines[i] = ",".join(cells)
                return
        raise AssertionError("sample %r not found in the source" % sample)
    return mutate


def test_the_committed_source_yields_the_documented_census():
    """132 must be a RESULT of source validation, not 44 x 3."""
    records = ORACLE.read_source_records()
    assert len(records) == 44
    assert sum(len(ORACLE.observation_ids(r)) for r in records) == 132
    for record in records:
        assert [o["solute"] for o in record["observations"]] == list(ORACLE.SOLUTES)


def test_every_scored_solute_declares_its_source_column():
    """The map is the point of the fix: a solute with no column is an unmeasured claim."""
    assert dict(ORACLE.ANALYTE_COLUMNS) == {"caffeine": "CF", "trigonelline": "TR", "5CQA": "5CQA"}
    for _solute, column in ORACLE.ANALYTE_COLUMNS:
        assert column in ORACLE.REQUIRED_COLUMNS


@pytest.mark.parametrize("name,mutate,expect", [
    ("missing CF column", _drop_column("CF"), "CF"),
    ("missing TR column", _drop_column("TR"), "TR"),
    ("missing 5CQA column", _drop_column("5CQA"), "5CQA"),
    ("blank CF cell", _set_cell("CF", ""), "blank"),
    ("blank TR cell", _set_cell("TR", "   "), "blank"),
    ("non-numeric TR cell", _set_cell("TR", "n/a"), "non-numeric"),
    ("non-numeric 5CQA cell", _set_cell("5CQA", "below LOD"), "non-numeric"),
    ("NaN analyte cell", _set_cell("CF", "NaN"), "non-finite"),
    ("positive infinite analyte cell", _set_cell("CF", "inf"), "non-finite"),
    ("negative infinite analyte cell", _set_cell("5CQA", "-inf"), "non-finite"),
])
def test_the_oracle_refuses_a_source_that_cannot_supply_the_observations(name, mutate, expect):
    """The reproduced common-mode failure: a CSV with no scored columns certified 132 observations."""
    path = _mutated_source(mutate)
    try:
        with pytest.raises(ValueError, match=expect):
            ORACLE.read_source_records(path)
    finally:
        path.unlink()


def test_the_oracle_names_the_sample_solute_and_source_column():
    """"132 != 132" would not tell anyone which cell to open."""
    path = _mutated_source(_set_cell("TR", "", sample="R19"))
    try:
        with pytest.raises(ValueError) as exc:
            ORACLE.read_source_records(path)
    finally:
        path.unlink()
    message = str(exc.value)
    assert "R19" in message and "trigonelline" in message and "TR" in message


def test_observation_ids_come_from_validated_cells_only():
    record = {"sample_id": "A12", "observations": ({"solute": "caffeine"},)}
    assert ORACLE.observation_ids(record) == ["A12|caffeine"]
    with pytest.raises(ValueError, match="no validated scored observations"):
        ORACLE.observation_ids({"sample_id": "A12", "observations": ()})
    with pytest.raises(ValueError, match="duplicate observation ids"):
        ORACLE.observation_ids({"sample_id": "A12",
                                "observations": ({"solute": "caffeine"},
                                                 {"solute": "caffeine"})})


def test_the_oracle_still_shares_no_grouping_code_with_production():
    """The independent analyte map must not have been imported from the contract."""
    tree = ast.parse((REPO / "puckworks" / "paper_a"
                      / "source_resampling_oracle.py").read_text(encoding="utf-8"))
    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(a.name for a in node.names)
        elif isinstance(node, ast.ImportFrom):
            imported.add(node.module or "")
            imported.update("%s.%s" % (node.module or "", a.name) for a in node.names)
    assert not any("transfer_contract" in m for m in imported), sorted(imported)

    called = {n.func.id for n in ast.walk(tree)
              if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)}
    called |= {n.func.attr for n in ast.walk(tree)
               if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)}
    for forbidden in ("cluster_key_of", "stratum_key_of", "cluster_membership",
                      "scheme_design", "resampling_design", "build_transfer_corpus_manifest"):
        assert forbidden not in called, forbidden


def test_the_two_analyte_maps_agree_but_are_declared_separately():
    """Independence is the point; agreement is the check. Two copies that DISAGREE is a real defect."""
    assert dict(ORACLE.ANALYTE_COLUMNS) == dict(TC.SOLUTE_SOURCE_COLUMNS)
    assert ORACLE.SOLUTES == TC.SOLUTES


# ── P1-2: the production manifest's admission rule ──────────────────────────────────────────
def _source_rows():
    from puckworks import data as d
    return d.angeloni_bioactives()


def test_the_production_manifest_reads_the_scored_columns():
    rows = [dict(r) for r in _source_rows()]
    manifest = TC.build_transfer_corpus_manifest(rows)
    assert (manifest["n_held_out_records"], manifest["n_observations"]) == (44, 132)
    assert TC.validate_corpus_manifest(manifest, True) == []


@pytest.mark.parametrize("column,value,expect", [
    ("CF", "", "blank"),
    ("TR", "n/a", "non-numeric"),
    ("5CQA", "nan", "non-finite"),
    ("CF", "inf", "non-finite"),
])
def test_the_production_manifest_refuses_an_unscoreable_retained_row(column, value, expect):
    """Byte-identical output for valid data; a refusal, not a phantom observation, for invalid."""
    rows = [dict(r) for r in _source_rows()]
    target = next(r for r in rows if r["granulometry"] in ("C", "F"))
    target[column] = value
    with pytest.raises(ValueError, match=expect):
        TC.build_transfer_corpus_manifest(rows)


def test_a_solute_without_a_declared_source_column_is_refused():
    with pytest.raises(ValueError, match="no source column is declared"):
        TC.build_transfer_corpus_manifest(_source_rows(), solutes=("caffeine", "melanoidin"))


def test_dropping_a_scored_column_entirely_is_refused_by_production_too():
    rows = [{k: v for k, v in r.items() if k != "CF"} for r in _source_rows()]
    with pytest.raises(ValueError, match="has no 'CF' column"):
        TC.build_transfer_corpus_manifest(rows)


@pytest.mark.parametrize("name,mutate,expect", [
    ("top-level solute renamed",
     lambda m: m.__setitem__("solutes", ["caffeine", "trigonelline", "chlorogenic acid"]),
     "expected exactly"),
    ("top-level solute duplicated",
     lambda m: m.__setitem__("solutes", ["caffeine", "caffeine", "5CQA"]),
     "expected exactly"),
    ("top-level solutes reordered",
     lambda m: m.__setitem__("solutes", ["5CQA", "caffeine", "trigonelline"]),
     "canonical order"),
    ("n_solutes wrong",
     lambda m: m.__setitem__("n_solutes", 2),
     "n_solutes"),
    ("record solute renamed",
     lambda m: m["records"][0].__setitem__("solutes", ["caffeine", "trigonelline", "CQA"]),
     "expected exactly"),
    ("record solute duplicated",
     lambda m: m["records"][3].__setitem__("solutes", ["caffeine", "caffeine", "5CQA"]),
     "expected exactly"),
    ("record solutes reordered",
     lambda m: m["records"][7].__setitem__("solutes", ["trigonelline", "caffeine", "5CQA"]),
     "canonical order"),
    ("records not a list",
     lambda m: m.__setitem__("records", {}),
     "expected a list"),
    ("record not a mapping",
     lambda m: m["records"].__setitem__(2, "A14"),
     "expected a mapping"),
])
def test_manifest_solute_label_mutations_all_fail(name, mutate, expect):
    """The predecessor compared only the LENGTH of each record's solute list."""
    manifest = copy.deepcopy(TC.build_transfer_corpus_manifest(_source_rows()))
    mutate(manifest)
    problems = TC.validate_corpus_manifest(manifest, True)
    assert problems, "FALSE GREEN: %s" % name
    assert any(expect in p for p in problems), (name, expect, problems)


def test_a_relabelled_record_with_a_refreshed_hash_still_fails():
    """A refreshed self-hash proves only that someone remembered to rehash."""
    manifest = copy.deepcopy(TC.build_transfer_corpus_manifest(_source_rows()))
    manifest["records"][0]["solutes"] = ["caffeine", "trigonelline", "CQA"]
    manifest["manifest_sha256"] = TC.sha256_of(manifest["records"])
    problems = TC.validate_corpus_manifest(manifest, True)
    assert any("expected exactly" in p for p in problems), problems


def test_the_manifest_validator_never_raises():
    for junk in ({}, {"records": None}, {"records": [None]}, {"records": [{}]},
                 {"records": [], "n_solutes": "three"}):
        assert isinstance(TC.validate_corpus_manifest(junk, True), list)


# ── P1-1: typed semantics as the sole geometry authority ────────────────────────────────────
#: Publication renderers. Artefact construction and validation may read the cached flags; prose may
#: not, because the flags are a second authority for a fact the bounds already determine.
_RENDERER_SOURCES = ("tools/paper_a_transfer_text.py", "tools/paper_a_figure_captions.py",
                     "tools/paper_a_supplement.py", "tools/paper_a_front_matter.py")

_CACHED_ZERO_FLAGS = {"contains_zero_full_precision", "excludes_zero_full_precision"}


@pytest.mark.parametrize("relative", _RENDERER_SOURCES)
def test_publication_renderers_do_not_read_the_cached_zero_flags(relative):
    """An AST guard, so reintroducing the shortcut fails rather than merely being noticed later."""
    tree = ast.parse((REPO / relative).read_text(encoding="utf-8"))
    found = {node.value for node in ast.walk(tree)
             if isinstance(node, ast.Constant) and node.value in _CACHED_ZERO_FLAGS}
    assert not found, (
        "%s reads %r directly. Interval geometry has one authority — the full-precision bounds, "
        "through transfer_semantics — and a cached flag is a second one that a mutated or "
        "unvalidated record can make disagree." % (relative, sorted(found)))


def test_the_contract_may_still_read_them():
    """Non-vacuity: the guard must be scoped to renderers, not to the whole repository."""
    source = (REPO / "puckworks" / "paper_a" / "transfer_contract.py").read_text(encoding="utf-8")
    assert "contains_zero_full_precision" in source


def test_the_renderer_follows_the_bounds_when_the_cached_flag_contradicts_them():
    """The exact contradiction the review asked for: bounds say BELOW, the cache says CONTAINS."""
    from tools import paper_a_transfer_text as TT

    ep = _endpoint()
    corpus = json.loads(TT.CORPUS_JSON.read_text(encoding="utf-8"))
    loss = json.loads(TT.LOSS_JSON.read_text(encoding="utf-8"))

    mutated = copy.deepcopy(ep)
    for row in mutated["rows"]:
        interval = row["resampling"][TC.PRIMARY_SCHEME]["interval"]
        interval["full_precision_pp"] = {"lower": -0.8, "upper": -0.1}
        interval["contains_zero_full_precision"] = True
        interval["excludes_zero_full_precision"] = False

    text = TT.block_endpoint_reading(mutated, corpus, loss)
    assert "excludes zero on the negative side at 38 g, 40 g and 42 g" in text
    assert "contains zero at" not in text

    # …and the validator refuses the contradictory record outright.
    interval = mutated["rows"][0]["resampling"][TC.PRIMARY_SCHEME]["interval"]
    problems = TC.validate_interval_record(interval)
    assert any("full-precision bounds imply" in p for p in problems), problems


@pytest.mark.parametrize("bounds,expect", [
    ([(-0.9, -0.1), (-0.8, -0.2), (-0.7, -0.3)],
     "excludes zero on the negative side at 38 g, 40 g and 42 g"),
    ([(-0.9, 0.1), (-0.8, 0.2), (-0.7, 0.3)],
     "contains zero at 38 g, 40 g and 42 g"),
    ([(0.1, 0.9), (0.2, 0.8), (0.3, 0.7)],
     "excludes zero on the positive side at 38 g, 40 g and 42 g"),
    ([(-0.9, -0.1), (-0.8, 0.2), (0.3, 0.7)],
     "excludes zero on the negative side at 38 g, contains zero at 40 g, and excludes zero "
     "on the positive side at 42 g"),
    ([(-0.9, 0.0), (-0.8, 0.2), (-0.7, 0.3)],
     "contains zero at 38 g, 40 g and 42 g"),
])
def test_the_endpoint_sweep_names_every_relation_present(bounds, expect):
    """Including ABOVE, which no current Paper A range occupies — the untested branch is the risk."""
    from tools import paper_a_transfer_text as TT

    ep = copy.deepcopy(_endpoint())
    corpus = json.loads(TT.CORPUS_JSON.read_text(encoding="utf-8"))
    loss = json.loads(TT.LOSS_JSON.read_text(encoding="utf-8"))
    for row, (lower, upper) in zip(ep["rows"], bounds):
        row["resampling"][TC.PRIMARY_SCHEME]["interval"] = TC.interval_record(lower, upper)
    assert expect in TT.block_endpoint_reading(ep, corpus, loss)


def test_group_by_relation_returns_every_relation_key():
    """So a caller cannot mistake "nothing above zero" for "I never handled above zero"."""
    groups = TS.group_by_relation([("a", TS.interval_semantics(-0.5, -0.1))])
    assert set(groups) == set(TS.ZeroRelation)
    assert groups[TS.ZeroRelation.BELOW] == ["a"]
    assert groups[TS.ZeroRelation.ABOVE] == []


def test_group_by_relation_refuses_untyped_input():
    with pytest.raises(TypeError, match="typed IntervalSemantics"):
        TS.group_by_relation([("a", {"contains_zero_full_precision": True})])


# ── P2-1 / P2-2: what the supplement says about itself ──────────────────────────────────────
def _supplement() -> str:
    return (REPO / "docs" / "submission"
            / "PAPER_A_JFE_SUPPLEMENT.md").read_text(encoding="utf-8")


def test_table_s6_does_not_claim_to_contain_membership_it_does_not_show():
    text = _supplement()
    assert "Cluster keys, strata and membership for every declared scheme" not in text
    assert "Exact cluster-by-cluster membership under every scheme" in text
    assert "Table S7 lists the held-out records with their primary cluster" in text


def test_the_audited_bound_is_named_explicitly():
    text = " ".join(_supplement().split())
    assert "The **upper** bound's sign is stable across seeds" in text
    assert "The bound's sign is" not in text


def test_the_audit_prose_still_states_its_exact_scope():
    text = " ".join(_supplement().split())
    assert "Monte Carlo audit of one target only — 40 g, cond_in_variety, primary fitting loss" \
        in text
    assert "0.000520" in text and "0.000466" in text


# ── P2-3: validators are total, accessors are controlled ────────────────────────────────────
@pytest.mark.parametrize("targets,expect", [
    ("nope", "expected a list"),
    (None, "expected a list"),
    ({}, "expected a list"),
    (["not-a-number", 40.0, 42.0], "targets[0] must be a finite JSON number"),
    ([38.0, float("nan"), 42.0], "targets[1] must be finite"),
    ([38.0, 40.0, float("inf")], "targets[2] must be finite"),
    ([True, 40.0, 42.0], "targets[0] must be a finite JSON number"),
    ([38.0, 40.0], "exact set and order"),
    ([38.0, 42.0, 40.0], "exact set and order"),
])
def test_malformed_endpoint_targets_return_named_problems_and_never_raise(targets, expect):
    """`validate_endpoint_contract` raised ValueError from a list comprehension on a bad target."""
    artifact = {"endpoint": dict(TC.endpoint_object(), targets=targets),
                "rows": [{"m_target_g": v} for v in TC.ENDPOINT_TARGETS]}
    problems = TC.validate_endpoint_contract(artifact)
    assert problems, targets
    assert any(expect in p for p in problems), (targets, expect, problems)


def test_one_bad_target_does_not_also_produce_a_misleading_order_complaint():
    artifact = {"endpoint": dict(TC.endpoint_object(), targets=["x", 40.0, 42.0]),
                "rows": [{"m_target_g": v} for v in TC.ENDPOINT_TARGETS]}
    problems = TC.validate_endpoint_contract(artifact)
    assert not any("exact set and order" in p for p in problems), problems


@pytest.mark.parametrize("audits,expect", [
    ([3], "stability_audits[0] is int"),
    (["x"], "stability_audits[0] is str"),
    ([None], "stability_audits[0] is NoneType"),
    ([{"target": 7}], "stability_audits[0].target is int"),
    ([{"target": "40 g"}], "stability_audits[0].target is str"),
    ("not-a-list", "carries no `stability_audits` list"),
])
def test_a_malformed_audit_element_raises_a_controlled_keyerror(audits, expect):
    """It used to raise AttributeError: 'int' object has no attribute 'get'."""
    with pytest.raises(KeyError) as exc:
        TS.find_exact_audit({"stability_audits": audits}, TS.AUDITED_TARGET)
    assert expect in str(exc.value), (audits, str(exc.value))


def test_has_exact_audit_is_false_rather_than_raising_on_a_malformed_list():
    assert TS.has_exact_audit({"stability_audits": [3]}, TS.AUDITED_TARGET) is False
    assert TS.has_exact_audit(_endpoint(), TS.AUDITED_TARGET) is True


# ── the whole chain, on the committed tree ──────────────────────────────────────────────────
def test_the_artefact_checker_passes_on_the_committed_tree():
    result = subprocess.run([sys.executable, "tools/paper_a_transfer_artifacts.py", "--check"],
                            cwd=REPO, capture_output=True, text=True)
    assert result.returncode == 0, result.stderr or result.stdout


def test_the_checker_reports_a_named_problem_rather_than_a_traceback(monkeypatch):
    """A source-contract failure must exit non-zero with a diagnostic, not die."""
    from tools import paper_a_transfer_artifacts as ART

    def refuse(*_args, **_kwargs):
        raise ValueError("source row A12: 'CF' is blank, so its caffeine observation is not "
                         "scoreable")

    monkeypatch.setattr(ART, "reference_manifest", refuse)
    problems = ART.check()
    assert problems and problems[0].startswith("source-observation contract: ")
    assert "caffeine" in problems[0]
