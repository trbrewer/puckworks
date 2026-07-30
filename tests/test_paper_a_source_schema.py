"""Round-11 P1-4: the premises the production manifest and the source oracle BOTH accepted.

The two implementations share no membership code, and that separation is what round-9 and round-10
bought. Round 11 found that independence stopping one layer up: four assumptions neither
implementation validated, and agreeing on an unchecked premise is a common mode however separately
you agree on it.

Reproduced at the round-11 commit, all four silently:

    C row marked on_grid=True, with no O-grind counterpart -> admitted; lookup_defined=True
    on_grid="true"      -> admitted as on_grid=False rather than rejected
    T_degC="NaN"        -> admitted; cluster id contains "nan"
    variety=" Arabica " -> silently excluded; zero retained records

    93.40004 -> "93.4"      9.000004 -> "9"
    93.40005 -> "93.4"      9.000005 -> "9"

Every one of them fails here with a named diagnostic, and the unchanged source still reproduces the
exact 44-record / 132-observation corpus with identical membership and identical hashes.
"""
from __future__ import annotations

import copy
import json
import pathlib
import sys
from decimal import Decimal

import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from puckworks import data as D  # noqa: E402
from puckworks.paper_a import source_resampling_oracle as ORACLE  # noqa: E402
from puckworks.paper_a import source_schema as SS  # noqa: E402
from puckworks.paper_a import transfer_contract as TC  # noqa: E402

CORPUS_JSON = REPO / "docs" / "paper1_resource" / "PAPER_A_TRANSFER_CORPUS_CONTRACTS.json"


def _rows():
    return copy.deepcopy(D.angeloni_bioactives())


def _set(rows, sample_id, **fields):
    for r in rows:
        if str(r["sample"]) == sample_id:
            r.update(fields)
            return rows
    raise AssertionError("no source row %r" % sample_id)


# ── 1. the unchanged source is unmoved ──────────────────────────────────────────────────────
def test_the_preflight_passes_the_committed_source():
    report = SS.preflight()
    assert report["n_rows"] == 66
    assert report["n_held_out_rows"] == 44
    assert report["n_optimal_grind_rows"] == 22
    assert report["n_lookup_defined_held_out_rows"] == 36        # 44 held out, 8 off grid
    assert "NOT transcription" in report["verification_boundary"]


@pytest.mark.parametrize("include_off_grid,key,records,observations", [
    (True, "complete_corpus", 44, 132),
    (False, "matched_on_grid", 36, 108),
])
def test_the_corpus_is_byte_identical_after_the_hardening(include_off_grid, key, records,
                                                          observations):
    """The strict parser must reproduce the SAME corpus, not merely a corpus of the same size."""
    manifest = TC.build_transfer_corpus_manifest(_rows(), include_off_grid=include_off_grid)
    archived = json.loads(CORPUS_JSON.read_text(encoding="utf-8"))[key]["corpus"]
    assert manifest["n_held_out_records"] == records
    assert manifest["n_observations"] == observations
    assert manifest["held_out_sample_ids"] == archived["held_out_sample_ids"]
    assert manifest["train_sample_ids"] == archived["train_sample_ids"]
    assert manifest["included_sample_ids_sha256"] == archived["included_sample_ids_sha256"]
    assert manifest["manifest_sha256"] == archived["manifest_sha256"], \
        "the record hash moved; no schema/hash migration was authorised for round 11"


def test_the_oracle_still_reproduces_the_documented_census():
    records = ORACLE.read_source_records()
    assert len(records) == 44
    assert len(ORACLE.source_observation_ids(records)) == 132
    design = ORACLE.expected_design(records)
    for scheme, census in ORACLE.EXPECTED_CENSUS.items():
        assert design[scheme]["n_clusters"] == census["n_clusters"], scheme
        assert design[scheme]["n_strata"] == census["n_strata"], scheme
        assert design[scheme]["cluster_size_distribution"] == census["sizes"], scheme


# ── 2. controlled strings, validated BEFORE anything filters ────────────────────────────────
@pytest.mark.parametrize("field,bad", [
    ("variety", " Arabica "), ("variety", "Arabica "), ("variety", " Arabica"),
    ("variety", "arabica"), ("variety", "Arabika"), ("variety", ""),
    ("granulometry", "C "), ("granulometry", " C"), ("granulometry", "c"),
    ("granulometry", "X"),
])
def test_a_corrupt_controlled_token_fails_rather_than_vanishing(field, bad):
    """`" Arabica "` used to fail the membership TEST and leave the corpus silently."""
    rows = _set(_rows(), "A12", **{field: bad})
    with pytest.raises(SS.SourceSchemaError, match="A12"):
        SS.parse_rows(rows)
    with pytest.raises(ValueError, match="A12"):
        TC.build_transfer_corpus_manifest(rows)


def test_whitespace_corruption_is_not_normalised_away():
    """Stripping would make a damaged controlled source look valid, which is the failure this
    finding is about — not a formatting inconvenience."""
    rows = _set(_rows(), "A12", variety=" Arabica ")
    with pytest.raises(SS.SourceSchemaError, match="whitespace"):
        SS.parse_rows(rows)


# ── 3. booleans, by declared token only ─────────────────────────────────────────────────────
@pytest.mark.parametrize("token", ["true", "TRUE", "1", "Tru", "yes", "Y", "", " True", "True ",
                                   "false", "FALSE", "0", "None"])
def test_an_unrecognised_boolean_token_fails_instead_of_becoming_false(token):
    """`row["on_grid"] == "True"` turned every unknown token into the negative case."""
    rows = _set(_rows(), "A12", on_grid=token)
    with pytest.raises(SS.SourceSchemaError, match="boolean tokens"):
        SS.parse_rows(rows)


def test_the_two_declared_tokens_still_parse():
    assert SS.parse_row(dict(sample="X1", variety="Arabica", granulometry="C", on_grid="True",
                             T_degC="93.4", p_bar="9")).on_grid is True
    assert SS.parse_row(dict(sample="X1", variety="Arabica", granulometry="C", on_grid="False",
                             T_degC="93.4", p_bar="9")).on_grid is False


# ── 4. coordinates must be finite ───────────────────────────────────────────────────────────
@pytest.mark.parametrize("field", ["T_degC", "p_bar"])
@pytest.mark.parametrize("bad", ["NaN", "nan", "Infinity", "-Infinity", "inf", "-inf",
                                 "", " 93.4 ", "ninety", None, True])
def test_a_non_finite_or_unparseable_coordinate_fails(field, bad):
    """The scored analyte cells were finite-checked; the design COORDINATES were not, so
    `float("NaN")` reached the manifest and produced a cluster id containing "nan"."""
    rows = _set(_rows(), "A12", **{field: bad})
    with pytest.raises(SS.SourceSchemaError):
        SS.parse_rows(rows)
    with pytest.raises(ValueError):
        TC.build_transfer_corpus_manifest(rows)


def test_no_cluster_identifier_can_contain_nan_or_inf():
    manifest = TC.build_transfer_corpus_manifest(_rows())
    for record in manifest["records"]:
        cid = record["primary_cluster_id"].lower()
        assert "nan" not in cid and "inf" not in cid, cid


# ── 5. lossless coordinate identity ─────────────────────────────────────────────────────────
@pytest.mark.parametrize("a,b", [
    ("93.40004", "93.40005"),
    ("9.000004", "9.000005"),
    ("88.0000001", "88.0000002"),
    ("1234567", "1234568"),
])
def test_near_equal_but_distinct_coordinates_stay_distinct(a, b):
    """Default `%g`/`:g` keeps six significant digits, so these collapsed into one cluster — and a
    clustered percentile range depends entirely on which outcomes move together."""
    assert "%g" % float(a) == "%g" % float(b), "the fixture no longer reproduces the %g collision"
    ka = SS.canonical_coordinate(Decimal(a))
    kb = SS.canonical_coordinate(Decimal(b))
    assert ka != kb, (a, b, ka)
    assert TC._cond_key(Decimal(a)) != TC._cond_key(Decimal(b))


@pytest.mark.parametrize("tokens", [
    ("9", "9.0", "9.00", "09"),
    ("88", "88.0", "88.000"),
    ("0", "-0", "0.0", "-0.00"),
])
def test_numerically_equal_coordinates_still_share_one_key(tokens):
    """The behaviour the `%g` version was for, and got right: `9` and `9.0` are one condition."""
    keys = {SS.canonical_coordinate(Decimal(t)) for t in tokens}
    assert len(keys) == 1, (tokens, keys)


def test_the_canonical_form_is_plain_not_exponential():
    assert SS.canonical_coordinate(Decimal("100")) == "100"
    assert SS.canonical_coordinate(Decimal("1E+2")) == "100"
    assert SS.canonical_coordinate(Decimal("0.00001")) == "0.00001"
    assert SS.canonical_coordinate(Decimal("-0")) == "0"


def test_a_collision_would_actually_move_a_cluster():
    """Non-vacuity: prove the lossless key changes the PARTITION, not just a string.

    Mutating OFF-GRID rows, because those are the held-out records with no optimal-grind counterpart
    — so moving their condition does not also trip the support reconciliation and mask the point
    being made here.
    """
    rows = _set(_rows(), "A21", T_degC="93.400040")
    rows = _set(rows, "A22", T_degC="93.400050")
    manifest = TC.build_transfer_corpus_manifest(rows)
    ids = {r["sample_id"]: r["primary_cluster_id"] for r in manifest["records"]}
    assert ids["A21"] != ids["A22"], "two distinct conditions merged into one cluster"
    assert "93.40004" in ids["A21"] and "93.40005" in ids["A22"]


# ── 6. lookup support is DERIVED and reconciled ─────────────────────────────────────────────
def test_a_row_claiming_support_that_does_not_exist_fails():
    """`lookup_defined = bool(on_grid)` copied a flag rather than checking the data, so a record
    could advertise a same-condition comparator that was not there."""
    rows = [r for r in _rows() if not (str(r["sample"]) == "A1")]      # remove one O record
    with pytest.raises(ValueError, match="no optimal-grind record exists"):
        TC.build_transfer_corpus_manifest(rows)


def test_a_row_denying_support_that_does_exist_fails():
    rows = _set(_rows(), "A12", on_grid="False")
    with pytest.raises(ValueError, match="an optimal-grind record exists"):
        TC.build_transfer_corpus_manifest(rows)


def test_an_optimal_row_whose_analytes_are_unusable_is_not_support():
    """Present is not the same as usable: a row whose measurements cannot be read cannot serve as
    the lookup comparator."""
    rows = _set(_rows(), "A1", CF="")
    with pytest.raises(ValueError, match="no optimal-grind record exists"):
        TC.build_transfer_corpus_manifest(rows)


def test_duplicate_optimal_support_needs_a_declared_rule():
    """Two O records at one condition, and no aggregation rule: taking whichever was read first is
    not a rule."""
    rows = _rows()
    clone = dict(next(r for r in rows if str(r["sample"]) == "A1"))
    clone["sample"] = "A1_DUPLICATE"
    rows.append(clone)
    with pytest.raises(ValueError, match="replicate-aggregation rule"):
        TC.build_transfer_corpus_manifest(rows)


def test_lookup_defined_equals_actual_support_for_every_record():
    manifest = TC.build_transfer_corpus_manifest(_rows())
    support = SS.optimal_grind_support(SS.parse_rows(_rows()))
    by_id = {r.sample_id: r for r in SS.parse_rows(_rows())}
    for record in manifest["records"]:
        assert record["lookup_defined"] == (by_id[record["sample_id"]].condition_key in support)
    assert manifest["n_lookup_observations"] == 108


# ── 7. the two implementations are still independent ────────────────────────────────────────
def test_the_oracle_does_not_import_the_production_membership_implementation():
    """Sharing a declarative schema is not sharing a membership implementation. If this module ever
    starts CALLING the production corpus builder, the round-9/10 common mode is back.

    Checked against the parsed syntax tree rather than the file text: the docstring names those
    functions in order to say it does not use them, and a substring search cannot tell the promise
    from the breach.
    """
    import ast

    tree = ast.parse((REPO / "puckworks" / "paper_a"
                      / "source_resampling_oracle.py").read_text(encoding="utf-8"))
    forbidden = {"build_transfer_corpus_manifest", "cluster_key_of", "stratum_key_of",
                 "cluster_membership", "scheme_design", "resampling_design"}
    used = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Name):
            used.add(node.id)
        elif isinstance(node, ast.Attribute):
            used.add(node.attr)
        elif isinstance(node, ast.Import):
            used.update(a.name for a in node.names)
        elif isinstance(node, ast.ImportFrom):
            used.add(node.module or "")
            used.update(a.name for a in node.names)
    assert not (used & forbidden), "the oracle now calls production %r" % sorted(used & forbidden)
    assert not any("transfer_contract" in name for name in used), \
        "the oracle now imports the production contract module"


def test_the_two_analyte_maps_are_declared_separately():
    assert ORACLE.ANALYTE_COLUMNS == TC.SOLUTE_SOURCE_COLUMNS, \
        "the maps agree, which is the point — they must AGREE while being written twice"
    oracle_src = (REPO / "puckworks" / "paper_a" / "source_resampling_oracle.py").read_text()
    assert "SOLUTE_SOURCE_COLUMNS" not in oracle_src


@pytest.mark.parametrize("column", ["CF", "TR", "5CQA"])
def test_changing_one_side_of_the_analyte_map_is_still_detected(column, monkeypatch):
    """Mutate the ORACLE's map only. The production manifest is unmoved, so the two disagree and
    the disagreement must surface rather than being averaged away."""
    mutated = tuple((s, "totOA" if c == column else c) for s, c in ORACLE.ANALYTE_COLUMNS)
    monkeypatch.setattr(ORACLE, "ANALYTE_COLUMNS", mutated)
    records = ORACLE.read_source_records()
    oracle_values = {(r["sample_id"], o["source_column"]) for r in records
                     for o in r["observations"]}
    assert any(col == "totOA" for _s, col in oracle_values)
    production = TC.build_transfer_corpus_manifest(_rows())
    assert all(c != "totOA" for _s, c in TC.SOLUTE_SOURCE_COLUMNS)
    assert production["n_observations"] == 132


# ── 8. the paper states the verification boundary ───────────────────────────────────────────
def test_the_paper_states_what_the_source_contract_does_not_verify():
    """Structural validation reads like source validation unless the difference is written down."""
    for path in (REPO / "docs" / "submission" / "PAPER_A_JFE_MANUSCRIPT.md",
                 REPO / "docs" / "PAPER_A_DRAFT.md"):
        text = " ".join(path.read_text(encoding="utf-8").split())
        assert "does not independently verify transcription" in text, path.name
