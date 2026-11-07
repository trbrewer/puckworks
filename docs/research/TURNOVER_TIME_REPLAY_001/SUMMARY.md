# Frozen-model replay and Visualizer coverage

**A. Both models reproduce a negative slope at observed-onset +10 s, but miss
the observed +40-s sampled minimum, +40→60-s 13-bar catch-up and +60→100-s
decreases in all three high-pressure flows.**

**B. Visualizer has 118,542 scored windows from 10,231 shots / 315 users;
the requested pressure partition is withheld under the frozen disclosure rules,
so its above-10-bar amount, distribution and timing cannot be released.**

At onset +10 s, the observed slope is **−0.0441**, versus A-J1 **−0.0432 /
−0.0493** and D0 **−0.0606 / −0.0612 g/s/bar** (LOCO / DESCRIPTIVE_ALL).
All four replay curves are most negative at stable **+60 s**, not +40 s.
Observed 100-minus-40 slope weakening is **+0.0804**; the A-J1 LOCO change is
**−0.0109**, giving a paired observed-minus-predicted difference of **+0.0914
[+0.0184, +0.1513] g/s/bar**. D0's diagnostic wrapper already predicts a
negative stable-10-s slope (−0.0478 LOCO), when observed flow is near zero.

For stable 10→40 s, observed 9-minus-13-bar flow growth is **+0.548 g/s**;
A-J1 predicts **+0.240 / +0.266**, D0 **+0.103 / +0.107**. For 40→60 s,
observed catch-up makes this difference **−0.256**; predictions remain
**+0.064 / +0.069** and **+0.033 / +0.031**, respectively.

| Stable 60→100-s flow change (g/s) | 9 bar | 11 bar | 13 bar |
|---|---:|---:|---:|
| Observed | −0.117 | −0.127 | −0.066 |
| A-J1 LOCO | +0.197 | +0.216 | +0.226 |
| A-J1 DESCRIPTIVE_ALL | +0.201 | +0.222 | +0.240 |
| D0 wrapper LOCO | +0.106 | +0.124 | +0.143 |
| D0 wrapper DESCRIPTIVE_ALL | +0.108 | +0.129 | +0.150 |

The 13-bar late-change discrepancy is **−0.292 [−0.333, −0.253] g/s** for
A-J1 LOCO and **−0.209 [−0.249, −0.170]** for D0 LOCO. Along those replays,
13-bar C(P) changes little (1.783→1.787 and 1.626→1.629 g/s), while predicted
liquid M rises and R(M) approaches one (0.850→0.985 and 0.900→0.989).
These describe the full predictor's behavior, not a unique recovery contribution.

All **317 historical checks**, **224 replays** and **2,240 windows** are available;
12 detector non-detections remain included. Historical instantaneous liquid
outputs, original D0 and its diagnostic R0 beverage wrapper remain distinct.
LOCO slopes pool different held-condition fits; DESCRIPTIVE_ALL uses one common
in-sample vector. Intervals use the same 1,000 brew draws and frozen parameters/Mc.

Suppressed coverage is withheld, not zero; no detection-power inference follows.
No aggregate AR improvement does not mean no fitted downturns. Pressure node,
coffee, machine, style and observation contracts differ across corpora. No
physical-validation, mechanism or cross-corpus agreement claim.

Data: Waszkiewicz et al., Zenodo 18046315 (CC-BY-4.0); Visualizer, with thanks to
the contributing users who made their shots public.
