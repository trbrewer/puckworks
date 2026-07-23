# Model card: Smrke 2024 — fines share and espresso extraction dynamics (fines-spiking study)

**Paper/thesis:** Smrke, S., Eiermann, A. & Yeretzian, C., "The role of fines in espresso extraction dynamics," Sci. Rep. 14, 5612 (2024). DOI 10.1038/s41598-024-55831-x. Open access (CC BY 4.0). Supplementary information online (incl. Fig. S1 flow-rate profiles); supplement not held in intake at card time.
**Stage(s):** grind (PSD/fines characterization), observables (EY, t_shot statistical prediction) · **Kind:** calibration (data source; statistical models are figure-only)
**Status:** LANDED (data-only, 2026-07-23) — figures digitized + manifest; consumer gate **S-A** (qualitative shape/slope-sign, `gate_smrke2024_fast_extraction_shape` on `cameron2020.extraction_bdf`) is live; the quantitative **S-B** point-match is deliberately deferred (blocked; unblock conditions below).

## Scope and mechanism
An experimental fines-spiking study, not a physics model. Espresso shots (20 g dose, 40 g beverage, 9 bar, single Costa Rica arabica, Bentwood Vertical 63 grinder) were pulled at six grinder settings (160–250 µm burr spacing), and at settings 190/210/250 additionally with 1, 2, or 4 g of pre-sieved fines (<120 µm sieve) substituted into the dose. Measured: full PSDs (Camsizer X2), dynamic beverage weight (load cell), extraction time, TDS/EY (VST refractometer), headspace VOCs (PTR-MS), and single-taster hedonic sensory. Headline mechanistic finding: within the tested range, added fines shift shots *along* a single EY-vs-time master curve rather than off it — the authors conclude fines act **only by reducing bed permeability**, not by changing the extraction mechanism. Three statistical models (one PLSR on whole PSDs, two polynomial regressions on X50 + Q100µm) predict extraction time and EY; none of their coefficients are published.

## Governing equations
The paper numbers no equations. Three statistical constructions, all figure-only:

1. **PLSR extraction-time model** (Fig. 4): t_shot = f(PSD density vector), fitted with the R "pls" package v2.8-1. Only the coefficient-vs-particle-size *profile* is published (as a plot): coefficients positive for sizes ≲150 µm, ≈0 for 150–250 µm, negative for >250 µm. No component count, loadings, or numeric coefficients given.
2. **MLR extraction-time model** (Fig. 5a): t_shot = second-order polynomial in X50 and Q100µm. The exact polynomial form (cross terms, which quadratics) is not stated; authors report both predictors "significantly contributing... with similar sized normalized model coefficients." No coefficients published.
3. **MLR extraction-yield model** (Fig. 5b): EY = f(Q100µm, X50, t_shot), same methodology. No coefficients published.

Supporting definitions (Methods): X50 = volume-weighted median particle size from projected particle area; Q100µm = volume share of particles < 100 µm ("share of fines"). A second-order polynomial relating fines share to burr spacing for unspiked samples is shown in Fig. 2 (black dashed) — again no coefficients.

Nothing is transcribable for implementation; any regression registered from this source would have to be refit registry-side `[RS]` from digitized figure data or the on-request raw data.

## Parameters
No model parameters are recoverable. Experimental constants and measured ranges:

| symbol / quantity | value | units | source |
|---|---|---|---|
| dose | 20 | g | nominal (measured to protocol) |
| beverage target | 40 | g | nominal (manually stopped) |
| brew pressure | 9 | bar | nominal (Black Eagle machine) |
| tamp force | 20 | kgF | nominal |
| grinder settings | 160, 170, 180, 190, 210, 250 | µm burr spacing | nominal (Bentwood dial, burr-spacing calibrated) |
| fines additions (at 190/210/250) | 1, 2, 4 g into 19, 18, 16 g | g | nominal |
| fines-fraction sieve cut | 120 | µm | nominal (Retsch sieve) |
| Q100µm threshold | 100 | µm | nominal (definition) |
| X50 range spanned | ≈230–360 | µm | measured (Fig. 2) |
| Q100µm range spanned | ≈15–31 | % | measured (Fig. 2) |
| extraction times spanned | ≈8–80 | s | measured (Fig. 3) |
| EY spanned | ≈16.5–21.5 | % | measured (Fig. 3) |
| EY at t < 10–15 s | 17–18 (>80% of max observed) | % | measured |
| practical max-EY time (this recipe) | >40 | s | assumed by authors from their data |
| replicates | 3 per condition | — | nominal |
| PLSR / MLR coefficients | not provided | — | — |
| water temperature, basket geometry (beyond "VST 20 g"), pressure/flow profile shape | not provided | — | — |

## Calibration and validation offered by the source
Statistical, internal-only. Fig. 5a/5b show predicted-vs-measured scatter with regression and (apparent) confidence/prediction bands, but **no R², RMSE, or cross-validation statistics are reported anywhere** — model quality must be judged by eye from the plots (visually, time predictions track 1:1 over 8–60 s; yield predictions over 16.5–21.5%). The PLSR is characterized only by its coefficient sign structure. No holdout, no second coffee, no second grinder or machine. The mechanistic claim (fines act only via permeability) rests on (i) spiked-fines points not deviating from the unspiked EY(t) cloud in Fig. 3 and (ii) no major flow-rate-profile anomalies (Supp. Fig. S1) — an absence-of-effect argument at n = 3 per condition, honestly framed by the authors as an assumption ("we assume the amount fines does not fundamentally change the extraction mechanism"). Sensory: single Q-grader, hedonic, explicitly not double-blind — authors disclaim it as optimization guidance only. PTR-MS compound IDs are tentative (formula-based).

## Assumptions and validity range
- **Single coffee, single roast (143 Colorette), single grinder, single machine, fixed recipe** (1:2 ratio, 9 bar, flat). The EY(t) master curve and the >40 s max-EY rule are recipe- and coffee-specific; the authors say maximum extraction yields "differ widely" across the literature.
- **Spiked fines ≠ native fines**: added fines were sieved (<120 µm) from finely ground coffee of the same roast, then shaker-homogenized. Shape/surface chemistry match native fines well, but spatial placement in the bed after homogenization may differ from grinding in situ; the design cannot detect placement effects.
- **Metric/sieve mismatch**: fines *metric* is <100 µm (Camsizer volume share); fines *fraction added* is <120 µm sieve cut. The 100–120 µm sliver is counted in the main peak by the metric but present in the spike. Flag on any transcription.
- Tested envelope: X50 ≈ 230–360 µm, Q100µm ≈ 15–31%, t_shot ≈ 8–80 s. Silent below/above; in particular silent on very fine grinds where uneven extraction / EY dip appears (their own citation of Lee et al.).
- No radial or axial resolution; no channeling observable; no temperature variation; permeability never computed (flow rate is the proxy — no k or Darcy analysis in the paper).
- PLSR sign structure (positive <150 µm, zero 150–250 µm, negative >250 µm) is conditional on this grinder's PSD family; coefficient profiles from collinear PSD bins are not causal weights.
- VOC findings are headspace-partitioning-confounded by the authors' own account (four hypothetical loss mechanisms offered); do not read Fig. 6 groups as extraction kinetics.

## Interface mapping
Inputs consumed: none (nothing executable). Outputs produced: none under contracts v0.1 without registry-side refits. Offline uses:
- **GrindState.fines_fraction operationalization:** Q100µm (volume share <100 µm, Camsizer projected-area basis) is exactly the quantity GrindState.fines_fraction wants, measured on the same instrument class as wadsworth2026_grindmap — supports a consistent cross-source definition (note wadsworth uses radius moments, not a fines threshold; an adapter/definition note is needed).
- **Validation target for the extraction chain:** the Fig. 3 EY(t) master curve at fixed 20 g/40 g/9 bar constrains cameron2020.extraction_bdf-style predictions — but only in SHAPE, not absolute EY (different coffee/grinder/machine). Realized as gate **S-A** (qualitative shape/slope-sign + fast-extraction sanity); the quantitative point-match is **S-B**, blocked (see Implementation estimate). At fixed brew ratio EY should collapse to a rising function of shot time across PSD manipulations; the turbo-efficiency constraint (17–18% EY at <15 s ≈ 80% of ceiling) is the necessary-not-sufficient clause S-A keeps.
- **Constraint on bed_dynamics hypotheses:** within Q100µm 15–31%, fines perturbations move shots along, not off, EY(t) — any fines-migration or mechanism-changing component (brewer2026 Rung B) must degenerate to a pure permeability effect in this envelope.
Coupling: offline data ingest only. No adapters can be built to the regressions themselves (coefficients unpublished).

## Extractable data
- **Fig. 3 → `data/smrke2024_EY_vs_time.csv`**: ~60 shots, EY vs t_shot, coded by added-fines mass (0/1/2/4 g). The core asset; digitization required (raw data available on request only).
- **Fig. 2 → `data/smrke2024_Q100_X50.csv`**: Q100µm vs X50 for all samples, spiked/unspiked flagged — real fines-fraction/median pairs for GrindState priors and pack_generator inputs.
- **Supp. Fig. S1 flow-rate profiles**: potentially the highest-value item — per-shot flow traces across the PSD grid would complement the DE1 fixture A trace on a second machine. Acquire the supplement before deciding on digitization effort.
- Fig. 4 PLSR coefficient sign structure: record qualitatively in the card only; not worth digitizing.
- Fig. 6 (PTR-MS groups A–D vs EY) and Fig. 7 (sensory vs time/EY): transcribe the group m/z membership lists (already in text) if the multi-class solute backlog item ever extends to volatiles; skip figure digitization.
- Raw datasets: **available on reasonable request** from corresponding author (S. Smrke, smrk@zhaw.ch) — not published. Candidate for the author-correspondence queue if Fig. 3/S1 digitization proves lossy.

## Overlaps and conflicts
- **wadsworth2026_grindmap (complements):** same instrument class (Camsizer X2), different grinder (Bentwood vs. Mahlkönig), overlapping goal (PSD → brew-relevant descriptors). Smrke adds the fines-share axis wadsworth's S-moment doesn't isolate, and directly serves the backlog item "grind: PSD models beyond bimodal" — its PLSR shows the main-peak position (>250 µm mass) matters with *opposite sign* to fines, i.e., two-descriptor (X50, Q100µm) minimum, confirming median-only is insufficient.
- **cameron2020.extraction_bdf (complements; gate data):** the Fig. 3 EY(t) curve at fixed 1:2/9 bar is an independent-machine check on Cameron-style EY predictions, and the paper explicitly confirms Cameron's fast-shot efficiency claim (their ref. 18) with 17–18% EY at <15 s. No conflict.
- **brewer2026.streamtube / Rung B fines migration (constrains):** no evidence here of fines changing mechanism or of migration signatures in flow profiles within the tested envelope — a negative constraint, not a refutation (no radial/axial resolution, n = 3).
- **wadsworth2026.permeability + brewer2026.pack_generator (complements):** "fines decrease permeability" is direction-consistent with the percolation/fines-sub-voxel treatments; Fig. 2 supplies measured (X50, Q100µm) pairs as realistic pack inputs. Note again: no k values here, only flow-rate/time proxies.
- **pocketscience2024 (complements):** both probe turbo vs. traditional styles; smrke has no radial resolution, pocketscience has no PSD variation — orthogonal datasets.
- **Backlog "extraction: multi-class solute chemistry" (informs, does not satisfy):** VOC groups A–D vs EY are headspace signals with tentative IDs and confounded loss mechanisms; not implementable chemistry. Non-volatile species (angeloni2023 territory) untouched.
- Predecessor capsule study (Eiermann 2020, their ref. 22) is not on file; it is where Q100µm originates — low acquisition priority since this paper supersedes it for espresso.
- No competition with any registered component; nothing here models transport.

## Implementation estimate
Effort S: digitize Figs. 2 and 3 into two CSVs with fines-spike flags and the 100/120 µm definition note; record PLSR sign structure and group m/z lists in metadata. No gate against the source is possible (no published coefficients or error statistics to reproduce).

### Consumer gate design — S-A (landed) and S-B (deferred, blocked)

The Impl-estimate originally proposed a **single** consumer gate: an extraction config at 20 g/40 g/9 bar must land its (EY, t_shot) pairs on the Fig. 3 curve within its scatter (~±0.5 pt EY at fixed t) across a Q100µm 15–31% sweep, and show EY ≥ 0.8 × EY_max by t = 15 s. **That gate is not achievable as written, cross-setup**, and rather than silently under-deliver against it (loosen the tolerance / cherry-pick conditions — the fudge the evidence-strength labels exist to catch), the gate is **split into two named gates** so the card records the deliberate downgrade and a documented path back up:

- **S-A — `gate_smrke2024_fast_extraction_shape` (LANDED, sign_or_compatibility / qualitative).** On `cameron2020.extraction_bdf`. Asserts only what survives cross-setup transfer: over an in-range EK43 grind sweep at 20 g:40 g / 9 bar, cameron's EY(t) (1) rises monotonically, (2) is **decelerating** (fast-rise-then-plateau), (3) reaches **≥ 80 % of its own final yield by t = 15 s** — a **necessary-not-sufficient** fast-extraction sanity check, the ONE clause of the original gate intact across setups (and matching smrke's own early shots, which sit at 0.77–0.83 of ceiling), (4) plateaus inside a plausible espresso EY band **bracketing** smrke's ceiling (a ballpark sanity band, not a match — the cross-coffee offset ≈ −30 % is *reported*, not asserted), and (5) across the sweep, longer shots yield more, i.e. the EY-vs-t_shot **slope sign matches smrke's Fig-3 master curve**. Reproduces **no** smrke curve; promotes nothing. Implementation: `puckworks/analysis/smrke2024_envelope.py`.

- **S-B — quantitative ±0.5 pt point-match (BLOCKED, not implemented).** The true "cameron's (EY, t_shot) lands on smrke's Fig-3 within ±0.5 pt at fixed t." Not honestly assertable now because cameron is calibrated on Cameron's coffee/EK43 grind/machine while Fig-3 is a **different coffee, grinder (Bentwood), and machine**, and smrke's absolute EY (16.4–21.3 %) is setup-specific — the ±0.5 pt window is **tighter than the cross-setup EY spread** (cameron's own plateau runs ≈ 30 % below smrke's ceiling here). **Unblock conditions (either suffices):** (a) a defensible **smrke-grind → extraction grain-size adapter** plus **ceiling calibration** to smrke's coffee — this is the **G5 grind-transfer gap** and belongs to G5, not this card; or (b) **smrke's raw (EY, t, PSD) data** (available on reasonable request, `smrk@zhaw.ch`), which would let the comparison be made in smrke's own setup terms without building the adapter first (the cheaper path — author-correspondence queue).

**Ceiling parameter:** `EY_MAX_SMRKE = 21.3 %` (digitized Fig-3 max; paper text ~21.5 %) is parked in `smrke2024_envelope.py` as a **smrke-specific** ceiling — a prerequisite for any S-B attempt and the band anchor S-A reports its cross-coffee offset against. It is **not** transferable to another coffee.

Dependencies: supplement acquisition (Fig. S1) before closing the data-transcription scope; author request for raw tables is the highest-payoff / lowest-cost S-B unblock.

VERDICT: data-only — no recoverable model (all regressions figure-only, coefficients unpublished), but a clean fixed-recipe EY(t) master curve spanning a controlled fines sweep. Lands a qualitative consumer gate (S-A) that cameron-style extraction has smrke's fast-rise/plateau morphology and Fig-3 slope sign; the quantitative fines-via-permeability point-match (S-B) is deliberately deferred with documented unblock conditions — effort S.
