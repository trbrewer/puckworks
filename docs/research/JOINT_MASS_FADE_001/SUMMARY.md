# PW-JOINT-MASS-FADE-001

**0.2774 → 0.2565 g/s** held-out primary-flow score; **9/11** late-change
absolute discrepancies improve. The answer is **mixed**: meaningful held-out
improvement over refreshed A-J1, without reproducing all declines, catch-up or
early levels. Retain A-J1 as the baseline; this experiment does not establish
A-J1-F as its replacement. Scores below are inherited means of condition RMSEs.

1. **Late changes are not reproduced across conditions.** LOCO +60→100-s
   changes at 9/11/13 bar become −0.0427/+0.0156/+0.0607 g/s, versus refreshed
   +0.1936/+0.2146/+0.2263 and observed −0.1170/−0.1268/−0.0656.
   Fade gets the decline direction at 6/7/8/9 bar but still misses the negative
   observed point changes at 1/3.5/11/13; 1-/3.5-bar observed intervals include
   zero. It invents a 5-bar point decline (−0.0051 versus +0.1023), and worsens late
   discrepancies at 2/4 bar. DESCRIPTIVE_ALL also improves 9/11 discrepancies,
   but still misses 1/3.5/9/11/13-bar declines; it preserves the positive 5-bar
   direction. The modeled split remains liquid-dominated: LOCO 13-bar fade
   change is +0.0739 liquid −0.0132 solute = +0.0607 g/s.
2. **Catch-up remains incomplete.** LOCO 9-minus-13 increments across
   +10→40, +40→60, +60→100 s are +0.2900/+0.0278/−0.1033 g/s versus observed
   +0.5484/−0.2560/−0.0514. The first two discrepancies shrink, but the middle
   sign remains wrong and the last discrepancy grows. DESCRIPTIVE_ALL has the
   same pattern (+0.2757/+0.0403/−0.0848).
3. **Flow gains trade against early/low-pressure performance.** LOCO
   primary/companion/endpoint scores change by −0.0209/−0.0146/−0.0512 g/s;
   paired primary interval is [−0.0370, −0.0061]. Onset+10-s levels worsen
   at 9/11/13 bar: 1.422/1.262/1.211 versus observed 0.675/0.622/0.511 g/s.
   Their 100-s levels improve; 2/5/6-bar 100-s discrepancies worsen.
   Low-pressure primary scores worsen at 1/2 bar, improve at 3.5 bar.
   LOCO onset computed lower bound is 8.5806→8.5946 s, with 52/56 detections
   in both arms; this difference is not a bound on the true-error difference.
   Descriptive flow scores improve, but onset is 2.9283→2.9299 s (56/56),
   with similar early-level and low-pressure tradeoffs.
4. **The selected regime is consistent across folds.** γ=0.001045–0.001406
   g⁻¹, γMc=0.03000–0.03905, all rise-then-fall, M*=89.29–100.67 g;
   no fade parameter contacts a bound. This is fit-to-fit consistency, not
   parameter uncertainty or evidence of a unique optimum. M* describes
   constant-pressure liquid flow, not beverage peak timing or pressure ordering.

**24 fits, 456 starts, 60.2185 core-hours**, no failed scientific commands.
Both steps retain every detection; maximum phase-change sensitivity is
0.000080 g/s. Intervals condition on frozen fits and omit refit uncertainty.
The fade is phenomenological; delivered mass is a tested driver, not an
established mechanism. See the [paired tables](METRICS_PAIRED.csv),
[all-condition late changes](CROSS_CONDITION_LATE.csv) and [figure](FLOW.svg).
