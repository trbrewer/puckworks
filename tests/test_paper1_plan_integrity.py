"""Mechanical integrity of the OPERATIVE Paper 1 pivot plan.

Two consecutive plan revisions were returned by review with defects that a machine could have found:

* v1 built two headline claims on pooled means that hid coarse/fine reversals, in violation of a
  rule stated in the same document;
* v2 fixed the science and then failed on internal consistency — stale gate ids from the previous
  numbering scheme, a sequence that contradicted its own drafting rule, a gate that depended on the
  manuscript it forbade writing, and a list introduced as "the four findings" above eleven rows.

A plan whose own controls disagree with each other cannot enforce anything, and I should not be the
one checking that by eye. These tests scan the operative plan only; superseded revisions are
deliberately exempt, because rewriting history would destroy the audit trail.
"""
from __future__ import annotations

import pathlib
import re
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

RESOURCE = REPO / "docs" / "paper1_resource"

#: The single operative plan. Superseded revisions carry a banner and are not scanned.
OPERATIVE = RESOURCE / "PAPER_1_PIVOT_AND_REDRAFT_PLAN_V2_1.md"

SUPERSEDED = (
    RESOURCE / "PAPER_1_PIVOT_AND_REDRAFT_PLAN.md",
    RESOURCE / "PAPER_1_PIVOT_AND_REDRAFT_PLAN_V2.md",
)

#: Phrases the second review required be removed. Each maps to why, so a failure explains itself.
DEPRECATED = {
    r"\bcannot localize\b": "categorical; one profile is finite and the rest are threshold-dependent",
    r"\bhydraulic attribution\b": "implies causal separation the contrast does not achieve",
    r"\bfreeze rather than fit\b": "the universal rule was withdrawn in v2",
    r"\btwo (?:well-chosen )?conditions beat all nine\b": "false on total sensitivity spread",
    r"\bunbounded above\b": "the acceptable set is right-censored, not proven unbounded",
}

#: Bare legacy gate ids that collided with the P0-G* scheme. `P0-G3` is fine; a bare `G3` is not.
LEGACY_GATE = re.compile(r"(?<![\w-])G[345](?![\w])")


#: Spans that MENTION rather than assert: quoted text and inline code.
_QUOTED = re.compile(r"\"[^\"\n]*\"|\u201c[^\u201d\n]*\u201d|`[^`\n]*`")


def _asserted(text: str) -> str:
    """Everything the plan states in its own voice.

    A plan that documents what it removed has to name the removed wording, so a bare substring
    search would make correction impossible to write down. The rule is therefore: a deprecated
    phrase is a defect when ASSERTED, and fine when quoted or set in code. That is self-enforcing —
    to mention a banned phrase you must quote it, which is exactly the discipline wanted.
    """
    return _QUOTED.sub(" ", text)


@pytest.fixture(scope="module")
def plan():
    if not OPERATIVE.exists():
        pytest.skip("operative plan not present")
    return OPERATIVE.read_text(encoding="utf-8")


# ── 1. terminology ───────────────────────────────────────────────────────────────────────────
@pytest.mark.parametrize("pattern,reason", list(DEPRECATED.items()))
def test_deprecated_wording_is_absent(plan, pattern, reason):
    """Outside the explicit correction tables, which have to quote what they are correcting."""
    hits = re.findall(pattern, _asserted(plan), flags=re.I)
    assert not hits, "%r appears in the operative plan: %s" % (pattern, reason)


def test_the_fitted_parameter_is_named_exactly(plan):
    """It multiplies the Sherwood prefactors; "extraction rate" is a different quantity, and the
    paper also discusses flow rate, so the ambiguity is live."""
    assert "mass-transfer-rate multiplier" in plan
    body = _asserted(plan)
    assert not re.search(r"\bthe extraction rate\b", body, flags=re.I)


# ── 2. gate-id hygiene ───────────────────────────────────────────────────────────────────────
def test_no_bare_legacy_gate_ids(plan):
    """`G3`/`G4`/`G5` collided with `P0-G3`/`P0-G4`/`P0-G5` and produced contradictory statuses."""
    hits = LEGACY_GATE.findall(_asserted(plan))
    assert not hits, "bare legacy gate ids still present: %s" % sorted(set(hits))


def test_the_renamed_numerical_gates_are_used(plan):
    for gate in ("NUM-TIME-01", "NUM-ENV-01"):
        assert gate in plan, gate


def test_every_referenced_p0_gate_is_defined(plan):
    """A gate mentioned in the sequence but absent from the table is an unenforceable requirement."""
    referenced = set(re.findall(r"P0-G(\d+)", plan))
    assert referenced, "no P0 gates referenced at all"
    for n in referenced:
        assert re.search(r"\*\*P0-G%s\*\*" % n, plan), "P0-G%s referenced but never defined" % n


def test_the_protocol_freeze_gate_exists_and_leads_the_sequence(plan):
    """Every policy and threshold in the plan was chosen after seeing results; that must be gated."""
    assert "P0-G0" in plan
    sequence = plan.split("## 12.")[-1]
    first_gate = re.search(r"P0-G(\d+)", sequence)
    assert first_gate and first_gate.group(1) == "0", (
        "the protocol freeze must come first in the execution sequence, not merely exist")


# ── 3. internal consistency ──────────────────────────────────────────────────────────────────
def test_the_drafting_rule_does_not_contradict_itself(plan):
    """v2 said all ten gates block the results narrative, then allowed drafting before P0-G10."""
    assert "before step 6" not in _asserted(plan)
    assert re.search(r"P0-G10\*{0,2},? included|including \*{0,2}P0-G10", plan), (
        "the drafting rule must say explicitly that P0-G10 also blocks the results narrative")


def test_no_gate_depends_on_the_manuscript_it_forbids_writing(plan):
    """v2's P0-G3 required a scope table *in the manuscript* while the manuscript was frozen."""
    assert "model-scope table in the manuscript" not in _asserted(plan)
    assert "PAPER_A_MODEL_SCOPE_MATRIX.md" in plan


def test_stated_counts_match_the_tables_they_introduce(plan):
    """v2 introduced an eleven-row table as "the four findings below"."""
    assert "the four findings below" not in _asserted(plan)


def test_superseded_revisions_carry_a_banner_and_are_not_scanned():
    """The audit trail is preserved deliberately; the tests must not tempt anyone to rewrite it."""
    for path in SUPERSEDED:
        if path.exists():
            head = path.read_text(encoding="utf-8")[:900]
            assert "SUPERSEDED" in head.upper(), path.name


# ── 4. the claim that keeps being got wrong ──────────────────────────────────────────────────
def test_the_pooled_median_is_not_described_as_a_mean_of_medians(plan):
    """Median is not linear: (1.234 - 0.037)/2 = 0.5985, but the archived pooled median is 0.524.

    v2 said "both pooled numbers are means of two opposite results", which is true fold by fold and
    false of the reported medians.
    """
    assert "must not" in plan.lower() and "component medians" in plan
    assert "0.5985" in plan, "the arithmetic that makes the point should be shown, not asserted"


def test_the_grind_reversal_is_stated_wherever_the_pooled_figure_appears(plan):
    """The defect that cost v1: a pooled headline with its reversal left off the page."""
    assert "+1.234" in plan and "-0.037" in plan.replace("−", "-")
