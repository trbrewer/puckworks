"""Paper B2 semantic audit: numerical verification is not enough for this paper.

Third review P0.7 and major comment 13. Paper B2's central contribution is careful inference
terminology, and the prose had outpaced the code, figures, manifest labels and captions. The review
listed the drift explicitly:

* main prose said the cubic is not a lower bound, while Table 1, Figure 2 and the figure code called
  it a "flexibility bound";
* Methods used LOPO-EC, while Figure 3 and the manifest still said "held-out";
* the code correctly recorded that Phi(t) is not fully cross-fitted, while Methods called the
  comparison "like-for-like";
* manuscript and manifest called 0.149 a "noise floor";
* Figure 4 said "drift, not oscillation" and assigned 40 s/80 s dominant periods.

The review's own acceptance test was a repository-wide search. This is that search, executed. A
figure can reproduce a verified number while mislabelling its estimand, so these assertions are
about words, not values.
"""
import re
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[1]

#: Everything a reader or a downstream consumer could see.
SURFACES = [
    _ROOT / "docs" / "PAPER_B2_TEMPORAL_DRAFT.md",
    # Exported source data is a reader-visible artefact too: its column names were still
    # `dominant_period_s` after the manuscript withdrew the reading (fourth review 6.4).
    _ROOT / "docs" / "figures" / "paper_b2" / "source_data" / "fig4_residual_structure.csv",
    _ROOT / "puckworks" / "figures_paper_b2.py",
    _ROOT / "puckworks" / "analysis" / "waszkiewicz_shot_level.py",
    _ROOT / "puckworks" / "analysis" / "waszkiewicz_cross_pressure.py",
    _ROOT / "puckworks" / "paper_b2" / "build.py",
    _ROOT / "docs" / "figures" / "paper_b2" / "ALT_TEXT.md",
]

#: (pattern, why it is prohibited). A match is allowed ONLY on a line that also explicitly
#: withdraws or negates the term -- that is how a paper records a retraction without re-asserting
#: the claim.
PROHIBITED = [
    (r"noise floor",
     "P0.1: 0.149 is a leave-in dispersion, optimistic by exactly n/(n-1). It is not a noise "
     "floor, a lower bound, or a resolvability threshold."),
    (r"flexibility bound",
     "the same-trace cubic is a descriptive comparator, not a bound on achievable error"),
    (r"like-for-like",
     "P0.2: the spline is fully held out; Phi(t) retains an unwithheld dissolved-mass channel"),
    (r"drift, not oscillation",
     "P0.5: an 80-point window cannot distinguish drift from oscillation"),
    (r"dominant[_ ](?:residual[_ ])?period",
     "P0.5: 80 s and 40 s are the first two nonzero Fourier periods of the window, not measured "
     "timescales"),
    (r"shape information is real",
     "P0.3: the interval-holdout result does not survive comparator or gap sensitivity"),
    (r"held-out means",
     "P0.7: LOPO-EC withholds only the equilibrium calibration point, not the temporal inputs"),
    # Narrowly the SPLINE. "prespecified" is also a legitimate parameter-access level in the
    # dependency graph ("declared before running"), which the review did not object to.
    (r"prespecified (?:penalized|cubic|spline|smoother|B-spline)|"
     r"(?:spline|smoother|comparator) (?:is |was )?prespecified",
     "P1.1: no dated protocol predating result inspection is on record for the spline; use "
     "'fixed-architecture'"),
    # Fourth review 6.2. The Foster null contains ponding and a sharp wetting front advancing into
    # an initially dry bed (`docs/cards/foster2025.md`), so the wetted fraction and hydraulic path
    # length DO evolve. "machine-only" and "no evolving bed" claim more than the model supports,
    # and in a paper whose subject is mechanism non-identifiability the null taxonomy has to be
    # exact. What the model actually excludes is EXTRACTION-DRIVEN bed change.
    (r"machine[- ]only",
     "6.2: the Foster null is not machine-only -- it contains sharp-front infiltration through "
     "the bed. Use 'machine-wetting', 'pump-headspace-sharp-front-infiltration' or "
     "'boundary-and-infiltration'"),
    (r"no evolving bed|without an evolving bed|no bed (?:process|mechanism|dynamics)",
     "6.2: the wetting front IS evolving bed state. Say 'no extraction-driven bed change' and "
     "name what is held fixed: the saturated-bed constitutive law"),
]

#: A line that negates or withdraws the term is allowed to contain it.
_WITHDRAWAL = re.compile(
    # Negations and retractions.
    r"\b(?:not|none|never|no longer|neither|nor|withdraw|withdrawn|withdraws|retired|"
    r"prohibited|previously|used to|earlier version|must not|cannot|isn't|rather than|"
    # Error-naming. A sentence that says a label would be WRONG is disavowing it, not asserting
    # it: "plotting the leave-in dispersion and captioning it a noise floor" is an example of the
    # defect. These are narrow enough not to leak -- a sentence asserting a noise floor does not
    # describe itself as mislabelling.
    r"mislabel|mislabelling|mislabeled|mislabelled|wrongly|incorrectly|erroneously|falsely|"
    # `overstat` needs a suffix wildcard: `overstat\b` never matched, because every real spelling
    # continues -- overstates, overstated, overstating. The alternative was silently dead.
    r"mistakenly|overstat\w*|overclaim\w*)\b", re.I)


#: Sentence boundary. Deliberately includes `;` and `:` because the withdrawals in these files are
#: often clause-level ("... is not a noise floor; it is a leave-in dispersion").
_SENTENCE_END = re.compile(r"(?<=[.;:])\s+")

#: How close a disavowal must sit to the banned phrase to count as being ABOUT it. A sentence can
#: legitimately contain an unrelated "never" or "only" far from the term -- the spline sentence
#: does, and it exempted a reinstated "prespecified" 200 characters away. Every genuine withdrawal
#: in these files sits within ~80 characters of the phrase it withdraws.
_NEAR = 120


def _string_spans(src: str):
    """Character spans of every string literal in a Python source file.

    Tokenising rather than regex-matching quotes: nested and triple-quoted forms make a regex
    wrong in exactly the cases that matter (docstrings).
    """
    import io
    import tokenize
    starts = [0]
    for line in src.splitlines(keepends=True):
        starts.append(starts[-1] + len(line))

    def off(row, col):
        return starts[row - 1] + col

    spans = []
    try:
        for tok in tokenize.generate_tokens(io.StringIO(src).readline):
            if tok.type == tokenize.STRING:
                spans.append((off(*tok.start), off(*tok.end)))
    except (tokenize.TokenError, IndentationError, SyntaxError):
        return []
    return spans


def _offending_lines(path: Path, pattern: str, lookback: int = 1):
    """Flag a match unless the SENTENCE containing it withdraws or negates the term.

    Two scoping bugs were found here by mutation-testing this guard against itself, and both made
    it weaker than it looked:

    1. It originally used a +/-2 LINE window. These files are paragraph-per-line, so that was a
       +/-2 PARAGRAPH window -- 2181 characters in the case that exposed it, containing five
       different withdrawal markers. Injecting "The shot-to-shot noise floor is 0.149 g/s and sets
       the resolution limit" into the manuscript did NOT fail the audit.
    2. The first fix split sentences per line. Sentences span wrapped lines in docstrings and
       Markdown, so a withdrawal in the first half of a sentence did not protect the second half,
       and a legitimate sentence was flagged.

    The scope is therefore computed on the WHOLE text: the sentence containing the match, plus
    `lookback` sentences before it -- one by default, because a withdrawal sometimes introduces its
    list in the preceding sentence. Line numbers are recovered from the match offset.

    3. A third gap, found the same way: every space in a pattern was a LITERAL space, so a
       prohibited phrase that happened to wrap across a line break was invisible. The Figure 4
       caption asserted "Dominant residual\nperiod" -- a claim the manuscript had already
       withdrawn in its own body -- and this guard passed. Pattern spaces are now compiled to
       `\s+`, so wrapping cannot hide a term.
    """
    if not path.exists():
        return []
    pattern = re.sub(r"(?<!\\)(?<!\\s)\s+", r"\\s+", pattern)
    text = path.read_text(encoding="utf-8")
    literals = _string_spans(text) if path.suffix == ".py" else []
    # Sentence spans over the whole file, so a sentence may cross newlines.
    bounds = [0] + [m.end() for m in _SENTENCE_END.finditer(text)] + [len(text)]
    spans = [(bounds[i], bounds[i + 1]) for i in range(len(bounds) - 1)]

    out = []
    for m in re.finditer(pattern, text, re.I):
        k = next(i for i, (a, b) in enumerate(spans) if a <= m.start() < b)
        lo = max(spans[max(0, k - lookback)][0], m.start() - _NEAR)
        hi = min(spans[k][1], m.end() + _NEAR)
        # A disavowal must live in the SAME textual artefact as the claim. In source, each string
        # literal is its own artefact: a figure title reading "Dominant residual period" is not
        # excused by the neighbouring axis label reading "not a measured timescale". Confining the
        # scope to the enclosing literal fixes that without breaking the opposite case, where a
        # long docstring legitimately disavows a term it names further down.
        own = next((s for s in literals if s[0] <= m.start() < s[1]), None)
        if own is not None:
            lo, hi = max(lo, own[0]), min(hi, own[1])
        # EXCISE THE MATCH ITSELF before looking for a disavowal. Two of the prohibited phrases
        # contain their own negation -- "drift, not oscillation" is the clearest -- so a naive
        # search finds the "not" inside the very phrase being banned and exempts it. Injecting
        # "The residual structure is drift, not oscillation." passed the audit before this.
        scope = " ".join((text[lo:m.start()] + " " + text[m.end():hi]).split())
        if _WITHDRAWAL.search(scope):
            continue
        line = text.count("\n", 0, m.start()) + 1
        out.append(f"{path.name}:{line}: {' '.join(text[lo:hi].split())[:130]}")
    return out


def test_a_withdrawal_protects_the_whole_sentence_even_when_wrapped(tmp_path):
    """The over-correction, pinned. A sentence split across lines must be judged whole."""
    f = tmp_path / "x.py"
    f.write_text('"""A figure can reproduce a value while mislabelling its estimand -- it is\n'
                 'not a noise floor merely because a caption says so."""\n', encoding="utf-8")
    assert not _offending_lines(f, r"noise floor")


@pytest.mark.parametrize("pattern,why", PROHIBITED, ids=[p for p, _ in PROHIBITED])
def test_no_load_bearing_use_of_a_withdrawn_term(pattern, why):
    hits = [h for p in SURFACES for h in _offending_lines(p, pattern)]
    assert not hits, f"{why}\n  " + "\n  ".join(hits)


def test_the_audit_is_not_vacuous(tmp_path):
    """A guard that matched nothing would pass silently forever."""
    f = tmp_path / "x.md"
    f.write_text("The shot-to-shot noise floor is 0.149.\n", encoding="utf-8")
    assert _offending_lines(f, r"noise floor")


def test_a_withdrawal_sentence_is_allowed_to_name_the_term(tmp_path):
    """The papers must be able to SAY what they withdrew."""
    f = tmp_path / "x.md"
    f.write_text("None of these is an irreducible noise floor or a threshold.\n", encoding="utf-8")
    assert not _offending_lines(f, r"noise floor")


def test_the_exemption_does_not_leak_across_sentences(tmp_path):
    """THE VACUITY BUG, pinned. A negation elsewhere in the same PARAGRAPH must not exempt a
    violation. This is what a line-scoped window got wrong: the paragraph it exempted was 2181
    characters long and contained five withdrawal markers."""
    f = tmp_path / "x.md"
    f.write_text(
        "Nothing here is a threshold and no claim is made. "
        "The shot-to-shot noise floor is 0.149 g/s and sets the resolution limit. "
        "We never treat it as a bound.\n", encoding="utf-8")
    hits = _offending_lines(f, r"noise floor")
    assert hits, "a violation was exempted by a negation in a NEIGHBOURING sentence"


# ── the positive half: the corrected vocabulary must actually be present ──────────────────────
REQUIRED = [
    ("leave-in", "the 0.149 value must be labelled as a leave-in dispersion"),
    ("other-four", "the honest 0.186 empirical-template scale must be reported"),
    ("fixed-architecture", "the spline's architecture claim must be the defensible one"),
    ("partly target-informed", "the LOSO asymmetry must be stated where the two are compared"),
]


@pytest.mark.parametrize("phrase,why", REQUIRED, ids=[p for p, _ in REQUIRED])
def test_the_corrected_vocabulary_is_present_in_the_manuscript(phrase, why):
    text = (_ROOT / "docs" / "PAPER_B2_TEMPORAL_DRAFT.md").read_text(encoding="utf-8").lower()
    assert phrase.lower() in text, why


def test_the_interval_holdout_claim_is_absent_from_the_abstract_and_conclusions():
    """P0.3: it must not appear as a result in the two places an editor reads first."""
    text = (_ROOT / "docs" / "PAPER_B2_TEMPORAL_DRAFT.md").read_text(encoding="utf-8")
    abstract = text.split("\n")[10]
    conclusions = text.split("## 9. Conclusions")[1].split("## Data and code")[0]
    for where, body in (("abstract", abstract), ("conclusions", conclusions)):
        assert "unobserved time interval" not in body, f"interval-holdout claim in the {where}"
        assert "interior segments" not in body, f"interval-holdout claim in the {where}"


def test_the_abstract_states_the_access_asymmetry():
    """P0.2: the abstract places the held-out spline beside Phi(t); it must say they differ."""
    abstract = (_ROOT / "docs" / "PAPER_B2_TEMPORAL_DRAFT.md"
                ).read_text(encoding="utf-8").split("\n")[10]
    assert "fully held out" in abstract
    assert "partly target-informed" in abstract
