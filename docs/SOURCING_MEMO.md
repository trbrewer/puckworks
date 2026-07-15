# Sourcing pass — G1, G3, G10 (CHAT venue, 2026-07-12)

Three Tier-1 needs worked this session. Summary of what was found, at what
strength, and what remains owed. All grades use ROADMAP §0 vocabulary.

## Outcomes at a glance

| gap | result | strength | action needed from Tim | closes gap? |
|-----|--------|----------|------------------------|-------------|
| G1  | glass-bead retention/K_r closure (arXiv:2501.13361, open) | REFERENCE/qualitative | none — fetched clean | NO — analog shape prior; search-target stays OPEN |
| G3  | Ulka vibe-pump P-Q envelope + DE1-shape context | reference (endpoints) + qualitative (shape) | none for envelope; bench pull or Decent request for independent DE1 curve | PARTIAL — no independent DE1 curve is publicly obtainable |
| G10 | coffee-extract mu,rho vs T,TDS (Telis-Romero) | source_curve_reproduction for the EXTRACT rheology (espresso still extrapolated) | Table-1/Table-2 per-cell digitization for a mu(c,T) sensitivity study; independent espresso-TDS measurement | UPGRADED 2026-07-15 — telisromero2001 Eq(10)/(12)/(13) closures transcribed + gated (`data.telisromero_viscosity_pas`, `gate_g10_telisromero_closure`); bulk shot-TDS mu ~=1.06x water confirmed. Composition + dilute-end caveats stand |

## The honest headline
None of the three closes its gap at `independent` strength — and that is not a
search failure, it is the state of the literature:
- **G1:** nobody has published a saturation-resolved theta(psi) on a coffee bed.
  Confirmed the Foster/Vynnycky/Moroney 2025 lineage is sharp-front (the
  search-target's own negative filter). The glass-bead analog is the sanctioned
  fallback and is genuinely useful for making the Richards machinery *run*, but
  it stays reference-strength and the search target stays open.
- **G3:** the real DE1 pump model is closed ESP32 firmware (Decent confirms it
  exists, is country-calibrated, coefficients unpublished). Public sources give
  the Ulka physical envelope and the (important) fact that the curve is a concave
  droop, not a clean quadratic. An independent DE1 curve needs a TB bench pull or
  a §5.8 request to Decent.
- **G10:** the canonical source (Telis-Romero) measured instant-coffee
  processing concentrations; espresso TDS is below their dilute end. Espresso is
  Newtonian (good — validates the single-viscosity assumption) but its mu is an
  extrapolation. Real gain over "pure water everywhere," at reference-strength.

## Value delivered this session
1. Two gaps (G3, G10) move from "not on file / open search" to "reference-strength
   data on disk with a graded card and a clear owed-item for upgrade."
2. G1 gets a runnable closure so P3 hypothesis #2 stops being blocked on the
   *machinery* even while the *validation* stays open.
3. Each card states exactly what would upgrade it to independent — turning three
   vague "acquisition projects" into three specific, bounded asks.

## Proposed BLOCKED_INTAKE.md edits (for a CC commit)
Reclassify, do not delete:
- **G1:** keep 🔴 but add sub-line: "reference-strength glass-bead analog now on
  disk (sourcing_2026-07-12/g1_glassbead_retention/); search target still OPEN
  for a coffee measurement."
- **G3:** downgrade 🔴 -> 🟡 with note: "Ulka envelope + DE1-shape context on
  disk; independent DE1 curve needs TB bench pull or Decent request (new §5.8
  line)."
- **G10:** downgrade 🔴 -> 🟡 with note: "Telis-Romero reference envelope on disk;
  quantitative per-cell mu(T,c) needs Tim drop of Telis-Romero 2001/2000 tables
  (paywalled, bot-blocked here)."
- Add to §5.8 correspondence tracker: (a) Decent — DE1 pump characteristic /
  firmware model coefficients; (b) note Telis-Romero tables as an institutional-
  access drop.

## What is genuinely still owed after this session
- G1: a coffee-specific retention curve (unchanged — hardest, may not exist).
- G3: an independent DE1 P-Q curve (bench or Decent).
- G10: Telis-Romero numeric fit tables (Tim institutional access) for quantitative
  use; a true espresso-TDS rheology measurement for independent strength.
- G2 (not worked this session): still an acquisition project (ASIC proceedings /
  ellero2019 Elsevier).
- bruno2026 Table 2 (not worked): still a transcription pending host reachability.

NOTE: these are staged in `sourcing_2026-07-12/` (CHAT-venue output). Promotion
into `puckworks/data/` + MANIFEST.csv rows + BLOCKED_INTAKE edits is a CC-venue
commit (cards-before-code, manifest rule, §7.1 changelog entry). Do not hand-copy
without the manifest rows.
