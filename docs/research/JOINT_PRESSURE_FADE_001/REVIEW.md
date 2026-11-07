# Independent read-only final review

Reviewer: `/root/pressure_fade_final_review`, separate from implementation.
Reviewed scientific/report head:
`c9e322fbcc2fb0f395136ffaf62a79a6499a9092`.
Disposition: **no remaining actionable findings**.

- Both integration paths independently carry post-breakthrough Phi through
  old/mid/new fade factors and the transport water increment. Fixed Mc remains
  separate from gamma_P; tau0 stays last. Zero/control reuse is consistent.
- All **228 starts / 177,304 trial records / 12 winners** authenticate. Every
  retained start minimum equals its lowest evaluated trial, and every selected
  fit matches its winning start. All embedded controls reproduce exactly and
  every winner is no worse than control. Mc, membership, identity and trial
  gzip hashes match the frozen bank and source artifacts.
- Reconstructed all **8,960 fixed windows** from **896** stored observer traces;
  independently checked detectors and errors. All three inherited arms reproduce
  #427 exactly. The primary contrast uses PF minus refreshed inside shared draws.
  An artificial PF=refreshed arm gives zero paired contrasts throughout.
- Independently reproduced all **22 cross-condition late-change rows** and
  **480 paired metric rows**, including bootstrap intervals. The summary's
  incomplete rising/falling pattern, catch-up failure and early/endpoint/
  low-pressure/onset tradeoffs match the tables.
- Verified all **144 slice rows** and **132 fit×condition peak groups**.
  The summary correctly distinguishes interior grid preference from the two
  selected vectors above a grid minimum; these slices do not prove convergence.
- The browser-rendered five-condition/two-scope figure is clear and correctly
  labeled. The mixed conclusion and A-J1 baseline recommendation are supported;
  no mechanism or physical-validation claim is made.
- All artifact/code/external hashes and timer entries verify:
  **111,229.29 CPU seconds = 30.897025 core-hours**, including failure and recovery.
  Recovery changes only two metadata boolean casts. Numerical evaluations and
  slices remained byte-identical; no fitting was repeated.
- **90 focused/inherited tests** and the full-diff whitespace check pass.

Two review findings were resolved within this task: extend peak diagnostics to
all fit/condition pairs, and serialize NumPy comparison flags as built-in bool.
No unresolved scientific or implementation findings remain. The reviewer made
no edits, optimization calls or EWP writes. This closeout adds the review record
and refreshes its receipt/documentation hashes; scientific artifacts are unchanged.

The same independent reviewer checked the subsequent CI portability correction:
only the log/exp coordinate round-trip assertion gains `rtol=1e-14, atol=0`,
matching the existing adapter test. Frozen start/common parameters, gamma, Mc,
embedding and control-reproduction checks remain exact. No scientific source
or result changes, and the scientific review remains valid. The corrected
focused/inherited suite has **90 passing tests**; all **21** pressure-fade tests
pass without JIT and at minimum dependencies.
