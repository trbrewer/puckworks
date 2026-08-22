# Candidate finalization protocol

This tracked record contains no replay hash and makes no future exact-head claim. After this and every other intended tracked file is committed, the resulting commit is frozen externally. No tracked file is changed afterward.

Two detached checkouts at that exact HEAD/tree run producer and verifier, field-by-field export comparison, complete declared-extra QA, normal push, and exact-SHA CI. Exact-head hashes and qualification are retained only in the external C1-R5 evidence bundle and GitHub records. Any needed tracked correction creates an additive successor and restarts the entire exact-head sequence.
