# Targeted correction results — PR 321

**IMPLEMENTED_QUALIFICATION_INCOMPLETE.** All eight maxima qualify. Seven complete comparisons qualify as **NO_MATERIAL_DIFFERENCE** at the unchanged 1e-6 kg material margin. N400/h=.01 unconditioned remains unresolved because the historical prefix replay discrepancy has no demonstrated cause. PHYSICAL_VALIDATION=NOT_ESTABLISHED.

The same original-coordinate U, early bands, histories, primary schedules, windows, four operators, equal-child map, epsilon=1e-9 kg and delta=1e-6 kg were retained. B_MINUS_A and the exact structural common-past proof remain unchanged. No forward source, parameter, default, 004–006 artifact or EWP lock changed.

## Complete endpoint evidence

All maxima previously had null gaps and NUMERICALLY_UNRESOLVED status. Seven minima were already qualified; their old replay receipts are retained unchanged with exact dependency/delta bindings. The eighth historical minimum remains unresolved. Gaps below include both-branch response and forward allowances. A null is a missing qualification, never zero.

| Operator | Query | Checked outer B−A (kg) | Min status / complete gap (kg) | Max status / complete gap (kg) |
|---|---|---|---|---|
| N400-h0.02 | unconditioned | [-3.392064790123e-07, 4.219803233884e-07] | QUALIFIED / 1.667394258e-13 | QUALIFIED / 1.871748777e-13 |
| N400-h0.02 | conditioned | [-3.388984297596e-07, 4.061771080532e-07] | QUALIFIED / 1.589452959e-13 | QUALIFIED / 2.217599192e-13 |
| N400-h0.01 | unconditioned | [-3.392064461458e-07, 4.219828665682e-07] | null — historical prefix discrepancy | QUALIFIED / 2.770834924e-13 |
| N400-h0.01 | conditioned | [-3.388984138212e-07, 4.061797783907e-07] | QUALIFIED / 2.352363152e-13 | QUALIFIED / 3.153588068e-13 |
| N400-h0.005 | unconditioned | [-3.392064558437e-07, 4.219835202764e-07] | QUALIFIED / 4.021725567e-13 | QUALIFIED / 4.563596568e-13 |
| N400-h0.005 | conditioned | [-3.388984230397e-07, 4.061804622248e-07] | QUALIFIED / 3.873500033e-13 | QUALIFIED / 5.019808048e-13 |
| N800-h0.02 | unconditioned | [-3.398150883324e-07, 4.224767577221e-07] | QUALIFIED / 2.261207323e-13 | QUALIFIED / 2.784777829e-13 |
| N800-h0.02 | conditioned | [-3.394745998347e-07, 4.070698279717e-07] | QUALIFIED / 2.306050371e-13 | QUALIFIED / 3.090529733e-13 |

All queries have established compatibility, including the incomplete query through its qualified maximum. Each of the seven complete queries has opposite-sign compatible witnesses, but **no material-reversal witnesses**: the small sign reversal coexists with no material difference. The outer enclosure of the incomplete query is also within the material band; it does not replace the missing complete endpoint qualification.

## Witnesses and paired replay

Every fresh maximum replay used one original-coordinate reconstructed state for both complete plans. N800 used the declared equal-child lift. Each accepted state passed exact original/actual-inner rows and concentration bounds; paired forward uncertainty hulls were contained in every early band. Fresh maxima have bitwise-equal common-prefix mass/concentration traces, branch state, outlet increments and prescribed volume.

| Operator / query | Endpoint / evidence | A target mass (kg) | B target mass (kg) |
|---|---|---|---|
| N400-h0.02 / unconditioned | minimum, reused | 2.028498909663e-05 | 1.994578266040e-05 |
| N400-h0.02 / unconditioned | maximum, fresh | 1.639169982401e-05 | 1.681368010462e-05 |
| N400-h0.02 / conditioned | minimum, reused | 2.008576893416e-05 | 1.974687053877e-05 |
| N400-h0.02 / conditioned | maximum, fresh | 1.797956459426e-05 | 1.838574163327e-05 |
| N400-h0.01 / unconditioned | minimum, historical failed | 2.028498911255e-05 | 1.994578271941e-05 |
| N400-h0.01 / unconditioned | maximum, fresh | 1.639169750064e-05 | 1.681368031420e-05 |
| N400-h0.01 / conditioned | minimum, reused | 2.008576895812e-05 | 1.974687058621e-05 |
| N400-h0.01 / conditioned | maximum, fresh | 1.797956220545e-05 | 1.838574190547e-05 |
| N400-h0.005 / unconditioned | minimum, reused | 2.028498911653e-05 | 1.994578273417e-05 |
| N400-h0.005 / unconditioned | maximum, fresh | 1.639169691980e-05 | 1.681368036659e-05 |
| N400-h0.005 / conditioned | minimum, reused | 2.008576895985e-05 | 1.974687059382e-05 |
| N400-h0.005 / conditioned | maximum, fresh | 1.797956161144e-05 | 1.838574197664e-05 |
| N800-h0.02 / unconditioned | minimum, reused | 2.026903012415e-05 | 1.992921509081e-05 |
| N800-h0.02 / unconditioned | maximum, fresh | 1.640160539460e-05 | 1.682408207370e-05 |
| N800-h0.02 / conditioned | minimum, reused | 2.007452910802e-05 | 1.973505456657e-05 |
| N800-h0.02 / conditioned | maximum, fresh | 1.793942902486e-05 | 1.834649875486e-05 |

Target-window and entire post-branch volumes coincide here: both are 1e-5 m³ for A and B, checked with `FlowHistory.integral` and the unchanged 1.4210854715202002e-19 m³ allowance. Their definitions remain distinct in the general interface. Supporting individual-delivery intervals in CORRECTION_RESULTS.json are reused **outer-only** bounds, not replayed marginal extrema.

## Repair diagnosis

All eight retained raw maxima are identical. Their coarse-inventory exact row excess is 1.038442540999071e-20 kg, becomes 1.0331485850787316e-20 kg after the mass/concentration round trip, and remains 1.0172667173177134e-20 kg after box projection. The rounded legacy inventory receipt reports 8.000000000000002e-5 kg against 8e-5 kg (excess 1.3552527156068805e-20 kg). These are different arithmetic views of the same failed candidate, not contradictory acceptance tolerances. Full residuals, active/limiting original/inner/search rows, objective enclosures and mass movements are retained for every stage.

The three native empty-query legacy states already pass strict 007 checks. Reusing their raw optimizer vectors discarded a valid prior repair; the adapter now preserves the actual state and both provenance records. Five other maxima use the general all-row local concentration proposal, with no positive-residual tolerance or phase-only rebalance.

For the default conditioned reproducer, the old inward LP reported status 2 with zero iterations. The translated/scaled proposal found a representable state satisfying **that same old tightened problem** exactly, with 1.7652828167672757e-12 kg total movement (below the unchanged 7.68e-12 kg cap). Thus the old solver status was a numerical failure on a nonempty search problem. This establishes the scaling remedy for that reproducer; it does not independently diagnose every old solver invocation. Optional slack, rather than compulsory tightening of every row, also allows equality/dependent-row examples with no strict interior.

## Remaining prefix blocker

One diagnostic pair from the exact retained N400/h=.01 unconditioned minimum agrees bitwise before transport, after transport, and after immutable-array freezing. Both match the old A trace hash. Branch state, solute delivery, volume and concentration views agree. The old B trace hash differs; its arrays were not retained. The later archive audit localized fresh corruption between pre-transport serialization and parent receipt in two h=.005 future concentration views. Checked file/content transport now fails closed on such changes. Both affected maximum receipts were recomputed from four verified complete pre-transport outputs with exact input matches and unchanged replay checks, without new propagation or LPs. This does not prove the historical B failure had the same cause. Its first differing primary index, absolute time, phase/cell, raw values and ULP distance are therefore **unavailable**, not reconstructed from hashes. Arithmetic/nondeterminism, mutation, indexing and receipt construction remain hypotheses rather than established causes. No tolerance, operator or deterministic-execution correction was introduced; the fresh agreement alone does not erase the blocker.

## Discretization sensitivity

Fixed-operator qualification is separate from these changes; no continuum certificate or monotone-convergence assertion follows.

| Change | Query | Lower endpoint change (kg) | Upper endpoint change (kg) | Width change (kg) |
|---|---|---|---|---|
| timestep-.02-.01 | unconditioned | 3.286650021e-14 | 2.543179796e-12 | 2.510313296e-12 |
| timestep-.02-.01 | conditioned | 1.593835289e-14 | 2.670337501e-12 | 2.654399148e-12 |
| timestep-.01-.005 | unconditioned | -9.697883766e-15 | 6.537081409e-13 | 6.634060246e-13 |
| timestep-.01-.005 | conditioned | -9.218511557e-15 | 6.838341599e-13 | 6.930526714e-13 |
| mesh-N400-N800 | unconditioned | -6.086093201e-10 | 4.964343336e-10 | 1.105043654e-09 |
| mesh-N400-N800 | conditioned | -5.761700752e-10 | 8.927199185e-10 | 1.468889994e-09 |

N400/h=.01 unconditioned remains incomplete in the timestep comparison; all other fixed queries qualify. Sensitivity magnitudes do not repair its missing evidence or change 004–006 historical findings.

## Accounting and interpretation

Cumulative: **67/80 propagations, 77/160 LP calls, 648.190972/1800 charged seconds**, 528,908 exponential actions. Measured campaign/revalidation time is 588.190972 s; an additional conservative 60 s charge covers pre-budget full-array/hash/state inspections (including the measured 10.097655 s initial diagnosis). This upper charge is distinguished from stopwatch time. Corrections added 18 forwards and six LPs: two diagnostic forwards, sixteen maximum-witness forwards, five joint repair LPs and one old-problem diagnostic LP. No backward response was rerun. Seven minima reuse fourteen historical forwards with explicit unchanged-dependency bindings; their historical complete trajectories remain unavailable.

More modeled caffeine delivery is not better espresso, a taste recommendation, an experimental causal effect or a probability. No fitting, schedule search, private-corpus inspection/exhaustion, new data acquisition, laboratory work or successor occurred. Source-derived outputs retain Pannusch/Schmieder CC-BY-NC-3.0 attribution, separately from first-party code licensing.
