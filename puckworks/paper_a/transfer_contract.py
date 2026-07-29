"""Paper A transfer analysis — the one contract the producer, artefacts and prose answer to.

Round-8 P0-1..P1-4. The Round-8 review found the same defect in five different costumes: the
transfer result is *represented independently* in the producer, in three JSON artefacts, in the
manuscript, in the standalone captions, in the package record, in the release gate and in the
tests — and those representations drifted apart. A caption still quoted the superseded 108-point
benchmark; the Methods still named the superseded primary resampling unit; the release gate still
looked for a retired ``v_targets`` key it could never find.

This module is the fix's foundation. It owns, once:

  * the ENDPOINT contract — collected mass, in grams, at 38/40/42 g (never a volume);
  * the CORPUS manifest — which sample records the benchmark scored, canonically hashed, so a
    *different* set of 44 records cannot masquerade as the same corpus behind a matching count;
  * the RESAMPLING design — every cluster scheme's key, strata, role and membership, as data;
  * the INTERVAL representation — signed full-precision bounds, from which the analytical flags
    are derived, kept strictly apart from the display-rounded text;
  * the DISPLAY formatter — one renderer for every publication surface.

Nothing here does numerical work and nothing here writes files. The producer
(:mod:`puckworks.validation.slow.angeloni_bracket`) imports these definitions instead of
re-expressing them in docstrings and local literals; the artefact writer and the text generator
render from them; the tests assert against them.

Deliberately absent: any acceptance of a volume endpoint key. An artefact carrying ``v_targets``
is *rejected*, never silently coerced — coercion would convert a scientific unit error into an
ambiguous compatibility layer and hide exactly the defect Round 7 corrected.
"""

from __future__ import annotations

import hashlib
import json
from decimal import Decimal, ROUND_HALF_UP

#: Bump when a field's *meaning* changes, not when a value is regenerated. Consumers use this to
#: tell a corrected collected-mass artefact from an untyped legacy one.
#:
#: v3 (round-9 P1-1): the single top-level `stability_audit` scalar became a
#: `stability_audits` LIST keyed by exact target, because a Monte Carlo precision estimate
#: for one endpoint/scheme/loss is not a property of any other. Cluster ids for the
#: variety x solute schemes were also normalised to the pipe delimiter.
SCHEMA_VERSION = 3

# ─────────────────────────────────────────────────────────────────────────────────────────────
# Endpoint contract (round-8 P0-3)
# ─────────────────────────────────────────────────────────────────────────────────────────────

ENDPOINT_QUANTITY = "collected_mass"
ENDPOINT_SYMBOL = "m_target"
ENDPOINT_UNIT = "g"
ENDPOINT_ROW_KEY = "m_target_g"
ENDPOINT_TARGETS = (38.0, 40.0, 42.0)

#: The endpoint was analytically defined in MASS. These keys are from the retired volume contract
#: and must fail validation rather than be translated: 38 mL and 38 g are not the same quantity,
#: and a reader who sees a silent conversion cannot tell which one was actually solved.
RETIRED_ENDPOINT_KEYS = ("v_targets", "v_target_ml", "v_target_mL", "v_target_mls")


def endpoint_object() -> dict:
    """The typed endpoint declaration embedded in every transfer artefact."""
    return {
        "quantity": ENDPOINT_QUANTITY,
        "symbol": ENDPOINT_SYMBOL,
        "unit": ENDPOINT_UNIT,
        "targets": [float(v) for v in ENDPOINT_TARGETS],
    }


def endpoint_label() -> str:
    """Human-readable endpoint label for claim names and headings — derived, never retyped."""
    return "%s g" % "/".join(_trim(v) for v in ENDPOINT_TARGETS)


def _trim(value: float) -> str:
    return ("%f" % float(value)).rstrip("0").rstrip(".")


def validate_endpoint_contract(artifact: dict, require_rows: bool = True) -> list[str]:
    """Return a list of problems with an artefact's endpoint contract; empty means valid.

    Checks the top-level declaration AND, when ``require_rows``, the row-level representation.
    Checking only the target array lets a row keep a wrong key or unit; checking only rows lets the
    declaration lie.

    ``require_rows=False`` is for artefacts whose ``rows`` are indexed by something other than the
    endpoint — the comparator-loss artefact keys its two rows by fitting loss and evaluates them all
    at one endpoint, so it must satisfy the endpoint *declaration* without carrying one row per
    target.
    """
    problems: list[str] = []

    for key in RETIRED_ENDPOINT_KEYS:
        if key in artifact:
            problems.append(
                "artefact carries the retired volume-endpoint key %r; the endpoint is a "
                "collected MASS in grams and must be migrated explicitly, not coerced" % key)

    ep = artifact.get("endpoint")
    if not isinstance(ep, dict):
        problems.append("artefact has no typed `endpoint` object")
    else:
        if ep.get("quantity") != ENDPOINT_QUANTITY:
            problems.append("endpoint.quantity is %r, expected %r"
                            % (ep.get("quantity"), ENDPOINT_QUANTITY))
        if ep.get("unit") != ENDPOINT_UNIT:
            problems.append("endpoint.unit is %r, expected %r — the collected endpoint is a "
                            "mass, not a volume" % (ep.get("unit"), ENDPOINT_UNIT))
        if ep.get("symbol") != ENDPOINT_SYMBOL:
            problems.append("endpoint.symbol is %r, expected %r"
                            % (ep.get("symbol"), ENDPOINT_SYMBOL))
        targets = ep.get("targets")
        if [float(t) for t in (targets or [])] != [float(t) for t in ENDPOINT_TARGETS]:
            problems.append("endpoint.targets is %r, expected %r (exact set and order)"
                            % (targets, list(ENDPOINT_TARGETS)))

    if require_rows:
        problems += validate_endpoint_rows(artifact)
    return problems


def validate_endpoint_rows(artifact: dict) -> list[str]:
    """Require exactly the three complete endpoint result rows. **Fails closed.**

    Round-9 P1-2. This check used to be guarded by

        if isinstance(rows, list) and rows and ENDPOINT_ROW_KEY in (rows[0] or {}):

    so every way of making the rows *absent* skipped validation entirely and the contract returned
    a clean bill of health. All four of these were demonstrated false greens: deleting `rows`,
    setting it to `[]`, removing `m_target_g` from every row, and removing it from the first row
    only. The endpoint rows are the actual realisation of the 38/40/42 g science — a contract named
    for the endpoint that tolerates their disappearance has not checked the thing it is named for.

    Malformed input is reported as a problem, never raised: a validator that crashes on a bad
    artefact cannot be used to reject one.
    """
    expected = sorted(float(t) for t in ENDPOINT_TARGETS)
    rows = artifact.get("rows")

    if rows is None:
        return ["artefact has no `rows`: the endpoint result rows are missing entirely"]
    if not isinstance(rows, list):
        return ["artefact `rows` is %s, expected a list of %d endpoint rows"
                % (type(rows).__name__, len(expected))]
    if not rows:
        return ["artefact `rows` is empty; expected one row per endpoint target %r" % (expected,)]

    problems: list[str] = []
    if len(rows) != len(expected):
        problems.append("artefact carries %d endpoint rows, expected exactly %d (one per target "
                        "%r)" % (len(rows), len(expected), expected))

    seen: list[float] = []
    for i, r in enumerate(rows):
        if not isinstance(r, dict):
            problems.append("endpoint row %d is %s, expected a mapping" % (i, type(r).__name__))
            continue
        for key in set(RETIRED_ENDPOINT_KEYS) | {"v_target_ml"}:
            if key in r:
                problems.append("endpoint row %d carries the retired key %r" % (i, key))
        if ENDPOINT_ROW_KEY not in r:
            problems.append("endpoint row %d has no %r" % (i, ENDPOINT_ROW_KEY))
            continue
        raw = r[ENDPOINT_ROW_KEY]
        try:
            value = float(raw)
        except (TypeError, ValueError):
            problems.append("endpoint row %d has non-numeric %s=%r" % (i, ENDPOINT_ROW_KEY, raw))
            continue
        if value != value or value in (float("inf"), float("-inf")):
            problems.append("endpoint row %d has non-finite %s=%r" % (i, ENDPOINT_ROW_KEY, raw))
            continue
        seen.append(value)

    if sorted(seen) != expected:
        problems.append("endpoint rows cover %r, expected exactly one row per target %r"
                        % (sorted(seen), expected))
    return problems


# ─────────────────────────────────────────────────────────────────────────────────────────────
# Display formatting (round-8 P1-2, P1-3)
# ─────────────────────────────────────────────────────────────────────────────────────────────

#: Publication typography: U+2212 MINUS SIGN, not the ASCII hyphen. One convention everywhere,
#: so a test can assert an exact string instead of tolerating a regex family.
MINUS = "−"

#: Percentage-point ranges are quoted to three decimals throughout Paper A.
PP_DIGITS = 3

#: Pooled MAPE percentages are quoted to two decimals (8.44%, not 8.4%).
PCT_DIGITS = 2


def quantize_for_display(value: float, digits: int) -> Decimal:
    """Round for display with an explicit rule, normalising a negative zero to positive.

    ``round()`` is banker's rounding and its behaviour at a tie is not the convention a reader
    assumes. More importantly this is DISPLAY only: the caller keeps the signed full-precision
    value, because ``-0.0004`` displaying as ``0.000`` must never be what decides whether an
    interval "excludes zero" (round-8 P1-2).
    """
    quantum = Decimal(1).scaleb(-int(digits))
    out = Decimal(str(float(value))).quantize(quantum, rounding=ROUND_HALF_UP)
    return abs(out) if out == 0 else out


def format_pp(value: float, digits: int = PP_DIGITS, explicit_plus: bool = True) -> str:
    """Render one percentage-point value: Unicode minus, fixed digits, optional explicit plus."""
    q = quantize_for_display(value, digits)
    text = f"{abs(q):.{int(digits)}f}"
    if q < 0:
        return MINUS + text
    return ("+" + text) if explicit_plus else text


def format_pp_range(lower: float, upper: float, digits: int = PP_DIGITS) -> str:
    """Render a percentage-point range exactly as the paper quotes it, e.g. ``[−0.825, +0.000]``.

    This is the single production renderer. The generated prose and the contract tests both call
    it, so a test can require an exact string and cannot be satisfied by an unrelated interval
    that merely matches a numeric shape (round-8 P1-3).
    """
    return "[%s, %s]" % (format_pp(lower, digits), format_pp(upper, digits))


def format_pct(value: float, digits: int = PCT_DIGITS) -> str:
    """Render a percentage for publication, e.g. ``8.44%``."""
    return f"{quantize_for_display(value, digits):.{int(digits)}f}%"


# ─────────────────────────────────────────────────────────────────────────────────────────────
# Interval representation (round-8 P1-2)
# ─────────────────────────────────────────────────────────────────────────────────────────────

INTERVAL_KIND = "fixed_predictor_clustered_percentile_sensitivity_range"


def interval_record(lower: float, upper: float, digits: int = PP_DIGITS) -> dict:
    """Build the interval object: signed full precision, derived flags, and separate display.

    The Round-8 defect was that ``excludes_zero`` was decided on ``round(lo, 3)``/``round(hi, 3)``.
    A full-precision upper bound of ``-0.0004`` therefore displayed as ``0.000`` AND set the flag
    from that display, so presentation precision controlled an analytical classification. Here the
    flags come from the unrounded bounds and the display fields are clearly marked as display.

    ``contains_zero`` uses the closed-interval convention: a bound of exactly 0.0 touches zero.
    """
    lo = float(lower)
    hi = float(upper)
    contains = bool(lo <= 0.0 <= hi)
    if hi < 0.0:
        signed_nearest = hi
    elif lo > 0.0:
        signed_nearest = lo
    else:
        signed_nearest = 0.0

    d_lo = quantize_for_display(lo, digits)
    d_hi = quantize_for_display(hi, digits)
    return {
        "kind": INTERVAL_KIND,
        "full_precision_pp": {"lower": lo, "upper": hi},
        "contains_zero_full_precision": contains,
        "excludes_zero_full_precision": not contains,
        "signed_nearest_bound_to_zero_pp": signed_nearest,
        "width_pp": hi - lo,
        "display": {
            "digits": int(digits),
            "lower": float(d_lo),
            "upper": float(d_hi),
            "text": format_pp_range(lo, hi, digits),
            "touches_zero": bool(d_lo <= 0 <= d_hi),
        },
    }


def interval_display_text(interval: dict) -> str:
    """The exact publication string for an interval object, as stored."""
    return interval["display"]["text"]


def validate_interval_record(interval: dict) -> list[str]:
    """Confirm an interval's display fields reconcile with its full-precision bounds."""
    problems: list[str] = []
    try:
        lo = float(interval["full_precision_pp"]["lower"])
        hi = float(interval["full_precision_pp"]["upper"])
    except (KeyError, TypeError, ValueError):
        return ["interval record has no usable full_precision_pp bounds"]
    if hi < lo:
        problems.append("interval bounds are reversed (upper < lower)")
    rebuilt = interval_record(lo, hi, int(interval.get("display", {}).get("digits", PP_DIGITS)))
    for field in ("contains_zero_full_precision", "excludes_zero_full_precision"):
        if bool(interval.get(field)) != rebuilt[field]:
            problems.append("interval.%s disagrees with its full-precision bounds" % field)
    if interval.get("display", {}).get("text") != rebuilt["display"]["text"]:
        problems.append("interval display text %r does not match the production formatter (%r)"
                        % (interval.get("display", {}).get("text"), rebuilt["display"]["text"]))
    return problems


# ─────────────────────────────────────────────────────────────────────────────────────────────
# Canonical serialisation and hashing (round-8 P1-4)
# ─────────────────────────────────────────────────────────────────────────────────────────────

def canonical_json(obj) -> str:
    """Deterministic JSON for hashing: sorted keys, tight separators, UTF-8, no timestamp."""
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha256_of(obj) -> str:
    """SHA-256 over the canonical serialisation of ``obj``."""
    return hashlib.sha256(canonical_json(obj).encode("utf-8")).hexdigest()


# ─────────────────────────────────────────────────────────────────────────────────────────────
# Corpus manifest (round-8 P1-4)
# ─────────────────────────────────────────────────────────────────────────────────────────────

SOLUTES = ("caffeine", "trigonelline", "5CQA")
VARIETIES = ("Arabica", "Robusta")

#: The eight coarse/fine validation records that lie off the declared 3x3 calibration grid. No
#: same-(T,p) optimal-grind record exists for any of them, so the lookup comparator is undefined
#: there — but they ARE part of the headline level-only comparison (round-7 P0-3).
OFF_GRID_SAMPLE_IDS = ("A21", "A22", "A32", "A33", "R21", "R22", "R32", "R33")

COMPLETE_CORPUS_ESTIMAND = "complete held-out C/F corpus (on-grid + off-grid)"
MATCHED_GRID_ESTIMAND = "matched 3x3 on-grid C/F transfer benchmark"

#: Two DISTINCT support sets. Every reported result must name which one it used, so a number
#: correct on 108 matched-grid observations can never be printed as the 132-observation headline.
SUPPORT_COMPLETE = "complete_cf_corpus_132"
SUPPORT_MATCHED_GRID = "matched_grid_cf_corpus_108"


def _cond_key(value: float) -> str:
    """Canonical string for a condition coordinate — stable across float repr differences."""
    return f"{float(value):g}"


def sample_cluster_id(record: dict) -> str:
    """Canonical id for one sample record."""
    return str(record["sample"])


def condition_cluster_id(variety: str, T: float, p: float) -> str:
    """Canonical id for a (variety, T, p) condition. Always includes variety: without it the
    Arabica and Robusta conditions at the same (T,p) collide into one cluster."""
    return "%s|%s|%s" % (variety, _cond_key(T), _cond_key(p))


def build_transfer_corpus_manifest(source_rows, include_off_grid: bool = True,
                                   varieties=VARIETIES, solutes=SOLUTES) -> dict:
    """Build the canonical corpus manifest directly from the source data rows.

    This is the SOLE owner of inclusion logic. The source-to-artefact test calls it independently
    of the producer, so the two sides of the corpus assertion are not both derived from the same
    JSON file — deriving both from one artefact would only prove internal consistency and could
    certify a wrong corpus.
    """
    records = []
    for r in source_rows:
        if r["variety"] not in varieties or r["granulometry"] not in ("C", "F"):
            continue
        on_grid = (r["on_grid"] == "True")
        if not include_off_grid and not on_grid:
            continue
        records.append({
            "sample_id": str(r["sample"]),
            "variety": str(r["variety"]),
            "grind": str(r["granulometry"]),
            "temperature_degC": float(r["T_degC"]),
            "pressure_bar": float(r["p_bar"]),
            "on_grid": bool(on_grid),
            # The lookup comparator needs a same-(T,p) OPTIMAL-grind record. Every off-grid
            # condition lacks one; no on-grid condition does.
            "lookup_defined": bool(on_grid),
            "solutes": list(solutes),
            "primary_cluster_id": condition_cluster_id(r["variety"], r["T_degC"], r["p_bar"]),
            "sample_cluster_id": str(r["sample"]),
        })

    records.sort(key=lambda x: (x["variety"], x["grind"], x["sample_id"],
                                x["temperature_degC"], x["pressure_bar"]))

    all_cf = sorted(str(r["sample"]) for r in source_rows
                    if r["variety"] in varieties and r["granulometry"] in ("C", "F"))
    included = [r["sample_id"] for r in records]
    excluded = [s for s in all_cf if s not in set(included)]
    train = sorted(str(r["sample"]) for r in source_rows
                   if r["variety"] in varieties and r["granulometry"] == "O"
                   and r["on_grid"] == "True")

    off_grid = sorted(r["sample_id"] for r in records if not r["on_grid"])
    lookup_undefined = sorted(r["sample_id"] for r in records if not r["lookup_defined"])
    n_obs = len(records) * len(solutes)
    n_lookup_obs = sum(len(solutes) for r in records if r["lookup_defined"])

    manifest = {
        "schema_version": SCHEMA_VERSION,
        "estimand": COMPLETE_CORPUS_ESTIMAND if include_off_grid else MATCHED_GRID_ESTIMAND,
        "support_set": SUPPORT_COMPLETE if include_off_grid else SUPPORT_MATCHED_GRID,
        "include_off_grid": bool(include_off_grid),
        "train_grind": "O",
        "train_sample_ids": train,
        "n_train_records": len(train),
        "held_out_sample_ids": sorted(included),
        "n_held_out_records": len(included),
        "excluded_sample_ids": excluded,
        "n_excluded_records": len(excluded),
        "excluded_reason": (
            None if include_off_grid else
            "off-grid C/F validation records; no same-(T,p) O counterpart exists for any of "
            "them, so the lookup comparator is undefined there"),
        "n_cf_records_available": len(all_cf),
        "n_solutes": len(solutes),
        "solutes": list(solutes),
        "n_observations": n_obs,
        "off_grid_sample_ids": off_grid,
        "n_off_grid_records": len(off_grid),
        "lookup_undefined_sample_ids": lookup_undefined,
        "n_lookup_observations": n_lookup_obs,
        "records": records,
    }
    # A count alone cannot detect a *different* set of 44 records. The ID hash catches membership
    # drift; the full hash also catches changed grind/condition metadata under unchanged IDs.
    manifest["included_sample_ids_sha256"] = sha256_of(sorted(included))
    manifest["manifest_sha256"] = sha256_of(records)
    return manifest


def validate_corpus_manifest(manifest: dict, include_off_grid: bool = True) -> list[str]:
    """Structural checks on a corpus manifest, independent of the source data."""
    problems: list[str] = []
    records = manifest.get("records") or []
    if len(records) != manifest.get("n_held_out_records"):
        problems.append("n_held_out_records disagrees with the record list length")
    n_solutes = int(manifest.get("n_solutes") or 0)
    if len(records) * n_solutes != manifest.get("n_observations"):
        problems.append("n_observations is not n_held_out_records x n_solutes")
    ids = [r["sample_id"] for r in records]
    if len(set(ids)) != len(ids):
        problems.append("corpus manifest contains duplicate sample ids")
    for r in records:
        if len(r.get("solutes") or []) != n_solutes:
            problems.append("sample %s does not carry the canonical solute set" % r.get("sample_id"))
    if manifest.get("manifest_sha256") != sha256_of(records):
        problems.append("manifest_sha256 does not match the record list it is supposed to fix")
    if manifest.get("included_sample_ids_sha256") != sha256_of(sorted(ids)):
        problems.append("included_sample_ids_sha256 does not match the included ids")
    if include_off_grid:
        if sorted(manifest.get("off_grid_sample_ids") or []) != sorted(OFF_GRID_SAMPLE_IDS):
            problems.append("the complete corpus does not carry exactly the eight known "
                            "off-grid records %r" % (list(OFF_GRID_SAMPLE_IDS),))
        if manifest.get("n_excluded_records"):
            problems.append("the complete corpus declares exclusions but must have none")
    return problems


# ─────────────────────────────────────────────────────────────────────────────────────────────
# Resampling design (round-8 P0-2, P1-1)
# ─────────────────────────────────────────────────────────────────────────────────────────────

#: The declared PRIMARY scheme. Retained from round 7 as a pre-declared *conservative* choice.
#: It is deliberately NOT reselected after seeing which range touches zero (round-8 P1-1).
PRIMARY_SCHEME = "cond_in_variety"

RESAMPLING_ESTIMAND = ("observation-weighted mean paired model-minus-comparator MAPE loss "
                       "difference over the complete held-out C/F observation corpus")

#: Every scheme's design, as inspectable data rather than prose. The Methods paragraph and the
#: supplementary table are both GENERATED from this, so a later priority change cannot leave the
#: general Methods describing a superseded primary unit (round-8 P0-2).
SCHEMES = {
    "cond_in_variety": {
        "name": "cond_in_variety",
        "role": "primary_conservative_sensitivity",
        "label": "(variety, temperature, pressure) condition, resampled within variety",
        "strata": ["variety"],
        "cluster_key": ["variety", "temperature_degC", "pressure_bar"],
        "rationale": (
            "keeps all three co-measured solutes at a condition together and, where both grinds "
            "exist, additionally moves the distinct C and F sample records together. This is a "
            "deliberately conservative dependence assumption, not a uniquely identified "
            "experimental sampling unit."),
    },
    "sample_in_variety_grind": {
        "name": "sample_in_variety_grind",
        "role": "design_aligned_secondary_sensitivity",
        "label": "sample record, resampled within variety x grind",
        "strata": ["variety", "grind"],
        "cluster_key": ["sample_id"],
        "rationale": (
            "one cluster per coffee sample record, carrying the three solute outcomes measured "
            "from that sample. This is the dependency the source establishes most directly."),
    },
    "cond_in_group": {
        "name": "cond_in_group",
        "role": "secondary_sensitivity",
        "label": "(temperature, pressure) condition within variety x solute group",
        "strata": ["variety", "solute"],
        "cluster_key": ["variety", "solute", "temperature_degC", "pressure_bar"],
        "rationale": (
            "keeps C and F together for one solute but lets different solutes of a variety draw "
            "different conditions, so it does not preserve cross-solute condition dependence."),
    },
    "group": {
        "name": "group",
        "role": "secondary_coarse_sensitivity",
        "label": "whole variety x solute group",
        "strata": [],
        "cluster_key": ["variety", "solute"],
        "rationale": (
            "the coarsest construction: six clusters only, so its percentile distribution is "
            "highly discrete. Reported as a stress test, not as a high-resolution analysis."),
    },
}

#: Order used wherever schemes are listed, primary first.
SCHEME_ORDER = ("cond_in_variety", "sample_in_variety_grind", "cond_in_group", "group")


def _group_of(record: dict) -> str:
    """The variety x solute group label.

    Producer records carry it pre-joined as ``group`` ("Arabica:caffeine"). That field is
    authoritative when present: it is what the producer clusters on, and synthetic records used
    by the resampling unit tests supply it without separate variety/solute fields.
    """
    if record.get("group"):
        return str(record["group"])
    return "%s:%s" % (record["variety"], record["solute"])


def cluster_key_of(record: dict, scheme: str) -> str:
    """Canonical cluster id for one per-observation producer record under ``scheme``.

    Producer records carry: group ("variety:solute"), variety, solute, sample, grind, T, p.
    """
    if scheme == "cond_in_variety":
        return condition_cluster_id(record["variety"], record["T"], record["p"])
    if scheme == "sample_in_variety_grind":
        return str(record["sample"])
    if scheme == "cond_in_group":
        return "%s|%s|%s" % (_variety_solute_id(record),
                             _cond_key(record["T"]), _cond_key(record["p"]))
    if scheme == "group":
        return _variety_solute_id(record)
    raise ValueError("unknown resampling scheme %r; expected one of %r"
                     % (scheme, list(SCHEME_ORDER)))


def _variety_solute_id(record: dict) -> str:
    """``variety|solute``, pipe-joined like every other cluster id in the design.

    The producer supplies the pair pre-joined with a colon as ``group``; using that field directly
    put a colon inside an otherwise pipe-delimited id, so the same cluster had two spellings
    depending on which code path built it. The source oracle declares the pipe form, so the
    delimiter is normalised here rather than left to the caller.
    """
    if record.get("variety") is not None and record.get("solute") is not None:
        return "%s|%s" % (record["variety"], record["solute"])
    return str(record["group"]).replace(":", "|")


def stratum_key_of(record: dict, scheme: str) -> str:
    """Canonical stratum id — clusters are drawn within strata, preserving the design balance."""
    if scheme not in SCHEMES:
        raise ValueError("unknown resampling scheme %r; expected one of %r"
                         % (scheme, list(SCHEME_ORDER)))
    strata = SCHEMES[scheme]["strata"]
    if not strata:
        return ""
    # `cond_in_group` strata are (variety, solute) — i.e. the group label, which the producer
    # supplies pre-joined. Normalised to the pipe delimiter for the same reason as the cluster id.
    if strata == ["variety", "solute"]:
        return _variety_solute_id(record)
    parts = []
    for s in strata:
        if s == "variety":
            parts.append(record["variety"])
        elif s == "solute":
            parts.append(record["solute"])
        elif s == "grind":
            parts.append(record["grind"])
        else:
            raise ValueError("unknown stratum field %r" % s)
    return "|".join(parts)


def cluster_membership(records, scheme: str) -> list[dict]:
    """Archive exact cluster membership for ``scheme`` — not merely the cluster count.

    Round-8 P1-1 asked for membership to be auditable: a count of 26 cannot distinguish the
    correct partition from one that split a sample's solutes across two clusters.
    """
    by_cluster: dict[str, dict] = {}
    for r in records:
        cid = cluster_key_of(r, scheme)
        entry = by_cluster.setdefault(cid, {
            "cluster_id": cid,
            "stratum": stratum_key_of(r, scheme),
            "sample_ids": set(),
            "grinds": set(),
            "observation_ids": [],
        })
        entry["sample_ids"].add(str(r["sample"]))
        entry["grinds"].add(str(r["grind"]))
        entry["observation_ids"].append("%s|%s" % (r["sample"], r["solute"]))

    out = []
    for cid in sorted(by_cluster):
        e = by_cluster[cid]
        out.append({
            "cluster_id": cid,
            "stratum": e["stratum"],
            "sample_ids": sorted(e["sample_ids"]),
            "grinds": sorted(e["grinds"]),
            "observation_ids": sorted(e["observation_ids"]),
            "n_observations": len(e["observation_ids"]),
        })
    return out


def cluster_size_distribution(membership) -> dict:
    """``{observations_per_cluster: n_clusters}`` with string keys, for JSON stability."""
    dist: dict[str, int] = {}
    for c in membership:
        key = str(c["n_observations"])
        dist[key] = dist.get(key, 0) + 1
    return dict(sorted(dist.items(), key=lambda kv: int(kv[0])))


def scheme_design(records, scheme: str) -> dict:
    """The full inspectable design object for one scheme, including membership and its hash."""
    membership = cluster_membership(records, scheme)
    spec = SCHEMES[scheme]
    return {
        "name": spec["name"],
        "role": spec["role"],
        "label": spec["label"],
        "rationale": spec["rationale"],
        "strata": list(spec["strata"]),
        "cluster_key": list(spec["cluster_key"]),
        "n_clusters": len(membership),
        "cluster_size_distribution": cluster_size_distribution(membership),
        "n_strata": len({c["stratum"] for c in membership}),
        "membership_sha256": sha256_of(membership),
        "membership": membership,
    }


def resampling_design(records, primary: str = PRIMARY_SCHEME) -> dict:
    """The complete resampling design: every scheme, its role and its exact membership."""
    return {
        "schema_version": SCHEMA_VERSION,
        "estimand": RESAMPLING_ESTIMAND,
        "predictors_refit_inside_resampling": False,
        "interval_kind": INTERVAL_KIND,
        "primary_scheme": primary,
        "scheme_order": list(SCHEME_ORDER),
        "schemes": {name: scheme_design(records, name) for name in SCHEME_ORDER},
    }


def validate_resampling_design(design: dict, n_observations: int) -> list[str]:
    """Every scheme must partition exactly the same observation set."""
    problems: list[str] = []
    if design.get("primary_scheme") not in SCHEMES:
        problems.append("primary_scheme %r is not a declared scheme" % design.get("primary_scheme"))
    if design.get("predictors_refit_inside_resampling"):
        problems.append("the fixed-predictor contract is violated: predictors are marked as "
                        "refitted inside resampling")
    reference = None
    for name in SCHEME_ORDER:
        s = (design.get("schemes") or {}).get(name)
        if not s:
            problems.append("resampling design omits scheme %r" % name)
            continue
        obs = sorted(o for c in s["membership"] for o in c["observation_ids"])
        if len(obs) != n_observations:
            problems.append("scheme %r covers %d observations, expected %d"
                            % (name, len(obs), n_observations))
        if len(set(obs)) != len(obs):
            problems.append("scheme %r assigns an observation to more than one cluster" % name)
        if reference is None:
            reference = obs
        elif obs != reference:
            problems.append("scheme %r does not cover the same observation set as %r"
                            % (name, SCHEME_ORDER[0]))
        if s["n_clusters"] != len(s["membership"]):
            problems.append("scheme %r n_clusters disagrees with its membership" % name)
        if s["membership_sha256"] != sha256_of(s["membership"]):
            problems.append("scheme %r membership hash does not fix its membership" % name)
    return problems
