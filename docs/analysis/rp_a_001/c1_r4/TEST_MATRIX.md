# Test and mutation matrix

Negative tests cover empty evidence, classification-only change, dangling IDs for every record class, duplicates, wrong types, cross-case/requirement/question/channel/gate/model evidence, stale classification/result, contract fields, malformed intervals/uncertainty, terminal-status/result injection, and a self-consistent derivative-chain mutation.

Positive tests cover complete PASS, complete FAIL, legitimate partial and missing-uncertainty `UNRESOLVED`, no-comparator `NOT_EVALUATED`, justified `NOT_APPLICABLE`, dynamic/spatial only after genuine rule-out, actual additional-data pilot, and order determinism. Behavioral verifier independence monkeypatches producer high-level evaluation and confirms independent verification is unaffected/rejects retained drift.

QA: focused and full pytest, Ruff, Mypy, deterministic run/verify twice, generated/governance/paper checks, packaging/security, exact-head CI.
