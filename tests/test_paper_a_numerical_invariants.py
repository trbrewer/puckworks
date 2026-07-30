"""The round-10 remediation must not move a verified number.

Round-10 found the stale-number category empty and asked for five *semantic* repairs: an
evidence-limited central claim, one manuscript source of truth, a bound estimand, exact interval
validation, and a paragraph-aware publication scanner. None of them is fixed by changing a value —
which is exactly the condition under which a silent numerical regression ships unnoticed, because
every reviewer's attention is on sentences and validator internals.

So the accepted values are pinned and this test is the ratchet.
"""
from __future__ import annotations

import copy
import json
import pathlib
import subprocess
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from tools import paper_a_numerical_invariants as NI  # noqa: E402


def test_every_protected_value_is_unchanged():
    assert NI.check() == []


def test_the_invariant_file_is_what_the_artefacts_produce():
    frozen = json.loads(NI.INVARIANTS.read_text(encoding="utf-8"))
    assert NI._diff(frozen, NI.extract(), "invariants") == []


def test_the_headline_values_the_paper_quotes_are_the_frozen_ones():
    """A short, human-readable restatement: if this fails, read the diff, not the code."""
    inv = json.loads(NI.INVARIANTS.read_text(encoding="utf-8"))
    at40 = inv["endpoints"]["40"]
    assert at40["pooled_model_mape"] == 8.44
    assert at40["pooled_const_mape"] == 8.83
    assert at40["paired_difference_pp"] == -0.394
    assert at40["n_model_worse_than_const"] == 62
    assert at40["n_points"] == 132
    assert at40["relative_mape_reduction_pct"] == pytest.approx(4.4167, abs=5e-4)
    primary = at40["schemes"]["cond_in_variety"]["interval"]
    assert primary["lower"] == pytest.approx(-0.8290522506, abs=1e-10)
    assert primary["upper"] == pytest.approx(+0.0037905184, abs=1e-10)
    assert inv["stability_audit"]["upper_monte_carlo_se_at_canonical_B_pp"] == \
        pytest.approx(0.000466, abs=5e-7)
    assert inv["stability_audit"]["lower_monte_carlo_se_at_canonical_B_pp"] == \
        pytest.approx(0.000520, abs=5e-7)


@pytest.mark.parametrize("path,mutate", [
    ("40 g upper bound, last digit",
     lambda inv: inv["endpoints"]["40"]["schemes"]["cond_in_variety"]["interval"]
     .__setitem__("upper", 0.003790518393922993)),
    ("model pooled MAPE",
     lambda inv: inv["endpoints"]["40"].__setitem__("pooled_model_mape", 8.45)),
    ("model-worse count",
     lambda inv: inv["endpoints"]["40"].__setitem__("n_model_worse_than_const", 63)),
    ("Monte Carlo standard error",
     lambda inv: inv["stability_audit"].__setitem__(
         "upper_monte_carlo_se_at_canonical_B_pp", 0.000467)),
    ("corpus manifest hash",
     lambda inv: inv["corpus"].__setitem__("manifest_sha256", "0" * 64)),
    ("primary membership hash",
     lambda inv: inv["design_census"]["cond_in_variety"].__setitem__(
         "membership_sha256", "0" * 64)),
    ("a deleted field",
     lambda inv: inv["endpoints"]["40"].pop("paired_difference_pp")),
])
def test_a_one_digit_mutation_of_any_protected_value_fails(path, mutate):
    """The ratchet has to bite on the last digit, or it is decoration."""
    frozen = copy.deepcopy(json.loads(NI.INVARIANTS.read_text(encoding="utf-8")))
    mutate(frozen)
    problems = NI._diff(frozen, NI.extract(), "invariants")
    assert problems, "FALSE GREEN: a mutated %s went undetected" % path


def test_the_cli_check_passes():
    r = subprocess.run([sys.executable, "tools/paper_a_numerical_invariants.py", "--check"],
                       cwd=REPO, capture_output=True, text=True)
    assert r.returncode == 0, r.stderr or r.stdout
