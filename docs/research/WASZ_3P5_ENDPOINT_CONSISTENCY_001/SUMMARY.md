# PW-WASZ-3P5-ENDPOINT-CONSISTENCY-001

**56/56 endpoint pairs match SCI-MD-010 exactly. No identifiable 3.5-bar record or
processing inconsistency accounts for the recurring endpoint discrepancy.**
Observed flows/onsets also match FORM_A, JOINT_CLOCK_001 and pinned LC_JOINT_TRANSFER_001.

At nominal 2/3.5/4 bar, mean endpoint flows are **0.374813/1.052907/1.674454 g/s**
and matched pressures **1.791125/3.445750/4.076975 bar**. The two adjacent changes
are **0.452063/1.243095 g/s/bar** on nominal pressure and
**0.409817/0.984668** on matched pressure. The documented 2-bar mapping remains;
its endpoints span **1.57175–2.00975 bar**. Achieved pressure changes the graphical
spacing; the models already receive measured pressure histories.
[All pairs](ENDPOINT_PAIRS.csv) · [steps](STEP_COMPARISON.csv).

The **77,245 original records** contain no malformed lines or repeated/backward
timestamps; available adjacent intervals span **0.092–0.095 s**. One trailing
**7-1** record lacks t/m and is already omitted by the inherited loader; its raw
end timestamp remains unavailable. The three 3.5-bar files are complete.
[Raw audit](RAW_INTEGRITY.csv).

| Nominal bar (brews) | Reporting pressure mean / mean within-brew SD, bar | Stable elapsed / observed onset / clean end, s | Final-clean-30-s flow trend, g/s² | Beverage mass 100 s / clean end, g |
|---|---:|---:|---:|---:|
| 1 (5) | 1.0494 / 0.0183 | 6.565 / 25.478 / 126.201 | −0.000837 | 9.519 / 12.364 |
| 2 (4) | 1.7921 / 0.0177 | 4.392 / 13.616 / 123.391 | +0.001557 | 27.547 / 36.534 |
| 3.5 (3) | 3.3533 / 0.0910 | 3.518 / 10.959 / 123.533 | +0.002182 | 98.997 / 123.408 |
| 4 (10) | 4.0876 / 0.0420 | 3.766 / 12.375 / 120.897 | +0.007154 | 128.153 / 164.483 |
| 5 (5) | 4.9567 / 0.0593 | 3.831 / 12.670 / 118.963 | +0.002807 | 155.172 / 194.164 |

Equal-brew means; SD is not pooled. Stable elapsed starts at the first raw
timestamp; onset/end use stable zero. Mass is baseline-relative.
[Separate supports](PLAN.md) · [every brew](SUPPORTING_SUMMARIES.csv).

**3-5-5** has **6.258 s** below its inherited lower band (**3.042675 bar**),
longest **50.532–56.044 s**; its clean-support pressure minimum is **2.843 bar**.
The other two have zero below-band time. No pump pause or causal explanation is
identified. [Author question](AUTHOR_QUESTIONS.md).

Nonlinear response, shared model assumptions and unrecorded experimental
differences remain possible. Zero fits/model evaluations/scores; observations,
defaults and EWP unchanged. No physical-validation claim or successor.

[All-56-brew figure](ENDPOINT_PRESSURE.svg) · [reproduction, hashes and CPU](REPRODUCE.md)
· [verification](VERIFICATION.json).
