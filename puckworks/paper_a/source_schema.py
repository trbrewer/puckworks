"""What a row of `bioactives.csv` is allowed to be, checked before anything filters on it.

Round-11 P1-4. The production manifest and the independent source oracle are usefully separate —
separate analyte maps, separate parsers, separate membership logic — and that separation should
stay. But independence stops above the premises BOTH implementations accepted without checking, and
a common mode one layer up is still a common mode. Four of them were reproduced:

``variety=" Arabica "``
    silently EXCLUDED the record. Inclusion is tested against the raw cell before anything strips
    it, so a stray space does not fail the source contract — it quietly shrinks the corpus. The
    oracle strips after testing; production never strips at all. Both agree, and both are wrong.

``on_grid="true"``
    became ``False``. The flag is parsed as exact string equality to ``"True"``, so ``true``,
    ``TRUE``, ``1`` and a misspelling are all silently the negative case rather than errors.

``T_degC="NaN"``
    was admitted. Scored analyte cells are finite-checked; the design COORDINATES are not, so
    ``float("NaN")`` flowed into the manifest and into cluster identifiers containing ``"nan"``.

``93.40004`` and ``93.40005``
    became one condition. Both sides canonicalise with default ``%g``/``:g`` formatting, which keeps
    six significant digits, so distinct measured conditions merge into a single cluster — and a
    clustered range depends entirely on which outcomes move together.

Plus a fifth, about support rather than parsing: ``lookup_defined`` was copied from ``on_grid``
rather than derived from whether an optimal-grind record actually EXISTS at the same condition. A
row could declare a comparator that was not there.

So this module owns the declarative schema — what the columns are, which tokens are legal, what a
coordinate means — and validates a whole file before either implementation filters on it. It is
deliberately data plus a parser, not membership logic: production and the oracle still derive
inclusion, analytes, partitions and support separately, because that is the common mode round-9 and
round-10 broke and it must not be rebuilt here.

**What this does not do.** It checks structure, controlled tokens, coordinate finiteness and
parseability, and the internal consistency of the support declaration. It does NOT verify that the
numbers were transcribed correctly from Angeloni et al. (2023), that the units are what the column
names say, or that any value is physically plausible. That boundary is stated in the paper's
data-provenance text as well, because structural validation reads like source validation if nobody
writes down the difference.
"""

from __future__ import annotations

import csv
import pathlib
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation

SCHEMA_VERSION = 1

_REPO = pathlib.Path(__file__).resolve().parents[2]
SOURCE_CSV = _REPO / "puckworks" / "data" / "angeloni2023" / "bioactives.csv"

#: Controlled vocabularies. Values outside these fail with a row-specific diagnostic rather than
#: being dropped by a filter that cannot tell "not wanted" from "corrupt".
VARIETIES = ("Arabica", "Robusta")
GRINDS = ("C", "F", "O")
OPTIMAL_GRIND = "O"
HELD_OUT_GRINDS = ("C", "F")

#: The ONLY tokens accepted for `on_grid`, mapped explicitly. The controlled CSV writes exactly
#: these two. `true`, `TRUE`, `1`, `yes`, `` and misspellings are REJECTED, not read as False:
#: silently mapping an unknown token to the negative case is how source corruption becomes a
#: smaller corpus instead of an error.
BOOLEAN_TOKENS = {"True": True, "False": False}

#: Structural columns every row must carry. Analyte columns are declared by each consumer, because
#: which solutes the benchmark scores is a scientific choice and the two implementations must go on
#: making it independently.
REQUIRED_COLUMNS = ("sample", "variety", "T_degC", "p_bar", "granulometry", "on_grid")

#: Declared units, recorded so the paper's provenance text and this parser cannot drift apart. This
#: is a DECLARATION, not a verification: the column name says degrees Celsius, and nothing here can
#: confirm the article's table was in Celsius.
COORDINATE_UNITS = {"T_degC": "degree_Celsius", "p_bar": "bar"}


class SourceSchemaError(ValueError):
    """A source row is not what the schema says a source row is."""


# ─────────────────────────────────────────────────────────────────────────────────────────────
# Coordinates: lossless identity
# ─────────────────────────────────────────────────────────────────────────────────────────────


def parse_coordinate(raw, field: str, sample_id: str) -> Decimal:
    """One condition coordinate, as an exact decimal.

    ``Decimal`` rather than ``float`` because this value is an IDENTITY, not an input to arithmetic:
    it decides which observations share a cluster. Binary floating point is the wrong type for that
    even before the ``%g`` rounding, and converting back to ``float`` for the key would reintroduce
    the collision by a different route.

    Whitespace is REJECTED rather than stripped. In a controlled, hand-transcribed source file a
    stray space is evidence of damage, and normalising it away makes damaged data look clean.

    Both cell types are accepted, because the two consumers read the file differently and that
    difference is deliberate. The oracle parses the CSV itself and hands over the raw token, which
    is the exact source text. Production goes through ``puckworks.data``, whose typed loader has
    already turned numeric cells into floats — so the token is gone before this sees it, and the
    float is converted through ``repr`` (the shortest round-tripping form) to recover it exactly.
    A non-finite float still fails here, which is what the reproduced ``T_degC="NaN"`` needs:
    ``float("NaN")`` parses, so the typed loader admits it silently and only this check stops it.
    """
    if isinstance(raw, bool):
        raise SourceSchemaError("source row %s: %s is a boolean, expected a coordinate"
                                % (sample_id, field))
    if isinstance(raw, (int, float)):
        try:
            value = Decimal(repr(raw) if isinstance(raw, float) else raw)
        except InvalidOperation:
            raise SourceSchemaError("source row %s: %s is %r, which is not a decimal number"
                                    % (sample_id, field, raw)) from None
        if not value.is_finite():
            raise SourceSchemaError("source row %s: %s is %r, which is not finite; a design "
                                    "coordinate must name a real condition"
                                    % (sample_id, field, raw))
        return value
    if not isinstance(raw, str):
        raise SourceSchemaError("source row %s: %s is %s, expected a string or numeric cell"
                                % (sample_id, field, type(raw).__name__))
    if raw != raw.strip():
        raise SourceSchemaError("source row %s: %s is %r, which carries leading or trailing "
                                "whitespace; controlled source data is not silently trimmed"
                                % (sample_id, field, raw))
    if not raw:
        raise SourceSchemaError("source row %s: %s is empty" % (sample_id, field))
    try:
        value = Decimal(raw)
    except InvalidOperation:
        raise SourceSchemaError("source row %s: %s is %r, which is not a decimal number"
                                % (sample_id, field, raw)) from None
    if not value.is_finite():
        raise SourceSchemaError("source row %s: %s is %r, which is not finite; a design coordinate "
                                "must name a real condition" % (sample_id, field, raw))
    return value


def canonical_coordinate(value: Decimal) -> str:
    """The canonical, LOSSLESS string form of a coordinate.

    Numerically equal tokens share a key — ``9``, ``9.0`` and ``9.00`` are one condition, which is
    the behaviour the ``%g`` version was reaching for and got right. Numerically DISTINCT tokens
    never share one: ``93.40004`` and ``93.40005`` stay two conditions, which is what ``%g`` got
    wrong by keeping six significant digits.

    Plain (non-exponential) form, and ``-0`` written as ``0``, so the key is a stable identifier
    rather than a repr.
    """
    if not isinstance(value, Decimal):
        raise SourceSchemaError("a condition coordinate must be a Decimal, got %s"
                                % type(value).__name__)
    if not value.is_finite():
        raise SourceSchemaError("a condition coordinate must be finite, got %r" % (value,))
    text = format(value.normalize(), "f")
    if text.startswith("-") and Decimal(text) == 0:
        text = text[1:]
    return text


@dataclass(frozen=True, order=True)
class ConditionKey:
    """``(variety, T, p)`` as an exact, orderable identity.

    Used for support membership, partition membership and duplicate detection. Conversion to
    ``float`` happens only at a downstream arithmetic boundary, never for identity.
    """

    variety: str
    temperature_degC: Decimal
    pressure_bar: Decimal

    @property
    def cluster_id(self) -> str:
        """The published cluster identifier. Always carries the variety: without it the Arabica and
        Robusta conditions at one (T, p) collide into a single cluster."""
        return "%s|%s|%s" % (self.variety, canonical_coordinate(self.temperature_degC),
                             canonical_coordinate(self.pressure_bar))


# ─────────────────────────────────────────────────────────────────────────────────────────────
# Rows
# ─────────────────────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class SourceRow:
    """One validated source row. Every field has already been adjudicated against the schema."""

    sample_id: str
    variety: str
    granulometry: str
    on_grid: bool
    temperature_degC: Decimal
    pressure_bar: Decimal
    raw: dict

    @property
    def condition_key(self) -> ConditionKey:
        return ConditionKey(self.variety, self.temperature_degC, self.pressure_bar)

    @property
    def is_optimal_grind(self) -> bool:
        return self.granulometry == OPTIMAL_GRIND

    @property
    def is_held_out(self) -> bool:
        return self.granulometry in HELD_OUT_GRINDS


def _controlled(raw, field: str, allowed, sample_id: str) -> str:
    """A controlled string, validated BEFORE anything filters on it.

    This ordering is the whole point of the round-11 finding. The oracle tested ``row["variety"] not
    in VARIETIES`` and then stripped; production never stripped. Either way ``" Arabica "`` failed
    the membership test and the row was skipped as "not one of ours" — so a damaged controlled cell
    left the corpus silently rather than failing the source contract.
    """
    if not isinstance(raw, str):
        raise SourceSchemaError("source row %s: %s is %s, expected a string cell"
                                % (sample_id, field, type(raw).__name__))
    if raw != raw.strip():
        raise SourceSchemaError("source row %s: %s is %r, which carries leading or trailing "
                                "whitespace; a controlled value is not silently trimmed, because "
                                "trimming makes damaged source data look valid"
                                % (sample_id, field, raw))
    if raw not in allowed:
        raise SourceSchemaError("source row %s: %s is %r, which is not one of the declared values "
                                "%r" % (sample_id, field, raw, list(allowed)))
    return raw


def _boolean(raw, field: str, sample_id: str) -> bool:
    if not isinstance(raw, str) or raw not in BOOLEAN_TOKENS:
        raise SourceSchemaError(
            "source row %s: %s is %r, which is not one of the declared boolean tokens %r; an "
            "unrecognised token must fail rather than become False, because equality comparison "
            "silently turns 'true', 'TRUE' and '1' into the negative case"
            % (sample_id, field, raw, sorted(BOOLEAN_TOKENS)))
    return BOOLEAN_TOKENS[raw]


def parse_row(row: dict) -> SourceRow:
    """Validate and type one CSV row. Raises :class:`SourceSchemaError` naming the sample."""
    sample_raw = row.get("sample")
    if not isinstance(sample_raw, str) or not sample_raw or sample_raw != sample_raw.strip():
        raise SourceSchemaError("a source row has sample id %r, which is absent, empty or padded"
                                % (sample_raw,))
    if "|" in sample_raw:
        raise SourceSchemaError("source row %r: the sample id contains the observation delimiter "
                                "'|'" % sample_raw)
    return SourceRow(
        sample_id=sample_raw,
        variety=_controlled(row.get("variety"), "variety", VARIETIES, sample_raw),
        granulometry=_controlled(row.get("granulometry"), "granulometry", GRINDS, sample_raw),
        on_grid=_boolean(row.get("on_grid"), "on_grid", sample_raw),
        temperature_degC=parse_coordinate(row.get("T_degC"), "T_degC", sample_raw),
        pressure_bar=parse_coordinate(row.get("p_bar"), "p_bar", sample_raw),
        raw=dict(row))


def read_rows(path: pathlib.Path = None) -> list[dict]:
    """The raw CSV rows, comment lines skipped. No validation — that is :func:`parse_rows`."""
    path = SOURCE_CSV if path is None else path
    lines = [ln for ln in path.read_text(encoding="utf-8").splitlines()
             if not ln.lstrip().startswith("#")]
    reader = csv.DictReader(lines)
    missing = [c for c in REQUIRED_COLUMNS if c not in (reader.fieldnames or [])]
    if missing:
        raise SourceSchemaError("source CSV lacks required column(s) %r" % (missing,))
    return list(reader)


def parse_rows(rows=None, path: pathlib.Path = None) -> list[SourceRow]:
    """Every row, validated. One bad row fails the file: this is controlled, transcribed data."""
    rows = read_rows(path) if rows is None else rows
    parsed = [parse_row(r) for r in rows]
    seen = {}
    for r in parsed:
        if r.sample_id in seen:
            raise SourceSchemaError("duplicate sample id %r in the source" % r.sample_id)
        seen[r.sample_id] = r
    return parsed


# ─────────────────────────────────────────────────────────────────────────────────────────────
# Optimal-grind support, DERIVED
# ─────────────────────────────────────────────────────────────────────────────────────────────


def optimal_grind_support(rows, is_usable=None) -> dict:
    """``{ConditionKey: [sample_id, …]}`` for the conditions an O-grind record actually covers.

    ``is_usable`` lets the caller require the O row's scored analytes to be present and finite — a
    row whose measurements cannot be read is not lookup support, however present it is. It is a
    callback rather than a shared analyte map on purpose: production and the oracle must go on
    deciding what "scoreable" means independently.
    """
    support: dict = {}
    for row in rows:
        if not row.is_optimal_grind:
            continue
        if is_usable is not None and not is_usable(row):
            continue
        support.setdefault(row.condition_key, []).append(row.sample_id)
    return support


def reconcile_lookup_support(rows, support: dict) -> list[str]:
    """Compare each held-out row's DECLARED ``on_grid`` with the support that actually exists.

    Returns named problems; empty means the declaration and the data agree. The declaration is not
    silently overwritten — a disagreement is evidence about the source that a person has to
    adjudicate, and quietly preferring one side would hide exactly the defect this check exists to
    surface.

    Duplicate support also fails. If replicate optimal-grind records at one condition are ever
    scientifically intended, the aggregation rule has to be declared and tested; taking whichever
    row happened to be read first is not a rule.
    """
    problems: list[str] = []
    for key, sample_ids in sorted(support.items()):
        if len(sample_ids) > 1:
            problems.append(
                "condition %s has %d optimal-grind records (%s); the lookup comparator is defined "
                "by ONE record per condition and no replicate-aggregation rule is declared"
                % (key.cluster_id, len(sample_ids), ", ".join(sorted(sample_ids))))
    for row in rows:
        if not row.is_held_out:
            continue
        derived = row.condition_key in support
        if row.on_grid != derived:
            problems.append(
                "source row %s declares on_grid=%r but %s optimal-grind record exists at %s; the "
                "lookup comparator's support must be derived from the data, and a disagreement is "
                "a source defect to adjudicate, not a flag to overwrite"
                % (row.sample_id, row.on_grid, "an" if derived else "no", row.condition_key
                   .cluster_id))
    return problems


# ─────────────────────────────────────────────────────────────────────────────────────────────
# Preflight
# ─────────────────────────────────────────────────────────────────────────────────────────────


def preflight(rows=None, path: pathlib.Path = None, is_usable=None) -> dict:
    """Validate the whole source file and report it. Raises on any schema violation.

    Runs BEFORE either the production manifest or the oracle's expectation is built, so a malformed
    file is rejected once, by name, rather than being interpreted twice.
    """
    parsed = parse_rows(rows, path)
    support = optimal_grind_support(parsed, is_usable=is_usable)
    problems = reconcile_lookup_support(parsed, support)
    if problems:
        raise SourceSchemaError("the source's optimal-grind support declaration does not match its "
                                "data:\n  - %s" % "\n  - ".join(problems))
    held_out = [r for r in parsed if r.is_held_out]
    return {
        "schema_version": SCHEMA_VERSION,
        "n_rows": len(parsed),
        "n_held_out_rows": len(held_out),
        "n_optimal_grind_rows": sum(1 for r in parsed if r.is_optimal_grind),
        "n_optimal_grind_conditions": len(support),
        "n_lookup_defined_held_out_rows": sum(1 for r in held_out
                                              if r.condition_key in support),
        "varieties": list(VARIETIES),
        "grinds": list(GRINDS),
        "boolean_tokens": sorted(BOOLEAN_TOKENS),
        "coordinate_units": dict(COORDINATE_UNITS),
        "verification_boundary": (
            "structure, controlled tokens, finite decimal coordinates, parseability and "
            "optimal-grind support membership; NOT transcription, units or measurement accuracy "
            "against the source publication"),
    }
