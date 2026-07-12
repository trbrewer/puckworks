# G3 DE1 pump-characteristic bench protocol

## Purpose

Acquire a measured pump/head characteristic Q(P) that can replace the repository's nominal
manufacturer quadratic in RC-3 machine mode.

Official Decent material documents a firmware pump model and scalar flow calibration, but it
does not publish a qualifying pressure–flow bench curve. Because voltage and frequency affect
pump behavior, those variables are mandatory:
https://decentespresso.com/blog/perfectly_calibrating_decent_flow_measurements

## Minimum viable bench

1. Run without a coffee puck. Use a controllable downstream restriction/back-pressure valve.
   A basket/restrictor is acceptable only if the downstream pressure node is measured directly.
2. Record the exact DE1 model, hardware revision, pump model if known, firmware, mains voltage,
   mains frequency, inlet pressure and water temperature.
3. Sweep downstream pressure from approximately 0 to 12 bar at several fixed pump-command
   levels. Include both increasing and decreasing pressure sweeps to detect hysteresis.
4. At each point, wait for a stable window of at least 10 s, then collect:
   - commanded pump level;
   - measured pressure at the named node;
   - gravimetric flow from a calibrated scale;
   - DE1 estimated flow, if available;
   - water temperature.
5. Use at least three repeats per point. Convert mass flow to volumetric flow with an explicitly
   stated water-density relation.
6. Preserve raw time series in addition to the steady-state summary.

## Recommended pressure grid

0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11 and 12 bar, subject to machine-safe limits.

## Output

Use `g3_de1_pump_curve_template.csv` for the summary and retain one raw CSV per sweep.

## Acceptance test

A useful dataset must contain paired measured pressure and measured flow over more than one
pressure and must state machine/electrical conditions. A scalar flow-calibration multiplier is
not a pump characteristic.
