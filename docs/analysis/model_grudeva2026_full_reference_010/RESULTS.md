# Full-equation reference 010: bounded incomplete result

**FULL_REFERENCE_QUALIFICATION_INCOMPLETE — unresolved archive state identity failure.**
PHYSICAL_VALIDATION=NOT_ESTABLISHED. No full-reference or output-specific precision qualification is awarded.

The independently derived implementation and all 15 focused controls are delivered. The single attempted full-case anchor completed both BDF segments through t=8, but its archive loader rejected a raw accepted-state identity. The original serial campaign stopped before the remaining 13 frozen rows. There was no scientific rerun, alternate case, mesh search or threshold change.

## Actual execution and integrity finding

The anchor took 2049.818725 seconds through the recorded failure. Its segments contain 7,826 and 18,003 accepted time entries (25,829 entries, including t=1 twice). All raw arrays, source/settings identities, warnings, start/failure records and the original incomplete report remain external.
All three archive file hashes match, and 25 of 26 decoded arrays match their producer-recorded identities. Every decoded array is finite. The failed array is `segment-1.npz:y`, shape `(24834, 18003)`.

| Identity | SHA256 |
|---|---|
| Producer-recorded raw state | `44beb9f18896f0515575d3bc4c032a5e6a1e149edbed4dbf1c5d1905cb1ea050` |
| Decoded / independently streamed raw state | `353cb660c94479c69488e19faf1b3dddd87033b9b0a8bfc76ec43d002b95293e` |
| State reconstructed from the separate concentration copy | `564a626f61a2544561875c513e66ce5fa47523e138fa68fb741119ab27d90e07` |

The post-wetting concentration copy, where s=1, should duplicate the PDE amount states. It instead disagrees at 19 entries, with maximum absolute difference **2.384185791015625e-7**. Substituting this hash-matching concentration copy does **not** recover the recorded raw-state hash. No substitution was adopted. Direct streaming of the C-order NPY member independently confirms the decoded raw-state hash.

Representative worst witness:

| t | z | Population | r | Raw amount state | Separate concentration | Absolute difference |
|---:|---:|---|---:|---:|---:|---:|
| 1.1972222631915606 | 0.232421875 | fines | 0.9998626708984375 | 0.94099822092216001 | 0.94099845934073911 | 2.384185791015625e-07 |

The origin of this inconsistency is **unestablished**. It is not attributed to hardware, the filesystem, NumPy or the integrator. The lost exact-state identity is an evidence dependency; it is separate from mathematical consistency or measured discretization accuracy. The strict loader correctly refuses the retained artifact. The original array/checksum, failure and all three read-only diagnostic attempts are preserved; no checksum repair, state clipping, mass correction, tolerance relaxation or environment change was used.

## Numerical requirements and observations

The archive check precedes observation production and numerical audit. Consequently conservation, native/common bounds, phase/inlet/outlet errors, refinement trends, combined budgets, temporal effectiveness and repeatability remain **unavailable**, not measured passes or measured precision failures. No full-case numerical uncertainty is estimated. The redundant-copy discrepancy above is not a continuum-error estimate.

| Observable | Requested | Required on physical support | Structurally unavailable | Qualified available |
|---|---:|---:|---:|---:|
| liquid | 44310 | 35612 | 8698 | 0 |
| outlet | 211 | 146 | 65 | 0 |
| grain_means | 88620 | 88620 | 0 | 0 |
| grain_radial | 1240680 | 1240680 | 0 | 0 |
| inventories | 844 | 844 | 0 | 0 |
| integrals | 422 | 422 | 0 | 0 |

Dry liquid/zero wet volume and pre-drip beverage account for structural absence. All required supported observations are unavailable because the archive prerequisite failed. Dry/birth grain states are included in the declared grain support; unavailable required observations cannot pass.

The unchanged engineering requirements are absolute conservation ≤1e-6 normalized mass; aqueous concentrations within [-1e-8,1+1e-8]; grain concentrations and inventories ≥-1e-8; liquid/outlet refinement ≤1e-3; grain means/radial profiles ≤2.3e-4; cup, each phase and signed inlet integral refinement ≤5e-5 normalized mass. CONTRACT and MATRIX retain the quadrature, reconstruction, aggregate-budget and arithmetic rules. None was relaxed.

## Delivered evidence and limits

- [CONTRACT](CONTRACT.md), [notation clarification](NOTATION.md), [separate card addendum](CARD_ADDENDUM.md), [source access/rights](SOURCE.json), and [exact frozen matrix/support](MATRIX.json).
- [DEVELOPMENT](DEVELOPMENT.json): 15 final focused tests pass; two original analytical-oracle truncation failures remain recorded. The correction increased the independently checked series resolution and preserved its allowance.
- [PRE_CAMPAIGN_REVIEW](PRE_CAMPAIGN_REVIEW.json): independent nonhuman review passed the frozen source, geometry, transfer, conservation and campaign design.
- [RESULTS.json](RESULTS.json): exact counts, failed identities, witness coordinates, all unrun rows and unavailable gates. [Reproduction](REPRODUCE.md) explains strict failure reproduction and safe archive inspection.

Development controls used 32 bounded 010 trajectories / 36 solve_ivp segments across two invocations. Two local quick-suite invocations add 30 bounded 010 trajectories / 30 segments. The three archive diagnostics execute no solver. The frozen raw report’s `executed_rows=0` counts completed audited rows; it does not erase the one actual full-case solve reported here. Other ordinary repository tests retain their existing fixtures; they are not 004–009 campaign reruns.

Initial ordinary QA caught an addendum appended to a historical hash-bound card and stale discovery exports. The addendum now lives separately; the card and tracked exports are byte-identical to the base. An intermediate check also caught a stale ignored export pack, which was rebuilt from the unchanged original snapshot. Failed QA records remain external; no historical guard was changed.

The implementation and verified mathematical controls remain useful development evidence. The archived full-case candidate is quarantined and cannot be used as a qualified reference. This outcome does not establish reduced-model approximation error, epsilon-convergence, Figure 5 reproduction, the cause of 009’s discrepancy, author error, physical validation or production/Guided Pull/EWP adoption. CORROBORATED_PUBLICATION_DISCREPANCY and FIG5_REFERENCE_INCOMPLETE remain preserved. No automatic continuation is launched.
