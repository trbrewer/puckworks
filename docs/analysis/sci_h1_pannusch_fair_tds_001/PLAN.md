# SCI-H1-PANNUSCH-FAIR-TDS-001

G1 / NO_GOVERNING_PHYSICS_CHANGE / RESEARCH_ONLY. One retrospective comparison;
SOURCE_INTERNAL / CAMPAIGN_SEPARATED / TARGET_EXPOSED. Physical validation and
practical adequacy are unestablished. Historical analyses remain unchanged.

Fetched main before branching: PW ff38d1e5dc10829f98901e679c7a037599c4a82b;
EWP f44c33dbb9b4fb80143e360e6f4a90f8ac0aa516. No intervening commits.
P1 began 2026-10-26 15:37 UTC; concluded within 30 minutes using the configured
owner inventory, source registers, cards and existing exposure receipts. No
census or prospective protected-outcome access. See HOLDOUT_MAP.csv.
**No verified executable blind candidate in inspected scope.** Unknowns are
retained; the corpus is not declared exhausted.

1. Verify original-source identities and accepted exports for FIT-C09/C10/C11/
   C14/C15 (15 shots, 90 windows) and PRED-C01/C02/C05/C06 (12 shots, 72 windows).
   Retain fractions 1,2,3,5,7,10, measured masses, boundaries and gaps; exclude
   all temperature/flow ramps and other FIT conditions.
2. Fit F and E independently with the same balanced mass-weighted squared-error
   objective and analytical inventory amplitude. B is the equal-condition,
   equal-shot training mean by fraction ID. No evaluation assay is an input.
3. Freeze bounds/settings before fitting. Four predetermined starts per arm,
   at most 250 actual residual/objective calls per start, including numerical
   derivatives. F uses two initial full fits, then one training-only diagnostic
   reduction and two final fits (or retains all parameters). E uses four starts.
   No more than eight hours model computation; no expanding search.
4. Qualify conservation, positivity, spatial/time accuracy using training only.
   Freeze fits, source/code/config hashes, predictions, metrics and sensitivity
   rules; obtain independent pre-score scientific review, then score once.
5. Report all conditions, paired whole-shot/condition deletions without refits,
   descriptive between-shot spread and all threshold variants. Numerical
   allowances remain separate from unknown measurement/training uncertainty.
6. Assess Cameron from retained evidence only. Run focused tests and repository
   checks, obtain review of the completed result, open an unmerged draft PR with
   auto-merge disabled. Select exactly one next task from the actual outcome.

Common observation: TDS_percent=100*c_l/980; measured vial solute mass is
vial_mass*TDS_percent/100. Time-average over each supplied window at constant Q.
Q=flow_label/1000/980 is a shared mathematical convention with unresolved physical
flow-label meaning. Source-equilibrated initial liquid is retained. These are
conditional fraction predictions, not hydraulic or complete-cup EY predictions.

Report R=sqrt(sum(m*error²)/sum(m)), B=sum(m*error)/sum(m), A=abs(B) per shot;
then average shots within conditions and conditions equally. Also report equal-shot
aggregates, per-condition errors, coverage failures, and gains g=1-Rcandidate/Rref
for F/B, E/B, F/E. Bands: negative=worse; [0,.10)=small; [.10,.25)=moderate;
[.25,infinity)=large. Reclassify at .75/1/1.25 times each nonzero threshold both
individually and jointly (all nine combinations). These are descriptive bands,
not adequacy gates. Deletion ranges are not confidence intervals.

Public artifacts contain aggregates only; detailed observations, shot metrics,
predictions, deletion vectors, originals, logs and private locators stay outside
Git. Source-derived aggregates: Pannusch et al., Mendeley
10.17632/y2tz67f6ry.1, CC-BY-NC-3.0; first-party code licensing is separate.
