# Mandatory small verification and evidence map

No full-mesh computation belongs in pytest. All model fixtures N<=12; manufactured
matrices enter the numerical core directly without forging FVDeliveryResponse
identities. Tolerances below were selected before full-mesh execution.

| Area | Independent check and required failure meaning |
|---|---|
| Exact nonunique simplex | M=2^-10; rational vertices and explicit duals, no second optimizer as oracle; conditional interval [M/4,5M/16] |
| Analytical accuracy | absolute optimization discrepancy <=1e-10*M; zero cases exactly zero |
| Fixed-model response | independently assembled dense concentration equations at small N; discrepancy <=1e-11*M and within declared allowances |
| Empty observations | exact delegation to 005 bound_delivery and replay_extrema, including injected failures; no new propagation |
| Joint feasibility | individually feasible (1/2,0,0) and (0,1/2,0), both [3M/8,M/2], jointly incompatible; positive checked phase-I margin |
| Boundary/conditioning | exact bands, near contradictions, nearly dependent rows, redundant/duplicate/reordered rows, wider bands and uninformative bands |
| Error semantics | nonzero response errors prevent false nominal rejection/over-tightening; nonempty outer/empty inner never means incompatible |
| Degenerate inventory | singleton, genuine zero, positive observation against zero, tiny representable M, normalization/product/allowance underflow and overflow |
| Witness integrity | original cell/phase/total plus every observation after representable reconstruction; old inventory-only repair cannot bypass rows |
| Forward replay | all early windows and target batched on same plan; containment of full uncertainty interval, not overlap; parent accuracy retained |
| Identity/input | all model/source/config/basis/mesh/clock/plan identities, chronology, immutable arrays/nested records, labels/count limits, booleans/nonfinite/reversed values |
| Solver/resource failure | iteration/time limit, malformed duals, failed response/replay, epsilon below available numerical resolution; every failure remains visible |
| Windows | off-grid endpoints, unequal Q/T knots, original primary-step schedule unchanged |
| Conservation | independent disjoint-subset lower-mass sum; duplicate/overlap handling, negative remainder contradiction, no kinetic response use |
| Serialization | deterministic strict JSON, no NaN, array hashes by default/full arrays optional, timing opt-in |
| Campaign controls | persistent counters, reserve-before-launch including failures, external per-call deadlines, total budgets, no output/worktree reset |
| Fine comparison | P splits phase mass to two children; P^T response/allowance remains distinct from native identity; replay P*m and preserve coarse freedom |

Analytical minimum dual: multiplier -1 on the negative early row gives residual
(0,0,1/8) and D=M/4. Signed maximum dual: multipliers -1/8 on total-upper and
-3/4 on early-upper give residual (0,1/16,0), D=-5M/16. The incompatible pair's
common-violation phase-I lower reference is M/10 when all rows are relaxed:
multipliers -1/5 on total-upper and -2/5 on each negative early row.
These exact references establish no Pannusch operating case or physical validity.
