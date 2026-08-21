# SCI-MD-003 / RP-A-001 C1-R2 correction addendum

Protocol `sci-md-003-rp-a-001/c1-r2` is additive to the unchanged
`component-response-atlas/v1`, original RP-A protocol, C1 protocol, and C1-R1
protocol. It is frozen before C1-R2 comparative results are inspected.

The discrimination universe consists of explicit requirements keyed by pair,
scenario, intervention, and comparison basis. Channel eligibility is keyed by
requirement, channel, adapter identity, and adapter version. Direct comparisons
use `DIRECT_NATIVE/1.0.0`. Measurement records must match their requirement and
eligibility exactly for pair, ordered explanations, scenario, channel, adapter,
comparability, intervention, and basis. Incompatible observation contracts are
distinct measurement options.

Coverage is represented by validated measurement-to-requirement edges. Only a
level-1/2, uncertainty-complete, robust measurement with an exact scenario and
adapter contract covers its requirement. The set-cover universe is relevant
requirement IDs, never bare pair IDs. An empty universe or any uncovered
requirement returns `NO_COMPLETE_MEASUREMENT_SET`. Validation independently
reconstructs requirements, measurement classifications, coverage edges, and all
equally minimal sets before independently deriving the decision.

The frozen apparatus gates are SIGN, PRESSURE_OR_FLOW_ORDERING, PRESSURE_LAG,
TRANSIENT_TIMING, FIRST_DRIP_TIMING, FLOW_MINIMUM, FLOW_RECOVERY, and
CROSS_CONDITION_TRANSFER. SIGN and PRESSURE_OR_FLOW_ORDERING are primary when a
matched response provides them; the remaining gates are conditional when the
matched scenario physically exposes the named quantity. Missing evidence for an
applicable gate is UNRESOLVED, never NOT_APPLICABLE. Survival requires every
applicable gate across every matched apparatus scenario to pass with level-1/2
and complete uncertainty. Absence of a matched apparatus comparison is
NOT_EVALUATED, not failure.

Decision precedence is apparatus survival, then dynamic-bed only after robust
apparatus rule-out and complete global requirement coverage, then spatial-only
after apparatus rule-out (or frozen irrelevance) and complete global coverage,
otherwise additional data. Apparatus gate completeness and global
discrimination completeness are reported separately. Apparatus survival may
coexist with global incompleteness only under its limited survival claim.

Versions are `rp-a-001-decision/v2`, `rp-a-001-coverage/v2`,
`rp-a-001-apparatus-gates/v1`, and `puckworks.response-atlas-export/v4`.
Seed remains 20260820 and the producer-evaluation cap remains 16. The cases,
producers, physical equations, uncertainty assumptions, and claim ceiling are
unchanged. No OpenFOAM, EWP mutation, RP-C.1 activation, evidence promotion,
publication claim, or merge is authorized.
