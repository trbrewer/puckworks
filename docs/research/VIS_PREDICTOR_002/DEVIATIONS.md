# Declared post-hoc correction

PW-VIS-PREDICTOR-002 is explicitly motivated by the results of PW-VIS-PREDICTOR-001,
not a prospectively independent confirmation. Its sole scientific change is the
owner-declared exclusion of every shot carrying the existing `reset_like=True`
flag: any adjacent native reported-weight drop strictly greater than 5 g anywhere
in the original history. The flag does not establish the cause. Survivors are
called **unflagged shots**; negative increments and every other diagnostic flag
remain eligible.

The correction was identified from #421's reset-like breakdowns and extreme early
increments. The original #421 bundle and models remain unchanged. All surviving
window observations, calibration/guard/scoring roles, fold IDs and scientific
settings are carried over exactly. The final corrected pinned evaluator/runtime
is reused; none of 001's failed intermediate implementations is revived.

Runner changes are limited to output-root parameterization, strict fit-resume and
later-consumption provenance checks, whole-shot filtering, the mandatory C0
reproduction, the two added declared contrasts, matched-survivor comparison and
requested reporting. All outputs live in fresh 002 locations. No new harvest,
robust loss, model, tuning or additional exclusion is authorized.
