# PUCKWORKS — PRODUCT-FIRST REPRIORITIZATION

> Recorded verbatim 2026-07-16 (Tim strategic input). This is a NORTH-STAR /
> vision document. Its single-choice recommendation (build the product vertical
> slice) is in tension with the parallel `NEXT_STEP_PLAN_2026-07-16.md`
> (publication-integrity convergence). The primary-lane decision is OPEN — see
> `STATE_OF_TRUTH.md`.

## NORTH STAR

A coffee drinker with no knowledge of the repository should be able to:

1. open Puckworks;
2. choose a bundled example or import a shot;
3. see what happened during the shot;
4. compare plausible explanations;
5. understand what was measured, fitted, predicted, or simulated;
6. receive one useful interpretation or next-measurement suggestion;
7. save or share the result.

Success is not "all scientific infrastructure is complete."

Success is: a new user gets a meaningful, trustworthy result without reading a
paper, editing Python, understanding the component registry, or locating
datasets.

## P0 — BUILD ONE COMPLETE VERTICAL SLICE

Do not begin with a broad dashboard. Build one narrow, polished, end-to-end
experience using a bundled shot and existing results.

Recommended first product: **THE BEST-UNDERSTOOD ESPRESSO SHOT** — based on
PV-19, with the PV-02 "machine versus puck" interaction.

User journey: "Explore a real espresso shot" → animated shot timeline (pressure,
commanded pressure, flow, cumulative beverage mass, first-drip event,
extraction/composition where supported) → three layers (WHAT WAS MEASURED / WHAT
THE MODELS CAN EXPLAIN / WHAT REMAINS UNKNOWN) → toggle competing explanations
(machine/headspace dynamics, static puck resistance, time-changing bed behavior)
→ result ("This feature is compatible with X." / "It does not prove Y." /
"Measurement Z would distinguish the explanations.") → shareable result card.

Use the current fixed named-shot configuration first. Do NOT require custom
uploads, the large Visualizer corpus, every registered model, or a universal
recipe recommendation in the first slice.

Definition of done: one command launches locally; a hosted/static version opens
without installing Python; all bundled assets redistributable; works from a
fresh checkout; user never needs a component identifier; every graph has a
plain-language explanation; every result carries a visible evidence badge; ends
with a useful takeaway or next measurement; exportable as page/image/JSON.

## P1 — CREATE A PRODUCT ENGINE UNDER THE UI

Build one stable product-facing API instead of the frontend calling registry,
harness, figures, and public-claim modules independently.

Conceptual interface: `ShotInput` (metadata, pressure/flow/weight traces,
optional commands/setpoints, temperature, composition) → `normalize_and_validate()`
→ `analyze_shot()` → `ShotExplanationBundle` (descriptive metrics, detected
events, compatible/incompatible explanations, model comparisons, evidence
badges, caveats, suggested next measurement, plots and source data).

Support: bundled_example, generic CSV, later DE1/Visualizer adapter. The public
app consumes only `ShotExplanationBundle` — never harness internals, registry
details, manuscript producers, source-card structure, corpus-freeze state, or
model-specific output formats.

Recommended package structure:
- `puckworks/product/` — input.py, normalize.py, engine.py, explanations.py, recommendations.py, bundle.py, examples.py
- `puckworks/adapters/` — generic_csv.py, de1.py, visualizer.py (later)
- `puckworks/app/` — web/static frontend, plotting/presentation, accessibility assets

Definition of done: bundled example and generic CSV use the same engine; one
documented input/output contract; model failures degrade gracefully; unsupported
fields warn understandably; units detected or explicitly requested; outputs
don't expose internal Python objects; engine testable without the UI.

## P1 — TURN PV-00 INTO THE CONTENT API, NOT THE USER EXPERIENCE

Retain the public claim registry (producer-backed numbers, evidence badges,
caveats, validity ranges, dataset references, drift detection, reproduction
commands). But `claims.json` should be an INPUT to the product, not the product.

Extend it with presentation fields: audience_question, short_answer,
observed_or_modeled, why_it_matters, practical_action, what_it_does_not_prove,
compatible_explanations, discriminating_measurement, visual_asset,
related_interactive, reading_level, share_text.

Add a `puckworks public build` that generates static site data, story pages,
claim cards, plot source data, accessible text alternatives, share images,
product-version metadata.

Definition of done: existing producer-backed integrity intact; a scientific
result change auto-updates/invalidates the product artifact; the frontend never
scrapes Markdown or paper drafts; every public result has a human-readable scope
statement; every simulation is visibly labelled as a simulation.

## P1 — BUILD "PUCK COURT" AS THE MAIN INTERACTION MODEL

PV-08 is the strongest candidate for the public product shell. Framing:
OBSERVATION (what did the machine measure?) → SUSPECTS (which mechanisms could
produce it?) → EVIDENCE (which models reproduce it? which nulls suffice? which
fail?) → VERDICT (what can be concluded? what's ambiguous?) → NEXT TEST (which
measurement discriminates the suspects?).

Initial cases: (1) a flow dip does not necessarily prove a changing puck; (2) a
later rising-flow trace cannot be explained by the tested static-bed nulls; (3) a
model can fit one grind and fail in transfer; (4) adding more physics can make a
composition worse; (5) the apparent fine-grind optimum weakened after correcting
the analysis.

Each case: one familiar question; one main interactive graphic; ≤3 competing
explanations initially; a visible evidence badge; one practical consequence; one
scope sentence; one suggested experiment.

Definition of done: ≥2 cases fully interactive; measured/simulated layers cannot
be visually confused; users explain the verdict without technical docs; every
case has a shareable URL/export; mobile and static/no-JS fallbacks communicate
the core result.

## P1/P2 — ADD SHOT IMPORT AFTER THE DEMO WORKS

Constrained generic format: time, pressure, flow, cumulative weight, optional
pressure/flow goal, optional temperature, optional metadata. Sequence: upload →
column/unit mapping → trace preview → data-quality warnings → descriptive
analysis → compatible features → explanation bundle.

Behaviour: never pretend an absent channel was measured; never silently guess
units; separate "your shot" from reference-dataset conclusions; process locally
by default; don't retain uploaded data by default; explain why a model is
unavailable; provide value with only pressure+weight.

Initial output (modest): shot phases; first-drip timing; pressure tracking;
flow-shape description; command-vs-achieved; similarity to bundled shapes;
plausible alternatives; next measurement. Do NOT initially output: universal
channeling score; flavor prediction; optimal recipe; inferred permeability as
ground truth; mechanism diagnosis from curve shape alone.

## P2 — MAKE THE NEXT-SHOT RECOMMENDATION THE PRACTICAL PAYOFF

PV-15. Not "change grind finer by 0.7" but e.g. "the trace is compatible with
both machine dynamics and a changing puck; a pressure-step shot would make those
diverge." Recommendation classes: collect a timed fraction; repeat the recipe;
change pressure holding others fixed; compare pressure- vs flow-controlled;
log an omitted channel; calibrate grinder physically; make no change (evidence
insufficient). Each explains: what uncertainty it targets; what two explanations
it separates; what measurement is required; what outcome favours each;
difficulty/equipment.

## WHAT RIGOR REMAINS PRODUCT-CRITICAL

Keep: producer-backed public numbers; observed/reconstructed/predicted/simulated
badges; unit validation; provenance; licensing checks; deterministic sample
outputs; end-to-end smoke tests; privacy-safe upload; clear caveat language;
golden-path regression tests.

Deprioritize until a feature needs them: publication-grade corpus-freeze
architecture; elaborate manuscript release bundles; exhaustive gate-to-paper
evidence graphs; complete registry normalization; paper-specific appendices;
statistical machinery for unexposed claims; broad CI taxonomy unrelated to the
golden path.

Rule: no infrastructure project becomes P0 unless it unlocks, protects, or
materially improves a user-visible workflow.

## REVISED IMPLEMENTATION ORDER (product-first)

PR1 product contract + bundled example; PR2 static public app shell; PR3 first
complete Puck Court case; PR4 second/third stories; PR5 generic shot import; PR6
uploaded-shot explanation; PR7 next-shot recommendation; PR8 packaging &
distribution; PR9 audience test & refinement.

## SINGLE-CHOICE RECOMMENDATION (this document)

Choose: **PUBLIC-VALUE PRODUCT VERTICAL SLICE.** Build PV-19 as the end-to-end
sample experience, present it through the PV-08 "Puck Court" interaction, use the
existing PV-00 claim layer as the trusted data spine. Then add generic shot
import and PV-15 next-experiment recommendations. Treat papers as technical
records and derivative outputs of the working tool, not the primary customer.
