"""Manifest-driven integrity control for the Paper 1 pivot programme.

The previous version of this file was a set of literal string checks that advertised more assurance
than it delivered. Review found, correctly, that it:

* did not ban the terms its own plan banned, so the plan asserted "Response saturation is a model
  property" while the test passed;
* checked gate references against definitions in one direction only;
* validated exactly one stated count, by banning a single literal phrase;
* hard-coded the operative filename, so a later revision would be silently ignored;
* SKIPPED when the operative plan was absent, so a missing governance artefact produced a green run;
* never looked at any other repository surface, while three archives and two producers still
  asserted claims the plan had withdrawn.

It is now driven by `PAPER_A_PLAN_MANIFEST_V1.yaml` and is **fail-closed**: a missing manifest,
missing operative plan, orphan gate, dependency cycle, unclassified claim surface or banned assertion
is a FAILURE, not a skip. Moving to a later plan revision should require editing the manifest only.

The mention-versus-assert rule is retained deliberately: a document that documents what it removed
must be able to name it. Quote it or set it in code, and it is a mention; state it bare, and it is an
assertion.
"""
from __future__ import annotations

import json
import pathlib
import re
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

MANIFEST = REPO / "docs" / "paper1_resource" / "PAPER_A_PLAN_MANIFEST_V1.yaml"

#: Spans that MENTION rather than assert.
_QUOTED = re.compile(r"\"[^\"\n]*\"|“[^”\n]*”|`[^`\n]*`|'[^'\n]*'")


def _asserted(text: str) -> str:
    return _QUOTED.sub(" ", text)


@pytest.fixture(scope="module")
def manifest():
    """Fail-closed: the manifest is the control surface, so its absence is a defect."""
    assert MANIFEST.exists(), (
        "the plan manifest is missing; the integrity control cannot be skipped into passing")
    yaml = pytest.importorskip("yaml", reason="pyyaml absent on the minimum-dependency lane")
    return yaml.safe_load(MANIFEST.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def plan(manifest):
    path = REPO / manifest["operative_plan"]
    assert path.exists(), "operative plan %s named by the manifest does not exist" % path
    return path.read_text(encoding="utf-8")


# ── 1. the manifest itself ───────────────────────────────────────────────────────────────────
def test_the_manifest_names_exactly_one_operative_plan(manifest):
    assert manifest["operative_plan"]
    assert manifest["operative_plan"] not in manifest["superseded_plans"]


def test_every_superseded_plan_carries_a_banner(manifest):
    """The audit trail is preserved on purpose; it must be unmistakably marked."""
    for rel in manifest["superseded_plans"]:
        path = REPO / rel
        assert path.exists(), rel
        assert "SUPERSEDED" in path.read_text(encoding="utf-8")[:1200].upper(), rel


def test_operative_status_and_commit_agree(manifest):
    """A plan declared operative must be pinned to an immutable commit."""
    if manifest["operative_status"] == "operative":
        assert manifest["operative_commit"], (
            "an operative plan must pin operative_commit, or its normative content is mutable")
    else:
        assert manifest["operative_status"] == "proposal"


# ── 2. the gate graph ────────────────────────────────────────────────────────────────────────
def test_every_gate_has_the_required_fields(manifest):
    for name, gate in manifest["gates"].items():
        for field in ("title", "status", "dependencies", "deliverables", "blocks_drafting"):
            assert field in gate, "%s is missing %s" % (name, field)
        assert gate["status"] in ("open", "passed", "failed", "withdrawn"), name


def test_every_dependency_names_a_defined_gate(manifest):
    """An orphan REFERENCE is an unenforceable requirement."""
    defined = set(manifest["gates"])
    for name, gate in manifest["gates"].items():
        for dep in gate["dependencies"]:
            assert dep in defined, "%s depends on undefined gate %s" % (name, dep)


def test_every_defined_gate_is_reachable_or_terminal(manifest):
    """The reverse direction the old test never checked: a gate defined but referenced by nothing,
    and depending on nothing, is dead weight in the plan."""
    gates = manifest["gates"]
    referenced = {d for g in gates.values() for d in g["dependencies"]}
    for name, gate in gates.items():
        # A gate that blocks drafting is depended upon by the drafting step, which is not itself a
        # gate; that counts as reachable.
        reachable = (name in referenced or gate["dependencies"]
                     or gate["status"] == "passed" or gate["blocks_drafting"])
        assert reachable, (
            "%s is defined but neither depends on nor is depended upon by anything" % name)


def test_the_gate_graph_is_acyclic(manifest):
    gates = manifest["gates"]
    state = {}

    def visit(node, stack):
        if state.get(node) == "done":
            return
        assert node not in stack, "dependency cycle through %s: %s" % (node, " -> ".join(stack))
        stack.append(node)
        for dep in gates[node]["dependencies"]:
            visit(dep, stack)
        stack.pop()
        state[node] = "done"

    for name in gates:
        visit(name, [])


def test_a_passed_gate_has_produced_its_deliverables(manifest):
    for name, gate in manifest["gates"].items():
        if gate["status"] == "passed":
            for rel in gate["deliverables"]:
                assert (REPO / rel).exists(), "%s is passed but %s is missing" % (name, rel)


def test_no_gate_may_pass_before_its_dependencies(manifest):
    gates = manifest["gates"]
    for name, gate in gates.items():
        if gate["status"] == "passed":
            for dep in gate["dependencies"]:
                assert gates[dep]["status"] == "passed", (
                    "%s is passed but its dependency %s is %s" % (name, dep, gates[dep]["status"]))


def test_gates_referenced_by_the_plan_are_defined_in_the_manifest(manifest, plan):
    """Both directions, which is what the plan promised and the old test did not do."""
    defined = set(manifest["gates"])
    referenced = set(re.findall(r"\b(?:P0-G\d+[ab]?|NUM-[A-Z]+-\d+)\b", _asserted(plan)))
    missing = referenced - defined
    assert not missing, "the plan references gates absent from the manifest: %s" % sorted(missing)


def test_gates_defined_in_the_manifest_appear_in_the_plan(manifest, plan):
    unreferenced = {n for n in manifest["gates"] if n not in plan}
    assert not unreferenced, "manifest gates never mentioned in the plan: %s" % sorted(unreferenced)


# ── 3. banned assertions across ALL active surfaces ──────────────────────────────────────────
def test_every_active_surface_exists(manifest):
    for rel in manifest["active_claim_surfaces"]:
        assert (REPO / rel).exists(), "active claim surface %s is missing" % rel


def test_active_and_historical_classifications_do_not_overlap(manifest):
    overlap = set(manifest["active_claim_surfaces"]) & set(manifest["historical_exclusions"])
    assert not overlap, sorted(overlap)


def test_no_active_surface_asserts_a_withdrawn_claim(manifest):
    """The check that would have caught the PHYSICAL verdict, the stale docstrings and the labels.

    Exemption is by explicit manifest classification, never by filename convention, so a new
    artefact that nobody classified fails rather than passing silently.
    """
    failures = []
    for rel in manifest["active_claim_surfaces"]:
        text = _asserted((REPO / rel).read_text(encoding="utf-8"))
        for rule in manifest["banned_assertions"]:
            if re.search(rule["pattern"], text, flags=re.I):
                failures.append("%s asserts %r — %s" % (rel, rule["pattern"], rule["why"]))
    assert not failures, "\n  ".join([""] + failures)


def test_the_saturation_archive_carries_explicit_scope_fields():
    """The specific defect review found: a numerical result labelled as physical."""
    data = json.loads((REPO / "docs" / "paper1_resource"
                       / "PAPER_A_SATURATION_VERIFICATION.json").read_text(encoding="utf-8"))
    assert data["verdict"] != "PHYSICAL"
    assert data["evidence_type"] == "numerical-model-structural"
    assert data["physical_validity"] == "untested"


# ── 4. the claim ledger ──────────────────────────────────────────────────────────────────────
@pytest.fixture(scope="module")
def ledger():
    path = REPO / "docs" / "paper1_resource" / "PAPER_A_CLAIM_EVIDENCE_LEDGER_V2.json"
    assert path.exists(), "the initial claim ledger (P0-G1a) must exist before scientific runs"
    return json.loads(path.read_text(encoding="utf-8"))


def test_every_claim_carries_the_required_record(ledger):
    required = ("claim_id", "wording", "evidence_type", "robustness", "unit_of_analysis",
                "aggregation_rule", "source_artefact", "alternative_explanations",
                "external_validity_boundary", "falsifying_result", "status")
    for claim in ledger["claims"]:
        for field in required:
            assert field in claim, "%s is missing %s" % (claim.get("claim_id"), field)


def test_claim_vocabularies_match_the_manifest(manifest, ledger):
    for claim in ledger["claims"]:
        assert claim["evidence_type"] in manifest["evidence_types"], claim["claim_id"]
        assert claim["robustness"] in manifest["robustness_statuses"], claim["claim_id"]
        assert claim["status"] in ledger["status_vocabulary"], claim["claim_id"]


def test_estimand_tags_are_from_the_declared_set(manifest, ledger):
    for claim in ledger["claims"]:
        tag = claim.get("estimand_tag")
        if tag is not None:
            assert tag in manifest["required_estimand_tags"], (claim["claim_id"], tag)


def test_claim_ids_are_unique(ledger):
    ids = [c["claim_id"] for c in ledger["claims"]]
    assert len(ids) == len(set(ids))


def test_the_ledger_supersedes_the_markdown_predecessor(manifest, ledger):
    assert ledger["supersedes"].endswith("PAPER_A_CLAIM_LEDGER.md")
    assert ledger["supersedes"] in manifest["historical_exclusions"]


def test_the_historical_headline_is_marked_historical(ledger):
    """The -0.394 pp result must not creep back to a supported status."""
    hist = next(c for c in ledger["claims"] if c["claim_id"] == "C-HIST-01")
    assert hist["status"] == "historical-only"


def test_the_oracle_claim_stays_quarantined(ledger):
    oracle = next(c for c in ledger["claims"] if c["claim_id"] == "C-ORA-01")
    assert oracle["evidence_type"] == "exploratory-oracle"
    assert "selection on the test set" in oracle["external_validity_boundary"]


# ── 5. plan-internal consistency ─────────────────────────────────────────────────────────────
def test_the_plan_defines_its_own_rounds_and_estimands(plan):
    """v2.1 delegated normative content to a superseded file and to a review document."""
    for token in ("R0", "R5", "FULL-PUB", "LOCO-WIDE", "NUM-FULL"):
        assert token in plan, (
            "%s is used by the programme but not defined in the operative plan" % token)
    assert "carried from v2 unchanged" not in _asserted(plan)


def test_the_plan_does_not_defer_normative_content_to_a_review(plan):
    assert "review's §" not in _asserted(plan)


def test_stated_counts_match_their_tables(plan):
    """The defect class that produced "the four findings" above eleven rows, and "Three
    ambiguities" above five. Counts stated in prose are checked against the table that follows."""
    words = {"two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7,
             "eight": 8, "nine": 9, "ten": 10, "eleven": 11}
    lines = plan.splitlines()
    for i, line in enumerate(lines):
        m = re.match(r"^([A-Z][a-z]+) (ambiguities|findings|gates|workstreams)\b", line.strip())
        if not m or m.group(1).lower() not in words:
            continue
        rows = 0
        for follow in lines[i + 1:i + 40]:
            if follow.startswith("|") and not re.match(r"^\|[\s:|-]+\|$", follow):
                rows += 1
        if rows:
            rows -= 1                                   # header
            assert rows == words[m.group(1).lower()], (
                "%r introduces a table with %d rows" % (line.strip(), rows))


def test_the_drafting_rule_is_internally_consistent(plan):
    assert "before step 6" not in _asserted(plan)
    assert re.search(r"P0-G10\*{0,2},? included|including \*{0,2}P0-G10", plan)


def test_the_grind_reversal_accompanies_the_pooled_figure(plan):
    assert "+1.234" in plan and "-0.037" in plan.replace("−", "-")
    assert "0.5985" in plan, "the median-is-not-linear arithmetic should be shown"
