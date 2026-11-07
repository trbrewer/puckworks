# Pressure-time fade: partial held-out gains, persistent shape failures

**0.277365 → 0.264599 g/s** LOCO primary flow score, PF minus refreshed
**−0.012766 [−0.030039, +0.003497]**; mass fade: **0.256500**.
Intervals condition on frozen fits/Mc. Retain A-J1 as the baseline: the pressure
fade improves some held-out trajectories but leaves the requested cross-condition
pattern/catch-up incomplete and worsens early flow. Phenomenological only;
TARGET_EXPOSED; PHYSICAL_VALIDATION=NOT_ESTABLISHED.

1. **Late changes: partly reproduced.** Absolute discrepancies improve at **9/11
   conditions in each scope**, with no invented point declines. LOCO 4/5-bar
   changes are **+0.1455/+0.0983**, observed **+0.1892/+0.1023 g/s**. But 6/7/8
   remain rising (**+0.0570/+0.0240/+0.0087**) where observations fall; descriptive
   misses 6/7. LOCO 9/11/13 changes are **−0.0223/−0.0548/−0.0006**, observed
   **−0.1170/−0.1268/−0.0656**: signs improve over mass fade at 11/13, magnitudes
   remain too small. Versus mass fade in LOCO, it restores the 5-bar rise but
   loses the 6–8-bar declines. Both scopes also miss the 1/3.5-bar point declines, whose
   intervals cross zero (3.5 bar **[−0.2239,+0.00125]**).

2. **Catch-up: not reproduced.** The 9-minus-13 increments across the three
   phases are LOCO **+0.3311/+0.0855/−0.0217**, observed
   **+0.5484/−0.2560/−0.0514 g/s**. The middle phase has the wrong sign in both
   scopes; descriptive gives **+0.2636/+0.0786/−0.0009**. LOCO 100-s high-pressure
   slope worsens from **−0.0792 to −0.1081**, observed **−0.0638 g/s/bar**.

3. **Other outcomes: tradeoffs.** Onset+10-s overprediction worsens at 9/11/13 bar
   in both scopes; LOCO levels increase another **0.1556/0.2015/0.1008 g/s**.
   Their 100-s absolute level errors improve. LOCO endpoint score improves
   **0.2077→0.1794**; primary 1/2-bar scores improve **0.0514→0.0497 /
   0.1272→0.1110**, while 3.5 bar worsens **0.4045→0.4195 g/s**. Full-cohort onset
   lower bound worsens **8.5806→8.6240 s**, with **52/56** detections unchanged
   (1 bar **1/5**). Descriptive onset worsens **2.9283→2.9440 s**, **56/56** detected.

4. **Gamma_P: positive throughout, imperfect slice minima.** Fits span
   **0.00021694–0.00029096 (bar s)⁻¹**, product gamma_P×1300 **0.2820–0.3782**.
   All twelve fixed-coordinate slices have interior grid minima: **0.30** in
   eleven folds, **0.45** at LOCO-11. Ten selected values beat adjacent grid points;
   LOCO-3.5/13 exceed their grid minima by **0.00082694/0.00000218**. These are
   slices, not profile likelihoods or convergence proofs; no further fitting.

Tables retain all arms, conditions, paired intervals, split contributions,
finite-horizon peaks and numerical sensitivity. DESCRIPTIVE_ALL is in-sample.
EWP and production defaults are unchanged. No successor.
