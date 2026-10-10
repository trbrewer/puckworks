# 010 continuation handoff

**FULL_REFERENCE_QUALIFICATION_INCOMPLETE.** The one authorized replacement solved through t=8 but failed a dense capture commitment before serialization. No trustworthy replacement anchor was obtained; all thirteen outstanding frozen rows remain NOT_RUN. No further full simulation was launched. PHYSICAL_VALIDATION=NOT_ESTABLISHED.

## Separate dispositions

| Area | Disposition |
|---|---|
| Mathematical/source contract | COMPLETE for the unchanged declared case; original independent mathematical review reused by its original identity |
| Implementation | Analysis-only solver unchanged; capture/archive hardening delivered, but full-scale capture usability unresolved |
| Numerical qualification | INCOMPLETE; no full-case conservation, precision, refinement, repeatability or uncertainty qualification |
| Observation/archive qualification | Full-scale capture FAILED before serialization; zero qualified full rows or replacement trajectory arrays. Focused end-to-end and large serialization controls PASS on their own workloads |
| Local software QA | PASS: 6,482 quick tests, 73 affected document regressions, static/generated/gate/baseline/build/package checks; selectors and floors unchanged |
| Hosted candidate CI | Separate exact-delivery-head receipt in PR #333 and external closeout; old-head CI is not reused for this delta |
| Independent review | Scoped pre-execution PASS; final exact-candidate receipt is separately retained |

## Base, candidate and unchanged contract

- Selected live base: `3cd308ac5bed39acff3d995108b5178a53c982ee`; tree `96ad0b033c070a99416209828b5780034f438dba`. Rechecked unchanged immediately before continuation; the seven successful exact-base PUSH workflows are reused by [INTEGRATION.json](INTEGRATION.json).
- Starting PR head: `9b5ef8db725afaad3238494abcb43f2dd6c3e1f5`; tree `a320143bc5324e2204cbafddfbb104320a5bda93`. One existing branch `model/grudeva2026-full-reference-010` and one existing draft [PR #333](https://github.com/trbrewer/puckworks/pull/333). Final candidate identities are supplied by the exact-candidate review/closeout and PR delivery receipt; obtain the checked-out identity with `git rev-parse HEAD HEAD^{tree}`.
- Read-only EWP main: `4284e9460c8057053e95de7cfa2fb3590e68e9db`; tree `d9d9faaa56f22ab0bd7f47c43174024d15ada192`. Its production Puckworks dependency remains `fc61c4670ec7bf801e40bb391aab16048b8da26b`. No EWP writes.
- Original matrix SHA256: `092269b20b88d413abbfb1350240d32ab869e985cf1825ef1f28f73462e667d3`; unchanged byte-for-byte. Continuation binding: `64d92c5f87c46fad02aa7a2c078b7c473492d04d2d9296d12044af529c333b0a`.
- Solver SHA256 remains `c88427aa1fba29605e1301e2a9bfb0da571ed44332c86b569ab58e0d41fc5741`. All sixteen original 010 documents and 206 retained historical scientific-file hashes match. Production models/data/defaults/dependencies and the October 9 review remain unchanged.
- Changed scope: the 010 I/O module, runner and focused tests; continuation-specific documentation/results/receipts; narrow ROADMAP/SPRINTS/development-guide/status-source navigation and regenerated status. No runtime registration, scientific method/settings change, source-card rewrite or general evidence framework.

## Frozen case and exact execution matrix

`SYNTHETIC-GRUDEVA-FINITE-RATE-010-A`, equation source `GRUDEVA-EJAM-2026-E23-E29`: phi_f=.64, phi_b=.16, phi_l=phi_T=.20, varphi_lb=0, q=1, s_w=min(t,1), initial fines/boulders concentration=1.388, horizon=8. Synthetic epsilon=.01, D_sf=100, D_sb=1, D_eff=.01, radius ratio=.1, b_f=80/41, b_b=2/41; Q_f=5/48, Q_b=5/12, M0=5.552. The frozen 211 times, 210 physical z coordinates, 14 radii, event conventions, support and limits remain [MATRIX.json](MATRIX.json).

| Order / row | Axial | Fines | Boulders | rtol | atol | max step | startup |
|---|---:|---:|---:|---:|---:|---:|---:|
| anchor | 256 | 32 | 64 | 1e-09 | 1e-14 | 0.02 | 1e-07 |
| axial_coarse | 64 | 32 | 64 | 1e-09 | 1e-14 | 0.02 | 1e-07 |
| axial_medium | 128 | 32 | 64 | 1e-09 | 1e-14 | 0.02 | 1e-07 |
| fines_coarse | 256 | 8 | 64 | 1e-09 | 1e-14 | 0.02 | 1e-07 |
| fines_medium | 256 | 16 | 64 | 1e-09 | 1e-14 | 0.02 | 1e-07 |
| boulders_coarse | 256 | 32 | 16 | 1e-09 | 1e-14 | 0.02 | 1e-07 |
| boulders_medium | 256 | 32 | 32 | 1e-09 | 1e-14 | 0.02 | 1e-07 |
| startup_coarse | 256 | 32 | 64 | 1e-09 | 1e-14 | 0.02 | 1e-05 |
| startup_medium | 256 | 32 | 64 | 1e-09 | 1e-14 | 0.02 | 1e-06 |
| time_coarse | 256 | 32 | 64 | 1e-05 | 1e-10 | 0.08 | 1e-07 |
| time_medium | 256 | 32 | 64 | 1e-07 | 1e-12 | 0.04 | 1e-07 |
| combined_coarse | 64 | 8 | 16 | 1e-05 | 1e-10 | 0.08 | 1e-05 |
| combined_medium | 128 | 16 | 32 | 1e-07 | 1e-12 | 0.04 | 1e-06 |
| repeat | 256 | 32 | 64 | 1e-09 | 1e-14 | 0.02 | 1e-07 |

## Actual execution and diagnostic accounting

- Historical execution: one full trajectory, two successful BDF segments, 25,829 accepted entries, zero audited/qualified rows. Its archive and failure remain unchanged; it was not repaired or used as the repeat.
- Continuation execution: one replacement trajectory, two successful BDF segments, the same accepted-entry counts (7,826 and 18,003; counts alone do not establish state identity), zero audited/qualified rows. Thirteen remaining frozen rows NOT_RUN. Zero full trajectories reused.
- New diagnosis: one complete 19-entry comparison and a small first dense-endpoint sample; no repeat full hash census or unrestricted substitution search. HISTORICAL_ROOT_CAUSE_UNESTABLISHED; exact recovery ineligible on inspected retained sources.
- Prospective controls: five focused invocations, ending with 54 passing tests, total 85 bounded trajectories/95 solve_ivp segments. One solver-free large serialization test checks two payloads, with original whole-file/helper identities retained. One ordinary quick invocation adds 15 bounded 010 trajectories/15 segments. Total new local 010 fixtures: 100 trajectories/110 segments, separate from the one new full scientific trajectory. Reviewer executions: zero solvers. Hosted fixture executions are accounted for with their actual CI jobs in the delivery receipt.
- The one full-scale failure occurred during CAPTURING, before any trajectory file or manifest. The retained exception identifies a combined dense source-after/target commitment check, but not which comparison or digest values. The process exited without retaining its in-memory trajectory. This limits forensic diagnosis; it does not establish hardware cause or justify changing the numerical method.
- Peak sampled RSS: 67,069,992 KiB. Minimum available memory: 190,566,535,168 bytes; minimum free disk: 1,332,237,389,824 bytes. No resource-safety stop, OS-limit change, environment change or additional resource purchase. The pipeline failed after 1,030.452 seconds; supervisor returned code 1 after 1,034.292 seconds.

## Qualification limits and retained evidence

All required full-case observations are unavailable because capture failed. The [result](CONTINUATION_RESULTS.md) and [machine-readable record](CONTINUATION_RESULTS.json) distinguish this from structural dry-domain/pre-drip absence and give requested/required/unavailable counts. Numerical maxima, worst-case physical coordinates, individual/combined refinement changes, temporal effectiveness, repeatability and uncertainty estimates are not computable from an integrity-qualified trajectory. No output-specific full-case precision claim is made. Focused mathematical and archive-control capabilities retain their own limited scope.

The unchanged normalized-mass conservation limit is 1e-6; aqueous bounds are [-1e-8,1+1e-8]; grains/inventories are >=-1e-8. Required refinement limits remain 1e-3 for liquid/outlet, 2.3e-4 for grain means/radial profiles and 5e-5 for cumulative outlet and the declared inventory/inlet families. No limit or budget was relaxed, and the capture failure is not a measured numerical gate failure.

[CONTINUATION_EXTERNAL_EVIDENCE.json](CONTINUATION_EXTERNAL_EVIDENCE.json) binds the original archive identity, new execution/failure/resource records, and the two large serialization fixtures. New full trajectory archive bytes: **zero**. Original failed trajectory manifest: `e78201cceb99c773ccbe7d2d3359841d939c39734d99c03775b62569722d290e`. New external evidence manifest: `9f4d4e6d955d99afa82f36670f1fe09d1e01b50cb76835ff5c69610a6bc84c4d`. Private paths and raw logs remain external; no restricted source is redistributed.

[CONTINUATION_REPRODUCE.md](CONTINUATION_REPRODUCE.md) provides strict inspection, fixed controls, original exact-freeze and reviewed-continuation commands. These commands do not authorize another full replacement after this stop. The original failure documents, frozen source, manifest and closeout remain preserved.

## Final boundaries

Keep issue #67 open and PR #333 draft, unmerged and without auto-merge. No release, EWP change, production/default/lock change, Guided Pull adoption, publication rescore, reduced-model comparison, automatic retry or successor. CORROBORATED_PUBLICATION_DISCREPANCY and FIG5_REFERENCE_INCOMPLETE remain unchanged. PHYSICAL_VALIDATION=NOT_ESTABLISHED.
