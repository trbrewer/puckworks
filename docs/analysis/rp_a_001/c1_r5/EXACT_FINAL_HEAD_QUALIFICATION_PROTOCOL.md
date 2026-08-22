# Exact-final-head qualification protocol

All source, tests, and tracked documentation are committed before candidate freeze. The resulting HEAD/tree are recorded externally and no later commit, amendment, rebase, or force push is permitted. Two fresh detached checkouts at that exact candidate run producer, verifier, export hashing, field comparison, complete QA, and exact-SHA CI.

Exact-head hashes and final attestation live only in the external evidence bundle, issue #243, and PR #244. A required tracked correction invalidates the candidate and restarts qualification at the additive successor. A replay hash from an earlier commit may never qualify a later commit.
