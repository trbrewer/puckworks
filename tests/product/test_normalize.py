"""PR 2A — tests for the rights-independent normalization boundary (puckworks.product).

All inputs are synthetic/caller-owned; no upstream fixture data is used. Covers the happy path
(deterministic, contract-valid output) and the malformed-input rejections that make units, time
alignment, pressure nodes, and the flow-vs-cumulative-mass distinction explicit.
"""
import puckworks.product as p
import pytest


def _prov():
    return p.synthetic_provenance("syn-shot-1")


def _channels():
    return [
        p.RawChannel("pressure", "pressure", "bar", p.SeriesRole.PRESSURE, (1.0, 8.9, 9.0),
                     measurement_node="group_head", reference="gauge"),
        p.RawChannel("flow", "flow_rate", "g/s", p.SeriesRole.FLOW_RATE, (0.0, 1.8, 2.1)),
        p.RawChannel("mass", "cumulative_mass", "g", p.SeriesRole.CUMULATIVE_MASS, (0.0, 0.9, 2.0)),
        p.RawChannel("temp", "temperature", "C", p.SeriesRole.SCALAR, (92.0, 93.0, 93.5)),
    ]


def _normalize(**over):
    kw = dict(fixture_id="syn-shot-1", provenance=_prov(), time_unit="s", time_origin="shot start",
              time_values=[0.0, 0.5, 1.0], channels=_channels())
    kw.update(over)
    return p.normalize_shot_input(**kw)


# ── happy path ────────────────────────────────────────────────────────────────────
def test_normalizes_to_valid_shot_input():
    si = _normalize()
    assert isinstance(si, p.ShotInput)
    assert [s.series_id for s in si.series] == ["pressure", "flow", "mass", "temp"]
    assert si.time_axis.unit == "s" and si.time_axis.values == (0.0, 0.5, 1.0)


def test_output_serializes_deterministically():
    si = _normalize()
    j1 = p.shot_input_to_json(si)
    j2 = p.shot_input_to_json(p.shot_input_from_json(j1))   # round-trips through the contract
    assert j1 == j2
    # re-normalizing identical input yields identical bytes
    assert p.shot_input_to_json(_normalize()) == j1


def test_units_are_preserved_explicitly():
    si = _normalize()
    units = {s.series_id: s.unit for s in si.series}
    assert units == {"pressure": "bar", "flow": "g/s", "mass": "g", "temp": "C"}


def test_pressure_carries_node_and_reference_others_do_not_fabricate_it():
    si = _normalize()
    by_id = {s.series_id: s for s in si.series}
    assert by_id["pressure"].channel_semantics.measurement_node == "group_head"
    assert by_id["pressure"].channel_semantics.reference == "gauge"
    # a non-pressure series is not given a pressure reference
    assert by_id["flow"].channel_semantics.reference == "flow_rate"


def test_provenance_is_rights_independent_synthetic():
    prov = _prov()
    assert prov.rights_review_status is p.RightsReviewStatus.PENDING
    assert prov.redistribution_status is p.RedistributionStatus.PENDING
    assert not prov.is_redistributable
    assert "synthetic" in prov.source_member.lower()


# ── malformed input rejections ──────────────────────────────────────────────────────
def test_flow_unit_cannot_be_a_mass_unit():
    with pytest.raises(p.NormalizationError, match="not valid for role flow_rate"):
        _normalize(channels=[p.RawChannel("f", "flow", "g", p.SeriesRole.FLOW_RATE, (0.0, 1.0, 2.0))])


def test_cumulative_mass_unit_cannot_be_a_rate():
    with pytest.raises(p.NormalizationError, match="not valid for role cumulative_mass"):
        _normalize(channels=[p.RawChannel("m", "mass", "g/s", p.SeriesRole.CUMULATIVE_MASS, (0.0, 1.0, 2.0))])


def test_cumulative_mass_must_be_non_decreasing():
    with pytest.raises(p.NormalizationError, match="non-decreasing"):
        _normalize(channels=[p.RawChannel("m", "mass", "g", p.SeriesRole.CUMULATIVE_MASS, (0.0, 2.0, 1.0))])


def test_pressure_requires_node_and_reference():
    with pytest.raises(p.NormalizationError, match="requires measurement_node and reference"):
        _normalize(channels=[p.RawChannel("pp", "pressure", "bar", p.SeriesRole.PRESSURE, (1.0, 8.0, 9.0))])


def test_non_pressure_cannot_carry_a_pressure_reference():
    with pytest.raises(p.NormalizationError, match="must not carry a pressure reference"):
        _normalize(channels=[p.RawChannel("f", "flow", "g/s", p.SeriesRole.FLOW_RATE, (0.0, 1.0, 2.0),
                                          reference="gauge")])


def test_time_must_be_strictly_increasing():
    with pytest.raises(p.NormalizationError, match="strictly increasing"):
        _normalize(time_values=[0.0, 0.5, 0.5])


def test_series_length_must_match_time():
    with pytest.raises(p.NormalizationError, match="values length"):
        _normalize(channels=[p.RawChannel("f", "flow", "g/s", p.SeriesRole.FLOW_RATE, (0.0, 1.0))])


@pytest.mark.parametrize("bad", [(0.0, float("nan"), 1.0), (0.0, float("inf"), 1.0), (0.0, True, 1.0)])
def test_non_finite_or_non_numeric_values_rejected(bad):
    with pytest.raises(p.NormalizationError):
        _normalize(channels=[p.RawChannel("f", "flow", "g/s", p.SeriesRole.FLOW_RATE, bad)])


def test_duplicate_channel_ids_rejected():
    ch = p.RawChannel("dup", "flow", "g/s", p.SeriesRole.FLOW_RATE, (0.0, 1.0, 2.0))
    with pytest.raises(p.NormalizationError, match="duplicate channel_id"):
        _normalize(channels=[ch, ch])


def test_empty_time_and_empty_channels_rejected():
    with pytest.raises(p.NormalizationError):
        _normalize(time_values=[])
    with pytest.raises(p.NormalizationError, match="at least one channel"):
        _normalize(channels=[])


def test_missing_time_unit_and_bad_fixture_id_rejected():
    with pytest.raises(p.NormalizationError, match="time_unit"):
        _normalize(time_unit="")
    with pytest.raises(p.NormalizationError, match="fixture_id"):
        _normalize(fixture_id="")


def test_no_upstream_fixture_data_is_imported():
    # the boundary ships/loads no data; provenance is explicitly caller-owned synthetic
    si = _normalize()
    assert si.provenance.source_record.startswith("caller-owned")
