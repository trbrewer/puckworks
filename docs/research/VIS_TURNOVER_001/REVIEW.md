# Independent read-only review — 2026-11-05

A fresh reviewer session, separate from implementation, inspected the completed
bundle, audit code, focused tests, retained private receipts and source records.
The reviewer made no file changes and computed no scientific outcomes.

**Disposition: no open findings; the Step 0 stop is justified.**

Verified independently: all 465 source hashes; 11 accompanying metadata hashes;
no added files; zero machine labels across all 23,169 index records; separation
of parser identity from hardware and sensor authority; UNKNOWN control semantics
for absent/null/zero/-1 goals; the plan's requirement for both pressure bands in
the same groups; absence of groups and an outcome evaluator after qualification
failed; public CSV agreement with the private safe export; existing 20-shot/
10-user minima and conservative complementary suppression; EWP source pins,
code hashes and CPU accounting. The reviewer ran all eight new synthetic tests:
all passed.

One concrete P2 defect was found: the reproduction example asked for a new
private directory but `/usr/bin/time` opened its log before Python created that
directory. Implementation added `mkdir -p "$VIS_PRIVATE"` before the timing
command; the reviewer confirmed the correction. No scientific rule or result
changed. A separate implementation diff check also changed CSV line endings
to LF; counts were re-exported from the saved audit without rereading shots.

The reviewer accepted the disclosed limits: exact-path availability is not an
exhaustive source-schema search, and unchanged evidence cannot qualify this
matched comparison. Hosted CI was pending at review and is tracked on the PR
at the final head. Review does not imply physical validation or source-owner
endorsement.
