"""All three manuscripts: every number in the body is accounted for.

Paper 2 got this audit first and it paid immediately -- 150 unaccounted down to zero, three
unbacked values found, two of which had been transcribed from a reviewer's own table. Papers 1 and
3 had no equivalent: Paper 1 printed ~530 numerals against 27 checked claims.

Applying it to them found one real defect: Paper 3 quoted a leave-one-pressure-out RC-3b value of
0.525 where the producer gives 0.516 -- the same stale number that had already been corrected in
Paper 2's Table 3, in a copy Paper 3 kept.

The tests that matter here are the fault-injection ones. A coverage audit reporting zero is
worthless unless it can report non-zero.
"""
import pathlib
import tempfile

import pytest

from puckworks.paper3 import claim_coverage as P3
from puckworks.paper_a import claim_coverage as P1
from puckworks.paper_b2 import claim_coverage as P2

PAPERS = (("Paper 1", P1), ("Paper 2", P2), ("Paper 3", P3))


def _skips(mod):
    return getattr(mod, "SKIP_SECTIONS", None) or getattr(mod, "_SKIP_SECTIONS", ())


def _inject(mod, sentence):
    """Put a sentence inside the AUDITED region.

    The body ends at the EARLIEST skipped section, not at the end of the file. Appending would put
    the fault where the audit deliberately does not look, and the test would pass for the wrong
    reason -- which is exactly what happened on the first attempt at this check.
    """
    src = mod.MANUSCRIPT.read_text(encoding="utf-8")
    marks = [src.index(m) for m in _skips(mod) if m in src]
    assert marks, f"{mod.__name__}: no skip boundary found"
    cut = min(marks)
    tmp = pathlib.Path(tempfile.mkdtemp()) / "draft.md"
    tmp.write_text(src[:cut] + "\n\n" + sentence + "\n\n" + src[cut:], encoding="utf-8")
    return mod.audit(tmp)


@pytest.mark.parametrize("name,mod", PAPERS, ids=[n for n, _ in PAPERS])
def test_no_unaccounted_numerals(name, mod):
    rep = mod.audit()
    lines = [f"L{f['line']} {f['token']}  {f['context'][:90]}" for f in rep["unaccounted"]]
    assert rep["unaccounted"] == [], f"{name} unaccounted:\n  " + "\n  ".join(lines)


@pytest.mark.parametrize("name,mod", PAPERS, ids=[n for n, _ in PAPERS])
def test_the_ratchet_matches_reality(name, mod):
    assert mod.BASELINE_UNACCOUNTED == len(mod.audit()["unaccounted"])


@pytest.mark.parametrize("name,mod", PAPERS, ids=[n for n, _ in PAPERS])
def test_an_invented_number_is_caught(name, mod):
    """NON-VACUITY. An audit that cannot report a problem certifies nothing."""
    rep = _inject(mod, "The reconstruction error is 7.313131 g s per second.")
    assert any(f["token"] == "7.313131" for f in rep["unaccounted"]), name


@pytest.mark.parametrize("name,mod", PAPERS, ids=[n for n, _ in PAPERS])
def test_a_near_miss_is_caught(name, mod):
    """The subtler failure: a plausible value that no producer computes. Rounding is allowed
    (0.116 for 0.1157); a DIFFERENT number is not."""
    rep = _inject(mod, "The pooled held-out error is 41.7371 percentage points.")
    assert any(f["token"] == "41.7371" for f in rep["unaccounted"]), name


def test_paper_3_no_longer_carries_the_stale_rc3b_value():
    """THE DEFECT THIS AUDIT FOUND. Paper 2's Table 3 was corrected to 0.516; Paper 3 kept 0.525
    for the same leave-one-pressure-out quantity. Both must track the producer."""
    import json
    bundle = json.loads(
        (P2.REPO_ROOT / "docs/figures/paper_b_results.json").read_text(encoding="utf-8"))
    rc3b = bundle["loco"]["heldout_mean"]["rc3b"]
    assert rc3b == pytest.approx(0.516, abs=5e-4), rc3b
    for mod in (P2, P3):
        text = mod.MANUSCRIPT.read_text(encoding="utf-8")
        assert "0.525" not in text, f"{mod.__name__} still prints the stale RC-3b value"
        assert "0.516" in text


def test_the_registry_counts_paper_3_quotes_are_live():
    """Paper 3's prose counts are matched against the LIVE registry, so a 28th component fails the
    audit rather than silently invalidating the prose."""
    counts = P3._live_counts()
    import puckworks.models  # noqa: F401
    from puckworks import registry as R
    assert counts["n_components"] == len(R.components())
    assert counts["stage:extraction"] == sum(1 for c in R.components() if c.stage == "extraction")


def test_percent_and_significant_figure_matching_do_not_over_match():
    """The engine gained percent conversion and sig-fig rounding because correct numbers were being
    reported as unaccounted. Both are scoped so they cannot match unrelated values."""
    from puckworks.review.number_audit import matches_a_claim
    claims = [("c", "p", 0.76, 0.0)]
    assert matches_a_claim(76.0, claims, is_percent=True) == "c"
    assert matches_a_claim(76.0, claims, is_percent=False) is None      # no % token -> no match
    assert matches_a_claim(75.0, claims, is_percent=True) is None       # different number
    big = [("d", "p", 3619.2, 0.0)]
    assert matches_a_claim(3600.0, big, token="3600") == "d"
    assert matches_a_claim(3600.0, big, token="3600.0") is None         # decimals are not sig-fig
    assert matches_a_claim(3700.0, big, token="3700") is None


# ── verified vs exempt (claim-binding sweep, 2026-07-28) ──────────────────────────────────────
VERIFIED = ("producer", "archive", "code")
EXEMPT = ("config", "dataset", "cited", "derived")


@pytest.mark.parametrize("name,mod", PAPERS, ids=[n for n, _ in PAPERS])
def test_bound_values_count_as_verified_not_as_exemptions(name, mod):
    """Binding a number must move the headline figure, or the metric cannot show progress.

    Before this, a value bound to its archive kept the `config` disposition and only its
    explanation changed -- so Paper 1's "producer-bound" figure stayed at 14.9 % after 60 of its 77
    slow-lane values had been wired to the records that produced them. A progress metric that
    cannot register progress is the same class of defect this audit exists to catch, in the audit
    itself.
    """
    r = mod.audit()
    dispositions = {f["disposition"] for f in r["findings"]}
    assert dispositions <= set(VERIFIED) | set(EXEMPT) | {"structural", "UNACCOUNTED"}, (
        f"unknown disposition in {name}: {dispositions}")

    # Every ARCHIVE-BOUND / CODE-BOUND explanation must carry the matching disposition.
    for f in r["findings"]:
        why = str(f.get("why", ""))
        if why.startswith("ARCHIVE-BOUND"):
            assert f["disposition"] == "archive", (
                f"{name} {f['token']!r} is archive-bound but dispositioned {f['disposition']!r}")
        elif why.startswith("CODE-BOUND"):
            assert f["disposition"] == "code", (
                f"{name} {f['token']!r} is code-bound but dispositioned {f['disposition']!r}")


def test_paper_1_verified_share_does_not_regress():
    """Ratchet on the share of Paper 1 claims that are actually checked.

    This is the number that says whether the review process is converging. It was 14.9 % before the
    binding sweep. Lowering this constant is the work; raising it must be deliberate.
    """
    r = P1.audit()
    f = r["findings"]
    verified = sum(1 for x in f if x["disposition"] in VERIFIED)
    claims = sum(1 for x in f if x["disposition"] != "structural")
    share = 100.0 * verified / claims
    assert share >= 35.0, (
        f"Paper 1 verified share fell to {share:.1f} % ({verified}/{claims}); it was 35.3 % after "
        f"the binding sweep. A binding was removed or a claim was added without one")
