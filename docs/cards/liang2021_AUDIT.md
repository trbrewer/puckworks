# Cross-check audit: `liang2021.md` vs uploaded source

**Upload:** Liang, Chan & Ristenpart, "An equilibrium desorption model for the strength and
extraction yield of full immersion brewed coffee." *Sci. Rep.* **11**, 6904 (2021).
DOI 10.1038/s41598-021-85787-1. CC-BY.
**Standing card:** `/mnt/project/liang2021.md` (calibration-provider, effort S).
**Action taken:** no-redundancy rule — the upload is the paper of record for an existing
card, so this is an audit, **not** a second card. This document does not follow TEMPLATE.md.

**Standing status: CONFIRMED with one material correction.** Every transcribed equation
(1, 2–8, 11–18, 20–24) is faithful to the printed source, and I re-derived Eqs. 22 and 24
from Eqs. 9/10/16/20/21 to confirm the card's parse is the intended one. Every number in
the parameter table matches the paper to the digit. The validity-range list holds, the
interface mapping holds, and the verdict class (`calibration-provider`, effort S) is
unchanged.

Nine deltas below. **D1 is material** — it corrects a claim in the card that is true of
the paper as written but false of the model as written, and it adds a second calibration
product. D2, D3 and D4 change how much weight a gate can put on this source. The rest are
completeness and provenance.

---

## D1 — **Correction (material).** k_D and k_A *are* identifiable; the card says they are not

Card, Parameters section, closing line: *"Only the ratio K is identifiable; the kinetic
constants are not."* Card, Scope: *"The paper is silent on transient kinetics by design
(no rate constants reported); it predicts endpoints only."*

The second sentence is correct about the **authors**. It is not correct about the **model**.
Eq. (6) is not merely a steady-state condition — as printed it is a rate equation,
`dC_A/dt = −k_D C_A + k_A C_D`, and the authors only ever evaluate it at `dC_A/dt = 0`.
Carrying it with the conservation law of Eq. (4) at fixed `M_L`:

```
C_A + C_D = C_tot                        (Eq. 4 / 3a,3b)
dC_D/dt   = k_D(C_tot − C_D) − k_A C_D
          = k_D C_tot − (k_D + k_A) C_D
```

which integrates from `C_D(0) = 0` to

```
TDS(t) = K·E_max · M_g/M_L · (1 − e^{−t/τ}),    τ ≡ 1/(k_D + k_A)
```

i.e. the paper's own Eq. (11) endpoint multiplied by a single exponential approach. Because
K is fitted independently from the endpoint data, a fitted τ separates the constants
outright: `k_D = K/τ` and `k_A = (1 − K)/τ`. The data to fit τ is in the paper — see D2.

**What this buys the registry.** A second calibration product from a card currently
credited with one: an immersion relaxation time τ(T) at two brew ratios × three
temperatures, and τ(R_brew) at five ratios at 94 °C. That is the only transient anchor in
the registry for coarse-grind unpressurised immersion, and it makes this card a validation
target for the well-mixed batch family rather than an endpoint-only consistency check.

**Three caveats that must travel with any fitted τ, or the number will be over-sold:**

1. Eq. (6) is a lumped first-order law with **no particle-size dependence**. If the real
   mechanism is intragrain diffusion, τ ∼ r²/D and should scale ~5× across Liang's own
   grind range (x50 579 → 1311 µm). Liang ran dynamics at **one** grind (setting 5) only,
   so the form is untestable against its most obvious competitor on this data.
   Order-of-magnitude check at D = 1e-9 m² s⁻¹: r²/D = 5.6 min at x50 = 1160 µm, and
   3r²/D ≈ 17 min — consistent with the observed ~20 min plateau, so diffusion control is
   *not* excluded by the timescale. The first-order fit would be a surrogate, not a
   mechanism.
2. The 1-L brews were uninsulated and cooled through the run — see D3. Any τ from Fig. 2a
   is a temperature-**averaged** effective constant, not isothermal, and an Arrhenius fit
   across the three nominal temperatures inherits that.
3. `M_L` is treated as constant in the derivation above; strictly `M_L = M_w + M_d(t)`
   grows during extraction (Eq. 10). At R_brew ≥ 5 the correction is ≤ 4% and shrinks with
   R_brew, so this is second-order, but it should be stated rather than silently dropped.

**Suggested card edit:** replace the Parameters closing line with *"The paper reports only
the ratio K. The individual constants are recoverable from Eq. (6) plus the Fig. 2
transients — see audit D1 — but the authors do not perform that fit."* and soften Scope to
*"the authors report no rate constants, though Eq. (6) as printed is a rate law and Fig. 2
supplies the transients to close it."*

---

## D2 — **Omission (extractable data).** Figure 2 is absent from the card's data list

The card's Extractable data section lists Figs. 3, 4, 5, Table 1 and Supp. Fig. S1. It
does not list **Fig. 2**, which is 108 brews of TDS-versus-time:

- **Fig. 2a** — 1-L beaker, R_brew = 5 and 25 × 80/94/99 °C, sampled at 1, 3, 5, 10, 20,
  30, 45, 60 min (plus 90 min at R_brew = 5), triplicate → 18 brews. In-situ pipette
  sampling, no stirring.
- **Fig. 2b** — 300-mL beaker, R_brew = 12/14/16/18/20 × 94 °C, one destructive filtered
  measurement per brew at 3, 5, 8, 12, 20, 30 min, triplicate → 90 brews. Undisturbed
  until filtration, so this arm is free of the sampling-perturbation objection.

Per D1 this is the highest-value transcribable item in the paper for the registry, and it
was ranked zero. Recommend `data/liang2021_fig2a_tds_t.csv` and
`data/liang2021_fig2b_tds_t.csv`, and promoting them above Figs. 4/5 in priority.

Also unlisted, lower value: **Supp. Fig. S2** (brew temperature vs time — see D3),
**S3** (refractometer calibration curve — see D8), **S4** (TDS and E vs median particle
size at R_brew = 15, 99 °C), **S5** (E_oven linear regression whose intercept gives
R_vol = 0.0228). S4 and S5 are cited in the card's prose but not offered for transcription.

---

## D3 — **Validation caveat (unrecorded).** "80–99 °C" are *initial* water temperatures on cooling brews

Card, validity range: *"Hot brews 80–99 °C only."* This reads as a maintained condition.
It was not one. Methods: the beaker "sat on a room temperature wooden countertop with no
lid; no additional insulation was provided," and the authors state plainly that the
temperature decreased after addition (Supp. Fig. S2). Brew times were 20–60 min. The
temperature-insensitivity result — the paper's headline surprise, and the basis for the
card's independent-prediction (b) — is therefore obtained on brews that were **converging
toward the same room temperature** over the equilibration window, with the hotter brews
spending proportionally more of that window cooling.

This does not overturn the finding; the initial-temperature spread is 19 °C and the brews
plainly did not equilibrate instantly. But it means the paper does not establish
temperature-independence of K at *fixed* temperature, only that four *cooling schedules*
with different starting points land in the same place. Anything sourced from this card into
the backlog item **"observables: temperature effects"** must carry that qualifier, and a
τ(T) fit per D1 is fitting an effective constant over a moving temperature.

**Suggested card edit:** change the validity bullet to *"Hot brews, initial water
temperature 80–99 °C, uninsulated and cooling toward ~room temperature over the 20–60 min
brew (Supp. Fig. S2) — not isothermal; the temperature-insensitivity claim is over cooling
schedules, not over held temperatures."*

---

## D4 — **Internal inconsistency (quantitative).** The dynamics suites imply a lower K·E_max than the equilibrium suite, and the gap grows with brew ratio

The card takes `K·E_max = 0.215 ± 0.002` (Fig. 3, equilibrium suite) as the number.
Testing the plateau values the paper quotes for the *other two* suites against Eq. (11)
with that value:

| suite | R_brew | quoted plateau TDS | Eq. 11 pred. | obs/pred | implied K·E_max (Eq. 17) |
|---|---|---|---|---|---|
| 1-L dynamics (Fig. 2a) | 5 | 4.07 ± 0.15 % | 4.12 % | 0.987 | 0.2121 |
| 300-mL (Fig. 2b) | 12 | ≈1.65 % | 1.76 % | 0.937 | 0.2013 |
| 300-mL (Fig. 2b) | 20 | ≈0.95 % | 1.06 % | 0.893 | 0.1918 |
| 1-L dynamics (Fig. 2a) | 25 | 0.75 ± 0.04 % | 0.853 % | 0.880 | 0.1889 |

So `K·E_max` implied by the dynamics suites runs **0.189–0.212** against the equilibrium
suite's 0.215 — up to 12% low — and, critically, **the deficit is monotone in R_brew**.
The R_brew = 25 point is the sharpest: same coffee, same water, same beaker as the
equilibrium suite, and it implies E = 18.9%, well under the paper's flat-21% claim.

The obvious kinetic explanation does not work. The authors state (and Fig. 2a shows) that
**higher** brew ratios equilibrate **faster**; incomplete equilibration would therefore bias
the *low*-R_brew points, not the high ones. The observed sign is backwards.

Candidates the paper does not consider, none resolvable from the printed material:
(i) refractometer calibration slope error, which is a fixed *relative* error and would
produce exactly this ratio-independent-in-TDS/growing-in-R_brew pattern (at R = 25 the
absolute discrepancy is only 0.10 pp TDS); (ii) mild failure of the single-K assumption in
the dilute limit; (iii) the 300-mL arm differing in water (deionised) and coffee lot
(single-origin Rwanda Kivu Kanzu, not the four-coffee blend) — which explains its two rows
but not the 1-L R_brew = 25 row.

**Consequence for the gate.** The card's gate — *"reproduce K·E_max = 0.215 ± 0.002 from
digitized Fig. 3"* — is fine as written because it is confined to Fig. 3. But the ±0.002 CI
is a within-suite number and materially overstates how well this paper pins the immersion
equilibrium ceiling. **Recommend the card quote `K·E_max ≈ 0.19–0.215` as the honest
cross-suite range** wherever the value is exported as a bound on cameron2020, and reserve
0.215 ± 0.002 for the Fig. 3 refit gate specifically.

---

## D5 — **Gate ambiguity.** `R_brew > 3` (Fig. 3 caption) vs `R_brew = 2 excluded` (main text)

The card's gate says "refitting Eq. 11 (R_brew ≥ 3)" and its validity range says
"Validity R_brew ≥ 3." The paper says both things:

- Main text: at R_brew = 2 "the grounds looked like more like a moist sludge"; "we excluded
  **these three data points**" — three points is one triplicate, i.e. R_brew = 2 only, so
  R_brew = 3 was **in** the fit.
- Fig. 3 caption: "K = 0.717 ± 0.007 was determined by nonlinear regression with
  **R_brew > 3** data points" — strictly excluding R_brew = 3 as well.

Table 1 confirms R_brew = 3 was run. The E-averaging statement independently uses
"R_brew ≥ 3." Two of three statements favour the card's reading, so the card is probably
right, but a refit gate that reproduces 0.717 ± 0.007 to the stated CI will be sensitive to
which triplicate is dropped. Flag inline in the gate rather than picking silently.

---

## D6 — **Minor arithmetic.** The cupping caffeinated lumped fit is not the product of its own K

Both parameterisations are transcribed correctly in the card; the point is that they do not
agree with each other for one of the three fits:

| fit | K | K × 0.3 | lumped K·E_max fit | difference |
|---|---|---|---|---|
| 1-L blend | 0.717 | 0.2151 | 0.215 ± 0.002 | +0.0001 ✓ |
| cupping, decaf | 0.726 | 0.2178 | 0.218 ± 0.002 | +0.0002 ✓ |
| cupping, caffeinated | 0.792 | 0.2376 | 0.240 ± 0.002 | **+0.0024** |

The caffeinated discrepancy sits just outside the stated ±0.002 CI. The paper's own Fig. 5b
prediction line (23.79%) tracks `K × 0.3 = 0.2376`, not the lumped 0.240 — so the lumped
value is the odd one out, most likely a rounding or a separate regression not reconciled.
Immaterial physically; it matters only in that a gate reproducing the cupping fit should
target **0.2376**, not 0.240. Worth one parenthetical in the card's parameter table.

---

## D7 — **Confound list incomplete.** The cupping-vs-1-L K discrepancy has more candidates than the authors admit

Card: *"Cupping K exceeds 1-L K for the same nominal E_max; authors flag the discrepancy
(degassing/day-of-roast confound) as unresolved."* Accurate reporting of the authors. But
the two suites differ in at least five ways, and the authors discuss only the first:

1. **Degassing** — 1-L coffee rested 2 days then frozen at −20 °C; cupping coffee ground
   and brewed the same day as roasting, no degassing period.
2. **Water** — cupping used filtered water at **180 ppm dissolved ions** (SCA spec); the
   1-L suite used Nestlé Pure Life at pH 7.46; the 300-mL suite used **deionised** water.
   Three different waters across three suites. The paper itself states, under Eq. (15),
   that K "could depend on … the composition of the water" — so this is the authors'
   own nominated mechanism, left untested against their own design.
3. **Coffee** — 1-L was a four-coffee African Arabica blend; cupping was five commercial
   Peet's blends. Different lots entirely.
4. **Roast** — 1-L blend at Agtron **Gourmet** 67.2–70.4; cupping at Agtron **Commercial**
   26.9–54.6. These are different scales and cannot be compared directly; the cupping set
   is also substantially darker in practice (the authors note Peet's "light" is darker than
   the term usually implies).
5. **Grinder and grind** — Mahlkönig Guatemala Lab at setting 5 (x50 1160.5 ± 28.8 µm) vs
   Guatemala 710 at setting 10 (x50 548.3 ± 13.4 µm). A 2× difference in median size.

Item 5 is the one the paper's *own* results argue against mattering (equilibrium E is
grind-insensitive over 579–1311 µm), so it is weak. Items 2–4 are live and unexamined.
`[RS inference]` — the water-composition route (2) is the most economical single
explanation, since it is the only difference the authors' own theory names as acting on K,
but nothing in the paper discriminates it.

**Suggested card edit:** extend the validation paragraph's final clause to *"authors flag
degassing/day-of-roast; the suites also differ in water composition (180 ppm vs Nestlé Pure
Life vs DI), coffee lot, roast scale (Agtron Gourmet 67–70 vs Commercial 27–55) and
grinder — see audit D7. Treat the 1-L and cupping K values as two different materials, not
one material measured twice."*

---

## D8 — **Provenance (TDS convention).** All TDS is VST refractometer, calibrated against instant-coffee gravimetric standards

The card carries E values derived from TDS via Eq. (17) without recording how TDS was
measured. It was a **VST digital refractometer**, zeroed on distilled water, calibrated
against gravimetric solutions of Nescafé Clasico instant coffee at 0.5–4 g per 100 g
deionised water (Eq. 25, Supp. Fig. S3). Every TDS number in the paper is a refractometer
reading, not a gravimetric measurement of the brews themselves.

Two reasons this belongs on the card: (a) cross-source comparability — the registry holds
TDS from DE1 fixtures and from papers using dry-down gravimetry, and a refractometer-vs-
gravimetric convention difference is exactly the sort of ~few-percent offset the ROADMAP
normalization-hazards table exists to catch; (b) it is the cleanest candidate mechanism for
the D4 cross-suite offset, since a calibration slope error propagates as a fixed relative
error in TDS and hence in every E computed from Eq. (17).

Note also that the calibrant is **instant coffee**, whose refractive-index-per-unit-mass
relation need not match that of a brewed coffee's actual solute mix. Nothing in the paper
tests this.

---

## D9 — **Parameter table additions.** Values in the paper not carried on the card

Small, all useful for gates or for the grind stage:

| quantity | value | source type | why |
|---|---|---|---|
| TDS plateau, R_brew = 5, pooled over 80–99 °C | 4.07 ± 0.15 % | measured | D4 table; direct Eq. 11 check |
| TDS plateau, R_brew = 25, pooled over 80–99 °C | 0.75 ± 0.04 % | measured | D4 table |
| TDS at R_brew = 15, 99 °C, pooled over grinds | 1.36 ± 0.09 % | measured | grind-insensitivity magnitude |
| corr(TDS, x50) at R_brew = 15, 99 °C | −0.978 | measured | card says "weakly negatively correlated" without the number |
| corr(E, x50), same | −0.992 | measured | as above |
| grinder x50, Guatemala Lab settings 2–6 | 580 / 780 / 970 / 1160 / 1310 µm | measured | grind-stage reference, pairs with Supp. Fig. S1 |
| grinder x50, Guatemala 710 setting 10 | 548.3 ± 13.4 µm | measured | cupping suite |
| E spread across full grind range | ≈19–23 % | measured | bounds the "grind-insensitive" claim honestly |

---

## Overlaps section: three cards now bear on it that did not exist when it was written

The card's Overlaps names `cameron2020.extraction_bdf`, `foster2025`, `wadsworth2026` and
two backlog items. Since then:

- **`maille2024`** — well-mixed batch reactor with fitted fast/slow λ in the **seconds**
  range. Per D1, Liang's Fig. 2 gives the same class of quantity at **tens of minutes** on
  a ~1160 µm grind. These are not in conflict; they are the two ends of a grind-size lever
  arm on the same lumped-kinetics form, and together they are the beginnings of a τ(r) test
  that neither paper can run alone. This is the most productive new pairing.
- **`taip2025`** and **`zhai2022`** already name `liang2021` as the source that dominates
  them on immersion; that direction is recorded and needs no change.
- **`moroney2016.md`** (SIAM asymptotics) explicitly scopes out the *well-mixed* companion,
  Moroney et al., *J. Math. Ind.* **7**, 3 (2016) — Liang's ref 14 — which is **uncarded**.
  That paper is the direct modelling counterpart to Liang's regime, and Liang's Fig. 2 is
  candidate validation data for it. Flagging as an acquisition target, not resolving here.

---

## Verdict on the audit

**`liang2021.md` stands: `calibration-provider`, effort S.** The verdict line needs no
change — D1 adds a product but not enough work to move S, since fitting a one-parameter
exponential to digitized curves is the same order of effort as the digitisation already
budgeted.

## Judgment calls made here, for override

1. **Kept the verdict at effort S** despite D1 adding a τ(T) calibration product. Argument
   for M: the Fig. 2 digitisation is 108 brews across two figures, and a defensible τ fit
   needs the D1 caveats handled (non-isothermal, M_L drift). I judged that still S because
   no new machinery is involved. Easy to disagree.
2. **Did not treat D1 as grounds for a second card.** The τ product comes from the same
   equations and the same paper, and the split-card rule is for genuinely separable physics
   stages — this is one desorption model read at two times. One card, amended.
3. **D4 framing.** I present the cross-suite spread as a bound on the paper's precision
   rather than as an error in the paper. The alternative reading — that the quoted Fig. 2
   plateau values are eyeballed round numbers from a scatter plot and should not be held to
   three digits — is also available, and would deflate D4 considerably. I could not
   discriminate without the underlying points, which is itself an argument for the D2
   digitisation.
4. **D3 wording.** I stopped short of saying the temperature-insensitivity result is
   confounded, because the initial spread is real and large. "Not isothermal, and the claim
   is over cooling schedules" is the strongest statement the methods support.
5. **D7 item 2** is marked `[RS inference]` — the water-composition route is my nomination,
   not the authors'.
6. **Did not run the D1 fit.** No digitized Fig. 2 data exists yet; naming the computation
   and deferring it follows house practice.

## Registry amendments named, deferred to your next revision

- `liang2021.md`: Parameters closing line and Scope sentence per **D1**; validity-range
  temperature bullet per **D3**; export-range caveat on K·E_max per **D4**; gate ambiguity
  note per **D5**; parenthetical on the cupping lumped value per **D6**; confound list per
  **D7**; TDS-convention line per **D8**; table rows per **D9**; Extractable-data promotion
  of Fig. 2 and addition of S2–S5 per **D2**; Overlaps additions for `maille2024` and the
  uncarded Moroney well-mixed paper.
- `ROADMAP.md` normalization-hazards table (P1): candidate entry from **D8** — refractometer
  (VST, instant-coffee-calibrated) vs gravimetric TDS convention.
- Acquisition queue: Moroney, Lee, O'Brien, Suijver & Marra, "Coffee extraction kinetics in
  a well mixed system," *J. Math. Ind.* **7**, 3 (2016) — the uncarded immersion-transient
  counterpart identified above.
- `data/`: `liang2021_fig2a_tds_t.csv`, `liang2021_fig2b_tds_t.csv` added ahead of the
  existing Fig. 3/4/5 digitisation targets.

AUDIT VERDICT: standing card CONFIRMED with one material correction (D1) and eight
completeness/precision deltas — no change to class or effort — effort S to apply.
