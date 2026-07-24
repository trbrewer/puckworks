# Paper A — Table 7 inventory-constraint dimensional audit (review MC5 / P0-4)

**Question (review MC5).** Paper A intersects the Angeloni Table 7 caffeine value with the
profiled `pannusch2024` inventory curve `c*(rate)` and reports an implied rate ≈ 0.95 with a
±10 % band ≈ 0.60–1.76. Is that a dimensionally secure quantitative rate constraint?

**Verdict: no — demote to qualitative.** The intersection equates two `mg mL⁻¹` numbers whose
physical volume bases are not shown to match, and the dry-coffee assay's basis alone is ambiguous
by ~3.4× — far larger than the ±10 % perturbation the manuscript propagated. The valley *passing
near* an independently measured inventory of the same order of magnitude is real and useful
**qualitatively** (an orthogonal inventory measurement could break the inventory–rate
compensation); the specific numeric rate is not.

## The two quantities being equated

| Quantity | Source | Value (caffeine) | Stated units | Provenance |
|---|---|---|---|---|
| `pannusch2024` `c_s0` | fitted to Schmieder fractions | **10.80** | mg mL⁻¹ (`docs/cards/pannusch2024.md`) | **fitted** — volume basis not independently stated; cup conc. is exactly linear in `c_s0` via the solver normalisation `cl1`, so its absolute scale is entangled with the fit |
| Angeloni Table 7 `C₀^s` | R&G dry-coffee assay | **12 540 mg L⁻¹ → 12.54 mg mL⁻¹** | `mg/L (= mg/kg, 1 kg = 1 L assumed)` (`docs/cards/angeloni2023.md` L53) | **measured** dry-coffee assay in mg kg⁻¹, reinterpreted as mg L⁻¹ under ρ = 1 g mL⁻¹ |

The analysis code (`puckworks/validation/slow/angeloni_bracket.py`, `table7_rate_constraint`)
converts the Table 7 value by `C0_s_mg_L / 1000` → mg mL⁻¹ and assigns it directly to `c_s0`. The
numeric conversion is arithmetically correct; the **basis identification** is the unverified step.

## The conversion, from first principles

The assay is *mass of solute per mass of dry roast-and-ground coffee* (mg kg⁻¹). To compare it with a
model solid-phase concentration *per unit volume* (mg mL⁻¹) requires a density/volume basis:

    C_vol [mg mL⁻¹] = assay [mg kg⁻¹] · ρ [kg L⁻¹] / 1000        (per unit volume of coffee, density ρ)

or, on a per-bed-volume basis,

    C_bed [mg mL⁻¹] = assay [mg kg⁻¹] · m_dose [kg] / V_bed [mL]

The `1 kg = 1 L` assumption is exactly the choice **ρ = 1.0 g mL⁻¹** — a value that matches neither
the bulk density of R&G coffee nor its roasted-particle (skeletal) density.

## Basis-sensitivity of the caffeine Table 7 value

Using assay = 12 540 mg kg⁻¹, dose = 20 g, and the Angeloni bed geometry R = 29.25 mm, H = 13.88 mm
(⇒ V_bed = πR²H = 37.3 cm³), ε_O = 0.305 (⇒ solid volume V_bed·(1−ε) = 25.9 cm³):

| Basis | ρ or volume | caffeine `c_s0` [mg mL⁻¹] |
|---|---|---|
| **`1 kg = 1 L` (assumed)** | ρ = 1.0 g mL⁻¹ | **12.54** |
| roasted-particle / skeletal density | ρ ≈ 1.3 g mL⁻¹ | ~16.3 |
| R&G bulk density | ρ ≈ 0.38 g mL⁻¹ | ~4.8 |
| per mL of **bulk bed** | 20 g ÷ 37.3 mL | ~6.7 |
| per mL of **solid phase** | 20 g ÷ 25.9 mL | ~9.7 |

Defensible bases span roughly **4.8–16.3 mg mL⁻¹ (≈ 3.4×)**. The typical densities used above are
order-of-magnitude literature values for roasted coffee (bulk ≈ 0.30–0.45 g cm⁻³; particle/skeletal
≈ 1.2–1.4 g cm⁻³); the conclusion does **not** depend on their exact values — even the narrowest
plausible pair (bulk 0.38 vs the assumed 1.0) already differs by ~2.6×, i.e. ≫ the ±10 % propagated.

## Why the numeric rate is not secure

The intersection reads the rate where `c*(rate) = C₀^s`. Sliding `C₀^s` across 4.8–16.3 mg mL⁻¹
moves the intersection far along the profiled valley — well outside the reported 0.60–1.76 band, and
potentially off the tested rate domain — so **"rate ≈ 0.95" is an artefact of the ρ = 1.0 choice**,
not a measured constraint. Compounding this, `pannusch2024`'s `c_s0` is itself **fitted** with an
unanchored volume basis, so even the *correct* physical basis for the assay is not known to coincide
with the model's. The near-agreement of the two numbers (10.80 vs 12.54) is suggestive but, given the
~3.4× basis ambiguity, cannot carry quantitative weight.

## What survives (the qualitative claim)

An independently measured solid inventory of the **same order of magnitude** as the profiled valley
is consistent with the valley and demonstrates the *design lesson*: an orthogonal inventory
measurement **could** break the inventory–rate compensation that the beverage endpoint alone cannot.
That is the defensible, useful statement — and it is unchanged by the unit-basis problem. What is not
defensible is presenting Table 7 as a numerical tie-breaker that fixes the rate at ≈ 0.95.

## Recommendation (implemented in this PR)

- **Manuscript (canonical `PAPER_A_DRAFT.md` + synced JFE conversion):** demote the Table 7
  intersection to **qualitative**; keep the "conditional one-dimensional intersection band" framing
  but state explicitly that it is qualitative, not a quantitative rate constraint, and cite this audit
  for the unit-basis reason. Remove the load-bearing "rate ≈ 0.95 / 0.60–1.76" numbers from the claim.
- **Guard:** add a required phrase locking the demotion (`qualitative, not a quantitative rate
  constraint`) so a future edit cannot silently re-promote it.
- **Code:** add a unit-basis caveat to `table7_rate_constraint`'s docstring (no computation change —
  the number remains available as an *illustrative, basis-conditional* diagnostic).
- **Not changed:** the `1 kg = 1 L` assumption stays recorded in the Angeloni card/manifest as the
  transcription convention; this audit documents its consequence for the Paper A claim.

## To make it quantitative later (owed; out of scope here)

A secure constraint needs (i) `pannusch2024`'s `c_s0` volume basis derived from the solver
normalisation, and (ii) the Angeloni assay mapped to that same basis using a measured roasted-coffee
density (bulk or skeletal, as appropriate) with propagated uncertainty. Absent either, Table 7 stays
qualitative.
