"""Tests for the README publication-governance verifier (issue #41).

Offline + deterministic. Confirms the verifier passes on the current tree and that each objective
drift it is meant to catch actually fails it, without failing on subjective wording.
"""
import importlib
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))
RG = importlib.import_module("tools.readme_governance")


class _Comp:
    def __init__(self, name, role="runtime"):
        self.name = name
        self.execution_role = role


def test_verify_passes_on_current_tree():
    assert RG.check_readme() == []


def test_missing_component_is_detected():
    fake = [_Comp("totally.new_unlisted_component")]
    problems = RG.check_readme(components=fake)
    assert any("totally.new_unlisted_component" in p and "not in the README" in p for p in problems)


def test_exemption_suppresses_a_missing_component(monkeypatch):
    monkeypatch.setitem(RG.COMPONENT_EXEMPTIONS, "totally.exempt_component", "documented reason")
    fake = [_Comp("totally.exempt_component")]
    problems = RG.check_readme(components=fake)
    assert not any("totally.exempt_component" in p for p in problems)


def test_all_live_interactives_are_required():
    # every LIVE_INTERACTIVES url must be in both README and docs/public/README (currently satisfied)
    problems = RG.check_readme(components=[])
    assert not any("live interactive" in p for p in problems)
    assert set(RG.LIVE_INTERACTIVES) == {"flat-valley", "model-composition", "analysis-autopsy"}


def test_conditional_environment_required_only_when_path_exists():
    # Codespaces/Actions entries carry a `path`; they must be required only once that path exists
    for env in RG.ENVIRONMENTS:
        if env["name"] == "Codespaces":
            assert env.get("path") == ".devcontainer/devcontainer.json"
        if env["name"] == "Actions batch runner":
            assert env.get("path") == ".github/workflows/guided-pull-batch.yml"
    # neither devcontainer nor the batch workflow exists yet on this branch -> not required, verify clean
    assert not (_ROOT / ".devcontainer" / "devcontainer.json").exists()
    assert RG.check_readme() == []


def test_report_is_deterministic_and_readable():
    a = RG.report()
    b = RG.report()
    assert a == b
    assert "readme governance report" in a.lower()


def test_old_brand_absent_check_present():
    # the identity guard is part of governance
    assert RG.OLD_EMAIL == "brewer@synthetik-technologies.com"
    assert RG._BRAND.search("synthetik") and not RG._BRAND.search("synthetic")


def test_governance_workflow_is_secure():
    wf = (_ROOT / ".github" / "workflows" / "readme-governance.yml").read_text(encoding="utf-8")
    import re as _re
    # top-level permissions default to read-only
    assert _re.search(r"(?m)^permissions:\s*\n\s*contents:\s*read\s*$", wf)
    # every third-party action is SHA-pinned (40-hex), not a floating tag
    for use in _re.findall(r"uses:\s*([^\s]+)", wf):
        if use.startswith("actions/") or "/" in use.split("@")[0]:
            assert _re.search(r"@[0-9a-f]{40}$", use), f"action not SHA-pinned: {use}"
    # the PR-triggered verify job is read-only; issue writes are gated to trusted main
    assert "issues: write" in wf
    assert "github.ref == 'refs/heads/main'" in wf
    # PR trigger is present with path scoping (not every change triggers)
    assert "pull_request:" in wf and "paths:" in wf
    # no obvious untrusted-input shell interpolation of event inputs
    assert "${{ github.event.inputs" not in wf
