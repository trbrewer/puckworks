# 010 handoff

**FULL_REFERENCE_QUALIFICATION_INCOMPLETE.** The implementation and focused controls are delivered; exact accepted-state archive identity fails on the completed anchor. No full-case output precision qualification is awarded. PHYSICAL_VALIDATION=NOT_ESTABLISHED.

## Separate dispositions

| Area | Disposition |
|---|---|
| Mathematical/source contract | COMPLETE for declared case, with explicit dimensional-star clarification in NOTATION.md; primary retained mathematics and rights/access limits recorded |
| Implementation | DELIVERED, analysis-only; full equations and independent controls implemented; full-case archive integrity unresolved |
| Numerical qualification | INCOMPLETE: one solver-complete anchor; zero audited/qualified rows; thirteen rows NOT_RUN |
| Observation/archive qualification | FAILED: one of 26 array identities mismatches; required full-case observations/audits unavailable |
| Local software QA | PASS; 6443 quick tests, 65 document regressions, configured static checks, ordinary gates/baseline, generated checks and clean wheel/sdist |
| Hosted candidate CI | Exact final-head status is recorded externally and in the draft PR checks/body after this commit; local QA and selected-base integration do not substitute |
| Independent review | Pre-campaign PASS; [final independent nonhuman review](FINAL_REVIEW.json) PASS_FOR_BOUNDED_INCOMPLETE_HANDOFF on the exact scientific payload |

## Identities and scope

- Selected base head: `3cd308ac5bed39acff3d995108b5178a53c982ee`; tree: `96ad0b033c070a99416209828b5780034f438dba`. Live main still matched at handoff preparation.
- All seven exact-base PUSH workflows passed before the campaign; [INTEGRATION.json](INTEGRATION.json) binds them. No successful workflow was manually rerun.
- Reviewed scientific candidate: head `9ec7b1a2fbedb1650eb51afe0ee4d84d55ab063a`, tree `0d386fc8388a88c14fb8fa28f5c7c7f6e6f04a1e`. One branch: `model/grudeva2026-full-reference-010`. Final G0 receipt/status additions preserve scientific/result/archive hashes. The exact final tip/tree and hosted CI are recorded in the draft PR body and external closeout receipt after commit, avoiding a self-referential Git identity.
- Read-only EWP main `4284e9460c8057053e95de7cfa2fb3590e68e9db`, tree `d9d9faaa56f22ab0bd7f47c43174024d15ada192`; production Puckworks dependency remains `fc61c4670ec7bf801e40bb391aab16048b8da26b`.
- Changed scope: two new analysis modules, explicit campaign CLI, focused tests, the new 010 documentation/results bundle, and narrowly scoped ROADMAP/SPRINTS/development-guide/status-source navigation and generated status. No runtime registration, production equations, default, lock, historical card or scientific evidence changes.
- All 206 retained scientific-file hashes and the historical source card match. The October 9 review is unchanged. See [QA.json](QA.json).

## Frozen case and matrix

`SYNTHETIC-GRUDEVA-FINITE-RATE-010-A`, distinct from equation source `GRUDEVA-EJAM-2026-E23-E29`: phi_f=.64, phi_b=.16, phi_l=phi_T=.20, varphi_lb=0, q=1, s_w=min(t,1), both initial grain concentrations=1.388, horizon=8. Synthetic epsilon=.01, D_sf=100, D_sb=1, D_eff=.01, a_f/a_b=.1, b_f=80/41, b_b=2/41; Q_f=5/48, Q_b=5/12; M0=5.552. No dimensional geometry or fitted/publication coefficient is inferred.

Matrix SHA256: `092269b20b88d413abbfb1350240d32ab869e985cf1825ef1f28f73462e667d3`. [MATRIX.json](MATRIX.json) fixes all 211 times, 210 physical z coordinates, 14 radii, event/availability rules, dependencies and limits before execution.

| Row | Axial | Fines | Boulders | rtol | atol | max step | startup | Actual status |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| anchor | 256 | 32 | 64 | 1e-09 | 1e-14 | 0.02 | 1e-07 | Solver complete; archive failed |
| axial_coarse | 64 | 32 | 64 | 1e-09 | 1e-14 | 0.02 | 1e-07 | NOT_RUN |
| axial_medium | 128 | 32 | 64 | 1e-09 | 1e-14 | 0.02 | 1e-07 | NOT_RUN |
| boulders_coarse | 256 | 32 | 16 | 1e-09 | 1e-14 | 0.02 | 1e-07 | NOT_RUN |
| boulders_medium | 256 | 32 | 32 | 1e-09 | 1e-14 | 0.02 | 1e-07 | NOT_RUN |
| combined_coarse | 64 | 8 | 16 | 1e-05 | 1e-10 | 0.08 | 1e-05 | NOT_RUN |
| combined_medium | 128 | 16 | 32 | 1e-07 | 1e-12 | 0.04 | 1e-06 | NOT_RUN |
| fines_coarse | 256 | 8 | 64 | 1e-09 | 1e-14 | 0.02 | 1e-07 | NOT_RUN |
| fines_medium | 256 | 16 | 64 | 1e-09 | 1e-14 | 0.02 | 1e-07 | NOT_RUN |
| repeat | 256 | 32 | 64 | 1e-09 | 1e-14 | 0.02 | 1e-07 | NOT_RUN |
| startup_coarse | 256 | 32 | 64 | 1e-09 | 1e-14 | 0.02 | 1e-05 | NOT_RUN |
| startup_medium | 256 | 32 | 64 | 1e-09 | 1e-14 | 0.02 | 1e-06 | NOT_RUN |
| time_coarse | 256 | 32 | 64 | 1e-05 | 1e-10 | 0.08 | 1e-07 | NOT_RUN |
| time_medium | 256 | 32 | 64 | 1e-07 | 1e-12 | 0.04 | 1e-07 | NOT_RUN |

## Actual evidence and limitations

One full scientific trajectory completed (two BDF segments; 25,829 accepted entries), then the pipeline failed after 2049.818725 seconds. Zero full-model runs were reused; 004–009 qualified campaigns were not rerun. Two development invocations contain 32 bounded 010 trajectories/36 segments; two local quick suites add 30/30. Three read-only archive diagnostics execute zero solvers.

The exact post-wetting raw state identity remains unresolved. Twenty-five of 26 arrays and all three file hashes match; the separately stored state/concentration copies disagree at 19 entries. The largest observed discrepancy is 2.384185791015625e-7 at t=1.1972222631915606, z=.232421875, fines r=.9998626708984375. Direct raw-byte hashing confirms the stored state mismatch; rebuilding from the other copy does not recover the original hash. No replacement or checksum repair was adopted. Root cause is unestablished.

Every full-case observable has an explicit requested/supported/unavailable count in [RESULTS.json](RESULTS.json). Numerical maxima, refinement changes, combined budgets and uncertainty estimates are unavailable because the archive prerequisite failed. The copy discrepancy is an integrity diagnostic, not a discretization-error estimate. Focused analytical/manufactured control errors remain valid on their own fixtures; they do not establish full-case precision.

The 27,685,312,970-byte archive remains quarantined, with original state/coefficient files and every failure/diagnostic record. [EXTERNAL_EVIDENCE.json](EXTERNAL_EVIDENCE.json) supplies file and content identities; private mounted locators and raw logs remain external. The strict loader rejects it. [REPRODUCE.md](REPRODUCE.md) gives original-attempt and inspection commands and sampled resource use.

Retained failed attempts: two initial analytical-series truncation controls (corrected at unchanged allowance); initial/intermediate ordinary card/export checks (resolved by restoring historical inputs); the one anchor archive failure (unresolved). No new scientific row was added and no environment, threshold or protection changed.

## Final boundaries

Issue #67 remains open. The one PR stays draft and unmerged with auto-merge disabled. There is no automatic retry, downstream full-versus-reduced comparison, epsilon sweep, Figure 5 reconstruction, publication rescoring, production/Guided Pull/EWP adoption, release or successor. CORROBORATED_PUBLICATION_DISCREPANCY and FIG5_REFERENCE_INCOMPLETE are preserved. Physical validation is not established.
