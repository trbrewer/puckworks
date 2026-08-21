import copy

import pytest

from puckworks.analysis.response_atlas import runner
from puckworks.analysis.response_atlas.decision import ADDITIONAL, DYNAMIC


def test_real_bundle_decision_is_recomputed():
    bundle = runner.build_bundle()
    assert bundle["decision"]["selected_outcome"] == ADDITIONAL
    altered = copy.deepcopy(bundle)
    altered["decision"]["selected_outcome"] = DYNAMIC
    with pytest.raises(ValueError, match="inconsistent"):
        runner.validate_bundle(altered)


def test_channel_specific_generation_and_isolation():
    bundle = runner.build_bundle()
    for row in bundle["pair_eligibility"]:
        assert row["candidate_observable"] in row["eligibility_id"]
        assert row["adapter_id"] in row["eligibility_id"]
        assert row["requirement_id"] in row["eligibility_id"]
    assert all(r["eligibility_id"] in {e["eligibility_id"] for e in bundle["pair_eligibility"]}
               for r in bundle["measurement_value_records"])


def test_flow_eligibility_never_generates_other_channels():
    pair = runner._pairs()[0]
    assert pair.candidate_observable == "flow"
    _, records = runner._derive_measurements(
        [pair], [], {"channels": [{"channel": c, "assumption_class": "TEST",
                                   "measurement_uncertainty": "NOT_PROVIDED"}
                                  for c in runner.CHANNELS]},
        runner._explanations("r", {name: "c" for name in
            ["foster2025_2.md", "wadsworth2026_inertial.md", "cameron2020.md"]}))
    assert all(record.channel == "flow" for record in records)


def test_runner_calls_decision_function(monkeypatch):
    called = []
    original = runner.derive_scientific_decision

    def observed(**kwargs):
        called.append(kwargs)
        return original(**kwargs)

    monkeypatch.setattr(runner, "derive_scientific_decision", observed)
    runner.build_bundle()
    assert called and "requirements" in called[0] and "coverage_edges" in called[0]
