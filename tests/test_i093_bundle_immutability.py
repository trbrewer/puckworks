"""The I-093 evidence bundle is byte-identical to the branch base.

RP-D-LC-001 needed an optional diagnostic field export on `brewer2026.lb_reference`, which the
frozen I-093 screen once executed. The enabling commit corrected a provenance TEST (which wrongly
compared historical digests against the working tree) and touched no I-093 evidence. This module
makes that promise checkable rather than asserted: every tracked artifact in the bundle must match
its blob at the merge base with `main`, and neither the cheap nor the deep screen may be re-run to
satisfy any check.
"""
import pathlib
import subprocess

import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
BUNDLE_REL = "docs/insights/screens/I-093"

#: Every artifact that carries I-093's scientific evidence or its frozen provenance.
PROTECTED = (
    "PROTOCOL.md", "PROTOCOL_ERRATUM.md", "result.json", "decision.md",
    "DEEP_SCREEN_PROTOCOL.md", "DEEP_PROTOCOL_ERRATUM.md", "deep_run_raw.json",
    "deep_result.json", "deep_decision.md", "expected_run_matrix.json",
    "README.md", "NOVELTY_REVIEW.md",
)


def _git(*args):
    return subprocess.run(("git",) + args, cwd=REPO, capture_output=True)


def _base_commit():
    """The merge base with the integration branch — i.e. what this branch started from."""
    for ref in ("origin/main", "main"):
        p = _git("merge-base", "HEAD", ref)
        if p.returncode == 0 and p.stdout.strip():
            return p.stdout.strip().decode()
    return None


def test_no_i093_artifact_differs_from_the_branch_base():
    if _git("rev-parse", "--is-shallow-repository").stdout.strip() == b"true":
        pytest.skip("shallow checkout: the branch base is not observable here")
    base = _base_commit()
    if base is None:
        pytest.skip("no integration branch to compare against")
    diff = _git("diff", "--name-only", base, "--", BUNDLE_REL).stdout.decode().split()
    assert diff == [], (
        "the I-093 evidence bundle moved relative to the branch base %s: %s.\n"
        "RP-D-LC-001 must not regenerate or edit any I-093 artifact." % (base, diff))


def test_every_protected_artifact_is_present_and_unmodified():
    if _git("rev-parse", "--is-shallow-repository").stdout.strip() == b"true":
        pytest.skip("shallow checkout")
    base = _base_commit()
    if base is None:
        pytest.skip("no integration branch to compare against")
    for name in PROTECTED:
        path = REPO / BUNDLE_REL / name
        assert path.exists(), "%s/%s vanished" % (BUNDLE_REL, name)
        blob = _git("cat-file", "blob", "%s:%s/%s" % (base, BUNDLE_REL, name))
        if blob.returncode != 0:
            pytest.skip("%s not present at the branch base" % name)
        assert path.read_bytes() == blob.stdout, "%s/%s is not byte-identical" % (BUNDLE_REL, name)


def test_figures_are_unmodified():
    if _git("rev-parse", "--is-shallow-repository").stdout.strip() == b"true":
        pytest.skip("shallow checkout")
    base = _base_commit()
    if base is None:
        pytest.skip("no integration branch to compare against")
    diff = _git("diff", "--name-only", base, "--", BUNDLE_REL + "/figures").stdout.decode().split()
    assert diff == [], "I-093 figures moved: %s" % diff
