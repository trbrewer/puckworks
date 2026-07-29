"""Generate the claim-binding audit from the audits themselves.

Round-7 P1-5 found the failure this module exists to prevent: the committed audit was generated
at one commit, the manuscripts moved on, and the governance document that measures staleness went
stale. Its headline counts (65/436 Paper 1 claims, 60/77 slow-lane values, six unbindable)
disagreed with the reviewer brief written against the same tree.

The audit is therefore GENERATED, for the same reason the supplement and the bibliography are. It
carries its own provenance: the commit it was generated at, the command that generated it, and a
fingerprint of every input it read. `--check` recomputes and fails when the document no longer
matches its inputs, so a manuscript edit that does not regenerate the audit breaks CI instead of
quietly producing a confident, wrong number.

    python tools/claim_binding_audit.py            # report drift (exit 1 if stale)
    python tools/claim_binding_audit.py --write     # regenerate the document and its sidecar
    python tools/claim_binding_audit.py --json      # machine-readable coverage record
"""
from __future__ import annotations

import hashlib
import json
import pathlib
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

OUT = REPO / "docs" / "CLAIM_BINDING_AUDIT.md"
SIDECAR = REPO / "docs" / "CLAIM_BINDING_AUDIT.json"

#: Every file whose content can change the numbers below. Fingerprinted into the document so a
#: stale audit is detectable without rerunning anything expensive.
INPUTS = (
    "docs/PAPER_A_DRAFT.md",
    "docs/submission/PAPER_A_JFE_MANUSCRIPT.md",
    "docs/PAPER_B2_TEMPORAL_DRAFT.md",
    "docs/PAPER_3_PUCKWORKS_DRAFT.md",
    "puckworks/paper_a/claim_coverage.py",
    "puckworks/paper_a/slow_lane_bindings.py",
    "puckworks/paper_b2/claim_coverage.py",
    "puckworks/paper3/claim_coverage.py",
)

PAPERS = (
    ("Paper 1", "puckworks.paper_a.claim_coverage"),
    ("Paper B2", "puckworks.paper_b2.claim_coverage"),
    ("Paper 3", "puckworks.paper3.claim_coverage"),
)

#: Disposition classes that mean "resolved against something that computes or records the value",
#: as opposed to a hand-written explanation.
VERIFIED_KINDS = ("producer", "archive", "code", "derived")


def _commit() -> str:
    try:
        return subprocess.run(["git", "rev-parse", "HEAD"], cwd=REPO, capture_output=True,
                              text=True, check=True).stdout.strip()[:12]
    except Exception:                                            # pragma: no cover - no git
        return "unknown"


def _fingerprint() -> dict[str, str]:
    out = {}
    for rel in INPUTS:
        p = REPO / rel
        out[rel] = (hashlib.sha256(p.read_bytes()).hexdigest()[:16] if p.exists() else "absent")
    return out


def coverage() -> dict:
    """Live coverage numbers for all three papers, plus Paper 1's slow-lane binding state."""
    import importlib

    rows = {}
    for name, module in PAPERS:
        rep = importlib.import_module(module).audit()
        counts = rep["counts"]
        structural = counts.get("structural", 0)
        claims = rep["n_numerals"] - structural
        verified = sum(counts.get(k, 0) for k in VERIFIED_KINDS)
        rows[name] = dict(
            numerals=rep["n_numerals"], structural=structural, claims=claims,
            verified=verified, unbound=claims - verified,
            unaccounted=len(rep["unaccounted"]),
            by_kind={k: v for k, v in sorted(counts.items())})

    from puckworks.paper_a import claim_coverage as ca
    from puckworks.paper_a import slow_lane_bindings as sb
    sl = sb.verify()
    cov = ca.binding_coverage()

    # Round-8 P2-1. These are TWO populations and this table used to conflate them:
    #
    #   * `sb.verify()` counts BINDING RULES (62 fixed + 23 derived + 4 code constants = 89) and
    #     reports whether each still resolves and matches;
    #   * `ca.SLOW_LANE_RESULTS` is the 95 registered slow-lane numerals the manuscript quotes.
    #
    # Five binding rules bind values that are NOT registered slow-lane results, so subtracting the
    # rule count from the registered total ("95 - 89 = 6 unbound") credited those five against
    # results they do not cover and UNDERSTATED the gap. The registered population is the one that
    # answers "how many quoted numbers are checked", so coverage is taken from binding_coverage()
    # and rule health is reported separately rather than mixed into the same arithmetic.
    slow_lane = dict(
        total=cov["n_slow_lane"], bound=cov["n_archive_bound"],
        declared_unbindable=cov["n_declared_unbindable"], unbound=cov["n_still_unbound"],
        unbound_values=list(cov["still_unbound"]),
        binding_rules=sl["n_bound"], matching=sl["n_ok"],
        mismatched=sl["n_mismatched"], unresolvable=sl["n_unresolvable"],
        rules_outside_registered_set=sl["n_bound"] - cov["n_archive_bound"])
    _reconcile_slow_lane(slow_lane)

    return dict(
        source_commit=_commit(),
        generated_by="python tools/claim_binding_audit.py --write",
        input_fingerprints=_fingerprint(),
        papers=rows,
        totals=dict(
            numerals=sum(r["numerals"] for r in rows.values()),
            structural=sum(r["structural"] for r in rows.values()),
            claims=sum(r["claims"] for r in rows.values()),
            verified=sum(r["verified"] for r in rows.values()),
            unbound=sum(r["unbound"] for r in rows.values())),
        slow_lane=slow_lane)


def _reconcile_slow_lane(sl: dict) -> None:
    """Fail loudly if the coverage categories do not add up to the registered total.

    Round-8 P2-1 existed because nothing asserted this. The categories below are disjoint and
    exhaustive over the REGISTERED slow-lane results; the binding-rule counts deliberately are
    not part of the sum, because rules and registered results are different populations.
    """
    for key in ("total", "bound", "declared_unbindable", "unbound", "binding_rules",
                "matching", "mismatched", "unresolvable"):
        if not isinstance(sl.get(key), int) or sl[key] < 0:
            raise AssertionError(f"slow-lane coverage category {key!r} is missing or not a "
                                 f"non-negative integer: {sl.get(key)!r}")
    got = sl["bound"] + sl["declared_unbindable"] + sl["unbound"]
    if got != sl["total"]:
        raise AssertionError(
            "slow-lane coverage does not reconcile: bound(%d) + declared_unbindable(%d) + "
            "unbound(%d) = %d, but %d slow-lane results are registered"
            % (sl["bound"], sl["declared_unbindable"], sl["unbound"], got, sl["total"]))
    if sl["matching"] + sl["mismatched"] + sl["unresolvable"] != sl["binding_rules"]:
        raise AssertionError(
            "binding-rule health does not reconcile: matching(%d) + mismatched(%d) + "
            "unresolvable(%d) != %d rules"
            % (sl["matching"], sl["mismatched"], sl["unresolvable"], sl["binding_rules"]))


def _without_commit(text: str) -> str:
    """Drop the recorded commit before comparing.

    The commit is provenance, not an input: it changes on every commit, and CI checks out a
    synthetic merge commit that no committed document could ever name. Enforcing it would make
    this check fail permanently in CI while passing locally — the staleness signal that matters is
    the INPUT FINGERPRINTS, which change only when a manuscript or a coverage module does.
    """
    return "\n".join(ln for ln in text.splitlines()
                      if not ln.startswith("**Source commit:**"))


def _pct(a: int, b: int) -> str:
    return f"{100.0 * a / b:.1f} %" if b else "n/a"


def render(cov: dict) -> str:
    rows = cov["papers"]
    t = cov["totals"]
    sl = cov["slow_lane"]
    table = "\n".join(
        f"| {name} | {r['numerals']} | {r['structural']} | **{r['claims']}** | "
        f"{r['verified']} ({_pct(r['verified'], r['claims'])}) | "
        f"**{r['unbound']} ({_pct(r['unbound'], r['claims'])})** |"
        for name, r in rows.items())
    fp = "\n".join(f"| `{k}` | `{v}` |" for k, v in cov["input_fingerprints"].items())
    p1 = rows["Paper 1"]

    return f"""# How much of the three manuscripts is actually bound to a producer?

<!-- GENERATED by tools/claim_binding_audit.py. Do not edit by hand: run --write. -->

**Source commit:** `{cov['source_commit']}`
**Generated by:** `{cov['generated_by']}`
**Inputs:** the three numeral audits (`puckworks.paper_a.claim_coverage`,
`puckworks.paper_b2.claim_coverage`, `puckworks.paper3.claim_coverage`) and Paper 1's slow-lane
binding table (`puckworks.paper_a.slow_lane_bindings`), read live at generation time.

This exists to answer one question: *how much work is left, and where?* Seven review rounds have
found defects at a roughly constant rate, and the reason is measurable rather than mysterious.

## The headline

All three papers report **{sum(r['unaccounted'] for r in rows.values())} unaccounted numerals**.
That is not the same as bound.

| | numerals | of which structural | **claims** | verified against a producer, archive or constant | **unbound** |
|---|---:|---:|---:|---:|---:|
{table}
| **Total** | **{t['numerals']}** | **{t['structural']}** | **{t['claims']}** | \
**{t['verified']} ({_pct(t['verified'], t['claims'])})** | \
**{t['unbound']} ({_pct(t['unbound'], t['claims'])})** |

*Structural* = section, table, figure and equation numbers, years, citation markers. Not claims;
correctly excluded.

*Verified* counts the dispositions that resolve against something which computes or records the
value — a producer call, a committed archive, a module constant, or a recomputed derived quantity.
The remainder are accounted for by a hand-written explanation. That dictionary is what
"0 unaccounted" measures, and it is a weaker guarantee than it sounds.

## The correctness-critical subset: Paper 1's slow lane

Slow-lane results are the genuine computed outputs whose recomputation costs minutes to hours, so
they are the likeliest population to go stale — and five of the seven review rounds found stale
numbers there by hand.

Two populations are reported below and they must not be added together — conflating them is what
made this table overstate coverage before round 8. **Registered slow-lane results** are the
numerals the manuscript quotes; **binding rules** are the resolvers in
`slow_lane_bindings.py`, five of which bind values that are not registered slow-lane results.

| Paper 1 slow-lane results (registered population) | count |
|---|---:|
| Registered slow-lane numbers | {sl['total']} |
| **Bound to an archive, figure bundle or module constant** | **{sl['bound']}** |
| Declared unbindable, with the missing artefact named | {sl['declared_unbindable']} |
| **Still unbound** | **{sl['unbound']}** |

These three categories are disjoint and reconcile to the registered total; the generator asserts
that, so a repeat of the round-8 arithmetic defect fails the audit instead of being published.

| Binding-rule health (resolver population) | count |
|---|---:|
| Binding rules defined | {sl['binding_rules']} |
| Resolving and matching at this commit | {sl['matching']} |
| Mismatched (drifted) | {sl['mismatched']} |
| Unresolvable (archive or field missing) | {sl['unresolvable']} |
| Rules binding values outside the registered slow-lane set | {sl['rules_outside_registered_set']} |

`puckworks/paper_a/slow_lane_bindings.py` resolves each bound number against a committed archive,
the figure bundle, or a module constant, and `verify()` fails on drift. Bindings come in three
kinds: a **fixed path** into an archive or the committed figure bundle; a **derived** binding for
claims of the form *"smallest/largest X across the swept cases"*, which must be recomputed, since
pinning today's argmax would silently stop checking the claim the moment the extremum moved; and a
**code constant** — molecular weights, bed porosity — which is stronger than an archive, because the
manuscript is checked against the thing that actually runs. All four failure modes are
mutation-tested: a drifted archive value, a vanished archived field, a missing archive file, a
drifted code constant, and a moved derived extremum are each caught.

## What the unbound numbers actually are

They are not all equal, and the distinction decides how much matters.

**(a) Declared design settings — the large majority.** Thresholds, windows, condition counts, grid
sizes, decimation resolutions. These are *choices*, not results; recomputing them is meaningless.
But they are **retyped**, often dozens of times. The risk is not that any one is wrong; it is that
changing a design choice requires finding every occurrence by hand. This is a single-sourcing
problem, not a correctness problem.

**(b) Results exempted because they are expensive — the real risk.** Genuine computed outputs whose
explanation is a string rather than a producer call. Paper 1's are almost all prefixed
`SLOW LANE:` — endpoint propagation differences, PDE convergence deviations, objective-family
minima, paired resampling bounds. The table above is how many of those are now checked.

**(c) Values from sources.** Published calibrations, dataset facts, cited literature values. These
need *provenance*, not recomputation: a citation to the record they came from.

## Why Paper 3 leads Paper 1

Paper 3 is at {_pct(rows['Paper 3']['verified'], rows['Paper 3']['claims'])};
Paper 1 at {_pct(p1['verified'], p1['claims'])}. The difference is not diligence — it is
architecture. Paper 3 **splices generated blocks** from producers between explicit markers. Those
blocks have never drifted, in any round. Where Paper 3 drifted (round four's Appendix A), it was in
a hand-maintained *copy* of a spliced block, and the fix was to delete the copy.

That is the lesson of seven review rounds, visible as a number.

## A caveat on the "0 unaccounted" figure itself

Dispositions are keyed by the numeral's **value**, not its context, so the first matching entry
supplies the explanation for every occurrence of that token. A component count of 25 in Paper 3 was
once reported as accounted with the explanation *"draft date (25 July 2026)"* — the right
disposition class attached to an unrelated fact.

So the {t['verified']} verified figure is trustworthy: those resolve through a producer, archive or
constant path. The "explained" figure is softer than it looks — some of those explanations do not
describe the number they are attached to.

## The limit this audit does not reach

Round 7 found three submission-blocking defects that every count on this page would have passed:

| defect | why a value binding misses it |
|---|---|
| the manuscript's Reynolds number differed from the code's by α_l⁻² | the numerals are the same; the semantics are not |
| a 40 g endpoint labelled 40 mL throughout | the token "40" is identical either way |
| 108 scored records described as the complete coarse/fine corpus | 108 is arithmetically correct for the hidden subset |
| the resampling omitted cross-solute condition dependence | the output values match the producer exactly |
| the supplement described one least-squares fit for three objectives | every reported minimum still binds |

Binding a higher *proportion of numerals* would not have caught any of them. The next assurance
increment is **semantic binding** — model, observation, corpus, resampling, evidence and
presentation contracts asserted directly — which is what `tests/test_paper_a_model_contract.py`
now does.

## The adjudicated interval

Comparing the whole-group interval settled the earlier −0.72 / −0.73 question: the archive holds one
run, and `−0.725` sits exactly on a rounding boundary, so `−0.73` (half-away-from-zero) and `−0.72`
(half-to-even) are both defensible — which is why the manuscript once contained both. There were
never two runs. Every appearance is now rendered from the same canonical archive at one declared
precision, and `tests/test_paper_a_model_contract.py` fails when the main text and the supplement
disagree about it.

## Input fingerprints

`--check` fails when any of these changes without the audit being regenerated. That is the whole
mechanism by which this document cannot go stale again.

| input | sha256[:16] |
|---|---|
{fp}
"""


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else list(argv)
    cov = coverage()
    if "--json" in argv:
        print(json.dumps(cov, indent=2))
        return 0
    text = render(cov)
    if "--write" in argv:
        OUT.write_text(text, encoding="utf-8")
        SIDECAR.write_text(json.dumps(cov, indent=1) + "\n", encoding="utf-8")
        print(f"wrote {OUT.relative_to(REPO)} and {SIDECAR.relative_to(REPO)}")
        return 0
    if not OUT.exists():
        print(f"FAIL: {OUT.relative_to(REPO)} does not exist; run --write", file=sys.stderr)
        return 1
    if _without_commit(OUT.read_text(encoding="utf-8")) != _without_commit(text):
        print(f"FAIL: {OUT.relative_to(REPO)} is stale — its inputs have changed since it was "
              f"generated. Run: python tools/claim_binding_audit.py --write", file=sys.stderr)
        return 1
    print(f"{OUT.relative_to(REPO)} is current at commit {cov['source_commit']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
