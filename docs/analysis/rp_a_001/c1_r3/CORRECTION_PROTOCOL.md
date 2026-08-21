# SCI-MD-003 / RP-A-001 C1-R3 correction addendum

Protocol `sci-md-003-rp-a-001/c1-r3` is additive to and preserves the base
`component-response-atlas/v1` and the original, C1, C1-R1, and C1-R2 protocols.
It is frozen before C1-R3 comparative results are inspected.

Scientific questions are canonical records (`rp-a-001-scientific-questions/v1`).
Their relevance is determined solely from model roles, scenario, intervention,
comparison basis, and evidence domain. Requirements (`rp-a-001-requirements/v3`)
are derived from those questions before channel eligibility. A relevant
requirement remains in the coverage universe when every channel is unsupported,
uncertain, or lacks an adapter. Row order cannot affect relevance.

Every comparison uses a canonical observation contract
(`rp-a-001-observation-contract/v1`) binding quantity, channel, unit, value type,
control mode, pressure node/reference, flow/mass/concentration/deformation/
temperature bases, time origin, event, summary window, spatial/aggregation and
history bases, native/adapter status, adapter identity/version/contract hash,
uncertainty basis, and provenance. `NOT_APPLICABLE` and `NOT_PROVIDED` are
explicit. Level 1/2 requires every applicable field. Direct comparison uses
`DIRECT_NATIVE/1.0.0` and its canonical contract hash. Measurement options are
channel plus observation-contract hash.

The canonical apparatus rules (`rp-a-001-apparatus-gates/v2`) contain primary
SIGN and PRESSURE_OR_FLOW_ORDERING gates and conditional PRESSURE_LAG,
TRANSIENT_TIMING, FIRST_DRIP_TIMING, FLOW_MINIMUM, FLOW_RECOVERY, and
CROSS_CONDITION_TRANSFER gates. Applicability is derived from the frozen
question/scenario and capabilities, not record presence. The real evaluator
queries validated comparisons, predictions, measurements, observation
contracts, and uncertainty. It emits evidence-backed PASS, FAIL, UNRESOLVED, or
protocol-justified NOT_APPLICABLE, then aggregates apparatus status. Absence of
matched evidence is NOT_EVALUATED and never rule-out.

Coverage uses all RELEVANT requirement IDs. Only exact, robust, uncertainty-
complete level-1/2 measurement records create edges. Empty or uncovered
universes return NO_COMPLETE_MEASUREMENT_SET. Decision precedence
(`rp-a-001-decision/v3`) is apparatus survival, unique complete dynamic route
after apparatus rule-out, unique complete spatial-only route after its apparatus
prerequisite, otherwise additional data.

Semantic validation (`rp-a-001-semantic-validation/v2`) independently regenerates
canonical questions, requirements, observation contracts, channel eligibility,
measurement classifications, coverage edges and matrix, minimum sets, apparatus
specifications/evidence/results/status, decision, and summary counts. The sole
authoritative eligibility field in v5 is `channel_eligibility`.

Export schema is `puckworks.response-atlas-export/v5`. Seed is 20260820 and the
producer-evaluation cap is 16. Cases, producers, equations, uncertainty
assumptions, and claim ceiling remain unchanged. No EWP mutation, OpenFOAM,
RP-C.1, evidence promotion, publication claim, or merge is authorized.
