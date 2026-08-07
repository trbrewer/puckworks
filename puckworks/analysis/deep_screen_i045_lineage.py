"""I-045 DEEP SCREEN (Insight Foundry IF-7) — evidence-lineage adjudication.

Protocol: ``docs/insights/screens/I-045/DEEP_SCREEN_PROTOCOL.md``, frozen and committed BEFORE
this module existed. Everything this module does is a step the protocol names.

WHAT THIS IS
    A repository-bound audit of one claim: that the MANIFEST cell
    ``independent (CT data) / verification (fitted curves)`` and the ``gate_foster_ct_trajectory``
    docstring attach an INCORRECT evidence type to the CT arm of
    ``foster2025_2/fig12_14_curves``.

    The cheap screen established that from the CONTROLLING CARD. This deep screen goes to the
    PAPER, then measures how far the attribution reaches, then asks whether the defect is
    peculiar to this row or general across the corpus's mixed-strength cells.

WHAT THIS IS NOT
    * No model is executed. Protocol stop condition S5: the lineage question is answered from
      text, and no bounded source-lineage reproduction is authorized. A test asserts it.
    * No evidence label, gate, manifest cell, card, registry entry, public claim or generated
      artifact is edited. The screen says what a LATER human-owned correction should say.
    * No Foundry lens, generator, schema or scoring is added, and no generalized
      evidence-provenance framework is implemented.
    * External novelty findings live in ``NOVELTY_REVIEW.md`` and are deliberately NOT
      fabricated into this deterministic output (stop condition S6).

STRUCTURE
    1. glossary        — ROADMAP S0, verified verbatim at run time (reuses the cheap screen's
                         contract; drift raises rather than silently applying a stale definition)
    2. source_lineage  — L1-L7 answered from the paper, hand-transcribed with locations. Marked
                         `verifiable_in_repo: false` because the paper is not vendored.
    3. blast_radius    — an over-approximating scan for the attribution across the repository,
                         the latest tag and the released tag, then HAND attribution of every hit
                         to one of six exposure classes.
    4. generality      — the protocol's frozen parenthesis-aware mixed-strength rule over
                         MANIFEST.csv, then G1-G5 per PRIMARY-SET row.
    5. alternatives    — A1-A5 challenges, each with the evidence that settles it.
    6. formulations    — F1-F4 correction wordings, assessed, not implemented.
    7. decision        — one of the protocol's six output classes, derived from the above.
"""
import csv
import json
import pathlib
import re
import subprocess

from puckworks.analysis.screen_i045_evidence_halves import (
    EXPECTED_GLOSSARY_DEFINITIONS, GLOSSARY_ANCHOR, GlossaryDrift, verify_glossary,
)

#: re-exported so a test can assert the deep screen fails on the same authority drift
GLOSSARY_DRIFT_ERROR = GlossaryDrift

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
BUNDLE = REPO_ROOT / "docs/insights/screens/I-045"
DATASET_ID = "foster2025_2/fig12_14_curves"
CHEAP_SCREEN_DISPOSITION = "SURVIVE"          # frozen history; this screen may not rewrite it

PROTOCOL = "docs/insights/screens/I-045/DEEP_SCREEN_PROTOCOL.md"

# --------------------------------------------------------------------------------------------
# 1. THE GOVERNING VOCABULARY
# --------------------------------------------------------------------------------------------
def glossary():
    """ROADMAP S0, verified verbatim at run time. Raises GlossaryDrift if the authority moved."""
    text = (REPO_ROOT / "docs/ROADMAP.md").read_text(encoding="utf-8")
    block = verify_glossary(text)
    return dict(source="docs/ROADMAP.md S0", anchor=GLOSSARY_ANCHOR,
                method="VERBATIM_RUNTIME_VERIFICATION",
                definitions=EXPECTED_GLOSSARY_DEFINITIONS,
                all_expected_definitions_verified=True,
                block=block,
                independent_is_about_the_fit_not_the_modality=True)


# --------------------------------------------------------------------------------------------
# 2. PRIMARY-SOURCE LINEAGE  (protocol S4, questions L1-L7)
# --------------------------------------------------------------------------------------------
#: How the paper was obtained. Recorded because the protocol forbids elevating the card into
#: primary-source confirmation, so a reader must be able to check the access route.
SOURCE_ACCESS = dict(
    citation=("J. Foster, W. Lee, K. Moroney, D. Prjamkov, M. Salamon, A. Smith, "
              "J. Petrassem-de-Sousa, M. Vynnycky, 'Dynamics of liquid infiltration into an "
              "espresso bed using time-resolved micro-computed tomography: Insights from "
              "experiment and modeling,' Phys. Fluids 37, 013383 (2025)."),
    doi="10.1063/5.0245167",
    open_access="hybrid, CC BY-NC (publisher version)",
    obtained_from=("University of Limerick institutional repository (DSpace bitstream), "
                   "located via the Unpaywall OA-location index"),
    publisher_pdf_blocked=True,
    publisher_block_detail=("pubs.aip.org returns HTTP 403 to automated fetches, and the "
                            "University of Portsmouth research-portal file endpoint is behind a "
                            "Cloudflare interstitial; the UL repository copy is the same "
                            "published version"),
    version_read="final published version, 22 pages",
    supplementary_material_found=False,
    supplementary_note=("The article declares no supplementary material and the card records "
                        "'No code or data repository published'; raw CT data is 'available from "
                        "the corresponding author on reasonable request'."),
    vendored_into_repository=False,
    quotes_are_hand_transcribed=True,
)

#: Verbatim from the paper. Short quotations for identification and criticism; each carries its
#: location so a reader can check it rather than trust this transcription.
SOURCE_QUOTES = [
    dict(id="Q1", location="Sec. III D 'Numerical solution and model fitting'",
         quote=("Estimates for the majority of the model parameters are available from the "
                "literature (see Table I). The exceptions are K and phi_T, and so these will be "
                "tuned to achieve a best fit to the experimental data."),
         bears_on=["L1"]),
    dict(id="Q2", location="Sec. III D, Eq. (39)",
         quote=("Systematic fitting was carried out by minimizing the objective function "
                "L = sum_i^N [ (s_i - s(t_i - t_shift))^2 + (H_i - H(t_i - t_shift))^2 ], "
                "where s_i and H_i are the experimentally determined positions of the wetting "
                "front and height of water in the headspace, respectively, ... t_i are the times "
                "from the experiment start time at which the values of s(t) and H(t) were "
                "measured, and N is the number of experimental measurement times."),
         bears_on=["L1", "L2", "L3", "L5"]),
    dict(id="Q3", location="Sec. III D",
         quote=("Note that the model output is shifted to start at some time, t_shift, after the "
                "experimental start time that should be determined as part of the fitting."),
         bears_on=["L1"]),
    dict(id="Q4", location="Sec. III D",
         quote=("The fmincon function in MATLAB using the default 'interior-point' algorithm was "
                "employed. ... We allowed fmincon to vary phi_T, K, and t_shift within the "
                "respective bounds [0.3, 0.9], [0, 0.2], [0, 1]."),
         bears_on=["L1"]),
    dict(id="Q5", location="Sec. III D",
         quote=("We verified that the results reported in Sec. IV were robust to variations in "
                "the initial guesses for the parameters using MATLAB's Multistart function to "
                "sample a large number of initial guesses, giving confidence that the solution "
                "reported is not simply a local minimum."),
         bears_on=["L7"]),
    dict(id="Q6", location="Sec. IV A 'Model comparison with experimental data'",
         quote=("For the purposes of model fitting, we compare the model outputs: (i) the front "
                "locations at the center of the portafilter (x = 265 pixels and y = 370 pixels) "
                "and (ii) the mean front location averaged across the five positions. The fitting "
                "algorithm follows that described in Sec. III D using the mean locations for "
                "s(t) and H(t) as the data to fit."),
         bears_on=["L1", "L4"]),
    dict(id="Q7", location="Figs. 12, 13, 14 captions",
         quote=("Best fit of s, position of wetting front. The mean front locations are indicated "
                "by squares, with the associated standard deviations indicated by the vertical "
                "lines centered on the squares. The crosses indicate the location of the front at "
                "the center of the portafilter."),
         bears_on=["L4", "L5", "L6"]),
    dict(id="Q8", location="Sec. IV (results narrative), Figs. 12-14",
         quote=("The results of the model fitting are shown in Figs. 12-14. ... The model appears "
                "to capture the general shape of the s profile well, while the profile for H in "
                "the headspace appears to have the correct shape but increases slightly more "
                "quickly compared to the experiments."),
         bears_on=["L6", "L7"]),
    dict(id="Q9", location="Sec. V Conclusions",
         quote=("The model shows a good fit to experimental data. By demonstrating the "
                "feasibility of combining time-resolved x-ray tomographic measurements with "
                "modeling, we have pioneered a new technique for experimentally validating "
                "coffee models, opening up several interesting avenues of future research."),
         bears_on=["L7"]),
    dict(id="Q10", location="Sec. V Conclusions (future work)",
         quote=("Finally, a significant increase in the accuracy of models could be possible by "
                "combining x-ray tomographic data with measurements of the mass concentration of "
                "coffee exiting the coffee bed, producing a richer dataset for model validation."),
         bears_on=["L7"]),
    dict(id="Q11", location="Sec. IV (fine vs coarse grind)",
         quote=("For this reason, we will only apply the front extraction algorithm in Sec. II C "
                "and the corresponding infiltration model to the fine grind data. More "
                "sophisticated modeling of infiltration into the coarse grind is outside the "
                "scope of this work."),
         bears_on=["L4"]),
    dict(id="Q12", location="Fig. 7 caption / Figs. 8-9 captions",
         quote=("Scaled absorption at different radii within the bed. ... Lines show fits to "
                "Eq. (1) from which interface positions can be extracted. ... These results are "
                "consistent with a well-defined, uniform wetting front."),
         bears_on=["L6"]),
]

#: L1-L7, answered from the quotes above.
LINEAGE = {
    "L1_what_entered_the_objective": dict(
        answer=("The CT-derived MEAN front locations — s_i and H_i averaged across five vertical "
                "positions through the portafilter — at every experimental measurement time."),
        fitted_parameters=["K (i.e. permeability k)", "phi_T", "t_shift"],
        objective="Eq. (39), unweighted sum of squared residuals in s and H",
        optimizer="MATLAB fmincon, interior-point, bounds phi_T [0.3,0.9], K [0,0.2], t_shift [0,1]",
        local_minimum_check="MATLAB MultiStart",
        evidence=["Q1", "Q2", "Q3", "Q4", "Q6"],
        settled=True),
    "L2_s_and_H_fitted_simultaneously": dict(
        answer="YES — one objective, summing the s and H squared residuals term by term.",
        evidence=["Q2"], settled=True),
    "L3_all_plotted_CT_times_entered_the_fit": dict(
        answer=("YES. The objective runs over i = 1..N where 'N is the number of experimental "
                "measurement times'. No subsetting, thinning, burn-in or time window is stated, "
                "and the repository artifact carries CT values at exactly the plotted times."),
        n_ct_rows_in_repository_artifact=8,
        evidence=["Q2"], settled=True),
    "L4_any_held_out_data": dict(
        answer="NO. No observation, time point, trajectory, shell or derived quantity is held out.",
        candidates_checked=[
            dict(candidate="centre-line front locations (crosses in Figs 12-14)",
                 held_out=False,
                 why=("Not independent and not held out: the centre line is ONE of the five "
                      "vertical positions averaged into the fit data. It is a sub-reduction of "
                      "the same measurements, plotted for context. The paper introduces it as "
                      "'For the purposes of model fitting, we compare the model outputs: (i) ... "
                      "and (ii) ...' and then fits (ii). It is never called validation.")),
            dict(candidate="whole-bed-average interface series (Fig. 6 right panel)",
                 held_out=False,
                 why=("A different REDUCTION of the same CT scans from the same single fine-grind "
                      "run, presented as data analysis with no model curve on it. Not used in "
                      "the objective, but also not offered as evidence about the model — and it "
                      "is NOT what the audited dataset contains (the MANIFEST caveat says "
                      "'Fig8 -H differs from Fig14 H (do not mix)').")),
            dict(candidate="radial-shell analysis (Figs. 7-9)",
                 held_out=False,
                 why=("Supports the 1-D sharp-front ASSUMPTION of the model. It is an assumption "
                      "check on the experiment, carries no model output, and cannot be "
                      "held-out evidence for parameters it never constrains.")),
            dict(candidate="normalized pressure / flow-rate curves (Fig. 15)",
                 held_out=False,
                 why=("Pure MODEL output with no data overlay — verification material, not "
                      "held-out measurement. It is a separate manifest row already labelled "
                      "'verification (model curve)'.")),
            dict(candidate="sensitivity study (Appendix B)",
                 held_out=False,
                 why="Model-vs-model parameter sweeps. Verification under S0, not data."),
            dict(candidate="coarse-grind run",
                 held_out=False,
                 why=("EXCLUDED FROM MODELLING ALTOGETHER, not reserved as evidence: 'we will "
                      "only apply the front extraction algorithm ... and the corresponding "
                      "infiltration model to the fine grind data.' A dataset the authors decline "
                      "to model is not a held-out test of the model.")),
            dict(candidate="reported t_p = 0.823 s and t_s = 6.669 s",
                 held_out=False,
                 why=("Model outputs of the fitted solution (they include the fitted t_shift), "
                      "not measurements. The repository already labels the params row "
                      "'verification (post-fit params)'.")),
        ],
        evidence=["Q6", "Q7", "Q11", "Q12"], settled=True),
    "L5_error_bars_role": dict(
        answer=("VISUALIZATION ONLY. The bars are 'the associated standard deviations' across the "
                "five positions. Eq. (39) contains no weights, no sigma and no covariance — it "
                "is an unweighted least-squares objective, so the uncertainties entered neither "
                "the fit nor any weighting."),
        entered_fit=False, entered_weighting=False,
        evidence=["Q2", "Q7"], settled=True),
    "L6_figure_and_column_roles": dict(
        answer="see mapping",
        mapping=[
            dict(item="Figs. 12-14 squares (5-line mean s, w, H)", role="FIT INPUT",
                 repository_columns=["s_data_mm", "H_data_mm", "w_data_mm"]),
            dict(item="Figs. 12-14 error bars", role="UNCERTAINTY DISPLAY (not in the objective)",
                 repository_columns=["s_data_err_mm", "H_data_err_mm", "w_data_err_mm"]),
            dict(item="Figs. 12-14 curves", role="FITTED-MODEL OUTPUT",
                 repository_columns=["s_fit_mm", "w_fit_mm", "H_fit_mm"]),
            dict(item="Figs. 12-14 crosses (centre line)",
                 role="SUB-REDUCTION OF THE FIT DATA, shown for context",
                 repository_columns=[]),
            dict(item="w = H + phi_T s", role="DERIVED QUANTITY (uses the fitted phi_T)",
                 repository_columns=["w_fit_mm", "w_data_mm"]),
            dict(item="Fig. 6", role="EXPERIMENTAL DATA ANALYSIS (no model)",
                 repository_columns=[]),
            dict(item="Figs. 7-9", role="ASSUMPTION CHECK on 1-D sharp front",
                 repository_columns=[]),
            dict(item="Fig. 15", role="MODEL OUTPUT (verification)", repository_columns=[]),
            dict(item="Appendix B", role="MODEL SENSITIVITY (verification)",
                 repository_columns=[]),
            dict(item="k = 2.97e-15 m^2 vs literature; phi_T = 0.322 vs 0.4-0.6",
                 role="PLAUSIBILITY CHECK on fitted values", repository_columns=[]),
            dict(item="t_s (time base)", role="SHARED INDEX", repository_columns=["t_s"]),
        ],
        no_item_classified_independent=True, settled=True),
    "L7_authors_own_terms": dict(
        answer=("The authors call the model a good fit and describe the combined "
                "tomography-and-modeling approach as experimentally validating coffee models. "
                "They do NOT call the fitted observations independent or held out. Under "
                "ROADMAP S0 the audited CT observations remain post-fit, same-campaign evidence."),
        #: PRESENT-work language. The conclusions do use validation language about what this
        #: paper did — an earlier version of this screen wrongly reported that every use of
        #: 'validation' referred to future work, and that over-claim is corrected here.
        source_uses_validation_language_for_present_work=True,
        present_work_validation_language=(
            "Conclusions: 'The model shows a good fit to experimental data. By demonstrating the "
            "feasibility of combining time-resolved x-ray tomographic measurements with modeling, "
            "we have pioneered a new technique for experimentally validating coffee models.' The "
            "second clause is present tense and is about THIS work — it describes the METHOD as a "
            "way of experimentally validating coffee models."),
        future_work_validation_language=(
            "Separately, and later in the same section: combining tomographic data 'with "
            "measurements of the mass concentration of coffee exiting the coffee bed' would "
            "produce 'a richer dataset for model validation'. That is a proposal for measurements "
            "they did not make."),
        fit_quality_language=("'best fit' (Figs. 12-14 captions), 'a good fit to experimental "
                              "data' and 'Good agreement' (abstract, conclusions)."),
        independent_word_usage=("'independent' occurs three times and NEVER about evidence: a "
                                "symbols-table heading ('independent and dependent variables'), "
                                "an ODE remark ('independent of time'), and a parameter-"
                                "insensitivity remark ('essentially independent of P_m')."),
        #: The three that actually matter for the audit.
        source_calls_the_audited_data_independent=False,
        source_identifies_a_held_out_subset=False,
        source_claims_independent_validation=False,
        why_the_broad_usage_does_not_help=(
            "The source's broad, colloquial use of 'validating' is a claim about the TECHNIQUE, "
            "not about the evidentiary status of particular observations. ROADMAP S0 fixes "
            "independence by whether data were used in fitting, and Eq. (39) plus Sec. IV A "
            "establish that these were. An author calling their own comparison 'validation' "
            "cannot make fitted data held out."),
        source_supports_independent_label=False,
        evidence=["Q7", "Q8", "Q9", "Q10"], settled=True),
}

#: Does the controlling card survive comparison with the paper? Protocol stop condition S2.
CARD_CHECK = dict(
    card="docs/cards/foster2025_2.md",
    card_claim=("Three parameters (K i.e. k, phi_T, t_shift) fitted by fmincon least squares on "
                "s and H simultaneously; Multistart used to check against local minima."),
    paper_confirms=True,
    circularity_note_confirmed=True,
    #: quoted byte-identically from the card, so the test can prove it is really there
    circularity_note=("Note the circularity: k and \u03c6_T are fitted to the same s/H curves "
                      "being reproduced, so the source validates model FORM, not parameter-free "
                      "prediction."),
    contradiction_found=False,
    stop_condition_S2_triggered=False,
    minor_imprecision=("The card's 'Extractable data' section calls Figs 6/8 'the key validation "
                       "series'. The paper presents Fig. 6 as data analysis, not as validation of "
                       "the model, and the model is compared against Figs 12-14. This is card "
                       "prose about a DIFFERENT figure pair than the audited row and is recorded, "
                       "not corrected."),
)


def source_lineage():
    """L1-L7 with their evidence. Hand-transcribed: the paper is not vendored."""
    return dict(access=SOURCE_ACCESS, quotes=SOURCE_QUOTES, lineage=LINEAGE,
                card_check=CARD_CHECK,
                verifiable_in_repository=False,
                determination=("The CT observations in the audited dataset ARE the data the "
                               "tested parameters were fitted to. Nothing was held out."),
                ct_arm_evidence_type_under_S0="post-fit reconstruction (same campaign, not held out)",
                manifest_wording_for_that_arm="independent (CT data)",
                manifest_wording_correct=False)


# --------------------------------------------------------------------------------------------
# 3. BLAST RADIUS  (protocol S5)
# --------------------------------------------------------------------------------------------
MANIFEST_CELL = "independent (CT data) / verification (fitted curves)"
GATE_DOCSTRING_FRAGMENT = "(independent, 'qualitative-good')"

#: Deliberately excluded from the corpus scan: this deep screen's own artifacts. A screen may not
#: count its own output as corpus exposure, and excluding them keeps the scan stable while it is
#: being written. Declared here so the exclusion is auditable rather than silent.
SELF_EXCLUDED = (
    "docs/insights/screens/I-045/DEEP_SCREEN_PROTOCOL.md",
    "docs/insights/screens/I-045/deep_decision.md",
    "docs/insights/screens/I-045/deep_result.json",
    "docs/insights/screens/I-045/NOVELTY_REVIEW.md",
    "puckworks/analysis/deep_screen_i045_lineage.py",
    "tests/test_deep_screen_i045.py",
)

EXPOSURE_CLASSES = (
    "PRESENT_BUT_EXPLICITLY_REJECTED",
    "CURRENT_INTERNAL_MISWORDING",
    "CURRENT_READER_FACING_OVERCLAIM",
    "GENERATED_BUT_CORRECTLY_BOUNDED",
    "HISTORICAL_SUPERSEDED",
    "NO_EXPOSURE",
)

SCAN_NEEDLES = ("independent (CT data)", GATE_DOCSTRING_FRAGMENT)


def _tracked_files():
    out = subprocess.run(["git", "ls-files"], cwd=REPO_ROOT, capture_output=True, text=True)
    return sorted(p for p in out.stdout.split("\n") if p)


def scan_working_tree():
    """Over-approximating scan: every tracked file carrying either needle."""
    hits = []
    for rel in _tracked_files():
        if rel in SELF_EXCLUDED:
            continue
        p = REPO_ROOT / rel
        try:
            text = p.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError, IsADirectoryError):
            continue
        found = {n: text.count(n) for n in SCAN_NEEDLES if n in text}
        if found:
            hits.append(dict(path=rel, occurrences=found))
    return hits


#: Released/archived content, RECORDED rather than scanned at run time.
#:
#: A tag scan cannot live in the deterministic output: CI checks out at depth 1 with no tags, so
#: `git show v0.3.0:...` returns nothing there and the result would differ between a developer
#: machine and CI. That would make the canonical drift test environment-dependent — it would fail
#: in CI for a reason that has nothing to do with the audit. So the finding is declared here, and
#: `verify_released_content()` checks it against the real tags wherever they are available.
RELEASED_CONTENT = [
    dict(ref="v0.3.0", carries_attribution=True,
         files={"puckworks/data/MANIFEST.csv": 1, "puckworks/validation/gates.py": 1}),
    dict(ref="archive/lab-tour-educational-pre-recovery-2026-07-20", carries_attribution=True,
         files={"puckworks/data/MANIFEST.csv": 1, "puckworks/validation/gates.py": 1}),
]


def tags_available():
    return all(subprocess.run(["git", "cat-file", "-e", r["ref"] + "^{commit}"],
                              cwd=REPO_ROOT, capture_output=True).returncode == 0
               for r in RELEASED_CONTENT)


def verify_released_content():
    """Check the declared tag counts against the real tags. Returns None if tags are absent.

    Never called from `deep_screen()` — the deterministic output must not vary with what a
    checkout happens to have fetched. A test calls this where the tags exist.
    """
    if not tags_available():
        return None
    out = []
    for rec in RELEASED_CONTENT:
        actual = {}
        for path, needle in (("puckworks/data/MANIFEST.csv", "independent (CT data)"),
                             ("puckworks/validation/gates.py", GATE_DOCSTRING_FRAGMENT)):
            r = subprocess.run(["git", "show", "%s:%s" % (rec["ref"], path)],
                               cwd=REPO_ROOT, capture_output=True, text=True)
            actual[path] = (r.stdout.count(needle) if r.returncode == 0 else 0)
        out.append(dict(ref=rec["ref"], declared=rec["files"], actual=actual,
                        matches=actual == rec["files"]))
    return out


#: Hand attribution of every scanned surface. `kind` and `reader_can_take_the_independent_reading`
#: are read judgements about the surface, not string matches.
ATTRIBUTION = {
    "puckworks/data/MANIFEST.csv": dict(
        surface="MANIFEST validation_strength cell (the origin)",
        kind="current authority",
        value=MANIFEST_CELL,
        exposure="CURRENT_INTERNAL_MISWORDING",
        reader_can_take_the_independent_reading=True,
        reader_note=("A reader of the manifest can take it, but the manifest is a developer-facing "
                     "provenance table, not a published claim surface."),
        downstream_containment=False,
        correction_required=True),
    "puckworks/validation/gates.py": dict(
        surface="gate_foster_ct_trajectory docstring",
        kind="current authority",
        value=("...bracket a majority of the CT data points within their error bars "
               "(independent, 'qualitative-good')"),
        exposure="CURRENT_INTERNAL_MISWORDING",
        reader_can_take_the_independent_reading=True,
        reader_note=("Visible in API docs and gate output listings; still developer-facing. The "
                     "gate's NUMBERS are unaffected."),
        downstream_containment=False,
        correction_required=True),
    "puckworks/paper3/EVIDENCE_LINKS.json": dict(
        surface="Paper 3 evidence adjudication",
        kind="current authority",
        value=("the same dataset filed TWICE: eval/same_campaign AND fit/fit_input; "
               "relationship=same_campaign_not_held_out; reality_facing=false; "
               "support_status=context_only"),
        exposure="PRESENT_BUT_EXPLICITLY_REJECTED",
        reader_can_take_the_independent_reading=False,
        reader_note="It records the correct lineage in machine-readable fields.",
        downstream_containment=True,
        correction_required=False),
    "puckworks/public/claims.py": dict(
        surface="PV-02 evidence selection",
        kind="current authority",
        value="EXCLUDES gate_foster_ct_trajectory 'on its own merits ... a different observable'",
        exposure="NO_EXPOSURE",
        reader_can_take_the_independent_reading=False,
        reader_note="The gate never reaches a public claim.",
        downstream_containment=True,
        correction_required=False),
    "docs/public/generated/claims.json": dict(
        surface="generated PUBLIC claims artifact",
        kind="generated derivative / public output",
        value=("fit_evaluation=same_campaign_not_held_out; reality_facing=false; "
               "outcome=negative; and PV-02's explicit exclusion rationale"),
        exposure="GENERATED_BUT_CORRECTLY_BOUNDED",
        reader_can_take_the_independent_reading=False,
        reader_note=("Contains NEITHER needle. This is the closest thing to a reader-facing "
                     "surface that touches the gate, and it carries the correct adjudication."),
        downstream_containment=True,
        correction_required=False),
    "docs/paper3_resource/generated/evidence_graph.json": dict(
        surface="generated Paper 3 evidence graph",
        kind="generated derivative",
        value="renders the EVIDENCE_LINKS adjudication",
        exposure="GENERATED_BUT_CORRECTLY_BOUNDED",
        reader_can_take_the_independent_reading=False,
        reader_note="", downstream_containment=True, correction_required=False),
    "docs/figures/paper3/source_data/fig2_evidence_vectors.csv": dict(
        surface="Paper 3 Fig-2 evidence vector",
        kind="generated derivative",
        value="relation=source_curve_reproduction, outcome=negative",
        exposure="GENERATED_BUT_CORRECTLY_BOUNDED",
        reader_can_take_the_independent_reading=False,
        reader_note="", downstream_containment=True, correction_required=False),
    "puckworks/models/__init__.py": dict(
        surface="registry entry foster2025.machine_mode",
        kind="current authority",
        value="component evidence strength: source_curve_reproduction",
        exposure="NO_EXPOSURE",
        reader_can_take_the_independent_reading=False,
        reader_note="The registry never claims independence for this component.",
        downstream_containment=True, correction_required=False),
    "docs/insights/generated/evidence_lineage_index.csv": dict(
        surface="Insight Foundry lineage index (generated)",
        kind="generated derivative",
        value=MANIFEST_CELL,
        exposure="GENERATED_BUT_CORRECTLY_BOUNDED",
        reader_can_take_the_independent_reading=True,
        reader_note=("It copies the cell BYTE-IDENTICALLY by design, so it inherits the defect "
                     "verbatim. That is the Foundry's rule (never restate a label), so the fix "
                     "belongs upstream at the manifest — regenerating propagates it."),
        downstream_containment=False, correction_required=False,
        inherits_from="puckworks/data/MANIFEST.csv"),
    "docs/insights/generated/corpus_map.json": dict(
        surface="Insight Foundry corpus map (generated)",
        kind="generated derivative", value=MANIFEST_CELL,
        exposure="GENERATED_BUT_CORRECTLY_BOUNDED",
        reader_can_take_the_independent_reading=True,
        reader_note="Same byte-identical copy rule as the lineage index.",
        downstream_containment=False, correction_required=False,
        inherits_from="puckworks/data/MANIFEST.csv"),
    "docs/insights/generated/tension_atlas.csv": dict(
        surface="Insight Foundry tension atlas row T-0063",
        kind="generated derivative",
        value=("lineage_circularity / mixed_strength_cell — 'MANIFEST validation_strength for "
               "foster2025_2/fig12_14_curves names more than one strength'"),
        exposure="PRESENT_BUT_EXPLICITLY_REJECTED",
        reader_can_take_the_independent_reading=False,
        reader_note=("The atlas already FLAGS this cell as a tension and routes it to I-045. The "
                     "corpus's own machinery found the row before a human did."),
        downstream_containment=True, correction_required=False),
    "docs/insights/generated/tension_atlas.md": dict(
        surface="tension atlas, rendered",
        kind="generated derivative", value="T-0063 as above",
        exposure="PRESENT_BUT_EXPLICITLY_REJECTED",
        reader_can_take_the_independent_reading=False,
        reader_note="", downstream_containment=True, correction_required=False),
    "docs/ROADMAP.md": dict(
        surface="ROADMAP S7.1 changelog",
        kind="current authority (narrative)",
        value=("the 2026-08-05 correction entry, which states the attribution is INCORRECT and "
               "names the correction targets"),
        exposure="PRESENT_BUT_EXPLICITLY_REJECTED",
        reader_can_take_the_independent_reading=False,
        reader_note="The only quoting of the cell is to say it is wrong.",
        downstream_containment=True, correction_required=False),
    "puckworks/analysis/screen_i045_evidence_halves.py": dict(
        surface="the cheap screen's producer",
        kind="test/analysis text",
        value="quotes the cell as the audit target and classifies it as incorrect",
        exposure="PRESENT_BUT_EXPLICITLY_REJECTED",
        reader_can_take_the_independent_reading=False,
        reader_note="", downstream_containment=True, correction_required=False),
    "tests/test_screen_i045.py": dict(
        surface="cheap-screen regression tests",
        kind="test text", value="asserts the cell is the target incorrect label",
        exposure="PRESENT_BUT_EXPLICITLY_REJECTED",
        reader_can_take_the_independent_reading=False,
        reader_note="", downstream_containment=True, correction_required=False),
    "docs/insights/screens/I-045/result.json": dict(
        surface="cheap-screen result", kind="screen output",
        value="records the cell and its INCORRECT_INDEPENDENT_ATTRIBUTION classification",
        exposure="PRESENT_BUT_EXPLICITLY_REJECTED",
        reader_can_take_the_independent_reading=False,
        reader_note="", downstream_containment=True, correction_required=False),
    "docs/insights/screens/I-045/decision.md": dict(
        surface="cheap-screen decision", kind="screen output",
        value="states the misattribution and names three correction targets",
        exposure="PRESENT_BUT_EXPLICITLY_REJECTED",
        reader_can_take_the_independent_reading=False,
        reader_note="", downstream_containment=True, correction_required=False),
    "docs/insights/screens/I-045/README.md": dict(
        surface="cheap-screen README", kind="screen output",
        value="same", exposure="PRESENT_BUT_EXPLICITLY_REJECTED",
        reader_can_take_the_independent_reading=False,
        reader_note="", downstream_containment=True, correction_required=False),
    "docs/insights/candidates/I-045_which_strength_is_load_bearing_where_the_manifes.md": dict(
        surface="I-045 candidate card, hand-written block", kind="screen output",
        value="records the corrected outcome", exposure="PRESENT_BUT_EXPLICITLY_REJECTED",
        reader_can_take_the_independent_reading=False,
        reader_note="", downstream_containment=True, correction_required=False),
}

#: Surfaces inspected and found to carry NO occurrence. Recorded so a null is visible.
INSPECTED_CLEAN = [
    dict(surface="docs/public/site/** (the GitHub Pages publish root, per .github/workflows/"
                 "pages.yml `path: docs/public/site`)",
         finding="no occurrence of either needle in any published page"),
    dict(surface="notebooks/ (including espresso_lb_colab.ipynb)",
         finding="no occurrence; the gate is not referenced in notebook prose"),
    dict(surface="README.md and top-level documentation",
         finding="no occurrence"),
    dict(surface="puckworks/data/foster2025_2/PROVENANCE.md and README_digitization.md",
         finding=("no independence claim; PROVENANCE describes the CT arm as '(5-line mean)' and "
                  "records the 4-5/8 bracketing as 'qualitative-good, matching the paper's own "
                  "claim' — consistent with post-fit")),
]


def blast_radius():
    scanned = scan_working_tree()
    rows = []
    for h in scanned:
        a = ATTRIBUTION.get(h["path"])
        rows.append(dict(path=h["path"], occurrences=h["occurrences"],
                         scanned_by_needle=True, attributed=a is not None, **(a or {})))
    # Surfaces that carry NEITHER needle but DO consume the dataset or the gate. The needle scan
    # structurally cannot see them — the same lesson the cheap screen learned about
    # EVIDENCE_LINKS.json — so they are inspected by path and reported alongside.
    for path, a in ATTRIBUTION.items():
        if not any(r["path"] == path for r in rows):
            rows.append(dict(path=path, occurrences={},
                             scanned_by_needle=False, attributed=True, **a))
    rows.sort(key=lambda r: r["path"])
    unattributed = [r["path"] for r in rows if not r["attributed"]]
    reader_facing = [r["path"] for r in rows
                     if r.get("exposure") == "CURRENT_READER_FACING_OVERCLAIM"]
    needs_fix = [r["path"] for r in rows if r.get("correction_required")]
    return dict(
        needles=list(SCAN_NEEDLES),
        self_excluded=list(SELF_EXCLUDED),
        self_exclusion_reason=("a screen may not count its own output as corpus exposure; "
                               "excluding it also keeps the scan stable while it is written"),
        n_files_scanned=len(_tracked_files()),
        n_files_with_occurrence=sum(1 for r in rows if r["scanned_by_needle"]),
        n_surfaces_inspected_by_path_without_a_needle=sum(
            1 for r in rows if not r["scanned_by_needle"]),
        needle_scan_blind_spot_note=("a surface can consume this dataset or gate without "
                                     "containing either needle — EVIDENCE_LINKS.json, PV-02, the "
                                     "registry and the generated public claims artifact all do. "
                                     "They are inspected by path and attributed alongside the "
                                     "scan hits, never left to the grep."),
        surfaces=rows,
        inspected_and_clean=INSPECTED_CLEAN,
        coverage_complete=not unattributed,
        unattributed=unattributed,
        exposure_counts={c: sum(1 for r in rows if r.get("exposure") == c)
                         for c in EXPOSURE_CLASSES},
        n_reader_facing_overclaims=len(reader_facing),
        reader_facing_overclaims=reader_facing,
        correction_required=needs_fix,
        released_content=RELEASED_CONTENT,
        released_content_note_method=("declared, not scanned at run time — a depth-1 CI checkout "
                                      "has no tags, and a deterministic result may not vary with "
                                      "that. verify_released_content() checks it where tags exist."),
        released_note=("The tagged source trees DO carry both the manifest cell and the gate "
                       "docstring: the defect is in released source. It is not in any released "
                       "reader-facing CLAIM — the public claims artifact records "
                       "same_campaign_not_held_out and reality_facing=false, and PV-02 excludes "
                       "the gate outright."),
        pages_publish_root="docs/public/site",
        pages_carries_attribution=False,
    )


# --------------------------------------------------------------------------------------------
# 4. BOUNDED MIXED-STRENGTH GENERALITY CHECK  (protocol S6 — rule frozen before the answer)
# --------------------------------------------------------------------------------------------
S0_TOKENS = ("independent", "post-fit", "verification", "qualitative")


def split_segments(cell):
    """Parenthesis-aware split on top-level `/`, `+`, `;`.

    Protocol S6 step 1. Paren-awareness is what stops prose inside a caveat — e.g.
    "qualitative (... contrasts are independent ...)" — from reading as a second label.
    """
    out, buf, depth = [], [], 0
    for ch in cell:
        if ch in "([":
            depth += 1
        elif ch in ")]":
            depth = max(0, depth - 1)
        if depth == 0 and ch in "/+;":
            out.append("".join(buf).strip())
            buf = []
        else:
            buf.append(ch)
    out.append("".join(buf).strip())
    return [s for s in out if s]


def head_label(segment):
    """The S0 token a segment BEGINS with, or None. Protocol S6 step 2."""
    s = segment.strip().lower()
    for tok in S0_TOKENS:
        if re.match(r"^%s\b" % re.escape(tok), s):
            return "post-fit" if tok == "post-fit" else tok
    return None


def manifest_rows():
    with open(REPO_ROOT / "puckworks/data/MANIFEST.csv", newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def select_mixed_strength():
    """PRIMARY and SECONDARY sets, by the frozen rule alone."""
    primary, secondary = [], []
    for r in manifest_rows():
        cell = r["validation_strength"]
        segs = split_segments(cell)
        heads = [head_label(s) for s in segs]
        s0 = [h for h in heads if h]
        distinct = sorted(set(s0))
        rec = dict(dataset_id=r["dataset_id"], validation_strength=cell,
                   segments=segs, head_labels=heads, distinct_s0_labels=distinct)
        if len(distinct) >= 2:
            primary.append(rec)
        elif len(segs) >= 2 and s0 and any(h is None for h in heads):
            secondary.append(rec)
    return primary, secondary


#: G1-G5 per PRIMARY-SET row, hand-read against the row's own caveat and its consumers.
#: This is the generality test of I-045's METHOD. No other candidate's disposition is adjudicated.
GENERALITY_FINDINGS = {
    "foster2025_2/fig12_14_curves": dict(
        G1_same_evidence_unit=False,
        G2_scope="distinct COLUMNS of one file (s_fit/w_fit/H_fit vs s_data/H_data + errors)",
        G3_wording_identifies_scope=True,
        G3_note=("the cell's parentheticals '(CT data)' and '(fitted curves)' do name the two "
                 "arms — the scope is stated; it is the STRENGTH of one arm that is wrong"),
        G4_consumer_could_attach_stronger_label_to_wrong_assertion=True,
        G4_note="gate_foster_ct_trajectory does exactly this",
        G5_downstream_propagates_ambiguity=False,
        G5_note="EVIDENCE_LINKS, the public claims artifact and PV-02 all refuse it",
        is_the_audited_row=True,
        source_strength_status="CONFIRMED_INCORRECT",
        source_strength_note=("adjudicated against the primary source in this deep screen: "
                              "Eq. (39) and Sec. IV A show the CT arm was fitted")),
    "waszkiewicz2025/traces_time_dependent": dict(
        G1_same_evidence_unit=False,
        G2_scope=("distinct ASSERTIONS over the same columns — an equilibrium arm and a 9-bar "
                  "Q(t) reproduction arm"),
        G3_wording_identifies_scope=True,
        G3_note=("'independent within-rig (equilibrium) / post-fit (9-bar Q(t) reproduction)' "
                 "names both the strength and the assertion each applies to — this is the "
                 "best-scoped mixed cell in the corpus"),
        G4_consumer_could_attach_stronger_label_to_wrong_assertion=False,
        G4_note=("I-040 enumerated 27 consumers and found ZERO promotions; PV-02 already records "
                 "an explicit EXCLUSION of the one gate that could have over-claimed"),
        G5_downstream_propagates_ambiguity=False,
        G5_note="",
        is_the_audited_row=False,
        known_comparison_case="I-040 (RETIRE)",
        source_strength_status="NOT_SOURCE_ADJUDICATED",
        source_strength_note=("I-040 established that no CONSUMER over-claims relative to this "
                              "cell's own labels. It did NOT go to waszkiewicz2025 and check "
                              "whether 'independent within-rig' is correct against that source's "
                              "fit lineage, and neither did this screen. Nothing here says the "
                              "strength is right; nothing says it is wrong.")),
    "romancorrochano2017/y0_extractable": dict(
        G1_same_evidence_unit=True,
        G2_scope=("two DIFFERENT ASSERTIONS over the same table — the nested-ceiling quantities "
                  "(independent) and the monotone size-exclusion trend (qualitative)"),
        G3_wording_identifies_scope=True,
        G3_note=("'independent (distinct nested ceiling quantities, K<1) + qualitative (monotone "
                 "size-exclusion)' names, for each label, the assertion it covers — and the "
                 "single consuming gate is named in gate_use, so the mapping is recoverable"),
        G4_consumer_could_attach_stronger_label_to_wrong_assertion=True,
        G4_note=("STRUCTURALLY possible, because both labels cover one evidence unit: a consumer "
                 "asserting the size-exclusion TREND could cite the independent half. Whether any "
                 "consumer actually does is NOT tested here — that would be executing another "
                 "candidate. What matters for generality is that the wording already carries the "
                 "scope needed to tell them apart."),
        G5_downstream_propagates_ambiguity=None,
        G5_note="not determined — out of scope for a bounded generality test",
        is_the_audited_row=False,
        source_strength_status="NOT_SOURCE_ADJUDICATED",
        source_strength_note=("the primary source (romancorrochano2017, a Birmingham thesis) was "
                              "NOT read for this row. Nothing here says the strength is right or "
                              "wrong — adjudicating it would be executing another candidate.")),
}


def generality():
    primary, secondary = select_mixed_strength()
    rows = []
    for rec in primary:
        f = GENERALITY_FINDINGS.get(rec["dataset_id"])
        rows.append(dict(rec, findings=f, adjudicated=f is not None))
    scoped = [r for r in rows if (r.get("findings") or {}).get("G3_wording_identifies_scope")]
    at_risk = [r["dataset_id"] for r in rows
               if r.get("findings") and r["findings"].get(
                   "G4_consumer_could_attach_stronger_label_to_wrong_assertion")]
    status = {r["dataset_id"]: (r.get("findings") or {}).get("source_strength_status")
              for r in rows}
    confirmed_wrong_strength = sorted(k for k, v in status.items()
                                      if v == "CONFIRMED_INCORRECT")
    adjudicated = sorted(k for k, v in status.items() if v != "NOT_SOURCE_ADJUDICATED")
    not_adjudicated = {k: v for k, v in status.items() if v == "NOT_SOURCE_ADJUDICATED"}
    return dict(
        rule=("parenthesis-aware split on top-level / + ; then the S0 token each segment BEGINS "
              "with; PRIMARY = >= 2 distinct S0 head labels"),
        s0_tokens=list(S0_TOKENS),
        n_manifest_rows=len(manifest_rows()),
        primary_set=[r["dataset_id"] for r in primary],
        n_primary=len(primary),
        secondary_set=[dict(dataset_id=r["dataset_id"],
                            validation_strength=r["validation_strength"]) for r in secondary],
        n_secondary=len(secondary),
        secondary_note=("mixed in FORM but not in S0 vocabulary — one segment head is a non-S0 "
                        "label such as 'reference' or 'kernel check'. Counted, not adjudicated."),
        rows=rows,

        # --- SCOPE: does each cell say which assertion/column each label covers? -------------
        n_primary_set_rows=len(primary),
        n_rows_with_scope_stated=len(scoped),
        recurring_scope_failure_found=len(scoped) != len(primary),
        n_where_a_consumer_could_misattach=len(at_risk),
        consumers_could_misattach=at_risk,

        # --- SOURCE ACCURACY: is each stated strength correct against its primary source? ----
        # A DIFFERENT question from scope, and this bounded screen answered it for ONE row only.
        n_strengths_source_adjudicated_in_this_deep_screen=len(adjudicated),
        strengths_source_adjudicated=adjudicated,
        n_confirmed_incorrect_strengths=len(confirmed_wrong_strength),
        confirmed_incorrect_strengths=confirmed_wrong_strength,
        other_rows_strength_status=not_adjudicated,
        evidence_strength_generality="NOT_ESTABLISHED_AS_GENERAL",

        # --- what may be concluded, and what may not ----------------------------------------
        verdict=("SCOPE is stated in every primary-set cell, so no recurring scope failure was "
                 "found. SOURCE ACCURACY is a different question: this screen adjudicated ONE "
                 "row against its primary source and confirmed ONE incorrect strength. The other "
                 "two rows' strengths were NOT source-adjudicated — nothing here says they are "
                 "correct."),
        not_supported=("that the defect is globally isolated, or that the other mixed-strength "
                       "rows carry correct strengths. Establishing either would mean reading "
                       "those sources, which is executing another candidate."),
        recurring_defect_demonstrated=(len(confirmed_wrong_strength) >= 2
                                       or len(scoped) != len(primary)),
        no_other_candidate_adjudicated=True,
    )


# --------------------------------------------------------------------------------------------
# 5. ALTERNATIVE EXPLANATIONS  (protocol S7.2)
# --------------------------------------------------------------------------------------------
def alternatives():
    return [
        dict(id="A1", challenge="the CT observations were not actually used to fit the tested object",
             verdict="FAILS",
             settled_by=("Eq. (39) sums squared residuals in s_i and H_i, and Sec. IV A states the "
                         "fit used 'the mean locations for s(t) and H(t) as the data to fit'. The "
                         "repository artifact's CT columns are that 5-line mean."),
             evidence=["Q2", "Q6", "Q7"]),
        dict(id="A2", challenge="only some trajectories or time points were fitted, leaving a "
                                "defensible held-out subset",
             verdict="FAILS",
             settled_by=("The objective runs over all N measurement times. The only other series "
                         "in Figs 12-14 is the CENTRE LINE, which is one of the five positions "
                         "averaged into the fit data — a sub-reduction, not a holdout, and never "
                         "described as validation. Every other candidate holdout (Figs 6, 7-9, "
                         "15, Appendix B, the coarse grind, t_p/t_s) is either data analysis, an "
                         "assumption check, model output, or a run the authors decline to model."),
             evidence=["Q2", "Q6", "Q7", "Q11", "Q12"]),
        dict(id="A3", challenge="the manifest label describes everything in the artifact, not the "
                                "evidentiary status of each gate assertion",
             verdict="FAILS",
             settled_by=("Even read as a file-level union the cell is wrong, because NO part of "
                         "the artifact is independent under S0: the fitted columns are "
                         "verification and the CT columns are post-fit. The union of "
                         "{verification, post-fit} does not contain 'independent'. The union "
                         "reading would also make the corpus's own scoping convention — used "
                         "correctly in every other primary-set cell — meaningless."),
             evidence=["L6"]),
        dict(id="A4", challenge="because EVIDENCE_LINKS is correctly bounded, the manifest and "
                                "gate wording are inconsequential",
             verdict="PARTLY SUCCEEDS — and it is why this is not a publication finding",
             settled_by=("Containment is real and measured: zero reader-facing over-claims, the "
                         "public claims artifact records same_campaign_not_held_out and "
                         "reality_facing=false, and PV-02 excludes the gate. So the consequence "
                         "is bounded. It does NOT make the attribution correct, and the cell is "
                         "in released source where the next consumer would inherit it."),
             evidence=["blast_radius"]),
        dict(id="A5", challenge="'independent' means a distinct measurement modality",
             verdict="FAILS",
             settled_by=("Two reasons, NEITHER of which is that the paper avoids the word "
                         "'validation' — it does not avoid it, and an earlier version of this "
                         "screen wrongly said so. (1) GLOSSARY: ROADMAP S0 defines independent as "
                         "'data not used in fitting the thing being tested', which is a statement "
                         "about the FIT, not about the measurement modality. (2) FIT LINEAGE: "
                         "Eq. (39) and Sec. IV A establish that these observations WERE used in "
                         "fitting. The source contains no claim that any observation was held out "
                         "or independent, so nothing in it rescues the modality reading either."),
             does_not_rely_on=("any claim that the authors avoid validation language. They use it "
                               "about the technique in the present tense; it simply does not bear "
                               "on whether these particular data were fitted."),
             evidence=["L7", "Q2", "Q6", "glossary"]),
    ]


# --------------------------------------------------------------------------------------------
# 6. CORRECTION FORMULATIONS  (protocol S7.1 — assessed, NOT implemented)
# --------------------------------------------------------------------------------------------
def formulations():
    return [
        dict(id="F1", wording="post-fit reconstruction (CT data) / verification (fitted curves)",
             scientifically_accurate=True, glossary_compatible=True,
             preserves_source_wording=True,
             consumable_by_current_tools=True,
             consumable_note="same shape as the existing cell; no parser or gate changes",
             migration_cost="one cell + one docstring",
             risk_of_implying_held_out_validation="low",
             generalizes=True,
             assessment=("Minimal and correct. Loses the same-campaign detail, which "
                         "EVIDENCE_LINKS already carries.")),
        dict(id="F2", wording=("post-fit, same-campaign CT observations / verification of fitted "
                               "trajectories"),
             scientifically_accurate=True, glossary_compatible=True,
             glossary_note=("'same-campaign' is not an S0 rung; it is a qualifier on post-fit "
                            "reconstruction, matching EVIDENCE_LINKS' own "
                            "relationship=same_campaign_not_held_out"),
             preserves_source_wording=True,
             consumable_by_current_tools=True,
             migration_cost="one cell + one docstring",
             risk_of_implying_held_out_validation="lowest — it names the non-holdout explicitly",
             generalizes=True,
             assessment="RECOMMENDED. Most precise, no schema change, aligns with the downstream "
                        "record that is already correct."),
        dict(id="F3", wording="split into separately scoped records/views for fitted trajectories, "
                              "CT observations and the shared time base",
             scientifically_accurate=True, glossary_compatible=True,
             preserves_source_wording=True,
             consumable_by_current_tools=False,
             consumable_note=("would break the one-row-per-dataset assumption in the loader, the "
                              "gate, EVIDENCE_LINKS' dataset keys and the Foundry's generated "
                              "lineage index"),
             migration_cost="high — schema, loader, gate, evidence records, regenerated artifacts",
             risk_of_implying_held_out_validation="low",
             generalizes=True,
             generalization_note=("would need to be applied corpus-wide to be coherent, and the "
                                  "generality check found NO other cell that needs it"),
             assessment="REJECTED for now: cost and blast radius are wildly out of proportion to "
                        "one wrong word, and the check that would justify it came back negative."),
        dict(id="F4", wording="retain one row, add an explicit column-to-evidence mapping",
             scientifically_accurate=True, glossary_compatible=True,
             preserves_source_wording=True,
             consumable_by_current_tools=False,
             consumable_note="requires a new manifest column or sidecar the schema does not have",
             migration_cost="medium — additive schema change plus 110 rows to leave empty",
             risk_of_implying_held_out_validation="low",
             generalizes=True,
             assessment=("Genuinely better as a general convention, and it is what the audited "
                         "row's own parentheticals approximate in prose. But the generality check "
                         "shows the prose convention ALREADY states scope correctly everywhere, "
                         "so this buys machine-readability, not correctness. Out of scope here; "
                         "worth a separate proposal if a second such defect appears.")),
    ]


# --------------------------------------------------------------------------------------------
# 7. DECISION
# --------------------------------------------------------------------------------------------
OUTPUT_CLASSES = ("RETIRE_AFTER_DEEP_SCREEN", "NEEDS_PRIMARY_SOURCE", "CORRECTION_ONLY",
                  "TECHNICAL_NOTE_CANDIDATE", "METHODS_PAPER_CANDIDATE", "PUBLIC_STORY_CANDIDATE")

FUTURE_CORRECTION_TARGETS = [
    dict(n=1, target="puckworks/data/MANIFEST.csv — foster2025_2/fig12_14_curves validation_strength",
         current=MANIFEST_CELL,
         recommended="post-fit, same-campaign CT observations / verification of fitted trajectories",
         edited_in_this_pr=False),
    dict(n=2, target="puckworks/validation/gates.py — gate_foster_ct_trajectory docstring",
         current="...within their error bars (independent, 'qualitative-good')",
         recommended=("...within their error bars (post-fit reconstruction, same campaign, not "
                      "held out; 'qualitative-good')"),
         edited_in_this_pr=False),
    dict(n=3, target="regenerate the derived Foundry artifacts that copy the cell byte-identically",
         current="evidence_lineage_index.csv and corpus_map.json inherit the wording",
         recommended=("`python -m puckworks.insights write` after target 1 — no hand edit; they "
                      "are generated and must never be edited directly"),
         edited_in_this_pr=False),
]


def decide(lineage_r, blast, gen, alts):
    """Derive the output class from the evidence, by the protocol's own rules."""
    held_out = lineage_r["lineage"]["L4_any_held_out_data"]["answer"].startswith("NO")
    lineage_settled = all(v.get("settled") for v in lineage_r["lineage"].values())
    confirmed = (not lineage_r["manifest_wording_correct"]) and held_out and lineage_settled
    survives = all(a["verdict"].startswith("FAILS") for a in alts if a["id"] != "A4")

    if not lineage_settled:
        cls = "NEEDS_PRIMARY_SOURCE"
    elif not confirmed or not survives:
        cls = "RETIRE_AFTER_DEEP_SCREEN"
    elif gen["recurring_defect_demonstrated"]:
        cls = "TECHNICAL_NOTE_CANDIDATE"
    else:
        cls = "CORRECTION_ONLY"

    return dict(
        output_class=cls,
        cheap_screen_disposition=CHEAP_SCREEN_DISPOSITION,
        derivation=dict(
            lineage_settled_from_primary_source=lineage_settled,
            no_data_held_out=held_out,
            attribution_confirmed_incorrect=confirmed,
            survives_alternatives_A1_A2_A3_A5=survives,
            containment_measured=blast["n_reader_facing_overclaims"] == 0,
            recurring_defect_demonstrated=gen["recurring_defect_demonstrated"],
            recurring_scope_failure_found=gen["recurring_scope_failure_found"],
            n_confirmed_incorrect_strengths=gen["n_confirmed_incorrect_strengths"],
            n_strengths_source_adjudicated=gen[
                "n_strengths_source_adjudicated_in_this_deep_screen"],
            other_rows_strength_status=gen["other_rows_strength_status"],
            why_not_technical_note=("CORRECTION_ONLY is reached because no RECURRING defect was "
                                    "demonstrated — not because corpus-wide isolation was "
                                    "proved. It was not: the other two mixed-strength rows' "
                                    "strengths were never source-adjudicated."),
        ),
        strongest_supported_claim=(
            "In this repository, one MANIFEST cell and the gate docstring that copies it label a "
            "set of micro-CT observations 'independent' when the primary source's own objective "
            "(Phys. Fluids 37, 013383, Eq. 39) fitted the tested parameters to exactly those "
            "observations. Under ROADMAP S0 the arm is post-fit reconstruction, same campaign, "
            "not held out. The attribution is materially incorrect, it is present in released "
            "source, and it reaches ZERO reader-facing claim surfaces because every downstream "
            "record independently refuses the strong reading."),
        strongest_claim_NOT_supported=(
            "That this is a general defect, a novel method, or a publishable finding. The bounded "
            "corpus check found the scoping convention working correctly in every other "
            "mixed-strength cell; the audit method is a hand-read of one paper plus a grep, not a "
            "reusable instrument; and the underlying principle — calibration data are not "
            "independent validation — is textbook. Nor does it say the gate's NUMBERS are wrong, "
            "or that foster2025.machine_mode fails anything."),
        future_correction_targets=FUTURE_CORRECTION_TARGETS,
        recommended_correction_wording=(
            "post-fit, same-campaign CT observations / verification of fitted trajectories"),
        separate_correction_pr_recommended=True,
        further_literature_review_justified=False,
        manuscript_work_justified=False,
        experimental_work_justified=False,
    )


# --------------------------------------------------------------------------------------------
def deep_screen():
    g = glossary()
    lin = source_lineage()
    blast = blast_radius()
    gen = generality()
    alts = alternatives()
    forms = formulations()
    dec = decide(lin, blast, gen, alts)
    return dict(
        screen="I-045 deep screen (IF-7)",
        dataset=DATASET_ID,
        protocol=dict(path=PROTOCOL, frozen_before_analysis=True),
        models_executed=False,
        models_executed_note=("No model is executed anywhere in this screen. Protocol stop "
                              "condition S5: the lineage question is answered from text."),
        cheap_screen=dict(
            disposition=CHEAP_SCREEN_DISPOSITION,
            bundle="docs/insights/screens/I-045/",
            #: This refers to the historical SCIENTIFIC DISPOSITION, not to byte-preservation of
            #: the live files. The live snapshot WAS refreshed under an explicit post-protocol
            #: waiver; the frozen protocol predates that waiver and is not edited.
            historical_disposition_rewritten=False,
            live_snapshot_refreshed_under_authorized_waiver=True,
            waiver_is_post_protocol_authority=True,
            snapshot_provenance=dict(
                historical_if6b_snapshot=dict(
                    merge_commit="7d8114931c5bafbf3915d9f70b7c4621f8261a22",
                    n_static_references=102, n_static_reference_files=24),
                current_if7_snapshot=dict(n_static_references=136,
                                          n_static_reference_files=28),
                decision_bearing_fields_changed=False,
                cheap_screen_disposition=CHEAP_SCREEN_DISPOSITION,
                why=("adding this deep screen's own documents to a deliberately "
                     "repository-wide, over-approximating static inventory advanced the live "
                     "snapshot; the counts are declared here and the CURRENT values are also "
                     "recomputed from the committed cheap result at run time"),
            ),
        ),
        glossary=g,
        source_lineage=lin,
        blast_radius=blast,
        generality=gen,
        alternatives=alts,
        formulations=forms,
        decision=dec,
        novelty_review=dict(path="docs/insights/screens/I-045/NOVELTY_REVIEW.md",
                            note=("external findings are recorded there and are deliberately NOT "
                                  "fabricated into this deterministic output (stop condition S6)")),
    )


def figure(path=None, result=None):
    """source fit lineage -> manifest wording -> gate assertion -> downstream/public surfaces."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import FancyBboxPatch

    r = result or deep_screen()
    path = path or (BUNDLE / "figures/deep_primary.png")
    pathlib.Path(path).parent.mkdir(parents=True, exist_ok=True)

    INK, MUTE = "#1a1a1a", "#5c5c5c"
    BAD, OK, WARN = "#b3446c", "#2a7f62", "#c46a10"

    fig = plt.figure(figsize=(13.2, 8.6))
    gs = fig.add_gridspec(2, 1, height_ratios=[1.45, 1.0], hspace=0.18)

    ax = fig.add_subplot(gs[0])
    ax.set_xlim(0, 100); ax.set_ylim(0, 100); ax.axis("off")
    ax.set_title("A — the chain, from what the authors fitted to what a reader can see",
                 fontsize=10, color=INK, loc="left", pad=8)

    cols = [
        (2.0, 22.0, "SOURCE FIT LINEAGE", BAD,
         ["Phys. Fluids 37, 013383", "Eq. (39):  L = Σ (sᵢ−s)² + (Hᵢ−H)²",
          "fmincon + MultiStart", "fits K, φ_T, t_shift", "",
          "data = 5-line MEAN sᵢ, Hᵢ", "at ALL N measurement times", "",
          "held out: NOTHING", "error bars: display only"]),
        (26.0, 22.0, "MANIFEST WORDING", BAD,
         ["foster2025_2/fig12_14_curves", "", "“independent (CT data)", " / verification (fitted curves)”",
          "", "s_data/H_data = the fit data", "→ post-fit, same campaign", "",
          "✘ INCORRECT for the CT arm", "✔ correct for the fitted arm"]),
        (50.0, 22.0, "GATE ASSERTION", BAD,
         ["gate_foster_ct_trajectory", "", "(a) RMSE vs fitted ODE", "     0.002 / 0.053 mm",
          "(b) brackets 4/8, 5/8 CT pts", "", "docstring copies the label:", "“(independent,",
          " 'qualitative-good')”", "", "numbers unaffected"]),
        (74.0, 24.0, "DOWNSTREAM / PUBLIC", OK,
         ["EVIDENCE_LINKS.json", "  eval/same_campaign", "  AND fit/fit_input",
          "  reality_facing: false", "", "public claims.json", "  same_campaign_not_held_out",
          "  outcome: negative", "", "PV-02: EXCLUDES the gate", "Pages site: no occurrence"]),
    ]
    for x, w, title, colour, lines in cols:
        ax.add_patch(FancyBboxPatch((x, 8), w, 78,
                                    boxstyle="round,pad=0.4,rounding_size=1.2",
                                    fc=colour, ec=colour, alpha=0.09, lw=1.0))
        ax.text(x + w / 2, 89, title, fontsize=8.8, weight="bold", color=colour, ha="center")
        y = 80
        for ln in lines:
            ax.text(x + 1.4, y, ln, fontsize=7.2, color=INK if not ln.startswith(" ") else MUTE)
            y -= 6.6
    for x in (24.6, 48.6, 72.6):
        ax.annotate("", xy=(x + 1.2, 47), xytext=(x - 1.0, 47),
                    arrowprops=dict(arrowstyle="-|>", color="#4a4a4a", lw=1.3))
    ax.text(86, 3.2, "0 reader-facing over-claims", fontsize=8.4, weight="bold",
            color=OK, ha="center")
    ax.text(37, 3.2, "present in released source (v0.3.0)", fontsize=8.4, weight="bold",
            color=WARN, ha="center")

    ax2 = fig.add_subplot(gs[1])
    ax2.set_xlim(0, 100); ax2.set_ylim(0, 100); ax2.axis("off")
    ax2.set_title("B — bounded generality: is the corpus's mixed-strength convention broken?",
                  fontsize=10, color=INK, loc="left", pad=8)
    rows = r["generality"]["rows"]
    ax2.text(2, 86, "%d of %d MANIFEST rows carry ≥ 2 distinct §0 labels   ·   SCOPE and "
                    "SOURCE-STRENGTH are different questions"
             % (r["generality"]["n_primary"], r["generality"]["n_manifest_rows"]),
             fontsize=8.6, color=INK)
    hdr = [(2, "dataset"), (40, "scope stated?"), (58, "could a consumer\nmisattach?"),
           (78, "source-strength\ncorrectness")]
    for x, t in hdr:
        ax2.text(x, 74, t, fontsize=7.6, weight="bold", color=MUTE)
    y = 62
    for row in rows:
        f = row.get("findings") or {}
        wrong = bool(f.get("is_the_audited_row"))
        ax2.add_patch(FancyBboxPatch((1.2, y - 5.6), 97.0, 13.0,
                                     boxstyle="round,pad=0.2,rounding_size=0.6",
                                     fc=BAD if wrong else OK, ec="none", alpha=0.10))
        ax2.text(2, y + 2.6, row["dataset_id"], fontsize=7.4, color=INK,
                 weight="bold" if wrong else "normal")
        cell = row["validation_strength"]
        ax2.text(2, y - 3.4, cell if len(cell) <= 80 else cell[:78] + "…",
                 fontsize=6.3, color=MUTE)
        ax2.text(40, y, "✔ yes" if f.get("G3_wording_identifies_scope") else "✘ no",
                 fontsize=7.4, color=OK if f.get("G3_wording_identifies_scope") else BAD)
        mis = f.get("G4_consumer_could_attach_stronger_label_to_wrong_assertion")
        ax2.text(58, y, "yes" if mis else "no", fontsize=7.4, color=WARN if mis else OK)
        ax2.text(78, y, "✘ CONFIRMED WRONG" if wrong else "not adjudicated",
                 fontsize=7.4, weight="bold" if wrong else "normal",
                 color=BAD if wrong else MUTE, style="normal" if wrong else "italic")
        y -= 15.0
    ax2.text(2, 8, "One CONFIRMED wrong strength. No recurring scope failure found. The other "
                   "rows' strengths were NOT source-adjudicated —", fontsize=8.0, color=INK,
             style="italic")
    ax2.text(2, 2, "so this screen does NOT establish that they are correct, and does not prove "
                   "corpus-wide isolation.", fontsize=8.0, color=INK, style="italic")

    foot = ("CHEAP_SCIENTIFIC_SCREEN · NOT_A_PUBLICATION_RESULT · "
            "NOT_A_MODEL_VALIDATION_UPGRADE     cheap screen: %s   →   deep screen: %s"
            % (r["cheap_screen"]["disposition"], r["decision"]["output_class"]))
    fig.text(0.012, 0.012, foot, fontsize=7.6, color=MUTE)
    fig.suptitle("I-045 deep screen — the CT observations ARE the fit data, and the label says "
                 "otherwise", fontsize=12.4, weight="bold", color=INK, x=0.012, ha="left", y=0.985)
    fig.savefig(path, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return path


def main(argv=None):
    r = deep_screen()
    out = BUNDLE / "deep_result.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(r, indent=2) + "\n", encoding="utf-8")
    b, g = r["blast_radius"], r["generality"]
    print("protocol frozen before analysis: %s" % r["protocol"]["frozen_before_analysis"])
    print("models executed: %s" % r["models_executed"])
    print("lineage: %s" % r["source_lineage"]["determination"])
    print("blast radius: %d files carry the attribution; coverage complete=%s"
          % (b["n_files_with_occurrence"], b["coverage_complete"]))
    for c, n in b["exposure_counts"].items():
        if n:
            print("    %-34s %d" % (c, n))
    print("  reader-facing over-claims: %d" % b["n_reader_facing_overclaims"])
    print("generality: %d/%d primary-set rows; scope stated %d/%d; recurring scope failure = %s"
          % (g["n_primary"], g["n_manifest_rows"], g["n_rows_with_scope_stated"],
             g["n_primary_set_rows"], g["recurring_scope_failure_found"]))
    print("  strengths source-adjudicated %d; confirmed incorrect %d (%s); others %s"
          % (g["n_strengths_source_adjudicated_in_this_deep_screen"],
             g["n_confirmed_incorrect_strengths"],
             ", ".join(g["confirmed_incorrect_strengths"]),
             "NOT_SOURCE_ADJUDICATED"))
    print("alternatives: %s" % ", ".join("%s %s" % (a["id"], a["verdict"].split()[0])
                                         for a in r["alternatives"]))
    print("cheap screen: %s  ->  DEEP SCREEN: %s"
          % (r["cheap_screen"]["disposition"], r["decision"]["output_class"]))
    figure(result=r)
    print("wrote %s" % out.relative_to(REPO_ROOT))
    print("wrote %s" % (BUNDLE / "figures/deep_primary.png").relative_to(REPO_ROOT))
    return r


if __name__ == "__main__":
    main()
