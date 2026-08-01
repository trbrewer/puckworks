#!/usr/bin/env python3
"""Generate the data-bearing blocks of Paper A's transfer analysis from the canonical artefacts.

Round-8 §2.4. Every stale number rounds 5 through 8 found had the same shape: a value was correct
in the producer and the artefact, and *retyped* into the manuscript, a caption, a table note or a
package line — one of which was later missed. The round-8 blocker P0-1 is the purest example, a
standalone caption still quoting the superseded 108-point benchmark months after the manuscript,
the figure and the artefact had all moved to 132.

So the values stop being retyped. This tool owns bounded, marked regions of the submission files
and renders them from `PAPER_A_ENDPOINT_PROPAGATION.json`, `PAPER_A_TRANSFER_CORPUS_CONTRACTS.json`
and `PAPER_A_COMPARATOR_LOSS_ROBUSTNESS.json` through the shared formatters in
`puckworks.paper_a.transfer_contract`. Author prose outside the markers is never touched.

Each generated block carries a source stamp naming the schema version and the corpus manifest
hash, so a *different* 44-record corpus cannot masquerade as the same one behind a matching count.

CLI::

    python tools/paper_a_transfer_text.py --check   # exit 1 if any block is stale
    python tools/paper_a_transfer_text.py --write   # rewrite the blocks in place
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from puckworks.paper_a import claim_policy as CP  # noqa: E402
from puckworks.paper_a import transfer_contract as TC  # noqa: E402
from puckworks.paper_a import transfer_semantics as TS  # noqa: E402

RESOURCE = _REPO / "docs" / "paper1_resource"
ENDPOINT_JSON = RESOURCE / "PAPER_A_ENDPOINT_PROPAGATION.json"
CORPUS_JSON = RESOURCE / "PAPER_A_TRANSFER_CORPUS_CONTRACTS.json"
LOSS_JSON = RESOURCE / "PAPER_A_COMPARATOR_LOSS_ROBUSTNESS.json"

MANUSCRIPT = _REPO / "docs" / "submission" / "PAPER_A_JFE_MANUSCRIPT.md"
DRAFT = _REPO / "docs" / "PAPER_A_DRAFT.md"
SUPPLEMENT = _REPO / "docs" / "submission" / "PAPER_A_JFE_SUPPLEMENT.md"
#: The transfer caption is authored into the INTERNAL figure map, from which
#: `tools/paper_a_figure_captions.py` generates the upload-ready caption file (round-10 P2-1).
CAPTIONS = _REPO / "docs" / "figures" / "PAPER_A_FIGURE_MAP_INTERNAL.md"

HEADLINE_ENDPOINT_G = 40.0

_WORDS = {2: "Two", 3: "Three", 4: "Four", 5: "Five"}


def _tex_int(value: int) -> str:
    """Thousands separators that survive LaTeX math mode (a bare comma spaces badly)."""
    return f"{int(value):,}".replace(",", "{,}")


def _and_list_pp(values) -> str:
    """Render signed percentage-point values as prose: 'a, b and c'."""
    items = [TC.format_pp(v) for v in values]
    if len(items) <= 1:
        return "".join(items)
    return "%s and %s" % (", ".join(items[:-1]), items[-1])


def _and_list(masses) -> str:
    """Render endpoint masses as prose: '40 g', '40 g and 42 g', '38 g, 40 g and 42 g'."""
    items = [f"{_g(m)} g" for m in masses]
    if len(items) <= 1:
        return "".join(items)
    return "%s and %s" % (", ".join(items[:-1]), items[-1])


# ─────────────────────────────────────────────────────────────────────────────────────────────
# Marker handling
# ─────────────────────────────────────────────────────────────────────────────────────────────

def _markers(name: str) -> tuple[str, str]:
    return f"<!-- {name}:begin -->", f"<!-- {name}:end -->"


def extract_block(text: str, name: str) -> str:
    """Return the body between a block's markers, raising on any malformed marker state."""
    begin, end = _markers(name)
    if text.count(begin) != 1 or text.count(end) != 1:
        raise KeyError("block %r must appear exactly once (found %d begin / %d end markers)"
                       % (name, text.count(begin), text.count(end)))
    i = text.index(begin) + len(begin)
    j = text.index(end)
    if j < i:
        raise KeyError("block %r has its end marker before its begin marker" % name)
    body = text[i:j].strip("\n")
    if not body.strip():
        raise KeyError("block %r is empty" % name)
    return body


def replace_block(text: str, name: str, body: str) -> str:
    begin, end = _markers(name)
    if text.count(begin) != 1 or text.count(end) != 1:
        raise KeyError("block %r must appear exactly once before it can be written" % name)
    i = text.index(begin) + len(begin)
    j = text.index(end)
    return text[:i] + "\n" + body.strip("\n") + "\n" + text[j:]


def stamp(manifest: dict) -> str:
    """The invisible source stamp every generated block carries."""
    return ("<!-- paper-a:transfer-corpus schema=%d n_records=%d n_observations=%d "
            "manifest_sha256=%s -->"
            % (TC.SCHEMA_VERSION, manifest["n_held_out_records"], manifest["n_observations"],
               manifest["manifest_sha256"]))


# ─────────────────────────────────────────────────────────────────────────────────────────────
# Artefact access helpers
# ─────────────────────────────────────────────────────────────────────────────────────────────

def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def validated_analysis(ep: dict):
    """Return the artefact's ``(estimand, inferential_status)`` as validated typed objects.

    Round-10 P1-2. Every favourability sentence in this file used to come from
    ``TS.favourable_extremes(sem)`` with the direction defaulted at module scope, and from prose that
    hard-coded "negative values favour the mechanistic model" beside it. The artefact's own estimand
    was a free-text sentence nobody compared against either. A reversed artefact could therefore
    leave every rendered sentence unchanged.

    The renderer now takes its direction FROM the artefact, through this function, and a missing,
    unknown or self-inconsistent declaration raises here rather than rendering a default.
    """
    design = ep.get("resampling_design")
    if not isinstance(design, dict):
        raise KeyError("the endpoint artefact carries no resampling_design, so the estimand's "
                       "direction is undeclared; refusing to assume one")
    estimand = TS.estimand_from_dict(design.get("estimand"))
    status = TS.status_from_dict(design.get("inferential_status"))
    problems = TS.validate_inferential_status(status)
    if problems:
        raise ValueError("the artefact's inferential status is not internally consistent, so what "
                         "the analysis may claim is undefined: %s" % "; ".join(problems))
    # Round-11 P1-2. Coherence is not evidence. An artefact that GRANTS a decision must carry the
    # evidence record that produced it, and the schema has no place for one yet — so a decision flag
    # here is, necessarily, an assertion nobody can check. Fail closed rather than render prose from
    # it. (`claim_policy.granted()` would refuse to unlock the language anyway; this raises at the
    # artefact boundary so the contradiction is reported where it can be fixed.)
    if any(status.decision_flags.values()):
        raise ValueError(
            "the artefact's inferential status grants %s, but carries no verifiable evidence "
            "record; a decision must be DERIVED by "
            "`inferential_evidence.verify_inferential_evidence` from a registered procedure and "
            "the archived result, not declared in the artefact"
            % ", ".join(n for n, ok in status.decision_flags.items() if ok))
    return estimand, status


def endpoint_row(ep: dict, m_target_g: float) -> dict:
    """Select an endpoint row by its structured key, never by list position."""
    for row in ep["rows"]:
        if float(row[TC.ENDPOINT_ROW_KEY]) == float(m_target_g):
            return row
    raise KeyError("no endpoint row at %r g" % m_target_g)


def scheme_interval(row: dict, scheme: str) -> dict:
    return row["resampling"][scheme]["interval"]


def _g(value: float) -> str:
    return ("%g" % float(value))


def _md_cell(text: str) -> str:
    """Escape a value for a Markdown table cell.

    Canonical cluster ids are pipe-delimited (`Arabica|93.4|9`), and an unescaped pipe silently
    splits the row into extra columns — a rendering corruption that survives every value-level
    check because the numbers in it are all correct.
    """
    return str(text).replace("|", "\\|")


# ─────────────────────────────────────────────────────────────────────────────────────────────
# Block builders
# ─────────────────────────────────────────────────────────────────────────────────────────────

def block_transfer_methods(ep, corpus_art, loss) -> str:
    """General Methods, resampling. Round-8 P0-2: this said TWO schemes and named the wrong one
    primary; it is now rendered from the archived design object, so it cannot drift again."""
    design = ep["resampling_design"]
    manifest = ep["corpus"]
    prim = design["schemes"][TC.PRIMARY_SCHEME]
    sizes = prim["cluster_size_distribution"]
    six, three = sizes.get("6", 0), sizes.get("3", 0)
    row40 = endpoint_row(ep, HEADLINE_ENDPOINT_G)
    meta = row40["resampling"][TC.PRIMARY_SCHEME]
    audit = TS.find_exact_audit(ep, TS.AUDITED_TARGET)

    return "\n".join([
        stamp(manifest),
        "",
        "*Resampling.* For each held-out coarse/fine solute observation we form the **paired** "
        "difference between the frozen mechanistic loss and the frozen O-trained level-only "
        "comparator loss. Both predictors are fixed before any C/F response is scored and neither "
        "is refitted inside the resampling, so the resulting percentile intervals are "
        "**fixed-predictor clustered sensitivity ranges**, not calibrated confidence intervals. "
        "Whole clusters are drawn with replacement within their declared strata, every "
        "observation in a drawn cluster is retained, and model and comparator losses always move "
        "together because the paired difference is formed per observation before any draw. The "
        f"canonical run uses \\(B={_tex_int(meta['B'])}\\) draws at seed {meta['seed']} with the "
        f"{meta['rng']} generator and the {meta['quantile_method']} quantile convention at the "
        f"{meta['quantile_probabilities'][0]}/{meta['quantile_probabilities'][1]} percentiles.",
        "",
        f"**{_WORDS[len(TC.SCHEME_ORDER)]} cluster schemes** are reported, not two. The pre-declared "
        f"**primary** scheme resamples `{TC.PRIMARY_SCHEME}` — (variety, temperature, pressure) "
        f"conditions drawn within variety. The complete corpus contains "
        f"**{prim['n_clusters']} such clusters**, and they are **not** uniformly sized: "
        f"**{six} contain both a coarse and a fine sample record** for all three named solutes "
        f"(six observations each), while **{three} off-grid clusters contain one grind only** "
        f"(three observations each). This construction deliberately keeps same-condition "
        "cross-solute outcomes together and, where both grinds exist, additionally couples the "
        "distinct C and F sample records. It is a **conservative dependence assumption**, not the "
        "design's uniquely identified experimental unit: C and F at a shared nominal condition "
        "are separate espresso samples, and the source does not identify them as replicates of "
        "one unit. It is retained as primary for that pre-declared reason and not because of "
        "where its range falls relative to zero. Three secondary schemes are reported alongside "
        "it: " + ", ".join(
            f"`{n}` ({design['schemes'][n]['n_clusters']} clusters)"
            for n in TC.SCHEME_ORDER if n != TC.PRIMARY_SCHEME) + ". Every scheme covers the same "
        f"{manifest['n_observations']} observations and yields the same point estimate; only the "
        "range differs. Exact cluster keys, strata, counts and size distributions are in "
        "Supplementary Table S6, and per-scheme membership is archived in "
        "`PAPER_A_ENDPOINT_PROPAGATION.json`.",
        "",
        "Because the paper's headline range has a bound within hundredths of a percentage point "
        f"of zero, the Monte Carlo resolution of that bound is audited directly, for **one exactly "
        f"specified target** — {TS.AUDITED_TARGET.prose} — over {audit['n_runs']} independent "
        f"seeds at \\(B={_tex_int(audit['B_per_seed'])}\\) each. At the canonical draw count the "
        f"implied lower- and upper-bound Monte Carlo standard errors are "
        f"{audit['lower_monte_carlo_se_at_canonical_B_pp']:.6f} and "
        f"{audit['upper_monte_carlo_se_at_canonical_B_pp']:.6f} pp. Three decimals are retained in "
        "the reported ranges to distinguish a small non-zero bound from exact contact with zero, "
        "but the final displayed digit should not be read as seed-invariant. Monte Carlo quantile "
        "error depends on the resampling distribution and its local tail density, so this estimate "
        "is **not** transferred to the other endpoints, to the secondary schemes, or to the "
        "alternative fitting loss, none of which was separately audited. It measures numerical "
        "approximation of one resampling distribution; it confers no coverage interpretation. "
        "The held-out-error interval is a separate procedure: it resamples the nine "
        "temperature–pressure **conditions** with replacement, refits level and rate on the "
        "in-bag conditions and scores the out-of-bag conditions, with **600** draws at seed 0 of "
        "which **599** are effective (one draw left no condition out of bag). Its estimand is "
        "held-out error at an out-of-bag fraction of roughly three to four conditions in nine, "
        "which is **not** the single-condition leave-one-out estimand.",
    ])


def block_transfer_results(ep, corpus_art, loss) -> str:
    """Results: the complete-corpus comparison, the dependence discussion and the knife-edge."""
    manifest = ep["corpus"]
    design = ep["resampling_design"]
    row = endpoint_row(ep, HEADLINE_ENDPOINT_G)
    prim_i = scheme_interval(row, TC.PRIMARY_SCHEME)
    audit = TS.find_exact_audit(ep, TS.AUDITED_TARGET)
    prim = design["schemes"][TC.PRIMARY_SCHEME]
    sizes = prim["cluster_size_distribution"]
    estimand, _status = validated_analysis(ep)

    def rng_text(scheme):
        return scheme_interval(row, scheme)["display"]["text"]

    def width(scheme):
        return scheme_interval(row, scheme)["width_pp"]

    prim_w = width(TC.PRIMARY_SCHEME)
    lines = [
        stamp(manifest),
        "",
        f"Treating the {manifest['n_observations']} held-out observations as the **dependent** "
        f"observations they are, a **paired clustered resampling** of the model-minus-comparator "
        f"loss gives a sensitivity range on the pooled ΔMAPE of **{prim_i['display']['text']} pp** "
        f"under the pre-declared primary unit, the **(variety, temperature, pressure) condition**.",
        "",
        f"That unit is a deliberately **conservative** choice rather than the design's "
        f"demonstrated dependence structure. Of its {prim['n_clusters']} clusters, "
        f"**{sizes.get('6', 0)} hold both held-out grinds** — all three named solutes at both C "
        f"and F, six observations moving together — while **{sizes.get('3', 0)} off-grid clusters "
        f"hold one grind only** and move three. The dependency the source establishes most "
        f"directly is the shared coffee sample behind three co-measured solutes, not the pairing "
        f"of a coarse and a fine sample at a shared nominal condition; those are separate "
        f"espresso samples. We therefore also report a **sample-record** scheme (one cluster per "
        f"sample record, "
        f"{design['schemes']['sample_in_variety_grind']['n_clusters']} clusters, drawn within "
        f"variety × grind), which gives **{rng_text('sample_in_variety_grind')} pp**. The complete membership of the held-out corpus — every sample record, its condition, its grind and its primary cluster — is published as Supplementary Table S7.",
        "",
        f"Two coarser constructions complete the bracket. Resampling conditions separately within "
        f"each variety × solute group — which lets caffeine, trigonelline and 5-CQA draw "
        f"*different* conditions from the same variety, breaking cross-solute dependence — gives "
        f"**{rng_text('cond_in_group')} pp**; resampling whole variety × solute groups "
        f"({design['schemes']['group']['n_clusters']} clusters) gives **{rng_text('group')} pp**. "
        f"These do **not** all narrow the primary range: their widths are "
        + ", ".join(
            f"{width(n):.3f} pp (`{n}`)" for n in TC.SCHEME_ORDER if n != TC.PRIMARY_SCHEME)
        + f" against **{prim_w:.3f} pp** for the primary, so the whole-group scheme is in fact "
        f"**wider**. A single story in which dropping dependence manufactures precision does not "
        f"fit them, and we do not tell one; the schemes bracket plausible grouping assumptions "
        f"and none of them is selected or discarded for where its range falls.",
        "",
        f"The **practical size of the effect is the reportable result**: the pooled difference is "
        f"{TC.format_pp(row['paired_difference_pp'], 3, explicit_plus=False)} pp — negative "
        f"favours the {estimand.label_of[estimand.negative_favours]} — against pooled errors near "
        f"{TC.format_pct(row['pooled_model_mape'])}, and it is the *worse* predictor on "
        f"{row['n_model_worse_than_const']} of {row['n_points']} held-out observations. The "
        f"primary range's upper bound is "
        f"{TC.format_pp(prim_i['full_precision_pp']['upper'], 4)} pp — a magnitude three orders "
        f"below the errors both predictors carry. For this target — {TS.AUDITED_TARGET.prose} — its "
        f"**sign** is numerically settled: across {audit['n_runs']} independent seeds the "
        f"upper-bound Monte Carlo standard error at the canonical draw count is "
        f"{audit['upper_monte_carlo_se_at_canonical_B_pp']:.6f} pp, so the bound sits roughly "
        f"{abs(prim_i['full_precision_pp']['upper']) / audit['upper_monte_carlo_se_at_canonical_B_pp']:.0f} "
        f"standard errors above zero and the range genuinely contains zero rather than grazing it. "
        f"No equivalent audit exists for the other endpoints, the secondary schemes or the "
        f"alternative fitting loss, and this estimate is not extended to them. "
        f"Numerical resolution is not inferential resolution. We therefore make **no claim of "
        f"statistical distinguishability, non-distinguishability or equivalence** from these "
        f"ranges: they are fixed-predictor sensitivity ranges without calibrated coverage, and "
        f"neither a bound's sign nor its rounded contact with zero is treated as inferential "
        f"evidence.",
    ]
    return "\n".join(lines)


def block_endpoint_table(ep, corpus_art, loss) -> str:
    """Table 4a — the benchmark propagated through the declared collection tolerance."""
    manifest = ep["corpus"]
    audit = TS.find_exact_audit(ep, TS.AUDITED_TARGET)
    estimand, _status = validated_analysis(ep)
    out = [stamp(manifest), "",
           "**Table 4a. The transfer-versus-comparator benchmark propagated through the declared "
           "±2 g collection tolerance.** Ranges are the primary "
           f"`{TC.PRIMARY_SCHEME}` clustered percentile sensitivity ranges at the canonical draw "
           "count, not calibrated confidence intervals. The paired difference is "
           f"{estimand.prose}.", "",
           "| endpoint | model pooled MAPE (%) | level-only comparator (%) | paired difference (pp) "
           "| primary clustered percentile range (pp) | zero relation | model worse on |",
           "|---|---:|---:|---:|---:|---|---:|"]
    for row in ep["rows"]:
        m = float(row[TC.ENDPOINT_ROW_KEY])
        interval = scheme_interval(row, TC.PRIMARY_SCHEME)
        sem = TS.from_interval_record(interval)
        text = interval["display"]["text"]
        if m == float(TS.AUDITED_TARGET.endpoint_g):
            text += " †"
        cells = [f"{_g(m)} g", f"{row['pooled_model_mape']:.2f}",
                 f"{row['pooled_const_mape']:.2f}",
                 TC.format_pp(row["paired_difference_pp"], 3, explicit_plus=False),
                 text, sem.relation.prose,
                 f"{row['n_model_worse_than_const']} of {row['n_points']}"]
        if m == HEADLINE_ENDPOINT_G:
            cells = [f"**{c}**" for c in cells]
        out.append("| " + " | ".join(cells) + " |")
    out += ["",
            "† The retained multi-seed Monte Carlo audit applies to this row only — "
            f"{TS.AUDITED_TARGET.prose}. At the canonical draw count its lower- and upper-bound "
            f"standard errors are approximately "
            f"{audit['lower_monte_carlo_se_at_canonical_B_pp']:.6f} and "
            f"{audit['upper_monte_carlo_se_at_canonical_B_pp']:.6f} pp. The other endpoints' "
            "canonical ranges were computed identically but their Monte Carlo precision was not "
            "separately audited, and this estimate is not transferred to them."]
    return "\n".join(out)


def relation_sweep_prose(labelled) -> str:
    """Name which endpoints sit BELOW zero, which CONTAIN it, and which sit ABOVE it.

    Round-10 (second review) P1-1. This replaces a two-list construction built from the archived
    containment boolean. The grouping now comes from the typed relation, so all three geometries are
    named explicitly rather than one being inferred as "not the other" — a distinction that costs
    nothing today, because no Paper A range is wholly positive, and that is exactly why leaving it
    implicit was a latent defect rather than a visible one.
    """
    groups = TS.group_by_relation(labelled)
    parts = [("%s at %s" % (relation.prose, _and_list(labels)))
             for relation, labels in groups.items() if labels]
    if not parts:
        raise ValueError("no endpoint intervals to describe")
    if len(parts) == 1:
        return parts[0]
    return "%s, and %s" % (", ".join(parts[:-1]), parts[-1])


def block_endpoint_reading(ep, corpus_art, loss) -> str:
    """The endpoint interpretation. Carries the artefact's structured interpretation code, which
    is what the release gate binds instead of a magic phrase (round-8 P0-3).

    Round-10 (second review) P0-1. This block used to open "Two things follow, and they agree" and
    close by combining a small point difference, a roughly even win/loss split and a zero-containing
    range into one "unresolved throughout" verdict. Two of those readings were asymmetric: a
    zero-containing range was treated as conceding no advantage, while the wholly negative ranges at
    38 g and under every secondary scheme were set aside as non-inferential. By the paper's own rule
    both are non-inferential, so the three observations are now kept SEPARATE and the permitted
    inference is stated once, from the declared inferential status.
    """
    sens = ep["endpoint_sensitivity"]
    lo, hi = sens["point_difference_magnitude_range_pp"]
    alt = [r for r in loss["rows"] if r["alt_loss"]][0]
    base = [r for r in loss["rows"] if not r["alt_loss"]][0]

    rows = sorted(({float(r[TC.ENDPOINT_ROW_KEY]): r for r in ep["rows"]}).items())
    prim = [scheme_interval(r, TC.PRIMARY_SCHEME) for _m, r in rows]
    uppers = [i["full_precision_pp"]["upper"] for i in prim]
    prim_sem = [TS.from_interval_record(i) for i in prim]
    labelled = list(zip((m for m, _r in rows), prim_sem))
    loss_sem = [TS.from_interval_record(base["interval"]),
                TS.from_interval_record(alt["interval"])]
    estimand, status = validated_analysis(ep)
    best, worst = TS.favourable_extremes(prim_sem, estimand)
    audit = TS.find_exact_audit(ep, TS.AUDITED_TARGET)

    return "\n".join([
        f"<!-- paper-a:endpoint-interpretation code={sens['interpretation_code']} -->",
        "",
        "Three observations should be kept separate: the size of the observed effect, the position "
        "of the sensitivity boundary, and what the procedure permits us to infer from either.",
        "",
        f"**The observed effect size is stable.** The paired difference spans "
        f"{TC.format_pp(lo, 3, explicit_plus=False)} to {TC.format_pp(hi, 3, explicit_plus=False)} pp, a "
        f"spread of {abs(hi - lo):.3f} pp — an order of magnitude smaller than the ≈5 pp movement "
        "the same endpoint range produces in the blind optimal-grind residual. That contrast is "
        "the expected one: those are different estimands, and here both predictors are re-derived "
        "at each endpoint, so a shift common to both cancels. The sign never changes, and the "
        "model remains worse on roughly half the held-out observations at every endpoint. Those two "
        "facts are not in tension: a predictor can lower a pooled mean through fewer but larger "
        "improvements while losing narrowly on more individual observations.",
        "",
        f"**The position of the boundary moves with the endpoint.** At the canonical draw count the "
        f"primary clustered range {relation_sweep_prose(labelled)}. The three upper bounds are "
        f"{_and_list_pp(uppers)} pp: they differ from one another, and from zero, by less than a "
        f"twentieth of a percentage point, against pooled errors near 8.4 % in both arms. Whether "
        "such a bound falls just inside or just outside zero follows from the clustering assumption "
        "and the endpoint, not from any measurement of skill. The same holds across fitting losses: "
        "refitting both predictors under a log/relative-error level fit moves the paired difference "
        f"only from {TC.format_pp(base['paired_difference_pp'], 3, explicit_plus=False)} to "
        f"{TC.format_pp(alt['paired_difference_pp'], 3, explicit_plus=False)} pp, and the "
        f"loss-specific ranges {TS.describe_shared_relation(loss_sem)}.",
        "",
        f"**What follows is narrower than either observation suggests.** Because the estimand is "
        f"{estimand.contrast_label} in {estimand.units_label}, {estimand.direction_clause}: across "
        f"the sweep the most favourable bound is {TC.format_pp(best, 3, explicit_plus=False)} pp and "
        f"the least favourable is {TC.format_pp(worst)} pp, so the least favourable extreme lies "
        f"on the other side of zero. {CP.limits_sentence(status, estimand)} That applies symmetrically: the "
        f"wholly negative ranges do not establish an advantage, and the zero-containing ranges do "
        f"not establish its absence. We therefore do not convert a percentile bound's position into "
        f"an inequality that carries the conclusion. Per-endpoint values, under every declared "
        f"cluster scheme, are Supplementary Table S3.",
    ])


def block_table5(ep, corpus_art, loss) -> str:
    """Table 5 — every resampling quantity in the paper, by estimand."""
    row = endpoint_row(ep, HEADLINE_ENDPOINT_G)
    design = ep["resampling_design"]
    estimand, _status = validated_analysis(ep)
    pe = row["resampling"][TC.PRIMARY_SCHEME]["observed_mean_delta_pp"]
    out = [
        stamp(ep["corpus"]), "",
        "**Table 5. Resampling quantities used in this paper, by estimand.** These are numerically "
        "similar, easily conflated, and do not estimate the same target; the out-of-bag refit "
        f"interval is *not* an uncertainty interval for the "
        f"{TC.format_pp(pe, 3, explicit_plus=False)} pp model-minus-comparator "
        f"difference. The paired estimand is {estimand.prose}.", "",
        "| analysis | resampling unit | fit repeated? | held-out fraction | estimand | point "
        "estimate | percentile range | inferential status |",
        "|---|---|---|---|---|---|---|---|",
    ]
    notes = {
        "cond_in_variety": ("clustered percentile **sensitivity range**; not a calibrated CI; "
                            "pre-declared **conservative** unit, not the demonstrated one"),
        "sample_in_variety_grind": ("sensitivity only; the clearest source-established dependence "
                                    "(three solutes per coffee sample)"),
        "cond_in_group": "sensitivity only; does not preserve cross-solute condition dependence",
        "group": "sensitivity only; 6 clusters, so a coarse and highly discrete stress test",
    }
    for name in TC.SCHEME_ORDER:
        s = design["schemes"][name]
        i = scheme_interval(row, name)
        label = ("paired clustered resampling of model-minus-comparator loss (**primary**)"
                 if name == TC.PRIMARY_SCHEME else f"the same, resampling `{name}` (secondary)")
        out.append("| %s | %s (%d clusters) | no | n/a — fixed predictors | %s | %s pp | %s pp "
                   "| %s |"
                   % (label, s["label"], s["n_clusters"], estimand.short_contrast_label,
                      TC.format_pp(pe, 3, explicit_plus=False), i["display"]["text"],
                      notes[name]))
    out += [
        "| residual resampling of LOCO fold errors | individual fold error | no | 1 of 9 | "
        "descriptive spread of computed LOCO errors | 6.5 % | [5.0, 8.2] % | **descriptive "
        "fold-resampling range**; ignores fold dependence |",
        "| condition-level resampling of LOCO macro errors | (T,p) condition (9) | no | 1 of 9 | "
        "descriptive spread of computed LOCO errors | 6.5 % | [5.1, 8.3] % | descriptive "
        "fold-resampling range |",
        "| condition-cluster out-of-bag refit | (T,p) condition (9) | **yes** | ~3–4 of 9 | model "
        "held-out MAPE at a larger held-out fraction | 7.4 % | [4.3, 11.5] % | **out-of-bag refit "
        "percentile interval**; coverage not demonstrated |",
        "| leave-one-condition-out CV | (T,p) condition (9) | yes | 1 of 9 | model held-out MAPE | "
        "6.5 % (median 5.2 %) | — | point estimate |",
    ]
    return "\n".join(out)


def block_transfer_caption(ep, corpus_art, loss) -> str:
    """Figure 3's standalone caption — the round-8 P0-1 blocker.

    Round-11 P1-3. This caption is uploaded as a separate file and its own header says captions are
    written to stand alone, so it is read by people who never see §4. It said its ranges were "not
    calibrated confidence intervals" and stopped there — which states what the ranges ARE NOT
    without stating what they therefore cannot DECIDE. Standing alone, "pooled MAPE is 8.44 % versus
    8.83 %" then reads as a demonstrated advantage.

    The decision boundary and the transfer boundary are generated from the same renderers the
    manuscript uses, not paraphrased here: a caption that quietly weakens the caveat is the round-8
    defect (a standalone caption still quoting a superseded benchmark) in its editorial form.

    Round-12 P2-2. Carrying all four propositions made it a 287-word mini-review — accurate,
    self-contained, and no longer functioning as a caption. It duplicated Results and Methods
    material and buried the panel-reading instructions. Cut to ~200 words by removing the
    near-optimal-rate envelope mechanics and the lookup-support detail (both in the main text), and
    by tightening the prose — not by dropping any of the four propositions, which is what made the
    caption long and is also the reason it is trustworthy alone.
    """
    cc = corpus_art["complete_corpus"]
    mg = corpus_art["matched_on_grid"]
    manifest = cc["corpus"]
    estimand, status = validated_analysis(ep)
    return "\n".join([
        stamp(manifest),
        "",
        "**Figure 3. Within-campaign cross-grind prediction after target-specific calibration.** "
        "For each variety–solute group, inventory and rate were fitted to the nine optimal-grind "
        f"conditions and frozen for coarse/fine prediction at the matched "
        f"{_g(HEADLINE_ENDPOINT_G)} g endpoint. Panels compare observed and predicted "
        "concentrations by condition and summarize error by target grind. The comparator is an "
        "O-trained level-only constant: one concentration level, with no temperature, pressure, "
        "flow or kinetic response. The plotted comparison is the **complete held-out coarse/fine "
        f"corpus** — {manifest['n_held_out_records']} sample records × "
        f"{manifest['n_solutes']} named solutes = **{manifest['n_observations']} observations**, "
        f"including the {manifest['n_off_grid_records']} off-grid records. Pooled MAPE is "
        f"**{TC.format_pct(cc['pooled_model_mape'])}** for the mechanistic model versus "
        f"**{TC.format_pct(cc['pooled_const_mape'])}** for the constant — an observed paired "
        f"difference of "
        f"**{TC.format_pp(cc['paired_difference_pp'], 3, explicit_plus=False)} "
        f"{estimand.units_label}** ({estimand.short_contrast_label}), which favours the "
        f"{estimand.label_of[estimand.negative_favours]} — and the model has the larger absolute "
        f"percentage error on **{cc['n_model_worse_than_const']} of {cc['n_points']}** "
        f"observations. The {mg['corpus']['n_observations']}-observation matched-grid subset is "
        "secondary and supplies the lookup comparator. "
        f"{CP.limits_sentence_short(status, estimand)} "
        "Acceptable endpoint accuracy alone does not establish transfer of the kinetic mechanism. "
        "Evidence tier: within-campaign cross-grind holdout against a trained level-only "
        "comparator.",
    ])


def block_transfer_headline(ep, corpus_art, loss) -> str:
    """The Results paragraph that states the paper's principal quantitative comparison.

    Round-10 P0-1. This paragraph used to close "Acceptable endpoint accuracy therefore did not
    supply resolvable skill beyond a transferred concentration level" — a property-level negative
    verdict, from an analysis the Methods two pages earlier describe as having no calibrated
    coverage and supporting no distinguishability, non-distinguishability or equivalence claim. The
    point estimate favours the model; what is unestablished is whether that advantage is
    reproducible or useful.

    Round-12 P0-1. That round-10 correction landed everywhere EXCEPT here, and this is the
    principal quantitative claim surface. The paragraph closed "The observed advantage is therefore
    **small**" — a practical-magnitude verdict, from an analysis that says two sentences earlier
    that its ranges are uncalibrated and that no margin was predeclared — while this docstring
    asserted the sentence "now says exactly" what is unestablished. The docstring described the
    intention; the string carried the defect, and the scanner missed it because `therefore` sits
    between the noun and the adjective.

    Two lessons are worth keeping. Generating a sentence does not make it permissible: the generator
    is a source of text, not evidence about the text, so generated blocks are now scanned before
    insertion as well as after (see `check_blocks`). And a magnitude adjective is not made safe by
    the caveat that follows it — "small, and this analysis does not establish whether it is
    reproducible" asserts the magnitude and disclaims only the inference.
    """
    row = endpoint_row(ep, HEADLINE_ENDPOINT_G)
    i = scheme_interval(row, TC.PRIMARY_SCHEME)
    verb = TS.from_interval_record(i).relation.prose
    estimand, _status = validated_analysis(ep)
    favoured = estimand.label_of[estimand.negative_favours]
    bg = corpus_art["complete_corpus"]["pooled_by_grind"]
    return "\n".join([
        stamp(ep["corpus"]),
        "",
        "**Level-only comparator: absolute error alone does not establish transfer skill.** "
        "This is the paper's principal quantitative result, so we state it first. Against an "
        "**optimal-grind-trained MAPE-optimal constant**, the mechanistic model's pooled held-out "
        f"MAPE is **{TC.format_pct(row['pooled_model_mape'])}** versus "
        f"**{TC.format_pct(row['pooled_const_mape'])}** for the constant — a paired difference of "
        f"**{TC.format_pp(row['paired_difference_pp'], 3, explicit_plus=False)} percentage "
        f"points**, which favours the {favoured}. Its primary clustered percentile **sensitivity "
        f"range** — not a calibrated confidence interval — is **{i['display']['text']} pp** and "
        f"{verb}, and the mechanistic model is **worse on "
        f"{row['n_model_worse_than_const']} of {row['n_points']} held-out observations**. "
        "Because the reported ranges are "
        "uncalibrated and no practical margin was predeclared, this analysis does not establish "
        "that the observed advantage is reproducible or practically useful, and it does not "
        "establish that the advantage is absent: acceptable endpoint accuracy does not by itself "
        "establish transfer of the kinetic mechanism beyond a transferred concentration level.",
        "",
        # Domain-referee Major finding 1. The pooled figure hides a SIGN FLIP: the model beats the
        # constant on the coarse grind and is worse than it on the fine grind. Neither number
        # appeared anywhere in the manuscript or supplement, so a reader could only see the average
        # of two opposite results. Generated from the archived corpus contract so it cannot drift.
        f"**The pooled figure averages two opposite results.** By target grind, pooled MAPE is "
        f"**{TC.format_pct(bg['C']['model_mape'])}** for the mechanistic model against "
        f"**{TC.format_pct(bg['C']['const_mape'])}** for the constant on **coarse** "
        f"({TC.format_pp(bg['C']['model_mape'] - bg['C']['const_mape'], 2, explicit_plus=False)} "
        f"pp, favouring the model), and **{TC.format_pct(bg['F']['model_mape'])}** against "
        f"**{TC.format_pct(bg['F']['const_mape'])}** on **fine** "
        f"({TC.format_pp(bg['F']['model_mape'] - bg['F']['const_mape'], 2)} pp, favouring the "
        f"**constant**). The whole of the pooled advantage comes from the coarse grind; on the fine "
        f"grind the mechanistic model is the worse predictor. Per variety–solute group the gain is "
        f"similarly concentrated rather than general (Supplementary Table S3).",
        "",
        # Domain-referee Major finding 1: the level-only constant is a minimal ablation, and the
        # comparison against it confounds mechanistic structure with having ANY condition response.
        f"**A non-mechanistic response closes part of the gap.** The level-only constant carries no "
        f"temperature, pressure, flow or kinetic response, so the contrast above measures the value "
        f"of the mechanistic structure *and* the value of any condition dependence together. "
        f"Against a low-degree empirical response fitted only to the same nine optimal-grind "
        f"conditions — selected by leave-one-condition-out cross-validation and frozen before any "
        f"held-out record was scored — pooled MAPE is **8.69 %**, so the mechanistic model's margin "
        f"falls from **−0.394 pp** to **−0.251 pp**. That baseline still receives less information "
        f"than the mechanistic arm, which additionally gets a target-grind hydraulic map, so the "
        f"remaining margin is an upper bound on the value of the mechanistic structure. The panel "
        f"is a locked sensitivity analysis, not a prospectively registered plan.",
    ])


def block_loss_robustness(ep, corpus_art, loss) -> str:
    """The comparator-loss paragraph. Round-8 P1-2 retired its 'lands on opposite sides of zero'
    reading, which was an artefact of the superseded low draw count."""
    base = [r for r in loss["rows"] if not r["alt_loss"]][0]
    alt = [r for r in loss["rows"] if r["alt_loss"]][0]
    # Round-9 P0-1. This read `same_side = (base.contains_zero == alt.contains_zero)` and rendered
    # True == True as "both lie on the same side of zero". Both intervals CONTAIN zero — they do not
    # lie on a side of it. The relation is now named from the typed trinary classification.
    sem = [TS.from_interval_record(base["interval"]), TS.from_interval_record(alt["interval"])]
    return "\n".join([
        stamp(ep["corpus"]),
        "",
        "Refitting **both** the mechanistic model and the level-only comparator under the same "
        "log/relative-error level fit, and scoring both under the same rule, the paired "
        f"model-minus-comparator difference moves from "
        f"**{TC.format_pp(base['paired_difference_pp'], 3, explicit_plus=False)} pp** to "
        f"**{TC.format_pp(alt['paired_difference_pp'], 3, explicit_plus=False)} pp** (pooled "
        f"{TC.format_pct(alt['pooled_model_mape'])} versus "
        f"{TC.format_pct(alt['pooled_const_mape'])}; the model worse on "
        f"{alt['n_model_worse_than_const']} of {alt['n_points']} observations under either loss). "
        f"The primary clustered percentile range is {base['interval']['display']['text']} under "
        f"the primary loss and {alt['interval']['display']['text']} under the alternative, and at "
        f"the canonical draw count {TS.describe_shared_relation(sem)}. The fitting loss therefore "
        "does not materially change the point estimate, the zero relation, or the practical "
        "reading. It is that comparison, not the mechanistic model's own error, that establishes "
        "the verdict is not an artefact of the fitting loss.",
    ])


def relative_mape_reduction_pct(row: dict) -> float:
    """``100 x (comparator − model) / comparator``, from FULL-PRECISION pooled MAPE values.

    Round-10 P0-1 asked for Supplementary Table S3's final column — headed ``skill``, with no
    definition anywhere — to be defined or removed. "Skill" is the disputed word: it is the noun the
    retired "no resolvable skill" verdict was about, and an undefined column of 0.045 invites the
    reader to treat a descriptive error reduction as an inferential quantity.

    So the column is renamed for what it is and computed here rather than read from the artefact's
    ``skill_vs_const`` field, which is rounded to three decimals as a FRACTION. Computing a
    percentage from the rounded fraction would quantise the column to 0.1 pp steps; computing it
    from the rounded 8.44/8.83 table cells would differ again. Positive values favour the model.
    """
    model = float(row["pooled_model_mape"])
    comparator = float(row["pooled_const_mape"])
    if comparator == 0.0:
        raise ZeroDivisionError("a relative reduction against a zero comparator error is undefined")
    return 100.0 * (comparator - model) / comparator


def block_supplement_endpoint_table(ep, corpus_art, loss) -> str:
    """Supplementary Table S3 — the full per-endpoint sweep across all four schemes."""
    manifest = ep["corpus"]
    audit = TS.find_exact_audit(ep, TS.AUDITED_TARGET)
    estimand, status = validated_analysis(ep)
    out = [
        stamp(manifest), "",
        "Corpus: %s, %d held-out records × %d named solutes = %d observations. No coarse/fine "
        "record is excluded. Held-out record identifiers: %s."
        % (manifest["estimand"], manifest["n_held_out_records"], manifest["n_solutes"],
           manifest["n_observations"], ", ".join(manifest["held_out_sample_ids"])),
        "",
        "| endpoint | model pooled MAPE (%) | comparator (%) | paired difference (pp) | "
        + " | ".join("%s (pp)" % n for n in TC.SCHEME_ORDER)
        + " | primary zero relation | model worse on | relative pooled-MAPE reduction (%) |",
        "|---|---:|---:|---:|" + "---:|" * len(TC.SCHEME_ORDER) + "---|---:|---:|",
    ]
    for row in ep["rows"]:
        ranges = " | ".join(scheme_interval(row, n)["display"]["text"] for n in TC.SCHEME_ORDER)
        prim = TS.from_interval_record(scheme_interval(row, TC.PRIMARY_SCHEME))
        out.append("| %s g | %.2f | %.2f | %s | %s | %s | %d of %d | %.2f |"
                   % (_g(row[TC.ENDPOINT_ROW_KEY]), row["pooled_model_mape"],
                      row["pooled_const_mape"],
                      TC.format_pp(row["paired_difference_pp"], 3, explicit_plus=False),
                      ranges, prim.relation.prose,
                      row["n_model_worse_than_const"], row["n_points"],
                      relative_mape_reduction_pct(row)))

    diffs = [r["paired_difference_pp"] for r in ep["rows"]]
    prim_sem = [TS.from_interval_record(scheme_interval(r, TC.PRIMARY_SCHEME))
                for r in ep["rows"]]
    by_relation: dict[str, list[str]] = {}
    for r, s in zip(ep["rows"], prim_sem):
        by_relation.setdefault(s.relation.prose, []).append(_g(r[TC.ENDPOINT_ROW_KEY]) + " g")
    def _eps(items):
        return items[0] if len(items) == 1 else "%s and %s" % (", ".join(items[:-1]), items[-1])

    relation_text = "; ".join("%s at %s" % (rel, _eps(eps))
                              for rel, eps in sorted(by_relation.items()))
    # Round-9 P0-1: favourability comes from the declared estimand direction, not from assuming
    # the upper bound bounds the advantage. Negative model-minus-comparator favours the model, so
    # the smallest LOWER bound is the most favourable value and the largest UPPER bound the least.
    # Round-10 P1-2: that direction is now DERIVED from the artefact's typed estimand, not from a
    # module-level default this call used to fall back on.
    best, worst = TS.favourable_extremes(prim_sem, estimand)
    out += ["", "**Reading.** The effect size is stable: %s to %s pp across 38, 40 and 42 g, a "
                "spread of %.3f pp — an order of magnitude smaller than the ≈ 5 pp movement in the "
                "blind optimal-grind residual over the same endpoints, which is what one expects "
                "when both predictors are re-derived at each endpoint so that a shift common to "
                "both cancels. The sign never changes and the model remains worse on roughly half "
                "the held-out observations at every endpoint. At the canonical draw count the "
                "primary clustered range %s. Because the estimand is %s in %s, %s: across the "
                "sweep the most favourable bound is %s pp and the least favourable is %s pp, so at "
                "their "
                "unfavourable end these ranges concede the model no advantage at all. %s The final "
                "column is a descriptive relative error reduction, "
                "100 x (comparator − model) / comparator computed from the full-precision pooled "
                "values, not an inferential measure; positive values favour the mechanistic model."
                % (TC.format_pp(min(diffs), 3, explicit_plus=False),
                   TC.format_pp(max(diffs), 3, explicit_plus=False),
                   abs(max(diffs) - min(diffs)), relation_text, estimand.contrast_label,
                   estimand.units_label, estimand.direction_clause,
                   TC.format_pp(best, 3, explicit_plus=False), TC.format_pp(worst),
                   CP.limits_sentence(status, estimand)),
            "",
            "**Scope of the Monte Carlo audit.** All displayed ranges use the canonical draw "
            "count. A multi-seed estimate of Monte Carlo variability exists for **one** target "
            "only — %s — where the lower- and upper-bound standard errors are approximately "
            "%.6f and %.6f pp and the upper bound's sign is %s across %d independent seeds. The "
            "38 g and 42 g bounds, the three secondary schemes and the alternative fitting loss "
            "were **not** separately audited, and none of them inherits that value; only the "
            "multi-seed precision audit is absent, not the canonical range itself. The audit "
            "measures numerical approximation and confers no coverage interpretation."
            % (TS.AUDITED_TARGET.prose,
               audit["lower_monte_carlo_se_at_canonical_B_pp"],
               audit["upper_monte_carlo_se_at_canonical_B_pp"],
               "stable" if audit["upper_bound_sign_is_stable"] else "NOT stable",
               audit["n_runs"])]
    return "\n".join(out)


def block_supplement_scheme_table(ep, corpus_art, loss) -> str:
    """Supplementary table: the resampling design, one row per scheme."""
    design = ep["resampling_design"]
    row = endpoint_row(ep, HEADLINE_ENDPOINT_G)
    out = [
        stamp(ep["corpus"]), "",
        # Round-10 (second review) P2-1: this said "Cluster keys, strata and membership for every
        # declared scheme". The table has eight columns and none of them is a member identifier;
        # Table S7 lists the 44 sample records with their PRIMARY cluster only. Exact per-scheme
        # membership exists, but in the archived artefact, and the caption now says where.
        "**Table S6. Resampling design.** Cluster keys, strata, cluster census, ranges and widths "
        "for every declared scheme, at the canonical draw count. Exact cluster-by-cluster "
        "membership under every scheme — the sample records, grinds and named-solute observations "
        "in each cluster — is archived in the machine-readable endpoint-propagation record rather "
        "than reproduced here; Table S7 lists the held-out records with their primary cluster. "
        "Predictors are fixed in every scheme: no model, level parameter or comparator is refitted "
        "inside a draw.", "",
        "| scheme | role | strata | cluster key | clusters | cluster sizes (obs × n) | "
        f"range at {_g(HEADLINE_ENDPOINT_G)} g (pp) | width (pp) |",
        "|---|---|---|---|---:|---|---|---:|",
    ]
    for name in TC.SCHEME_ORDER:
        s = design["schemes"][name]
        i = scheme_interval(row, name)
        sizes = ", ".join(f"{k}×{v}" for k, v in s["cluster_size_distribution"].items())
        out.append("| `%s` | %s | %s | %s | %d | %s | %s | %.3f |"
                   % (name, s["role"].replace("_", " "),
                      ", ".join(s["strata"]) or "—",
                      ", ".join("`%s`" % k for k in s["cluster_key"]),
                      s["n_clusters"], sizes, i["display"]["text"], i["width_pp"]))
    audit = TS.find_exact_audit(ep, TS.AUDITED_TARGET)
    pp4 = lambda v: TC.format_pp(v, 4)                                            # noqa: E731
    out += ["", f"Monte Carlo audit of one target only — {TS.AUDITED_TARGET.prose}: "
                f"{audit['n_runs']} independent seeds at "
                f"B = {audit['B_per_seed']:,} each. Upper bound mean "
                f"{pp4(audit['upper_mean_pp'])} pp (SD {audit['upper_sd_pp']:.4f}, range "
                f"{pp4(audit['upper_min_pp'])} to {pp4(audit['upper_max_pp'])}); lower bound mean "
                f"{pp4(audit['lower_mean_pp'])} pp (SD {audit['lower_sd_pp']:.4f}). "
                # Round-10 (second review) P2-2: this read "The bound's sign is stable", immediately
                # after naming BOTH bounds, so the referent could be read as either. The archived
                # flag is `upper_bound_sign_is_stable` — upper-specific — and the noun is now tied to
                # it. A future lower-bound audit must add its own flag and its own sentence rather
                # than inheriting this one.
                f"The **upper** bound's sign is "
                f"{'stable' if audit['upper_bound_sign_is_stable'] else 'NOT stable'} "
                f"across seeds; no sign-stability flag is archived for the lower bound, which lies "
                f"far from zero. Implied Monte Carlo standard errors at the canonical "
                f"B = {audit['canonical_B']:,} are "
                f"{audit['lower_monte_carlo_se_at_canonical_B_pp']:.6f} pp on the lower bound and "
                f"{audit['upper_monte_carlo_se_at_canonical_B_pp']:.6f} pp on the upper — reported "
                f"separately rather than as one symmetric figure, since they are two different "
                f"estimators. This is numerical approximation error only and confers no coverage "
                f"interpretation."]
    return "\n".join(out)


def block_supplement_corpus_manifest(ep, corpus_art, loss) -> str:
    """Supplementary table: all 44 held-out sample records and their design metadata."""
    manifest = ep["corpus"]
    out = [
        stamp(manifest), "",
        f"**Table S7. Held-out coarse/fine corpus membership.** All "
        f"{manifest['n_held_out_records']} sample records scored by the headline benchmark. Each "
        f"contributes the same {manifest['n_solutes']} named-solute observations "
        f"({', '.join(manifest['solutes'])}), giving {manifest['n_observations']} observations. "
        f"No record is excluded. The lookup comparator is undefined on the "
        f"{len(manifest['lookup_undefined_sample_ids'])} off-grid records, so it is reported only "
        f"on its own {manifest['n_lookup_observations']}-observation support.", "",
        "| sample | variety | grind | T (°C) | p (bar) | on grid? | lookup defined? | "
        "primary cluster |",
        "|---|---|---|---:|---:|---|---|---|",
    ]
    for r in manifest["records"]:
        out.append("| %s | %s | %s | %s | %s | %s | %s | `%s` |"
                   % (r["sample_id"], r["variety"], r["grind"], _g(r["temperature_degC"]),
                      _g(r["pressure_bar"]), "yes" if r["on_grid"] else "**no**",
                      "yes" if r["lookup_defined"] else "**no**",
                      _md_cell(r["primary_cluster_id"])))
    return "\n".join(out)


#: Which block goes in which file. A block may legitimately appear in more than one file (the
#: manuscript and its canonical working draft are held in content agreement by CI).
BLOCKS = {
    "paper-a:transfer-methods": (block_transfer_methods, (MANUSCRIPT, DRAFT)),
    "paper-a:transfer-headline": (block_transfer_headline, (MANUSCRIPT, DRAFT)),
    "paper-a:transfer-loss-robustness": (block_loss_robustness, (MANUSCRIPT, DRAFT)),
    "paper-a:transfer-results": (block_transfer_results, (MANUSCRIPT, DRAFT)),
    "paper-a:transfer-endpoint-table": (block_endpoint_table, (MANUSCRIPT, DRAFT)),
    "paper-a:transfer-endpoint-reading": (block_endpoint_reading, (MANUSCRIPT, DRAFT)),
    "paper-a:transfer-table5": (block_table5, (MANUSCRIPT, DRAFT)),
    "paper-a:transfer-caption": (block_transfer_caption, (CAPTIONS,)),
}


def render_all() -> dict[str, str]:
    ep, corpus_art, loss = _load(ENDPOINT_JSON), _load(CORPUS_JSON), _load(LOSS_JSON)
    return {name: fn(ep, corpus_art, loss) for name, (fn, _paths) in BLOCKS.items()}


def scan_rendered_blocks(rendered: dict[str, str]) -> list[str]:
    """Scan generated text against the claim policy BEFORE it is written into a manuscript.

    Round-12 P0-1. The principal Results block was emitting "The observed advantage is therefore
    small" — a practical-magnitude verdict from an analysis that declares no margin — and the
    checker only ever saw it after insertion, mixed in with everything else. Worse, the generator's
    own docstring asserted the sentence said the opposite.

    A generator is a source of text, not evidence about the text. Scanning here means a prohibited
    verdict fails at the point it is produced, names the block that produced it, and never reaches a
    file at all.
    """
    from puckworks.paper_a import claim_policy as CP

    ep = _load(ENDPOINT_JSON)
    _estimand, status = validated_analysis(ep)
    problems = []
    for name in sorted(rendered):
        problems += ["generated block %r would emit prohibited claim language: %s" % (name, p)
                     for p in CP.scan(rendered[name], status)]
    return problems


def run(write: bool) -> list[str]:
    problems: list[str] = []
    rendered = render_all()
    # Fail before writing, not after: a block that must not ship must not be written either.
    blocked = scan_rendered_blocks(rendered)
    if blocked:
        return blocked
    by_file: dict[Path, str] = {}
    for name, (_fn, paths) in BLOCKS.items():
        for path in paths:
            if not path.exists():
                problems.append("%s: missing file for block %r" % (path.name, name))
                continue
            text = by_file.get(path) or path.read_text(encoding="utf-8")
            try:
                current = extract_block(text, name)
            except KeyError as exc:
                problems.append("%s: %s" % (path.name, exc))
                continue
            if current.strip() == rendered[name].strip():
                continue
            if write:
                by_file[path] = replace_block(text, name, rendered[name])
            else:
                problems.append("%s: block %r is stale — run "
                                "`python tools/paper_a_transfer_text.py --write`"
                                % (path.name, name))
    if write and not problems:
        for path, text in by_file.items():
            path.write_text(text, encoding="utf-8")
    return problems


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--check", action="store_true")
    g.add_argument("--write", action="store_true")
    args = ap.parse_args(argv)
    problems = run(write=bool(args.write))
    if problems:
        print("Paper A transfer text FAILED (%s):" % ("write" if args.write else "check"),
              file=sys.stderr)
        for p in problems:
            print("  - %s" % p, file=sys.stderr)
        return 1
    print("Paper A transfer text OK (%s)." % ("write" if args.write else "check"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
