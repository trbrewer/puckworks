"""puckworks.inventory — A4 SoluteInventory providers (ledger A4 / gap G6).

Builds a `contracts.SoluteInventory` (per-species initial chemistry) from a
measured roasted-chemistry source, so per-species inventory can flow to the
per-species extraction kinetics (pannusch2024 / romancorrochano2017). This is the
carrier that closes the G6 *inventory ↔ kinetics* link at the CONTRACT level.

STRENGTH / SCOPE (bruno card, emphatic): the source is a TOTAL roasted-bean
content, NOT an extractable solid inventory c_s0. This module provides a
reference PRIOR and cross-check ONLY -- it does NOT convert content to c_s0 (that
needs a per-species extractability factor Bruno does not measure), and it never
runs `Bruno-ODE -> extraction`. `SoluteInventory.extractable_fraction` is left
None (unknown) so a consumer cannot silently mistake content for c_s0.
"""
from puckworks import data as _d
from puckworks.contracts import SoluteInventory

# bruno2026 Table-2 label -> canonical species name. The three marked (pannusch)
# overlap the multi-solute extraction kinetics; the CGA family maps to the
# caffeoylquinic-acid isomers (5-CGA is 5-CQA, the dominant chlorogenic acid).
_BRUNO_CANON = {
    "Caffeine": "caffeine",            # pannusch, romancorrochano
    "Trigonelline": "trigonelline",    # pannusch
    "5-CGA": "5-CQA",                  # pannusch (5-caffeoylquinic acid)
    "3-CGA": "3-CQA",
    "3,5-diCGA": "3,5-diCQA",
    "Ferulic acid": "ferulic_acid",
    "Tartaric acid": "tartaric_acid",
    "Citric acid": "citric_acid",
    "Acetic acid": "acetic_acid",
    "Lipids": "lipids",
}

# the canonical species the multi-solute extraction models (pannusch2024) carry,
# i.e. where a Bruno inventory prior can actually meet a kinetic model
PANNUSCH_LINKABLE = ("caffeine", "trigonelline", "5-CQA")

_BRUNO_ORIGINS = ("Mexico", "Rwanda", "Nicaragua", "Indonesia")


def bruno_solute_inventory(origin):
    """A4 SoluteInventory for one bruno2026 origin (Mexico/Rwanda = Arabica;
    Nicaragua/Indonesia = Robusta). REFERENCE-strength TOTAL-content prior
    (mg/kg roasted powder; lipids % w/w dry basis) -- NOT c_s0; extractable
    fraction UNKNOWN (left None). Provenance carried."""
    rows = [r for r in _d.bruno_roasted_composition() if r["origin"] == origin]
    if not rows:
        raise KeyError("unknown bruno origin %r (have %s)" % (origin, _BRUNO_ORIGINS))
    species = {}
    for r in rows:
        canon = _BRUNO_CANON.get(r["compound"], r["compound"])
        species[canon] = dict(amount=float(r["mean"]), sd=float(r["sd"]),
                              unit=r["unit"], basis=r["basis"])
    return SoluteInventory(
        species=species, origin=origin,
        source="bruno2026 Table 2 (10.1038/s41598-026-43923-9); "
               "data/bruno2026/roasted_composition",
        strength="reference (independent measured roasted chemistry; "
                 "TOTAL content, not extractable c_s0)",
        extractable_fraction=None)   # UNKNOWN by design (bruno measures no c_s0)


def bruno_all_inventories():
    """All four origins -> {origin: SoluteInventory}."""
    return {o: bruno_solute_inventory(o) for o in _BRUNO_ORIGINS}


def species_ratio(name, num_origin, den_origin):
    """Content ratio of a canonical species between two origins (e.g. a
    Robusta/Arabica caffeine ratio) -- the reference PRIOR / cross-check that a
    kinetic model's per-species inventory ordering can be sanity-checked against.
    Ratios of a total-content prior; still not c_s0."""
    a = bruno_solute_inventory(num_origin).amount(name)
    b = bruno_solute_inventory(den_origin).amount(name)
    if a is None or b is None:
        return None
    return a / b
