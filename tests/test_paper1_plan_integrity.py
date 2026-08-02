"""Fail-closed integrity control for the Paper 1 pivot programme.

Third iteration. The history matters, because each version failed in the same shape:

* v1's control was prose rules a reader had to apply;
* v2.1's was literal string matching that advertised checks it did not implement;
* v2.2's added a manifest but (a) obtained it through ``pytest.importorskip("yaml")``, so the
  "fail-closed" control **skipped** on any lane without PyYAML, (b) iterated only over a hand-listed
  set of 14 surfaces out of 100 candidates, and (c) stripped every quoted span before matching —
  which, applied to JSON and Python, deleted exactly the content the rules were written to inspect,
  so ``{"verdict": "PHYSICAL"}`` and ``label = "RATE RECALIBRATION ALONE"`` could never match.

This version: the manifest is JSON (standard library only, no optional parser, no skip path);
candidate surfaces are DISCOVERED from declared globs and every one must be classified; and matching
is delegated to `tools.paper1_claim_scanner`, which reads each file according to its format.

The adversarial probes in §12 of the review are implemented as tests, because a scanner that reports
nothing is indistinguishable from a scanner that inspects nothing.
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

from tools import paper1_claim_scanner as SCAN  # noqa: E402

MANIFEST = REPO / "docs" / "paper1_resource" / "PAPER_A_PLAN_MANIFEST_V1.json"


@pytest.fixture(scope="module")
def manifest():
    """No skip path. JSON is standard library, so an absent parser cannot excuse a green run."""
    assert MANIFEST.exists(), "the plan manifest is missing; this control must not be skippable"
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def plan(manifest):
    path = REPO / manifest["operative_plan"]
    assert path.exists(), "operative plan %s named by the manifest does not exist" % path
    return path.read_text(encoding="utf-8")


# ── 1. the control cannot skip ───────────────────────────────────────────────────────────────
def test_the_manifest_is_json_and_needs_no_optional_parser():
    assert MANIFEST.suffix == ".json"
    assert not (MANIFEST.parent / "PAPER_A_PLAN_MANIFEST_V1.yaml").exists(), (
        "the YAML manifest forced pytest.importorskip and reintroduced a skip path")


def test_this_module_contains_no_skip_path():
    """Parsed, not grepped — the prose above legitimately NAMES the functions it forbids calling."""
    import ast

    tree = ast.parse(pathlib.Path(__file__).read_text(encoding="utf-8"))
    called = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            called.add(ast.unparse(node.func))
    banned = {c for c in called if c.endswith(("importorskip", "pytest.skip", "skip"))}
    assert not banned, "%s reintroduces a skip path into a fail-closed control" % sorted(banned)


# ── 2. exhaustive classification of claim surfaces ───────────────────────────────────────────
def test_every_candidate_surface_is_classified(manifest):
    """The gap that mattered: 14 surfaces were listed, 100 existed, 81 were unclassified."""
    candidates = SCAN.discover(REPO, manifest["claim_surface_globs"])
    classified = (set(manifest["active_claim_surfaces"])
                  | set(manifest["historical_exclusions"])
                  | {e["path"] for e in manifest["nonclaim_exclusions"]})
    unclassified = sorted(candidates - classified)
    assert not unclassified, (
        "unclassified candidate claim surfaces (a new artefact must be classified, not ignored):\n  "
        + "\n  ".join(unclassified))


def test_classifications_do_not_overlap(manifest):
    active = set(manifest["active_claim_surfaces"])
    historical = set(manifest["historical_exclusions"])
    nonclaim = {e["path"] for e in manifest["nonclaim_exclusions"]}
    assert not active & historical, sorted(active & historical)
    assert not active & nonclaim, sorted(active & nonclaim)


def test_the_current_protocol_is_an_active_surface(manifest):
    """It carries operative decision rules and was previously classified as neither."""
    assert ("docs/paper1_resource/PAPER_A_PIVOT_ANALYSIS_PROTOCOL_V2.md"
            in manifest["active_claim_surfaces"])


def test_every_claim_bearing_gate_deliverable_is_classified(manifest):
    """A future gate output must not arrive unclassified and therefore unscanned."""
    classified = (set(manifest["active_claim_surfaces"])
                  | set(manifest["historical_exclusions"])
                  | {e["path"] for e in manifest["nonclaim_exclusions"]})
    for name, gate in manifest["gates"].items():
        for rel in gate["deliverables"]:
            if (REPO / rel).exists():
                assert rel in classified, "%s deliverable %s exists but is unclassified" % (name, rel)


# ── 3. the scanner actually inspects content ─────────────────────────────────────────────────
def test_no_active_surface_asserts_a_withdrawn_claim(manifest):
    findings = SCAN.scan(REPO, manifest["active_claim_surfaces"], manifest["banned_assertions"],
                         manifest.get("assertion_exemptions", ()))
    assert not findings, "\n  ".join([""] + [str(f) for f in findings])


@pytest.mark.parametrize("name,body,should_catch", [
    ("probe.json", '{"verdict": "PHYSICAL"}', True),
    ("probe.py", 'label = "RATE RECALIBRATION ALONE"\n', True),
    ("probe.py", '"""The cup cannot localize the multiplier."""\n', True),
    ("probe.py", '# hydraulic attribution is established\n', True),
    ("probe.md", 'The acceptable set is unbounded above.\n', True),
    ("probe.json", '{"note": "freezing the rate transfers better"}', True),
    ("probe.md", 'We withdrew "cannot localize" from the title.\n', False),
])
def test_adversarial_probes(tmp_path, manifest, name, body, should_catch):
    """Review §12. A scanner reporting nothing must be shown to be capable of reporting something.

    The Markdown case that must NOT fire is the mention-versus-assert rule: a document recording
    what it removed has to be able to name it. That rule applies to prose ONLY — in JSON and Python
    the quotes are structure, which is what the previous control got catastrophically wrong.
    """
    (tmp_path / name).write_text(body, encoding="utf-8")
    findings = SCAN.scan(tmp_path, [name], manifest["banned_assertions"])
    assert bool(findings) is should_catch, (name, body, [str(f) for f in findings])


def test_a_json_field_rule_survives_structural_parsing(manifest):
    """`"verdict": "PHYSICAL"` must match a PARSED document, not just raw text.

    When the scanner began parsing JSON, the key and value became separate strings and the field
    rule silently stopped matching — the same defect as quote-stripping, one level down. It was
    caught only because the probe was run before the clean result was believed.
    """
    items = dict((loc, txt) for loc, txt in SCAN._json_assertions('{"verdict": "PHYSICAL"}'))
    assert any(txt == "verdict: PHYSICAL" for txt in items.values()), (
        "scalar members must also be emitted as a composite 'key: value'")


def test_a_missing_active_surface_is_a_finding(manifest, tmp_path):
    findings = SCAN.scan(tmp_path, ["docs/nonexistent.json"], manifest["banned_assertions"])
    assert findings and findings[0].rule == "<missing>"


def test_exemptions_are_bounded_by_occurrence_count(tmp_path, manifest):
    """A reviewed historical quotation stays permitted; a NEW occurrence still fails."""
    rule = [{"pattern": r"\bunbounded above\b", "why": "test"}]
    (tmp_path / "a.md").write_text("unbounded above\n", encoding="utf-8")
    ex = [{"path": "a.md", "pattern": r"\bunbounded above\b", "reason": "reviewed",
           "max_occurrences": 1}]
    assert not SCAN.scan(tmp_path, ["a.md"], rule, ex)
    (tmp_path / "a.md").write_text("unbounded above\nunbounded above\n", encoding="utf-8")
    assert SCAN.scan(tmp_path, ["a.md"], rule, ex)


# ── 4. gate graph and evidence-bound closure ─────────────────────────────────────────────────
def test_every_gate_has_the_required_fields(manifest):
    for name, gate in manifest["gates"].items():
        for field in ("title", "status", "dependencies", "deliverables", "blocks_drafting",
                      "closure_record"):
            assert field in gate, "%s is missing %s" % (name, field)
        assert gate["status"] in ("open", "passed", "failed", "withdrawn"), name


def test_dependencies_resolve_and_the_graph_is_acyclic(manifest):
    gates = manifest["gates"]
    for name, gate in gates.items():
        for dep in gate["dependencies"]:
            assert dep in gates, "%s depends on undefined gate %s" % (name, dep)
    state = {}

    def visit(node, stack):
        if state.get(node) == "done":
            return
        assert node not in stack, "dependency cycle: %s -> %s" % (" -> ".join(stack), node)
        stack.append(node)
        for dep in gates[node]["dependencies"]:
            visit(dep, stack)
        stack.pop()
        state[node] = "done"

    for name in gates:
        visit(name, [])


def test_a_passed_gate_is_bound_to_hashed_evidence(manifest):
    """"Passed" previously meant only that a path existed; a placeholder would have satisfied it."""
    import hashlib

    for name, gate in manifest["gates"].items():
        if gate["status"] != "passed":
            continue
        record_path = gate["closure_record"]
        assert record_path, "%s is passed with no closure record" % name
        full = REPO / record_path
        assert full.exists(), "%s closure record %s missing" % (name, record_path)
        record = json.loads(full.read_text(encoding="utf-8"))
        assert record["criteria"], "%s closure record states no criteria" % name
        assert "evidence_content_commit" in record, (
            "%s must use the content-commit/closure-commit pattern; a record cannot name its own "
            "containing commit" % name)
        assert record.get("evidence_unit_scope"), "%s closure record states no evidence scope" % name
        for item in record["deliverables"]:
            path = REPO / item["path"]
            assert path.exists(), item["path"]
            actual = hashlib.sha256(path.read_bytes()).hexdigest()
            assert actual == item["sha256"], (
                "%s deliverable %s changed after closure" % (name, item["path"]))
        producer = REPO / record["producer"]["path"]
        assert hashlib.sha256(producer.read_bytes()).hexdigest() == record["producer"]["sha256"], (
            "%s producer changed after closure" % name)


def test_no_gate_passes_before_its_dependencies(manifest):
    gates = manifest["gates"]
    for name, gate in gates.items():
        if gate["status"] == "passed":
            for dep in gate["dependencies"]:
                assert gates[dep]["status"] == "passed", (name, dep, gates[dep]["status"])


def test_every_drafting_blocker_has_an_inspectable_deliverable(manifest):
    """P0-G2 was a drafting-blocking gate with an empty deliverable list."""
    for name, gate in manifest["gates"].items():
        if gate["blocks_drafting"]:
            assert gate["deliverables"], "%s blocks drafting but delivers nothing inspectable" % name


# ── 5. the initial baseline is immutable ─────────────────────────────────────────────────────
def test_initial_and_final_artefacts_use_distinct_paths(manifest):
    """Sharing a path would let the final reconciliation erase the baseline that detects drift."""
    for a, b in (("P0-G1a", "P0-G1b"), ("P0-G3a", "P0-G3b")):
        initial = set(manifest["gates"][a]["deliverables"])
        final = set(manifest["gates"][b]["deliverables"])
        assert not initial & final, sorted(initial & final)


def test_the_initial_ledger_declares_itself_immutable():
    path = REPO / "docs" / "paper1_resource" / "PAPER_A_CLAIM_EVIDENCE_LEDGER_V2_INITIAL.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["baseline"]["role"] == "INITIAL"
    assert "MUST NOT be" in data["baseline"]["immutability"]


# ── 6. activation ceremony ───────────────────────────────────────────────────────────────────
def test_activation_is_two_stage_and_validated(manifest):
    """A commit cannot contain its own SHA, so a single self-pinning field is not implementable."""
    assert manifest["operative_status"] in ("candidate", "candidate-frozen", "operative")
    activation = manifest["activation"]
    assert "frozen_content_commit" in activation and "freeze_record" in activation
    assert (REPO / activation["freeze_record"]).exists()


# ── 7. plan/manifest agreement ───────────────────────────────────────────────────────────────
def test_gate_references_agree_in_both_directions(manifest, plan):
    defined = set(manifest["gates"])
    referenced = set(re.findall(r"\b(?:P0-G\d+[ab]?|P0-R0[ab]|NUM-[A-Z]+-\d+)\b", _asserted(plan)))
    assert not referenced - defined, sorted(referenced - defined)
    assert not {n for n in defined if n not in plan}, sorted(n for n in defined if n not in plan)


def test_the_plan_does_not_duplicate_manifest_status(plan):
    """Prose status and manifest status drifted apart in v2.2; the manifest is the only source."""
    assert "the manifest is the only status source" in plan or "status is recorded in the" in plan


def test_the_plan_states_no_unbounded_assurance_claim(plan):
    """No finite suite proves unanticipated defects are excluded."""
    assert "has to be one nobody has thought of" not in plan


def _asserted(text: str) -> str:
    return SCAN._PROSE_QUOTED.sub(" ", SCAN._FENCE.sub(" ", text))


# ── 8. normative-bundle cross-reference audit (B6) ───────────────────────────────────────────
STALE_CONTEXT = re.compile(
    r"supersed|historical|stale_reference_rules|superseded_plans|historical_exclusions|retained",
    re.I)


def test_no_active_surface_carries_a_stale_operative_reference(manifest):
    """A controlled bundle cannot be frozen while its members disagree on what is operative.

    A superseded name may still APPEAR — the manifest has to enumerate what it supersedes, and a
    protocol has to say what it replaces. It may not appear as a live reference. The discriminator
    is the surrounding context, not a count: the name must sit on a line that declares supersession.
    """
    failures = []
    exempt = set(manifest.get("stale_reference_exempt_paths", ()))
    for rel in manifest["active_claim_surfaces"]:
        if rel in exempt:
            continue          # the manifest's own classification lists must name what they classify
        if rel.endswith(".json"):
            lines = json.dumps(json.loads((REPO / rel).read_text(encoding="utf-8")),
                               indent=1).splitlines()
        else:
            lines = (REPO / rel).read_text(encoding="utf-8").splitlines()
        for rule in manifest["stale_reference_rules"]:
            stale = rule["pattern"]
            if rel.endswith(stale):
                continue                                  # a file may name itself
            for i, line in enumerate(lines, 1):
                if not re.search(re.escape(stale) + r"(?!\w)", line):
                    continue
                window = " ".join(lines[max(0, i - 3):i + 2])
                if not STALE_CONTEXT.search(window):
                    failures.append("%s:%d references %s outside a supersession context"
                                    % (rel, i, stale))
    assert not failures, "\n  ".join([""] + failures)


def test_the_stale_reference_rules_name_their_replacements(manifest):
    for rule in manifest["stale_reference_rules"]:
        assert rule["replacement"] and rule["replacement"] != rule["pattern"]


# ── 9. activation integrity (B7, B8) ─────────────────────────────────────────────────────────
def test_the_freeze_record_excludes_itself_and_the_mutable_manifest(manifest):
    """The second self-reference: a manifest cannot hash a bundle that contains the manifest."""
    record_path = manifest["activation"]["freeze_record"]
    record = json.loads((REPO / record_path).read_text(encoding="utf-8"))
    excluded = record["excluded_by_design"]
    assert record_path in excluded
    assert manifest_path_of(manifest) in excluded
    assert record_path not in record["content_files"]
    assert manifest_path_of(manifest) not in record["content_files"]


def manifest_path_of(_manifest) -> str:
    return "docs/paper1_resource/PAPER_A_PLAN_MANIFEST_V1.json"


def test_every_freeze_record_hash_is_a_full_sha256(manifest):
    record = json.loads((REPO / manifest["activation"]["freeze_record"]).read_text(encoding="utf-8"))
    for rel, digest in record["content_files"].items():
        assert re.fullmatch(r"[0-9a-f]{64}", digest), (rel, digest)
        assert (REPO / rel).exists(), rel


def test_frozen_states_verify_content_hashes(manifest):
    """Hash verification must apply in candidate-frozen too, not only operative.

    Verifying only at `operative` would let a candidate-frozen bundle drift silently right up to the
    moment it is activated.
    """
    import hashlib

    if manifest["operative_status"] not in ("candidate-frozen", "operative"):
        return                                            # nothing frozen yet; nothing to verify
    record = json.loads((REPO / manifest["activation"]["freeze_record"]).read_text(encoding="utf-8"))
    for rel, expected in record["content_files"].items():
        actual = hashlib.sha256((REPO / rel).read_bytes()).hexdigest()
        assert actual == expected, "%s drifted from its frozen hash" % rel


def test_operative_status_requires_a_real_commit(manifest):
    """A 40-hex string is not a pin; the commit must exist in this repository."""
    import subprocess

    if manifest["operative_status"] != "operative":
        return
    sha = manifest["activation"]["frozen_content_commit"]
    assert isinstance(sha, str) and re.fullmatch(r"[0-9a-f]{40}", sha), sha
    ok = subprocess.run(["git", "cat-file", "-e", "%s^{commit}" % sha],
                        cwd=REPO, capture_output=True)
    assert ok.returncode == 0, "frozen_content_commit %s does not exist" % sha


def test_p0_g0_is_not_passed_in_this_implementation_cycle(manifest):
    """The adjudication forbids closing P0-G0 in the implementation PR.

    Freeze commit F and activation commit A are separate, authority-controlled steps.
    """
    assert manifest["gates"]["P0-G0"]["status"] == "open"
    assert manifest["operative_status"] != "operative"


# ── 10. the pre-freeze premise audit is inspectable and binding ──────────────────────────────
def test_p0_g0_depends_on_the_premise_audit(manifest):
    assert "P0-R0a" in manifest["gates"]["P0-G0"]["dependencies"]


def test_the_premise_audit_records_evidence_matched_to_type(manifest):
    audit = json.loads((REPO / "docs" / "paper1_resource"
                        / "PAPER_A_PRE_FREEZE_PREMISE_AUDIT_R0A.json").read_text(encoding="utf-8"))
    required = ("premise_id", "premise", "type", "disposition", "evidence", "affected",
                "failure_consequence")
    for row in audit["premises"]:
        for field in required:
            assert field in row, (row.get("premise_id"), field)
    # a physical premise that cannot be tested must be scoped, never forced into a repo test
    physical = [r for r in audit["premises"] if r["type"] == "physical"]
    assert physical and any(r["disposition"].startswith("OPEN-AND-SCOPED") for r in physical)


def test_open_blocking_premises_keep_the_freeze_shut(manifest):
    """R0a exists to surface blockers BEFORE the freeze. If it found some, P0-G0 stays open."""
    audit = json.loads((REPO / "docs" / "paper1_resource"
                        / "PAPER_A_PRE_FREEZE_PREMISE_AUDIT_R0A.json").read_text(encoding="utf-8"))
    blocking = [r for r in audit["premises"] if r["disposition"] in ("OPEN", "OPEN-BLOCKED")]
    if blocking:
        assert manifest["gates"]["P0-G0"]["status"] == "open", (
            "premises %s are open but P0-G0 is not" % [r["premise_id"] for r in blocking])


def test_the_operative_plan_is_not_also_superseded(manifest):
    """It was both `operative_plan` and a member of `superseded_plans`."""
    assert manifest["operative_plan"] not in manifest["superseded_plans"]


def test_premise_blocking_is_gate_scoped(manifest):
    """Global blocking was too broad and conflicted with the declared gate graph.

    PR-09 belongs to P0-G9 and PR-15 to P0-G10; neither should hold P0-G0 shut. The control must
    still fail closed, but at the correct stage.
    """
    audit = json.loads((REPO / "docs" / "paper1_resource"
                        / "PAPER_A_PRE_FREEZE_PREMISE_AUDIT_R0A.json").read_text(encoding="utf-8"))
    for row in audit["premises"]:
        assert "resolution_stage" in row and "blocks_before" in row, row["premise_id"]
        assert row["resolution_stage"] in ("pre_freeze", "within_gate", "pre_drafting", "scoped")

    pre_freeze_open = [r for r in audit["premises"]
                       if r["disposition"] == "OPEN" and r["resolution_stage"] == "pre_freeze"]
    if pre_freeze_open:
        assert manifest["gates"]["P0-G0"]["status"] == "open", (
            "pre-freeze premises %s are open but P0-G0 is not"
            % [r["premise_id"] for r in pre_freeze_open])


def test_a_bound_that_cannot_serve_its_purpose_is_not_reported_as_closed():
    """PR-03's bound holds everywhere and is still ~5e13 too loose to propagate into J_inf.

    Reporting "established" without "not fit for purpose" would be the assurance-overclaim pattern
    this programme has repeatedly had to correct.
    """
    data = json.loads((REPO / "docs" / "paper1_resource"
                       / "PAPER_A_SINGULAR_LIMIT_BOUND.json").read_text(encoding="utf-8"))
    fitness = data["fitness_for_purpose"]
    assert fitness["verdict"] == "NOT_FIT_FOR_PROPAGATION"
    assert data["verdict"].endswith("NOT_FIT_FOR_PROPAGATION")

    audit = json.loads((REPO / "docs" / "paper1_resource"
                        / "PAPER_A_PRE_FREEZE_PREMISE_AUDIT_R0A.json").read_text(encoding="utf-8"))
    pr03b = next(p for p in audit["premises"] if p["premise_id"] == "PR-03b")
    assert pr03b["disposition"] == "NOT-ATTEMPTED"


def test_pr06_covers_every_declared_cell():
    data = json.loads((REPO / "docs" / "paper1_resource"
                       / "PAPER_A_SINGULAR_LIMIT_BOUND.json").read_text(encoding="utf-8"))
    cov = data["coverage"]
    assert cov["declared_cells"] == 9 * 2 * 3
    assert cov["cells_failing"] == 0
    assert "deduplication_proof" in cov, "deduplication must be proved, not assumed"
