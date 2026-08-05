"""screen_i045_evidence_halves.py — Insight Foundry cheap screen for candidate I-045.

    CHEAP_SCIENTIFIC_SCREEN
    NOT_A_PUBLICATION_RESULT
    NOT_A_MODEL_VALIDATION_UPGRADE

Question (generated, verbatim from the candidate):

    For the 1 datasets whose validation_strength names both independent + verification, which
    of those strengths does each consuming gate actually rely on?

The dataset is `foster2025_2/fig12_14_curves`. Controlling source card: `docs/cards/
foster2025_2.md` — NOT `docs/cards/foster2025.md`, which is a different card and carries its own
TEMPLATE_DEVIATION that this screen does not inherit.

INDEPENDENT AND VERIFICATION ARE NOT ORDINAL HERE. They are different evidentiary FUNCTIONS:

    verification  — does our port reproduce the source's own fitted ODE output?
    independent   — does the trajectory sit on the measured CT points?

A consumer may legitimately need both at once (measured data, verified implementation), and
"uses both" is a correct outcome, not a promotion. Nothing in this module ranks them.

WHAT MAKES THIS DATASET UNUSUALLY TRACTABLE. The two halves are not two readings of one column
(as in I-040) — they are DIFFERENT COLUMNS of one file:

    verification half : s_fit_mm, w_fit_mm, H_fit_mm      461 rows, the paper's ODE on a 0.02 s grid
    independent half  : s_data_mm, H_data_mm, w_data_mm    8 rows, pixel-digitized CT (5-line mean)
                        + the matching *_err_mm columns
    time base         : t_s                                shared, carries no evidentiary function

So attribution can be established by observing WHICH COLUMNS a consumer reads, and that is
exactly what layer 2 does.

METHOD — the accepted I-040 four-layer pattern, reused WITHOUT importing I-040's outcome:

  1. STATIC ENUMERATION, deliberately over-approximating: every reference to the loader, to the
     dataset id, and to the consuming gate, across source, tests, docs and generated evidence
     records.
  2. COLUMN-LEVEL ACCESS TRACING — the second, independent enumeration. The loader is wrapped so
     every row is a dict that records which KEYS are read, and each candidate consumer is
     executed. This is used solely to establish which evidence fields are read; it is not a
     model campaign and nothing is fitted or scored.
  3. MANUAL RECONCILIATION of the union.
  4. HUMAN ATTRIBUTION (`CONSUMERS`), one row per consumer, recording every field the brief
     requires including any misleading wording.
  5. ADVERSARIAL TEXT SCAN for independent / independently / verification / verified /
     validation across every consuming surface, each hit classified IN CONTEXT (negation,
     historical, other-dataset, post-fit vs predictive).

Run:  python -m puckworks.analysis.screen_i045_evidence_halves
"""
from __future__ import annotations

import ast
import inspect
import json
import pathlib
import re

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]

CANDIDATE_ID = "I-045"
DATASET_ID = "foster2025_2/fig12_14_curves"
LOADER = "foster_fig12_14_curves"
SOURCE_CARD = "docs/cards/foster2025_2.md"

#: The MANIFEST validation_strength cell, copied byte-identical. Never paraphrased.
MANIFEST_VALIDATION_STRENGTH = "independent (CT data) / verification (fitted curves)"

#: The MANIFEST caveat cell, copied byte-identical.
MANIFEST_CAVEAT = ("s_fit/H_fit = paper ODE (0.02s grid); s_data/H_data = pixel-digitized CT "
                   "(5-line mean); Fig8 -H differs from Fig14 H (do not mix)")

#: The controlling card's circularity note, copied byte-identical. This is the sentence that
#: settles which SENSE of "independent" the CT half can carry.
CARD_CIRCULARITY_NOTE = ("Note the circularity: k and φ_T are fitted to the same s/H curves "
                         "being reproduced, so the source validates model FORM, not "
                         "parameter-free prediction.")

# ------------------------------------------------------------------------------------------
# The halves — by COLUMN, and by evidentiary FUNCTION (not by rank)
# ------------------------------------------------------------------------------------------
HALVES = {
    "verification_fitted_curves": dict(
        key="verification_fitted_curves",
        manifest_wording="verification (fitted curves)",
        function="Does our port reproduce the SOURCE'S OWN fitted ODE output? A statement about "
                 "the implementation, not about reality.",
        columns=["s_fit_mm", "w_fit_mm", "H_fit_mm"],
        n_rows=461,
        provenance="the paper's ODE evaluated on a 0.02 s grid (MANIFEST caveat, verbatim)"),
    "independent_ct_data": dict(
        key="independent_ct_data",
        manifest_wording="independent (CT data)",
        function="Does the trajectory sit on the MEASURED micro-CT points? A statement about a "
                 "measurement — but see `independence_sense` below: measured is not the same as "
                 "held out.",
        columns=["s_data_mm", "s_data_err_mm", "w_data_mm", "w_data_err_mm",
                 "H_data_mm", "H_data_err_mm"],
        n_rows=8,
        provenance="pixel-digitized CT, 5-line mean (MANIFEST caveat, verbatim)",
        independence_sense=(
            "AMBIGUOUS IN THE MANIFEST, RESOLVED BY THE CARD. 'independent' here means an "
            "independent MEASUREMENT MODALITY (a real CT observation, as opposed to model "
            "output). It does NOT mean held out from the fit: the controlling card records "
            "that k and phi_T were fitted to these same s/H curves. Anything reading it in the "
            "ROADMAP S0 sense — 'data not used in fitting the thing being tested' — would be "
            "reading it wrongly.")),
    "time_base_only": dict(
        key="time_base_only",
        manifest_wording="(not an evidentiary half — the shared abscissa)",
        function="Supplies the time grid. Carries no evidentiary function of either kind.",
        columns=["t_s"], n_rows=461,
        provenance="the 0.02 s experiment-time grid both halves are expressed on"),
}

#: Functional classifications. DELIBERATELY NOT ORDERED — there is no ranking here.
CLS_INDEPENDENT = "INDEPENDENT_LOAD_BEARING"
CLS_VERIFICATION = "VERIFICATION_LOAD_BEARING"
CLS_BOTH = "BOTH_LOAD_BEARING"
CLS_NEITHER = "NEITHER_LOAD_BEARING"


def _rec(name, kind, location, half, reads, assertion, indep_lb, verif_lb, both_ok,
         neither, cls, rationale, misleading_wording=None):
    return dict(consumer=name, kind=kind, location=location, evidence_half=half,
                source_row_and_columns_read=reads, assertion=assertion,
                independence_load_bearing=indep_lb,
                verification_reproduction_load_bearing=verif_lb,
                both_legitimately_required=both_ok,
                neither_load_bearing=neither,
                misleading_wording=misleading_wording,
                classification=cls, rationale=rationale)


# ------------------------------------------------------------------------------------------
# LAYER 4 — HUMAN ATTRIBUTION. One row per consumer. Hand-read.
# ------------------------------------------------------------------------------------------
CONSUMERS = [
    _rec("gate_foster_ct_trajectory", "gate", "puckworks/validation/gates.py:1125",
         "both",
         "all 461 rows: t_s, s_fit_mm, H_fit_mm (RMSE arm); the 8 non-empty rows: s_data_mm, "
         "s_data_err_mm, H_data_mm, H_data_err_mm (bracketing arm)",
         "TWO assertions in one gate. (a) the port's s(t)/H(t) match the paper's own fitted ODE "
         "curves to < 0.2 mm RMSE; (b) the port brackets at least 4 of the 8 digitized CT points "
         "within max(err, 0.5 mm) error bars.",
         indep_lb=True, verif_lb=True, both_ok=True, neither=False, cls=CLS_BOTH,
         rationale="Assertion (a) is carried ONLY by the fitted-curve columns and is a "
                   "statement about the port. Assertion (b) is carried ONLY by the CT columns "
                   "and is a statement about a measurement. Both halves are genuinely required "
                   "and neither substitutes for the other — the legitimate 'uses both' case the "
                   "candidate's own alternative explanation anticipates.",
         misleading_wording=(
             "The docstring's parenthetical '(independent, \"qualitative-good\")' on the CT arm "
             "copies the MANIFEST word without the card's circularity qualifier. Read in the "
             "ROADMAP S0 sense ('data not used in fitting the thing being tested') it would be "
             "wrong — the card records k and phi_T as fitted to these same s/H curves. "
             "SURFACED, and see `verdict.misattribution_analysis`: every downstream consumer "
             "of this gate independently refuses the strong reading, so the wording does not "
             "propagate.")),

    _rec("EVIDENCE_LINKS foster2025.machine_mode::gate_foster_ct_trajectory", "evidence_record",
         "puckworks/paper3/EVIDENCE_LINKS.json",
         "both",
         "consumes the gate, and names the dataset TWICE with different roles: "
         "{evidence_role: eval, independence: same_campaign} and "
         "{evidence_role: fit, independence: fit_input}",
         "Records the gate's claim verbatim and adjudicates its evidentiary status: "
         "evidence_strength = source_curve_reproduction; relationship = "
         "same_campaign_not_held_out; reality_facing = false; support_status = context_only.",
         indep_lb=False, verif_lb=True, both_ok=False, neither=False, cls=CLS_VERIFICATION,
         rationale="DECISIVE FOR THIS AUDIT. This record does not merely avoid the strong "
                   "reading of 'independent' — it explicitly REFUSES it. It splits the one "
                   "dataset into an eval role and a FIT role, marks the eval role "
                   "`same_campaign` rather than independent, sets reality_facing false, and "
                   "carries the card's circularity into its own caveat field. Its "
                   "claim_not_supported field states that the record 'does not establish "
                   "parameter-free or out-of-sample prediction'. The load-bearing evidentiary "
                   "function it claims is verification/reproduction only.",
         misleading_wording=None),

    _rec("registry entry foster2025.machine_mode", "registry",
         "puckworks/models/__init__.py:328",
         "neither",
         "names the gate in its `gates` list; reads no column itself",
         "Registers the component with evidence_strength `source_curve_reproduction` and lists "
         "gate_foster_ct_trajectory among its gates.",
         indep_lb=False, verif_lb=False, both_ok=False, neither=True, cls=CLS_NEITHER,
         rationale="A registration, not an assertion about this dataset. The component-level "
                   "strength it carries is `source_curve_reproduction`, which is the "
                   "reproduction function, and it makes no independence claim of any kind.",
         misleading_wording=None),

    _rec("PV-02 evidence selection (exclusion rationale)", "public_claim",
         "puckworks/public/claims.py:208",
         "neither",
         "reads no column; names the gate only to EXCLUDE it",
         "States that `gate_foster_ct_trajectory` remains excluded from PV-02 'on its own "
         "merits: it concerns wetting-front depth s(t) and headspace H(t), which this claim "
         "does not mention.'",
         indep_lb=False, verif_lb=False, both_ok=False, neither=True, cls=CLS_NEITHER,
         rationale="An exclusion is the strongest possible non-use: the only reader-facing "
                   "public claim in the neighbourhood explicitly declines to stand on this "
                   "dataset at all, and gives an observable-scope reason for doing so.",
         misleading_wording=None),

    _rec("paper3 evidence graph (generated)", "generated_report",
         "docs/paper3_resource/generated/evidence_graph.json, evidence_graph_matrix.{csv,md}",
         "both",
         "derived from EVIDENCE_LINKS.json; reads no column directly",
         "Renders the same adjudication: source_curve_reproduction, "
         "same_campaign_not_held_out, context_only, reality_facing false.",
         indep_lb=False, verif_lb=True, both_ok=False, neither=False, cls=CLS_VERIFICATION,
         rationale="A faithful rendering of the evidence record above; it introduces no "
                   "attribution of its own and cannot promote what its source refuses.",
         misleading_wording=None),

    _rec("paper3 Fig 2 evidence vector (generated)", "generated_report",
         "docs/figures/paper3/source_data/fig2_evidence_vectors.csv",
         "both",
         "derived; reads no column directly",
         "Records relation `source_curve_reproduction`, scope naming BOTH 'the paper's fitted "
         "ODE curves' and 'digitized CT measurements', and outcome `negative`.",
         indep_lb=False, verif_lb=True, both_ok=False, neither=False, cls=CLS_VERIFICATION,
         rationale="Names both halves in its scope string — correctly, since the gate reads "
                   "both — while recording the relation as reproduction and the outcome as "
                   "NEGATIVE. A negative outcome cannot be an over-claim in either direction.",
         misleading_wording=None),

    _rec("tests/test_data_loaders.py::foster loader smoke", "test",
         "tests/test_data_loaders.py:131",
         "independent_ct_data",
         "asserts at least one row has a non-empty s_data_mm",
         "Asserts the loader returns rows in which the CT column is populated. A parsing "
         "check, not an evidentiary claim.",
         indep_lb=False, verif_lb=False, both_ok=False, neither=True, cls=CLS_NEITHER,
         rationale="Touches the independent half but asserts nothing about evidence: it checks "
                   "that the sparse column survived ingestion. Reading a half is not relying "
                   "on it.",
         misleading_wording=None),
]


# ------------------------------------------------------------------------------------------
# LAYER 1 — static enumeration, deliberately over-approximating
# ------------------------------------------------------------------------------------------
_SKIP = {"__pycache__", ".git", "build", "dist", ".venv"}
#: Generated Foundry artifacts are excluded from the SEARCH SPACE, not from the audit: they are
#: the candidate's own provenance record, they are byte-frozen, and this screen may not edit
#: them. Their mention of the dataset id is bookkeeping about the candidate, not a consumer.
_EXCLUDE_PATHS = ("docs/insights/generated",)


def _files():
    for p in sorted(REPO_ROOT.rglob("*")):
        if not p.is_file() or p.suffix not in (".py", ".md", ".json", ".csv"):
            continue
        rel = str(p.relative_to(REPO_ROOT))
        if any(part in _SKIP for part in p.parts) or rel.startswith(_EXCLUDE_PATHS):
            continue
        yield p, rel


def static_references():
    """Every textual reference to the loader, the dataset id, or the consuming gate.

    Over-approximating by design: it matches prose and generated tables as readily as code, so
    it flags non-consumers freely. It is a search over DIRECT, STATICALLY RECOVERABLE references
    and is not a proof of coverage for dynamic access — which is why layer 2 exists.
    """
    pats = {"loader": re.compile(r"\b%s\b" % LOADER),
            "dataset_id": re.compile(re.escape(DATASET_ID)),
            "gate": re.compile(r"\bgate_foster_ct_trajectory\b")}
    out = []
    for p, rel in _files():
        try:
            src = p.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):                  # pragma: no cover
            continue
        for kind, pat in pats.items():
            for m in pat.finditer(src):
                ln = src[:m.start()].count("\n") + 1
                line = src.splitlines()[ln - 1].strip()
                out.append(dict(file=rel, line=ln, match_kind=kind, text=line[:220]))
    return out


def static_call_sites():
    """AST-level call sites of the loader, with the enclosing function."""
    out = []
    for p, rel in _files():
        if p.suffix != ".py":
            continue
        src = p.read_text(encoding="utf-8")
        if LOADER not in src:
            continue
        try:
            tree = ast.parse(src)
        except SyntaxError:                                    # pragma: no cover
            continue
        funcs = [(n.lineno, n.end_lineno, n.name) for n in ast.walk(tree)
                 if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            f = node.func
            name = f.attr if isinstance(f, ast.Attribute) else getattr(f, "id", None)
            if name != LOADER:
                continue
            inner = sorted((q for q in funcs if q[0] <= node.lineno <= q[1]),
                           key=lambda q: q[1] - q[0])
            out.append(dict(file=rel, line=node.lineno,
                            function=inner[0][2] if inner else "<module>"))
    return out


# ------------------------------------------------------------------------------------------
# LAYER 2 — column-level access tracing (the second, independent enumeration)
# ------------------------------------------------------------------------------------------
class _TracingRow(dict):
    """A row that records which column keys are read. Behaves exactly like the original dict."""

    __slots__ = ("_seen",)

    def __init__(self, data, seen):
        super().__init__(data)
        self._seen = seen

    def __getitem__(self, k):
        self._seen.add(k)
        return super().__getitem__(k)

    def get(self, k, default=None):                            # pragma: no cover - completeness
        self._seen.add(k)
        return super().get(k, default)


def trace_columns(callables_by_name):
    """Execute each named callable with the loader wrapped; return the columns each one reads.

    Used SOLELY to establish which evidence fields are read. Nothing is fitted, scored or
    compared; the callables' return values are discarded.
    """
    from puckworks import data as D
    real = getattr(D, LOADER)
    seen: set = set()

    def traced():
        return [_TracingRow(r, seen) for r in real()]

    setattr(D, LOADER, traced)
    import sys
    rebound = []
    for name, mod in list(sys.modules.items()):
        if name.startswith("puckworks") and getattr(mod, LOADER, None) is real:
            setattr(mod, LOADER, traced)
            rebound.append(mod)
    try:
        out = {}
        for label, fn in callables_by_name.items():
            seen.clear()
            err = None
            try:
                fn()
            except Exception as exc:                           # pragma: no cover - diagnostic
                err = "%s: %s" % (type(exc).__name__, exc)
            cols = sorted(seen)
            out[label] = dict(
                columns_read=cols, error=err,
                halves_touched=sorted({h for h in HALVES
                                       if any(c in HALVES[h]["columns"] for c in cols)}))
        return out
    finally:
        setattr(D, LOADER, real)
        for mod in rebound:
            setattr(mod, LOADER, real)


def default_traced_callables():
    from puckworks.validation import gates as G
    return {"gate_foster_ct_trajectory": G.gate_foster_ct_trajectory}


# ------------------------------------------------------------------------------------------
# LAYER 5 — adversarial text scan
# ------------------------------------------------------------------------------------------
SCAN_TOKENS = ("independent", "independently", "verification", "verified", "validation")

#: A COVERAGE NOTE, not a defect. The gate docstring states its reproduction arm as "verifying
#: the port" — and "verifying" is not one of the five specified tokens, so the prose scan does
#: not raise a hit there. The phrase was read during hand attribution (layer 4) and is recorded
#: on the gate's consumer row; it is correct usage. Recorded here so a reader does not conclude
#: the docstring's verification language went unexamined.
SCAN_COVERAGE_NOTES = [
    dict(surface="gate docstring", phrase="verifying the port",
         token_scanned=False,
         why="the inflection 'verifying' is outside the five specified tokens",
         examined_by="layer 4 hand attribution; classified CORRECT_VERIFICATION_USE there"),
]

#: Surfaces that actually consume the dataset or the gate. The scan is over these, in context.
SCAN_SURFACES = [
    ("gate docstring", "puckworks/validation/gates.py", "gate_foster_ct_trajectory"),
    ("evidence record", "puckworks/paper3/EVIDENCE_LINKS.json", "gate_foster_ct_trajectory"),
    ("public claim (exclusion)", "puckworks/public/claims.py", "gate_foster_ct_trajectory"),
    ("controlling source card", SOURCE_CARD, None),
    ("MANIFEST row", "puckworks/data/MANIFEST.csv", DATASET_ID),
]

#: Per-hit context classification, hand-read. Each rule pairs a TOKEN with a verbatim FRAGMENT
#: that must contain that token, so a surface carrying several tokens cannot have one hit's
#: classification bleed onto another's — the first version of this scan did exactly that and
#: mislabelled the docstring's "independent" hit with the neighbouring "verifying the port".
HIT_RULES = [
    dict(token="independent", fragment="(independent, 'qualitative-good')",
         classification="AMBIGUOUS_MEASUREMENT_SENSE",
         note="Copies the MANIFEST word for the CT arm. True in the measurement-modality sense; "
              "would be wrong in the ROADMAP S0 held-out sense. No downstream consumer takes "
              "the strong reading — see the misattribution analysis. Surfaced as a wording "
              "risk."),
    dict(token="independent", fragment="independent (CT data) / verification (fitted curves)",
         classification="THE_TARGET_CELL",
         note="The MANIFEST cell under audit, quoted verbatim. Its 'independent' is the "
              "measurement-modality sense; the controlling card supplies the circularity that "
              "rules out the held-out sense."),
    dict(token="verification", fragment="independent (CT data) / verification (fitted curves)",
         classification="THE_TARGET_CELL",
         note="The other half of the same cell under audit."),
    dict(token="validation",
         fragment="item 1.6: front s(t)/headspace H(t) trajectory validation",
         classification="GATE_USE_FIELD_NOT_AN_EVIDENCE_CLAIM",
         note="The MANIFEST `gate_use` column names what the row is FOR. It is a routing "
              "field, not a strength claim; the strength claim is the adjacent "
              "validation_strength cell."),
    dict(token="validation", fragment="## Calibration and validation offered by the source",
         classification="SOURCE_CARD_SECTION_HEADING",
         note="A template section heading in the controlling card. Carries no attribution."),
    dict(token="validation", fragment="the key validation series",
         classification="OTHER_DATASET",
         note="Describes Figs 6/8 (s(t) and -H(t) at 1 s with error bars), which are the "
              "SEPARATE manifest rows foster2025_2/fig6_front_position and .../fig8_headspace "
              "— not the row under audit. The MANIFEST caveat warns explicitly that Fig 8 -H "
              "differs from Fig 14 H and must not be mixed."),
]

#: Tokens found on a scanned surface but belonging to a DIFFERENT manifest row. The scan window
#: is now clipped to the target row, so these should not arise; the rule is kept as a backstop
#: because a wider window silently attributing a neighbour's wording is exactly the failure the
#: first version of this scan had.
OTHER_ROW_MARKERS = ("independent (parameter-free triangle)", "verification (model curve)",
                     "independent (SPH-derived", "item 1.6: flow-minimum validation")


def structural_independence_fields():
    """Independence expressed as a STRUCTURED FIELD rather than prose.

    The prose scan finds nothing in `EVIDENCE_LINKS.json` — that record contains none of the
    five specified tokens. That is not a gap in coverage: the evidence layer states independence
    in a machine-readable `independence` field per source role instead of in sentences. A text
    scan alone would therefore report a silent surface and miss the strongest statement in the
    whole audit, so the field is read directly.
    """
    p = REPO_ROOT / "puckworks/paper3/EVIDENCE_LINKS.json"
    data = json.loads(p.read_text(encoding="utf-8"))
    recs = data if isinstance(data, list) else data.get("links", [])
    out = []
    for r in recs:
        if r.get("gate") != "gate_foster_ct_trajectory":
            continue
        for src in r.get("sources", []):
            if DATASET_ID not in src.get("dataset_manifest_ids", []):
                continue
            out.append(dict(file="puckworks/paper3/EVIDENCE_LINKS.json",
                            evidence_role=src.get("evidence_role"),
                            independence=src.get("independence"),
                            source_card=src.get("source_card"),
                            reading=("`%s` is not an independence claim — it is a refusal of "
                                     "one." % src.get("independence")
                                     if src.get("independence") in ("same_campaign", "fit_input")
                                     else "asserts independence")))
        out.append(dict(file="puckworks/paper3/EVIDENCE_LINKS.json", field="relationship",
                        value=r.get("relationship"), reading="records the dataset as not held out"))
        out.append(dict(file="puckworks/paper3/EVIDENCE_LINKS.json", field="reality_facing",
                        value=r.get("reality_facing"),
                        reading="false — the record does not face reality"))
        out.append(dict(file="puckworks/paper3/EVIDENCE_LINKS.json", field="support_status",
                        value=r.get("support_status"), reading="context_only"))
    return dict(records=out,
                n_prose_token_hits_on_this_surface=0,
                why_no_prose_hits=("EVIDENCE_LINKS.json contains none of the five scanned "
                                   "tokens; it expresses independence structurally. Read the "
                                   "fields, not the prose."),
                asserts_independence=any(
                    x.get("independence") not in (None, "same_campaign", "fit_input")
                    for x in out))


def _classify_hit(token, context):
    """Match a hand-read rule whose FRAGMENT contains this TOKEN and appears in this context."""
    lo = context.lower()
    best = None
    for rule in HIT_RULES:
        if rule["token"] != token:
            continue
        frag = rule["fragment"].lower()
        if token not in frag or frag not in lo:
            continue
        pos = lo.index(frag)
        if best is None or pos < best[0]:
            best = (pos, rule)
    if best:
        r = best[1]
        return dict(classification=r["classification"], note=r["note"],
                    matched_fragment=r["fragment"])
    for marker in OTHER_ROW_MARKERS:
        if marker.lower() in lo:
            return dict(classification="OTHER_DATASET", matched_fragment=marker,
                        note="Belongs to a different MANIFEST row that shares the file; not a "
                             "consumer of the dataset under audit.")
    return dict(classification="UNCLASSIFIED", matched_fragment=None,
                note="no hand-read rule matched — must be read before the audit can conclude")


def _surface_text(rel, anchor):
    """The text to scan for one surface, clipped so it cannot bleed into a neighbour."""
    p = REPO_ROOT / rel
    if not p.exists():                                         # pragma: no cover
        return ""
    text = p.read_text(encoding="utf-8")
    if rel.endswith("MANIFEST.csv"):
        # clip to the TARGET ROW ONLY — a character window bleeds into adjacent datasets
        for line in text.splitlines():
            if line.startswith(DATASET_ID + ","):
                return line
        return ""                                              # pragma: no cover
    if anchor == "gate_foster_ct_trajectory" and rel.endswith("gates.py"):
        from puckworks.validation import gates as G
        return inspect.getsource(G.gate_foster_ct_trajectory)
    if rel.endswith("EVIDENCE_LINKS.json"):
        data = json.loads(text)
        recs = data if isinstance(data, list) else data.get("links", [])
        for r in recs:
            if r.get("gate") == anchor:
                return json.dumps(r, indent=1, ensure_ascii=False)
        return ""                                              # pragma: no cover
    if rel.endswith("claims.py"):
        i = text.find(anchor)
        return text[max(0, i - 1200):i + 400] if i >= 0 else ""
    return text


def text_scan():
    """Every token hit on a consuming surface, each classified IN CONTEXT by a hand-read rule."""
    out = []
    for label, rel, anchor in SCAN_SURFACES:
        text = _surface_text(rel, anchor)
        if not text:
            continue
        low = text.lower()
        for tok in SCAN_TOKENS:
            for m in re.finditer(r"\b%s\b" % tok, low):
                ctx = text[max(0, m.start() - 150):m.end() + 150].replace("\n", " ")
                ctx = re.sub(r"\s+", " ", ctx).strip()
                out.append(dict(surface=label, file=rel, token=tok, context=ctx,
                                context_classification=_classify_hit(tok, ctx)))
    return out


# ------------------------------------------------------------------------------------------
# Reconciliation and the decision
# ------------------------------------------------------------------------------------------
def reconcile(refs, sites, traced):
    covered = {c["consumer"] for c in CONSUMERS}
    covered_short = {c.rsplit("::", 1)[-1] for c in covered} | {
        c.split(" ")[0] for c in covered}
    site_fns = {s["function"] for s in sites} - {LOADER}
    uncovered_sites = sorted(f for f in site_fns
                             if f not in covered_short and not f.startswith("test_"))
    uncovered_traced = sorted(k for k, v in traced.items()
                              if v["columns_read"] and k not in covered_short)
    ref_files = sorted({r["file"] for r in refs})
    return dict(
        n_static_references=len(refs), n_static_reference_files=len(ref_files),
        static_reference_files=ref_files,
        n_static_call_sites=len(sites), static_call_sites=sites,
        traced=traced,
        n_attributed_consumers=len(CONSUMERS),
        uncovered_call_site_functions=uncovered_sites,
        uncovered_traced_consumers=uncovered_traced,
        complete=not uncovered_sites and not uncovered_traced)


def misattribution_analysis(traced):
    """Does any consumer make a claim its read columns do not support?

    This is the SURVIVE test, and it has two arms per the candidate's decision rule:
      (a) presenting/relying on the independent half for an assertion carried only by the
          verification half; and
      (b) any other materially incorrect evidence-type attribution.
    """
    findings = []
    for c in CONSUMERS:
        cols = traced.get(c["consumer"], {}).get("columns_read")
        # arm (a): claims independence while reading only verification columns
        if c["independence_load_bearing"] and cols is not None:
            reads_indep = any(x in HALVES["independent_ct_data"]["columns"] for x in cols)
            if not reads_indep:
                findings.append(dict(consumer=c["consumer"], arm="a",
                                     detail="claims an independence-carried assertion but reads "
                                            "no CT column"))
    # arm (b): hand-read. The one wording risk found is recorded on the gate row; the question
    # is whether it PROPAGATES into any consumer's actual attribution.
    downstream = [c for c in CONSUMERS if c["kind"] in
                  ("evidence_record", "generated_report", "public_claim", "registry")]
    propagated = [c["consumer"] for c in downstream if c["independence_load_bearing"]]
    return dict(
        arm_a_findings=findings,
        wording_risk_located_at="gate_foster_ct_trajectory docstring",
        wording_risk_description=(
            "The docstring labels the CT arm '(independent, \"qualitative-good\")', copying the "
            "MANIFEST word without the controlling card's circularity qualifier."),
        downstream_consumers_examined=[c["consumer"] for c in downstream],
        downstream_consumers_asserting_independence=propagated,
        propagates=bool(propagated),
        resolution=(
            "Every downstream consumer independently REFUSES the strong reading: the evidence "
            "record splits the dataset into eval(same_campaign) and fit(fit_input) roles, sets "
            "reality_facing false and support_status context_only, and states in "
            "claim_not_supported that it 'does not establish parameter-free or out-of-sample "
            "prediction'; the generated graph and Fig-2 vector render that unchanged (the "
            "latter with outcome `negative`); the registry carries source_curve_reproduction; "
            "and the only public claim in the neighbourhood EXCLUDES the gate outright. The "
            "wording risk is real and is recorded, but it is contained at the docstring and "
            "reaches no evidentiary surface."))


def screen(run_trace=True):
    refs = static_references()
    sites = static_call_sites()
    traced = trace_columns(default_traced_callables()) if run_trace else {}
    rec = reconcile(refs, sites, traced)
    scan = text_scan()
    structural = structural_independence_fields()
    mis = misattribution_analysis(traced)
    unclassified = [h for h in scan
                    if h["context_classification"]["classification"] == "UNCLASSIFIED"]

    by_cls = {}
    for c in CONSUMERS:
        by_cls.setdefault(c["classification"], []).append(c["consumer"])

    if not rec["complete"]:
        decision = "NEEDS_NEW_DATA"
        why = ("The enumeration found a consumer the attribution table does not cover, so the "
               "evidentiary split cannot be asserted for every active use.")
    elif mis["arm_a_findings"] or mis["propagates"] or structural["asserts_independence"]:
        decision = "SURVIVE"
        why = ("At least one consumer presents or relies on the independent half for an "
               "assertion it does not carry, or otherwise makes a materially incorrect "
               "evidence-type attribution.")
    else:
        decision = "RETIRE"
        why = ("Every real consumer uses the correct evidentiary function, legitimately uses "
               "both, or makes no evidentiary-strength claim. The one wording risk is contained "
               "at a gate docstring and is refused by every downstream consumer.")

    return dict(
        screen=CANDIDATE_ID, dataset=DATASET_ID,
        disposition=["CHEAP_SCIENTIFIC_SCREEN", "NOT_A_PUBLICATION_RESULT",
                     "NOT_A_MODEL_VALIDATION_UPGRADE"],
        controlling_source_card=SOURCE_CARD,
        source_card_note=("docs/cards/foster2025.md is a DIFFERENT card and carries its own "
                          "TEMPLATE_DEVIATION; this screen does not use or inherit it."),
        manifest_validation_strength_verbatim=MANIFEST_VALIDATION_STRENGTH,
        manifest_caveat_verbatim=MANIFEST_CAVEAT,
        controlling_card_circularity_note_verbatim=CARD_CIRCULARITY_NOTE,
        evidence_types_are_not_ordinal=(
            "independent and verification are different evidentiary FUNCTIONS, not two strengths "
            "of one kind. A consumer may legitimately require both. Nothing in this screen ranks "
            "them, and 'uses both' is a correct outcome."),
        halves=HALVES, consumers=CONSUMERS, consumers_by_classification=by_cls,
        enumeration=rec,
        adversarial_text_scan=dict(n_hits=len(scan), hits=scan,
                                   n_unclassified=len(unclassified),
                                   tokens=list(SCAN_TOKENS),
                                   surfaces_scanned=[x[0] for x in SCAN_SURFACES],
                                   coverage_notes=SCAN_COVERAGE_NOTES),
        structural_independence_fields=structural,
        misattribution_analysis=mis,
        decision=decision, decision_reasoning=why)


# ------------------------------------------------------------------------------------------
# Primary figure
# ------------------------------------------------------------------------------------------
_INK, _MUTED, _GRID = "#1a1a1a", "#5a5a5a", "#d9d9d9"
_C_VER, _C_IND, _C_BOTH, _C_NONE = "#0072b2", "#e69f00", "#cc79a7", "#6b6b6b"


def figure(path=None, result=None):
    """Dataset -> evidence half -> consumer -> assertion -> the function actually load-bearing.

    Same shape as the accepted I-040 figure, with one deliberate difference: the two halves are
    drawn side by side as EQUAL FUNCTIONS, not as a ladder, because they are not ordinal.
    """
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import FancyBboxPatch

    plt.rcParams.update({"figure.dpi": 150, "savefig.dpi": 150, "font.size": 8.5,
                         "font.family": "DejaVu Sans"})
    r = result or screen()

    order = [CLS_VERIFICATION, CLS_BOTH, CLS_INDEPENDENT, CLS_NEITHER]
    colour = {CLS_VERIFICATION: _C_VER, CLS_BOTH: _C_BOTH,
              CLS_INDEPENDENT: _C_IND, CLS_NEITHER: _C_NONE}
    label = {CLS_VERIFICATION: "VERIFICATION is load-bearing — does our port reproduce the "
                               "source's own fitted ODE curves?",
             CLS_BOTH: "BOTH are load-bearing, legitimately — a measured datum AND a verified "
                       "implementation",
             CLS_INDEPENDENT: "INDEPENDENT (CT measurement) is load-bearing on its own",
             CLS_NEITHER: "NEITHER — registration, exclusion, or a loader/parse check"}

    rows = []
    for cls in order:
        members = [c for c in CONSUMERS if c["classification"] == cls]
        members.sort(key=lambda c: (c["kind"] != "gate", c["consumer"]))
        rows.append(("HEADER", cls, None))
        rows += [("ROW", cls, c) for c in members]
        if not members:
            rows.append(("EMPTY", cls, None))

    fig, ax = plt.subplots(figsize=(12.6, 0.46 * len(rows) + 5.0))
    ax.set_xlim(0, 100)
    ax.set_ylim(-5.0, len(rows) + 3.6)
    ax.axis("off")
    x_end = 97.0

    ax.text(0, len(rows) + 3.0, "I-045 — which evidentiary FUNCTION each consumer of a mixed "
            "'independent + verification' cell actually leans on",
            fontsize=11.5, weight="bold", color=_INK, va="top")
    ax.text(0, len(rows) + 2.35, "dataset  %s        MANIFEST validation_strength (verbatim): "
            "“%s”" % (DATASET_ID, MANIFEST_VALIDATION_STRENGTH),
            fontsize=8, color=_MUTED, va="top")
    ax.text(0, len(rows) + 1.85,
            "CHEAP_SCIENTIFIC_SCREEN · NOT_A_PUBLICATION_RESULT · "
            "NOT_A_MODEL_VALIDATION_UPGRADE — evidence-lineage bookkeeping; asserts nothing "
            "about physics and changes no label.", fontsize=7.2, color=_MUTED, va="top",
            style="italic")
    ax.text(0, len(rows) + 1.30,
            "These two are NOT ranked. They are different evidentiary functions and a consumer "
            "may legitimately require both — which is why the middle band exists.",
            fontsize=7.6, color=_INK, va="top")

    # the two halves, drawn as equal columns
    hv, hi = HALVES["verification_fitted_curves"], HALVES["independent_ct_data"]
    for i, (h, col) in enumerate(((hv, _C_VER), (hi, _C_IND))):
        x0 = 0.5 + i * 48.5
        ax.add_patch(FancyBboxPatch((x0, len(rows) - 0.30), 47.0, 1.32,
                                    boxstyle="round,pad=0.02,rounding_size=0.12",
                                    fc=col, ec="none", alpha=0.13, zorder=0))
        ax.text(x0 + 1.0, len(rows) + 0.72, "“%s”" % h["manifest_wording"],
                fontsize=8.6, weight="bold", color=_INK)
        ax.text(x0 + 1.0, len(rows) + 0.30, "columns: %s   (%d rows)"
                % (", ".join(h["columns"][:3]) + ("…" if len(h["columns"]) > 3 else ""),
                   h["n_rows"]), fontsize=7.0, color=_MUTED)
        import textwrap as _tw
        for j, ln in enumerate(_tw.wrap(h["function"], 62)[:2]):
            ax.text(x0 + 1.0, len(rows) - 0.05 - 0.34 * j, ln, fontsize=6.8, color=_MUTED)

    x_name, x_reads, x_cls = 3.0, 38.0, 74.0
    ax.plot([0, x_end], [len(rows) - 0.85] * 2, color=_GRID, lw=0.9)

    for i, (kind, cls, c) in enumerate(rows):
        y = len(rows) - 1.9 - i
        col = colour[cls]
        if kind == "HEADER":
            ax.add_patch(FancyBboxPatch((0.4, y - 0.16), x_end - 0.8, 0.56,
                                        boxstyle="round,pad=0.02,rounding_size=0.1",
                                        fc=col, ec="none", alpha=0.13, zorder=0))
            ax.plot([0.4, 0.95], [y + 0.12] * 2, color=col, lw=5, solid_capstyle="butt")
            ax.text(1.7, y + 0.02, label[cls], fontsize=8.2, weight="bold", color=_INK)
            continue
        if kind == "EMPTY":
            ax.text(x_name, y, "(none — no consumer relies on this function alone)",
                    fontsize=7.4, color=_MUTED, style="italic")
            ax.plot([0, x_end], [y - 0.34] * 2, color=_GRID, lw=0.5, zorder=0)
            continue
        ax.plot([1.2, 1.9], [y + 0.06] * 2, color=col, lw=4, solid_capstyle="butt")
        name = c["consumer"]
        if name.startswith("EVIDENCE_LINKS"):
            name = "EVIDENCE_LINKS …::gate_foster_ct_trajectory"
        elif len(name) > 40:
            name = name[:38] + "…"
        ax.text(x_name, y, name, fontsize=7.6, color=_INK,
                weight="bold" if c["kind"] in ("gate", "evidence_record") else "normal")
        reads = ", ".join(c["source_row_and_columns_read"].split(",")[:2])
        ax.text(x_reads, y, reads[:44] + ("…" if len(reads) > 44 else ""),
                fontsize=6.6, color=_MUTED)
        flags = []
        if c["independence_load_bearing"]:
            flags.append("indep")
        if c["verification_reproduction_load_bearing"]:
            flags.append("verif")
        if c["neither_load_bearing"]:
            flags.append("neither")
        mark = " ⚑ wording risk" if c["misleading_wording"] else ""
        ax.text(x_cls, y, "%s%s" % (" + ".join(flags) or "—", mark), fontsize=7.4,
                color="#d55e00" if mark else _INK)
        ax.plot([0, x_end], [y - 0.34] * 2, color=_GRID, lw=0.5, zorder=0)

    mis = r["misattribution_analysis"]
    e = r["enumeration"]
    foot = (
        "Enumeration  %d static references across %d files · %d loader call sites · "
        "column-level access tracing of the consuming gate · union reconciled, coverage "
        "complete=%s.\n"
        "The halves are DIFFERENT COLUMNS of one file, so attribution is observed, not "
        "inferred: the gate reads s_fit/H_fit on all 461 rows AND s_data/H_data + errors on the "
        "8 CT rows.\n"
        "Adversarial scan  %d token hits over %d consuming surfaces, each read in context; "
        "%d unclassified.\n"
        "Wording risk  the gate docstring calls the CT arm “independent” without the card's "
        "circularity qualifier. It does NOT propagate: the evidence record files the same "
        "dataset twice —\n"
        "    eval/same_campaign AND fit/fit_input — sets reality_facing false and "
        "support_status context_only, and states it “does not establish parameter-free or "
        "out-of-sample prediction”.\n"
        "DECISION  %s — %s"
        % (e["n_static_references"], e["n_static_reference_files"], e["n_static_call_sites"],
           e["complete"], r["adversarial_text_scan"]["n_hits"], len(SCAN_SURFACES),
           r["adversarial_text_scan"]["n_unclassified"], r["decision"],
           r["decision_reasoning"]))
    ax.text(0, -1.5, foot, fontsize=7.0, color=_MUTED, va="top", linespacing=1.6)

    fig.tight_layout()
    path = path or (REPO_ROOT / "docs/insights/screens/I-045/figures/primary.png")
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return path


def main(argv=None):
    r = screen()
    out = REPO_ROOT / "docs/insights/screens/I-045/result.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(r, indent=2) + "\n", encoding="utf-8")
    e = r["enumeration"]
    print("static references   %d over %d files" % (e["n_static_references"],
                                                    e["n_static_reference_files"]))
    print("loader call sites   %d" % e["n_static_call_sites"])
    for k, v in e["traced"].items():
        print("traced %-28s halves=%s" % (k, v["halves_touched"]))
        print("    columns: %s" % ", ".join(v["columns_read"]))
    print("consumers attributed %d  complete=%s" % (e["n_attributed_consumers"], e["complete"]))
    for cls, names in r["consumers_by_classification"].items():
        print("  %-26s %s" % (cls, ", ".join(names)))
    s = r["adversarial_text_scan"]
    print("text scan: %d hits, %d unclassified" % (s["n_hits"], s["n_unclassified"]))
    m = r["misattribution_analysis"]
    print("arm-a findings: %s" % (m["arm_a_findings"] or "none"))
    print("wording risk propagates: %s" % m["propagates"])
    print("DECISION: %s" % r["decision"])
    fig_path = figure(result=r)
    print("wrote %s" % out.relative_to(REPO_ROOT))
    print("wrote %s" % fig_path.relative_to(REPO_ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
