# Evidence graph contract

The evaluator indexes each record type and rejects duplicate identity. It resolves requirement→question/contract, measurement→eligibility/requirement/contract/predictions/comparison/uncertainty, and gate evidence/result→gate/requirement/measurement links. Case, channel, pair, model sides, units, node/reference, time/event/window, spatial/aggregation, bases, adapter identity/version/hash, and provenance must agree.

Canonical identities use compact sorted-key JSON and stable SHA-256. Bounds must be ordered and finite; uncertainty finite and nonnegative. Classification is recomputed from lower intervals and uncertainty and compared to the retained derivative. Gate results and aggregate are recomputed only from validated evidence.

The independent verifier separately indexes, resolves, classifies, evaluates gates, aggregates apparatus state, and selects the decision. It may share schema/canonical primitives but must not call the producer high-level apparatus evaluator or final-decision function.
