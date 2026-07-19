"""Reference-basis ontology + fail-closed inventory-adapter primitives (PV-19B Phase 5, #70).

Admitting a SECOND common-scenario lens means overlaying a second model's concentration/yield output on
Cameron's. That is only meaningful if both are expressed on the SAME quantity basis (the same reference
volume / inventory), or a **tested, inventory-conserving** conversion maps one onto the other. This module
makes the basis a typed value (not prose) and provides the conversion machinery — deliberately
**fail-closed**: the only conversion registered today is the identity (same basis), so every cross-basis
request raises. No cross-basis conversion has been validated against data, therefore none is offered, and
no second lens can be admitted by machinery that silently invents a scale factor.

Nothing here changes any model's numerics; it is scaffolding for a future, evidence-backed adapter.
"""
from __future__ import annotations

import dataclasses

# ── finite quantity-basis vocabulary (the reference volume / inventory a quantity is expressed on) ──
QUANTITY_BASES = (
    "bed_volume",            # per unit packed-bed volume (Cameron single-pool EY/TDS)
    "grain_volume",          # per unit grain volume incl. internal pores (Grudeva)
    "per_bed_cell",          # per discretized bed-depth cell (Mo)
    "per_species",           # per chemical species, not a single pool (Pannusch)
    "liquid_phase_profile",  # liquid-phase concentration profile along depth
    "flow_trend",            # a relative flow/extraction TREND, not an absolute yield (Roman-Corrochano)
    "unspecified",           # basis not established (treated conservatively; never overlaid)
    "not_applicable",
)

# Cameron is the current common-scenario lens; a second EY/TDS lens must reconcile TO this basis.
COMMON_LENS_BASIS = "bed_volume"


@dataclasses.dataclass(frozen=True)
class BasisSpec:
    component_id: str
    quantity_basis: str
    observable: str
    note: str = ""

    def __post_init__(self):
        if self.quantity_basis not in QUANTITY_BASES:
            raise ValueError(f"{self.component_id}: quantity_basis {self.quantity_basis!r} not in "
                             f"QUANTITY_BASES")


# authoritative typed basis per component (sourced from the cards / registry; prose lives in the audit)
_BASES: dict[str, BasisSpec] = {
    "cameron2020.extraction_bdf": BasisSpec(
        "cameron2020.extraction_bdf", "bed_volume", "single-pool EY/TDS",
        "Cameron c_s0 = 118 / phi_s on a bed-volume basis"),
    "grudeva2025.reduced": BasisSpec(
        "grudeva2025.reduced", "grain_volume", "grain-volume concentration",
        "grain volume incl. internal pores — not comparable to bed-volume"),
    "mo2023_2.coupled_bed": BasisSpec(
        "mo2023_2.coupled_bed", "per_bed_cell", "bed-depth-resolved concentration",
        "absolute yield needs one inventory scale to a bed-volume basis"),
    "pannusch2024.solver": BasisSpec(
        "pannusch2024.solver", "per_species", "multi-species concentrations",
        "per-species (caffeine/trigonelline/CGA); a justified per-species->pool collapse is required"),
    "romancorrochano2017.extraction": BasisSpec(
        "romancorrochano2017.extraction", "flow_trend", "relative extraction trend",
        "a trend, not an absolute EY/TDS on a comparable basis"),
}


def basis_of(component_id: str) -> BasisSpec:
    """The typed reference basis of a component (UNSPECIFIED when none is on record — never guessed)."""
    return _BASES.get(component_id, BasisSpec(component_id, "unspecified", "unknown",
                                              "no reference basis on record"))


def all_bases() -> list[BasisSpec]:
    return [basis_of(c) for c in sorted(_BASES)]


# ── inventory-conserving conversion primitives (fail-closed) ────────────────────────
class UnsupportedConversion(Exception):
    """Raised when no VALIDATED inventory-conserving conversion is registered for a basis pair. This is
    the default for every cross-basis pair — the framework never invents a scale factor."""


class InventoryNotConserved(Exception):
    """Raised when a conversion does not conserve total solute inventory within tolerance."""


@dataclasses.dataclass(frozen=True)
class ConversionRule:
    from_basis: str
    to_basis: str
    validated: bool
    provenance: str


# The ONLY registered conversion is the identity (same basis, exact, trivially conserving). No
# cross-basis rule is registered because none has been validated against data — so cross-basis conversion
# fails closed. Adding a rule here later REQUIRES validated=True and a conservation test.
_RULES: dict[tuple, ConversionRule] = {
    (b, b): ConversionRule(b, b, True, "identity (same basis)") for b in QUANTITY_BASES
}


def conversion_rule(from_basis: str, to_basis: str) -> ConversionRule | None:
    return _RULES.get((from_basis, to_basis))


def total_inventory(values, cell_measures) -> float:
    """Total solute inventory = sum(concentration_i * measure_i) — the quantity a basis conversion must
    conserve. `cell_measures` are the per-cell volumes/masses that define the basis."""
    vals = list(values)
    meas = list(cell_measures)
    if len(vals) != len(meas):
        raise ValueError("values and cell_measures must have equal length")
    return float(sum(v * m for v, m in zip(vals, meas)))


def assert_inventory_conserved(before_total: float, after_total: float, *, rel_tol: float = 1e-9) -> None:
    """Fail-closed conservation check: total inventory before == after within `rel_tol`."""
    denom = max(abs(before_total), abs(after_total), 1e-300)
    if abs(after_total - before_total) / denom > rel_tol:
        raise InventoryNotConserved(
            f"inventory not conserved: before={before_total!r} after={after_total!r} "
            f"(rel err {abs(after_total - before_total) / denom:.3e} > {rel_tol:.1e})")


def convert_inventory(values, from_basis: str, to_basis: str, *, cell_measures_from=None,
                      cell_measures_to=None):
    """Convert a per-cell concentration series from one basis to another **only** through a registered,
    validated, inventory-conserving rule. Today that is exclusively the identity; every cross-basis
    request raises UnsupportedConversion (fail-closed). When a real rule is added it must conserve
    total inventory or the result is rejected.

    Returns the converted values (a list)."""
    if from_basis not in QUANTITY_BASES or to_basis not in QUANTITY_BASES:
        raise ValueError(f"unknown basis in conversion {from_basis!r}->{to_basis!r}")
    rule = conversion_rule(from_basis, to_basis)
    if rule is None or not rule.validated:
        raise UnsupportedConversion(
            f"no validated inventory-conserving conversion {from_basis!r}->{to_basis!r}; refusing to "
            f"invent a scale factor (a tested rule must be registered first)")
    if from_basis == to_basis:                          # identity: exact, conserving by construction
        return list(values)
    # a real cross-basis rule (none today) would transform here; guard conservation regardless
    converted = list(values)                            # pragma: no cover - no cross-basis rule exists yet
    if cell_measures_from is not None and cell_measures_to is not None:  # pragma: no cover
        assert_inventory_conserved(total_inventory(values, cell_measures_from),
                                   total_inventory(converted, cell_measures_to))
    return converted


# ── second-lens admissibility (mechanical, from the typed basis + registered rules) ──
def adapter_readiness(component_id: str) -> dict:
    """Can this component be overlaid as a SECOND common-scenario (EY/TDS) lens on Cameron's basis? Only
    if it shares Cameron's basis OR a validated inventory-conserving conversion to it is registered, and
    its code rights are not blocked. Everything is derived — no prose judgement here."""
    from puckworks import rights
    spec = basis_of(component_id)
    rights_blocked = rights.is_code_rights_blocked(component_id)
    same_basis = spec.quantity_basis == COMMON_LENS_BASIS
    rule = conversion_rule(spec.quantity_basis, COMMON_LENS_BASIS)
    has_validated_conversion = bool(rule and rule.validated and spec.quantity_basis != COMMON_LENS_BASIS)
    admissible = (same_basis or has_validated_conversion) and not rights_blocked \
        and spec.quantity_basis not in ("unspecified", "flow_trend", "not_applicable")
    if rights_blocked:
        blocker = "code rights blocked (see rights registry / #73)"
    elif spec.quantity_basis == "flow_trend":
        blocker = "provides a flow/extraction trend, not an absolute EY/TDS — overlay would upgrade evidence"
    elif spec.quantity_basis == "unspecified":
        blocker = "no reference basis on record"
    elif same_basis:
        blocker = ""
    elif has_validated_conversion:
        blocker = ""
    else:
        blocker = (f"basis '{spec.quantity_basis}' differs from Cameron's '{COMMON_LENS_BASIS}' and no "
                   f"validated inventory-conserving conversion is registered")
    return {"component_id": component_id, "quantity_basis": spec.quantity_basis,
            "common_lens_basis": COMMON_LENS_BASIS, "same_basis": same_basis,
            "has_validated_conversion": has_validated_conversion, "code_rights_blocked": rights_blocked,
            "admissible_as_second_lens": admissible, "blocker": blocker, "note": spec.note}


def _second_lens_candidates() -> list:
    import puckworks
    return sorted(c.name for c in puckworks.components()
                  if c.stage == "extraction" and c.execution_role == "runtime"
                  and c.name != "cameron2020.extraction_bdf")


def build_basis_report() -> dict:
    rows = [adapter_readiness(c) for c in _second_lens_candidates()]
    admissible = [r["component_id"] for r in rows if r["admissible_as_second_lens"]]
    return {
        "report": "puckworks-lab-reference-basis-readiness",
        "common_scenario_lens": "cameron2020.extraction_bdf",
        "common_lens_basis": COMMON_LENS_BASIS,
        "quantity_bases": list(QUANTITY_BASES),
        "registered_conversions": sorted(f"{k[0]}->{k[1]}" for k, v in _RULES.items() if v.validated),
        "candidates": rows,
        "admissible_as_second_lens": admissible,
        "conclusion": ("No extraction candidate is admissible as a second common-scenario lens: each is on "
                       "a different quantity basis with no validated inventory-conserving conversion "
                       "registered (or is rights-blocked / a trend). Only the identity conversion is "
                       "registered, so the machinery cannot admit a lens without a tested rule. NO second "
                       "lens is added."
                       if not admissible else f"Admissible: {', '.join(admissible)}"),
        "boundaries": ["no cross-basis conversion is invented (fail-closed)",
                       "a conversion must conserve total solute inventory",
                       "a flow trend is not an absolute EY/TDS", "model agreement is not validation"],
    }


def canonical_json(report: dict) -> str:
    import json
    return json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def render_markdown(report: dict) -> str:
    lines = ["# Guided Pull Laboratory — reference-basis second-lens readiness", "",
             f"_Common-scenario lens: **{report['common_scenario_lens']}** "
             f"(basis `{report['common_lens_basis']}`)._", "",
             f"Registered inventory conversions (identity-only today): "
             f"`{', '.join(report['registered_conversions'])}`", "", "## Candidates", ""]
    for r in report["candidates"]:
        lines.append(f"### `{r['component_id']}` — basis `{r['quantity_basis']}`")
        lines.append(f"- admissible as a second lens: **{r['admissible_as_second_lens']}**")
        lines.append(f"- {r['blocker'] or 'no blocker'}")
        lines.append("")
    lines += ["## Conclusion", "", report["conclusion"], "", "## Boundaries", ""]
    lines += [f"- {b}" for b in report["boundaries"]] + [""]
    return "\n".join(lines)


def main(argv=None) -> int:
    import argparse
    import sys
    ap = argparse.ArgumentParser(prog="puckworks.product.reference_basis", description=__doc__)
    ap.add_argument("--format", choices=["md", "json"], default="md")
    a = ap.parse_args(argv)
    report = build_basis_report()
    sys.stdout.write(canonical_json(report) if a.format == "json" else render_markdown(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
