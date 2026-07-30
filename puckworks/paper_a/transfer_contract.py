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

from puckworks.paper_a import transfer_semantics as TS

#: Bump when a field's *meaning* changes, not when a value is regenerated. Consumers use this to
#: tell a corrected collected-mass artefact from an untyped legacy one.
#:
#: v3 (round-9 P1-1): the single top-level `stability_audit` scalar became a
#: `stability_audits` LIST keyed by exact target, because a Monte Carlo precision estimate
#: for one endpoint/scheme/loss is not a property of any other. Cluster ids for the
#: variety x solute schemes were also normalised to the pipe delimiter.
#:
#: v4 (round-10 P0-1, P1-2, P1-3): the resampling design's free-text `estimand` sentence became a
#: TYPED estimand object whose direction is derived and re-derived on validation; a typed
#: `inferential_status` object records which decisions the analysis can make at all; interval
#: records carry exact zero-contact flags and a display field named for what it means
#: (`display.contains_zero_rounded`, formerly the ambiguous `display.touches_zero`). A v3 artefact
#: is REJECTED rather than read under the v4 validator: its estimand is a sentence, so a v4 reader
#: could not tell a correct direction from a reversed one.
SCHEMA_VERSION = 4

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


#: Exactly the keys an interval record carries. Anything else is a named failure: an unvalidated
#: extra field is a place for a second, contradictory story about the same interval to live.
_INTERVAL_FIELDS = ("kind", "full_precision_pp", "contains_zero_full_precision",
                    "excludes_zero_full_precision", "touches_zero_at_lower",
                    "touches_zero_at_upper", "signed_nearest_bound_to_zero_pp", "width_pp",
                    "display")
_INTERVAL_DISPLAY_FIELDS = ("digits", "lower", "upper", "text", "contains_zero_rounded")

#: Display precisions the formatter is exercised at. A record asking for 12 digits is not a display
#: choice, it is a bug.
_MAX_DISPLAY_DIGITS = 6


def interval_record(lower, upper, digits: int = PP_DIGITS) -> dict:
    """Build the interval object: signed full precision, derived flags, and separate display.

    The Round-8 defect was that ``excludes_zero`` was decided on ``round(lo, 3)``/``round(hi, 3)``.
    A full-precision upper bound of ``-0.0004`` therefore displayed as ``0.000`` AND set the flag
    from that display, so presentation precision controlled an analytical classification. Here the
    flags come from the unrounded bounds and the display fields are clearly marked as display.

    ``contains_zero`` uses the closed-interval convention: a bound of exactly 0.0 touches zero, and
    the two ``touches_zero_at_*`` flags say WHERE — exact contact at full precision, which is a
    different fact from the display range rounding onto zero.

    Round-10 P1-3 renamed ``display.touches_zero`` to ``display.contains_zero_rounded``. One name
    was carrying two concepts: exact contact with zero (an analytical fact) and the DISPLAYED range
    covering zero after rounding (a typography fact). ``+0.0038 pp`` displays as ``+0.004`` and does
    not touch zero at all; the round-8 conclusion said it reached zero at its upper bound because
    the two ideas shared a field name.

    Bounds are validated as finite numbers before anything is derived from them.
    """
    lo = TS.require_finite_number(lower, "interval lower bound")
    hi = TS.require_finite_number(upper, "interval upper bound")
    if not lo <= hi:
        raise ValueError("interval lower bound %r exceeds upper bound %r" % (lo, hi))
    if isinstance(digits, bool) or not isinstance(digits, int) \
            or not 0 <= digits <= _MAX_DISPLAY_DIGITS:
        raise ValueError("interval display digits must be an int in [0, %d], got %r"
                         % (_MAX_DISPLAY_DIGITS, digits))

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
        # Exact contact, at full precision. `-0.0` is normalised by the comparison itself:
        # `-0.0 == 0.0` is True in IEEE 754, which is the behaviour we want here.
        "touches_zero_at_lower": bool(lo == 0.0),
        "touches_zero_at_upper": bool(hi == 0.0),
        "signed_nearest_bound_to_zero_pp": signed_nearest,
        "width_pp": hi - lo,
        "display": {
            "digits": int(digits),
            "lower": float(d_lo),
            "upper": float(d_hi),
            "text": format_pp_range(lo, hi, digits),
            # DISPLAY containment: does the ROUNDED range cover zero? Not exact contact.
            "contains_zero_rounded": bool(d_lo <= 0 <= d_hi),
        },
    }


def interval_display_text(interval: dict) -> str:
    """The exact publication string for an interval object, as stored."""
    return interval["display"]["text"]


def validate_interval_record(interval) -> list[str]:
    """Rebuild the record from its bounds and exact-compare EVERY stored field.

    Round-10 P1-3. The predecessor checked four things — that bounds were convertible, that they
    were ordered, the two containment booleans under ``bool(...)`` coercion, and the display text —
    and returned an empty problem list for all nine of these reproduced mutations:

        kind changed to "calibrated 95% confidence interval" · width 999 · signed nearest bound
        −999 · display.lower 999 · display.upper 999 · display contact flipped ·
        `excludes_zero_full_precision` deleted from a zero-containing interval ·
        `contains_zero_full_precision` deleted from a zero-excluding interval ·
        `contains_zero_full_precision` replaced by the STRING "false"

    The last two passed because ``bool(None)`` is falsey and ``bool("false")`` is TRUE, so a missing
    field and a string both coerced to the value the record needed. A validator whose docstring says
    it reconciles an interval's fields with full precision, and which in fact reconciles two of
    them, is worse than no validator: the artefact checker delegates every interval to it and
    reports a green chain.

    So: validate the primitives, rebuild the canonical record from them, and deep-compare. Malformed
    input returns NAMED PROBLEMS and never raises — a validator that crashes on a bad artefact
    cannot be used to reject one.
    """
    problems: list[str] = []
    if not isinstance(interval, dict):
        return ["interval record is %s, expected a mapping" % type(interval).__name__]

    for field in _INTERVAL_FIELDS:
        if field not in interval:
            problems.append("interval.%s: required field is missing" % field)
    for extra in sorted(set(interval) - set(_INTERVAL_FIELDS)):
        problems.append("interval carries the unexpected field %r; every stored field must be "
                        "validated or removed" % extra)

    fp = interval.get("full_precision_pp")
    if not isinstance(fp, dict):
        problems.append("interval.full_precision_pp is %s, expected a mapping of lower/upper"
                        % type(fp).__name__)
        return problems
    for extra in sorted(set(fp) - {"lower", "upper"}):
        problems.append("interval.full_precision_pp carries the unexpected field %r" % extra)
    try:
        lo = TS.require_finite_number(fp.get("lower"), "interval.full_precision_pp.lower")
        hi = TS.require_finite_number(fp.get("upper"), "interval.full_precision_pp.upper")
    except ValueError as exc:
        problems.append(str(exc))
        return problems
    if hi < lo:
        problems.append("interval bounds are reversed: lower=%r exceeds upper=%r" % (lo, hi))
        return problems

    display = interval.get("display")
    if not isinstance(display, dict):
        problems.append("interval.display is %s, expected a mapping" % type(display).__name__)
        return problems
    for field in _INTERVAL_DISPLAY_FIELDS:
        if field not in display:
            problems.append("interval.display.%s: required field is missing" % field)
    for extra in sorted(set(display) - set(_INTERVAL_DISPLAY_FIELDS)):
        problems.append("interval.display carries the unexpected field %r" % extra)
    digits = display.get("digits")
    if isinstance(digits, bool) or not isinstance(digits, int) \
            or not 0 <= digits <= _MAX_DISPLAY_DIGITS:
        problems.append("interval.display.digits is %r, expected an int in [0, %d]"
                        % (digits, _MAX_DISPLAY_DIGITS))
        return problems

    try:
        rebuilt = interval_record(lo, hi, digits)
    except ValueError as exc:                                   # pragma: no cover - guarded above
        problems.append("interval record cannot be rebuilt from its own bounds: %s" % exc)
        return problems

    for field in ("kind", "signed_nearest_bound_to_zero_pp", "width_pp"):
        if field in interval and not _same_value(interval[field], rebuilt[field]):
            problems.append("interval.%s is %r, its bounds imply %r"
                            % (field, interval[field], rebuilt[field]))
    for field in ("contains_zero_full_precision", "excludes_zero_full_precision",
                  "touches_zero_at_lower", "touches_zero_at_upper"):
        if field not in interval:
            continue
        value = interval[field]
        if not _exact_bool(value):
            problems.append("interval.%s is %r (%s), expected a JSON boolean — truthiness "
                            "coercion is how a missing field and the string \"false\" both passed "
                            "this check" % (field, value, type(value).__name__))
        elif value != rebuilt[field]:
            problems.append("interval.%s is %r, its full-precision bounds imply %r"
                            % (field, value, rebuilt[field]))
    for field in ("lower", "upper", "text"):
        if field in display and not _same_value(display[field], rebuilt["display"][field]):
            problems.append("interval.display.%s is %r, the production renderer gives %r at %d "
                            "digits" % (field, display[field], rebuilt["display"][field], digits))
    if "contains_zero_rounded" in display:
        value = display["contains_zero_rounded"]
        if not _exact_bool(value):
            problems.append("interval.display.contains_zero_rounded is %r (%s), expected a JSON "
                            "boolean" % (value, type(value).__name__))
        elif value != rebuilt["display"]["contains_zero_rounded"]:
            problems.append("interval.display.contains_zero_rounded is %r, rounding the bounds to "
                            "%d digits gives %r"
                            % (value, digits, rebuilt["display"]["contains_zero_rounded"]))
    return problems


def _same_value(value, expected) -> bool:
    """Exact comparison that does not let a bool masquerade as a number, or vice versa."""
    if _exact_bool(value) != _exact_bool(expected):
        return False
    if isinstance(expected, float):
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            return False
        return float(value) == float(expected)
    return value == expected


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

#: The estimand, as the typed object every renderer must consume. Round-10 P1-2 retired the
#: free-text sentence that used to live here: it stated the sign convention in prose while
#: `transfer_semantics` stated it again as a boolean, and nothing required the two to agree. The
#: support set is named separately (it belongs to the corpus manifest, not to the contrast).
RESAMPLING_ESTIMAND_SPEC = TS.POOLED_MAPE_ESTIMAND

#: The observation weighting and support, which the estimand object does not carry.
RESAMPLING_ESTIMAND_SUPPORT = ("observation-weighted mean over the complete held-out C/F "
                               "observation corpus")


def resampling_estimand_prose() -> str:
    """The one sentence that defines the contrast and its sign, for Methods, notes and captions."""
    return "%s, %s" % (RESAMPLING_ESTIMAND_SPEC.prose, RESAMPLING_ESTIMAND_SUPPORT)

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
        "estimand": RESAMPLING_ESTIMAND_SPEC.as_dict(),
        "estimand_support": RESAMPLING_ESTIMAND_SUPPORT,
        "inferential_status": TS.TRANSFER_INFERENTIAL_STATUS.as_dict(),
        "predictors_refit_inside_resampling": False,
        "interval_kind": INTERVAL_KIND,
        "primary_scheme": primary,
        "scheme_order": list(SCHEME_ORDER),
        "schemes": {name: scheme_design(records, name) for name in SCHEME_ORDER},
    }


#: Every top-level design field, so an unexpected one is reported instead of ignored. A field
#: nobody validates is a field that can carry a false statement into Methods or a table note.
_DESIGN_FIELDS = ("schema_version", "estimand", "estimand_support", "inferential_status",
                  "predictors_refit_inside_resampling", "interval_kind", "primary_scheme",
                  "scheme_order", "schemes")

#: Per-scheme fields. The first six are AUTHORIAL declarations pinned against `SCHEMES`; the rest
#: are derived from membership and recomputed here.
_SCHEME_DECLARED_FIELDS = ("name", "role", "label", "rationale", "strata", "cluster_key")
_SCHEME_DERIVED_FIELDS = ("n_clusters", "n_strata", "cluster_size_distribution",
                          "membership_sha256", "membership")
_CLUSTER_FIELDS = ("cluster_id", "stratum", "sample_ids", "grinds", "observation_ids",
                   "n_observations")


def _exact_bool(value) -> bool:
    """True only for the JSON boolean ``false``/``true`` — never for 0, "", None or "false".

    ``bool("false")`` is ``True``. Round-10 P1-3 reproduced a false green built on exactly that
    coercion, so booleans are type-checked everywhere in this module rather than truthiness-tested.
    """
    return isinstance(value, bool)


def validate_resampling_design(design: dict, n_observations: int) -> list[str]:
    """Exact-validate the WHOLE declared design, not only its observation coverage.

    Round-10 P1-2. The predecessor checked six things — primary name is known, predictors are not
    refitted, coverage is complete and non-duplicated, all schemes cover the same observations,
    ``n_clusters`` matches the membership length, and the self-hash matches — and reported nothing
    for any of these twelve reproduced mutations:

        reversed estimand text · interval kind changed to "calibrated 95% confidence interval" ·
        nested schema version 999 · reversed scheme order · wrong role · wrong label · wrong
        declared strata · wrong declared cluster key · wrong `n_strata` · wrong cluster-size
        distribution · wrong rationale · wrong archived grinds with a refreshed self-hash

    None of those changes a number. All of them change what the paper's Methods, Table 5 and
    Supplementary Table S6 SAY, because those are generated from this object. So every declared
    field is now pinned against the contract, every derived field is recomputed from the membership,
    and every field is enumerated so an unexpected one is a named problem rather than a silent pass.

    The membership itself is checked against the SOURCE data by
    :mod:`puckworks.paper_a.source_resampling_oracle`, which shares no code with this module. A
    self-hash proves only that nobody edited the artefact without rehashing it.
    """
    problems: list[str] = []
    if not isinstance(design, dict):
        return ["resampling design is %s, expected a mapping" % type(design).__name__]

    for extra in sorted(set(design) - set(_DESIGN_FIELDS)):
        problems.append("resampling design carries the unexpected field %r; extend "
                        "_DESIGN_FIELDS and validate it, or remove it" % extra)

    # ── schema ─────────────────────────────────────────────────────────────────────────────────
    if design.get("schema_version") != SCHEMA_VERSION:
        problems.append("resampling_design.schema_version is %r, expected %d; regenerate the "
                        "Paper A transfer artefacts rather than reading a legacy design under this "
                        "validator" % (design.get("schema_version"), SCHEMA_VERSION))

    # ── the estimand, re-derived rather than trusted ────────────────────────────────────────────
    try:
        estimand = TS.estimand_from_dict(design.get("estimand"))
    except ValueError as exc:
        estimand = None
        problems.append("resampling_design.estimand: %s" % exc)
    if estimand is not None:
        expected = RESAMPLING_ESTIMAND_SPEC.as_dict()
        got = design["estimand"]
        for field in sorted(set(expected) | set(got)):
            if field not in got:
                problems.append("resampling_design.estimand is missing %r" % field)
            elif field not in expected:
                problems.append("resampling_design.estimand carries the unexpected field %r"
                                % field)
            elif got[field] != expected[field]:
                problems.append("resampling_design.estimand.%s is %r, the contract declares %r"
                                % (field, got[field], expected[field]))
        # The serialised derived fields must be what the PRIMITIVES imply, not what was written
        # down: a hand-edited `negative_values_favour` would otherwise reverse every favourability
        # sentence while the primitives still said the opposite.
        rederived = estimand.as_dict()
        for field in ("negative_values_favour", "positive_values_favour", "contrast_label",
                      "short_contrast_label", "direction_clause", "zero_means",
                      "prose"):
            if got.get(field) != rederived[field]:
                problems.append("resampling_design.estimand.%s is %r, but its own primitives imply "
                                "%r" % (field, got.get(field), rederived[field]))
    if design.get("estimand_support") != RESAMPLING_ESTIMAND_SUPPORT:
        problems.append("resampling_design.estimand_support is %r, expected %r"
                        % (design.get("estimand_support"), RESAMPLING_ESTIMAND_SUPPORT))

    # ── inferential status ─────────────────────────────────────────────────────────────────────
    try:
        status = TS.status_from_dict(design.get("inferential_status"))
    except ValueError as exc:
        status = None
        problems.append("resampling_design.inferential_status: %s" % exc)
    if status is not None:
        problems += ["resampling_design.inferential_status: %s" % p
                     for p in TS.validate_inferential_status(status)]
        expected = TS.TRANSFER_INFERENTIAL_STATUS.as_dict()
        got = design["inferential_status"]
        for field in sorted(set(expected) | set(got)):
            if got.get(field) != expected.get(field):
                problems.append("resampling_design.inferential_status.%s is %r, the contract "
                                "declares %r" % (field, got.get(field), expected.get(field)))

    # ── interval kind, refit flag, primary, order ──────────────────────────────────────────────
    if design.get("interval_kind") != INTERVAL_KIND:
        problems.append("resampling_design.interval_kind is %r, expected %r — the reported ranges "
                        "are fixed-predictor clustered percentile sensitivity ranges and must not "
                        "be labelled as calibrated confidence intervals"
                        % (design.get("interval_kind"), INTERVAL_KIND))
    refit = design.get("predictors_refit_inside_resampling")
    if not _exact_bool(refit) or refit is not False:
        problems.append("resampling_design.predictors_refit_inside_resampling is %r, expected the "
                        "boolean false: the fixed-predictor contract is what makes these ranges "
                        "sensitivity ranges rather than nothing at all" % (refit,))
    if design.get("primary_scheme") != PRIMARY_SCHEME:
        problems.append("resampling_design.primary_scheme is %r, the contract declares %r"
                        % (design.get("primary_scheme"), PRIMARY_SCHEME))
    if design.get("scheme_order") != list(SCHEME_ORDER):
        problems.append("resampling_design.scheme_order is %r, expected %r (exact set and order — "
                        "the order is how every generated table lists the schemes, primary first)"
                        % (design.get("scheme_order"), list(SCHEME_ORDER)))

    # ── schemes: declared fields pinned, derived fields recomputed ─────────────────────────────
    schemes = design.get("schemes")
    if not isinstance(schemes, dict):
        problems.append("resampling_design.schemes is %s, expected a mapping of %d schemes"
                        % (type(schemes).__name__, len(SCHEME_ORDER)))
        return problems
    for extra in sorted(set(schemes) - set(SCHEME_ORDER)):
        problems.append("resampling design declares the undeclared scheme %r" % extra)

    reference = None
    for name in SCHEME_ORDER:
        s = schemes.get(name)
        if not isinstance(s, dict):
            problems.append("resampling design omits scheme %r" % name)
            continue
        spec = SCHEMES[name]

        for extra in sorted(set(s) - set(_SCHEME_DECLARED_FIELDS) - set(_SCHEME_DERIVED_FIELDS)):
            problems.append("scheme %r carries the unexpected field %r" % (name, extra))
        for field in _SCHEME_DECLARED_FIELDS:
            want = list(spec[field]) if isinstance(spec[field], list) else spec[field]
            if s.get(field) != want:
                problems.append("scheme %r declares %s=%r, the contract declares %r"
                                % (name, field, s.get(field), want))

        membership = s.get("membership")
        if not isinstance(membership, list) or not membership:
            problems.append("scheme %r has no membership list" % name)
            continue
        malformed = False
        for i, c in enumerate(membership):
            if not isinstance(c, dict):
                problems.append("scheme %r cluster %d is %s, expected a mapping"
                                % (name, i, type(c).__name__))
                malformed = True
                continue
            for field in _CLUSTER_FIELDS:
                if field not in c:
                    problems.append("scheme %r cluster %d has no %r" % (name, i, field))
                    malformed = True
            for extra in sorted(set(c) - set(_CLUSTER_FIELDS)):
                problems.append("scheme %r cluster %d carries the unexpected field %r"
                                % (name, i, extra))
        if malformed:
            continue

        for c in membership:
            if c["n_observations"] != len(c["observation_ids"]):
                problems.append("scheme %r cluster %r declares n_observations=%r but carries %d "
                                "observation ids" % (name, c["cluster_id"], c["n_observations"],
                                                     len(c["observation_ids"])))
            if not c["sample_ids"] or not c["grinds"]:
                problems.append("scheme %r cluster %r archives no sample ids or grinds"
                                % (name, c["cluster_id"]))

        obs = sorted(o for c in membership for o in c["observation_ids"])
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

        if s.get("n_clusters") != len(membership):
            problems.append("scheme %r declares n_clusters=%r, its membership has %d"
                            % (name, s.get("n_clusters"), len(membership)))
        strata = {c["stratum"] for c in membership}
        if s.get("n_strata") != len(strata):
            problems.append("scheme %r declares n_strata=%r, its membership realises %d (%r)"
                            % (name, s.get("n_strata"), len(strata), sorted(strata)))
        dist = cluster_size_distribution(membership)
        if s.get("cluster_size_distribution") != dist:
            problems.append("scheme %r declares cluster_size_distribution=%r, its membership "
                            "realises %r" % (name, s.get("cluster_size_distribution"), dist))
        if s.get("membership_sha256") != sha256_of(membership):
            problems.append("scheme %r membership hash does not fix its membership" % name)
    return problems
