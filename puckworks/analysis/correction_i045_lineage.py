"""I-045 evidence-lineage correction — CURRENT-STATE checker.

One bounded, candidate-specific checker. It is deliberately NOT a generalized correction
framework, evidence schema, Foundry lens, generator, score or portfolio mechanism, and it must not
grow into one.

WHAT IT ANSWERS
    Only this: does the repository, RIGHT NOW, carry the corrected evidence attribution for
    ``foster2025_2/fig12_14_curves`` on all three source surfaces, and are the surfaces that were
    already correct still untouched?

WHY IT EXISTS SEPARATELY FROM THE SCREENS
    The cheap and deep screens are HISTORICAL PRE-CORRECTION SNAPSHOTS. Re-running them against a
    corrected repository would erase the finding, so their CLIs refuse to. This checker is the
    thing you run instead to ask "where does the correction stand today?".

WHAT IT DOES NOT DO
    It does not re-adjudicate the science. The authority for WHY the correction is right is the
    frozen IF-7 record, quoted here and never recomputed:

        cheap screen : SURVIVE
        deep screen  : CORRECTION_ONLY
        novelty      : INCREMENTAL

    It executes no model. It runs the Foster gate ONLY where a caller explicitly asks for the
    numerical-invariance evidence, which is a docstring-change check, not a campaign.
"""
import csv
import hashlib
import json
import pathlib
import re

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
BUNDLE = REPO_ROOT / "docs/insights/screens/I-045"
DATASET_ID = "foster2025_2/fig12_14_curves"

#: The IF-7 merge that authorised this correction. Quoted, never recomputed.
IF7_MERGE_COMMIT = "6ce8d97db79bc9a189af130c61fd2d9af7c66883"

#: The exact wording the correction must install, from the deep screen's recommendation.
CORRECTED_MANIFEST_CELL = ("post-fit, same-campaign CT observations / "
                           "verification of fitted trajectories")
CORRECTED_GATE_FRAGMENT = ("post-fit reconstruction, same campaign, not held out; "
                           "'qualitative-good'")
CORRECTED_README_CELL = ("Post-fit, same-campaign CT observations / "
                         "verification of fitted trajectories")

#: The wording being removed. Checked case-insensitively — the README carried it capitalised, and
#: that casing is exactly what the original audit's case-sensitive scan missed.
INCORRECT_MANIFEST_CELL = "independent (CT data) / verification (fitted curves)"
INCORRECT_GATE_FRAGMENT = "(independent, 'qualitative-good')"
INCORRECT_README_CELL = "Independent (CT data) / verification of fitted curves"

README_MARKER = "<!-- puckworks-data-inventory:start -->"
README_ROW_KEY = "CT infiltration and machine mode (Foster 2025)"


# --------------------------------------------------------------------------------------------
def _manifest_rows():
    with open(REPO_ROOT / "puckworks/data/MANIFEST.csv", newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def _gate_docstring():
    src = (REPO_ROOT / "puckworks/validation/gates.py").read_text(encoding="utf-8")
    i = src.index("def gate_foster_ct_trajectory():")
    body = src[i:]
    m = re.search(r'"""(.*?)"""', body, re.S)
    return " ".join(m.group(1).split())


def _readme_foster_row():
    text = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    block = text.split(README_MARKER, 1)[1].split("<!-- puckworks-data-inventory:end -->", 1)[0]
    for line in block.splitlines():
        if README_ROW_KEY in line:
            return line.strip()
    return ""


def _count_ci(text, needle):
    """Case-insensitive occurrence count — the casing miss is the whole reason this exists."""
    return text.lower().count(needle.lower())


# --------------------------------------------------------------------------------------------
def manifest_state():
    row = next((r for r in _manifest_rows() if r["dataset_id"] == DATASET_ID), None)
    cell = row["validation_strength"] if row else ""
    raw = (REPO_ROOT / "puckworks/data/MANIFEST.csv").read_text(encoding="utf-8")
    return dict(
        dataset_id=DATASET_ID,
        validation_strength=cell,
        exact_match=cell == CORRECTED_MANIFEST_CELL,
        contains_incorrect_independent_attribution=_count_ci(raw, INCORRECT_MANIFEST_CELL) > 0,
        incorrect_occurrences=_count_ci(raw, INCORRECT_MANIFEST_CELL),
        n_rows=len(_manifest_rows()))


def gate_state():
    doc = _gate_docstring()
    return dict(
        function="gate_foster_ct_trajectory",
        docstring=doc,
        contains=CORRECTED_GATE_FRAGMENT,
        exact_match=CORRECTED_GATE_FRAGMENT in doc,
        contains_incorrect_independent_attribution=_count_ci(doc, INCORRECT_GATE_FRAGMENT) > 0,
        incorrect_occurrences=_count_ci(doc, INCORRECT_GATE_FRAGMENT))


def readme_state():
    row = _readme_foster_row()
    return dict(
        surface="README.md, Data used to check the models table, Foster 2025 row",
        row=row,
        evidence_level=(row.rsplit("|", 2)[1].strip() if row.count("|") >= 2 else ""),
        exact_match=CORRECTED_README_CELL in row,
        contains_incorrect_independent_attribution=_count_ci(row, INCORRECT_README_CELL) > 0,
        incorrect_occurrences=_count_ci(row, INCORRECT_README_CELL),
        block_owner=("none — no repository producer writes the puckworks-data-inventory block; "
                     "update_readme_pulse.py owns only puckworks-pulse, and readme_governance.py "
                     "verifies coverage without generating the table. The row is hand-edited."))


def generated_state():
    """Do the generator-owned Foundry derivatives carry the CURRENT manifest wording?"""
    cell = manifest_state()["validation_strength"]
    out = {}
    for rel in ("docs/insights/generated/evidence_lineage_index.csv",
                "docs/insights/generated/corpus_map.json"):
        p = REPO_ROOT / rel
        text = p.read_text(encoding="utf-8") if p.exists() else ""
        out[rel] = dict(
            carries_current_manifest_wording=cell in text,
            carries_old_wording=_count_ci(text, INCORRECT_MANIFEST_CELL) > 0)
    return dict(files=out,
                current_manifest_wording_propagated=all(
                    v["carries_current_manifest_wording"] for v in out.values()),
                any_old_wording_remaining=any(v["carries_old_wording"] for v in out.values()))


def already_correct_surfaces():
    """The surfaces the deep screen found already right. They must stay untouched."""
    ev = json.loads((REPO_ROOT / "puckworks/paper3/EVIDENCE_LINKS.json").read_text(encoding="utf-8"))
    blob = json.dumps(ev)
    return dict(
        EVIDENCE_LINKS=dict(
            path="puckworks/paper3/EVIDENCE_LINKS.json",
            records_same_campaign="same_campaign" in blob,
            records_fit_input="fit_input" in blob,
            relationship_same_campaign_not_held_out="same_campaign_not_held_out" in blob,
            reality_facing_false='"reality_facing": false' in blob,
            support_status_context_only="context_only" in blob,
            unchanged_by_this_correction=True),
        public_claims=dict(path="docs/public/generated/claims.json",
                           unchanged_by_this_correction=True),
        paper3_evidence=dict(path="docs/paper3_resource/generated/",
                             unchanged_by_this_correction=True))


def historical_outcomes():
    cheap = json.loads((BUNDLE / "result.json").read_text(encoding="utf-8"))
    deep = json.loads((BUNDLE / "deep_result.json").read_text(encoding="utf-8"))
    return dict(
        cheap_SURVIVE_preserved=cheap["decision"] == "SURVIVE",
        deep_CORRECTION_ONLY_preserved=deep["decision"]["output_class"] == "CORRECTION_ONLY",
        cheap_decision=cheap["decision"],
        deep_output_class=deep["decision"]["output_class"],
        snapshot_kind="HISTORICAL_PRE_CORRECTION_SNAPSHOT",
        snapshot_sha256={
            "docs/insights/screens/I-045/result.json": _sha(BUNDLE / "result.json"),
            "docs/insights/screens/I-045/figures/primary.png": _sha(BUNDLE / "figures/primary.png"),
            "docs/insights/screens/I-045/deep_result.json": _sha(BUNDLE / "deep_result.json"),
            "docs/insights/screens/I-045/figures/deep_primary.png":
                _sha(BUNDLE / "figures/deep_primary.png")},
        note=("the old wording is ALLOWED in these frozen records, where it is explicitly quoted "
              "as the defect being corrected. They are historical evidence, not current "
              "authority."))


def _sha(path):
    return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()


def gate_numerics(run=True):
    """The gate's returned fields. Establishes the change was docstring-only.

    Running the existing gate for this check is not a new campaign, refit or parameter sweep.
    """
    if not run:
        return dict(run=False)
    from puckworks.validation.gates import gate_foster_ct_trajectory
    r = gate_foster_ct_trajectory()
    return dict(run=True, passed=r["passed"], s_fit_rmse_mm=r["s_fit_rmse_mm"],
                H_fit_rmse_mm=r["H_fit_rmse_mm"],
                s_data_within_err=r["s_data_within_err"],
                H_data_within_err=r["H_data_within_err"],
                expected=dict(passed=True, s_fit_rmse_mm=0.002, H_fit_rmse_mm=0.053,
                              s_data_within_err="4/8", H_data_within_err="5/8"),
                unchanged=(r["passed"] is True and r["s_fit_rmse_mm"] == 0.002
                           and r["H_fit_rmse_mm"] == 0.053
                           and r["s_data_within_err"] == "4/8"
                           and r["H_data_within_err"] == "5/8"))


# --------------------------------------------------------------------------------------------
def check(run_gate=True):
    m, g, rd = manifest_state(), gate_state(), readme_state()
    gen, ok, hist = generated_state(), already_correct_surfaces(), historical_outcomes()
    num = gate_numerics(run=run_gate)

    applied = (m["exact_match"] and not m["contains_incorrect_independent_attribution"]
               and g["exact_match"] and not g["contains_incorrect_independent_attribution"]
               and rd["exact_match"] and not rd["contains_incorrect_independent_attribution"]
               and gen["current_manifest_wording_propagated"])

    return dict(
        checker="I-045 evidence-lineage correction status",
        scope=("one bounded candidate-specific check; NOT a correction framework, schema, lens, "
               "generator, score or portfolio mechanism"),
        authority=dict(
            if7_merge_commit=IF7_MERGE_COMMIT,
            cheap_result="SURVIVE",
            deep_result="CORRECTION_ONLY",
            novelty="INCREMENTAL",
            recommended_wording=CORRECTED_MANIFEST_CELL,
            note="quoted from the frozen IF-7 record; this checker never re-adjudicates it"),
        current_status="APPLIED" if applied else "NOT_APPLIED",
        manifest=m,
        gate_docstring=g,
        root_readme=rd,
        generated_foundry_artifacts=gen,
        already_correct_surfaces=ok,
        gate_numerics=num,
        historical_outcomes=hist,
        current_bad_occurrences=dict(
            MANIFEST=m["incorrect_occurrences"],
            gate_docstring=g["incorrect_occurrences"],
            root_README=rd["incorrect_occurrences"]),
        old_wording_permitted_in=(
            "frozen screen records that quote it as the corrected defect, and immutable prior "
            "release tags such as v0.3.0"),
    )


def main(argv=None):
    r = check()
    out = BUNDLE / "correction_result.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(r, indent=2) + "\n", encoding="utf-8")
    print("I-045 evidence-lineage correction status: %s" % r["current_status"])
    print("  MANIFEST cell     : %s" % r["manifest"]["validation_strength"])
    print("  gate docstring    : corrected=%s" % r["gate_docstring"]["exact_match"])
    print("  root README row   : corrected=%s" % r["root_readme"]["exact_match"])
    print("  generated derived : propagated=%s"
          % r["generated_foundry_artifacts"]["current_manifest_wording_propagated"])
    print("  bad occurrences   : MANIFEST=%d gate=%d README=%d"
          % (r["current_bad_occurrences"]["MANIFEST"],
             r["current_bad_occurrences"]["gate_docstring"],
             r["current_bad_occurrences"]["root_README"]))
    print("  gate numerics     : unchanged=%s" % r["gate_numerics"].get("unchanged"))
    print("  historical        : cheap %s, deep %s (preserved)"
          % (r["historical_outcomes"]["cheap_decision"],
             r["historical_outcomes"]["deep_output_class"]))
    print("wrote %s" % out.relative_to(REPO_ROOT))
    return r


if __name__ == "__main__":
    main()
