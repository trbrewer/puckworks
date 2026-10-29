# Why more pressure can mean less espresso: what we found

*Pressure-peak investigation, October 2026. Data: Waszkiewicz et al., "Under pressure: poroelastic regulation of flow in espresso brewing", Physics of Fluids 38, 063113 (2026); data CC BY 4.0, Zenodo 10.5281/zenodo.18046315. Analyses: [Stage A](PRESSURE_PEAK_STAGE_A/), [B0](PRESSURE_PEAK_STAGE_B0/), [B0b](PRESSURE_PEAK_STAGE_B0B/), [B0c](PRESSURE_PEAK_STAGE_B0C/), [B0d](PRESSURE_PEAK_STAGE_B0D/).*

## The question

In the Waszkiewicz experiments (56 retained brews, 11 pressures from about 1 to 13 bar, one coffee, grind and 18.5 g dose), the steady flow through the puck rises with pressure up to a point and then falls. Every flow model in Puckworks and Espresso Whole-Pull predicts the opposite: more pressure, more flow, levelling off at most. We set out to find out whether the fall is real, and what could cause it.

## What is now established

**1. The fall is real in this dataset.** Flow peaks at 6 bar (interval 5–6 bar) and falls by about 0.066 g/s for each extra bar above 9 bar (interval 0.040–0.088). The fall survives every check we tried:

- removing any single brew;
- using the raw sensor pressure instead of the authors' corrected basket pressure;
- scaling that correction by ±20%;
- using the authors' own "last ten seconds" window, once end-of-shot cup removal is excluded.

The authors noted it too: "upon increasing the pressure above a certain threshold, the flow rate decreases again." One check is still impossible: whether flow drifted during the session. The files record no brew order or dates.

**2. The standard compaction theory cannot produce it.** If pressure squeezes the puck locally, layer by layer, steady flow equals a sum of positive permeability contributions across the pressure drop. Raising the pressure only adds to that sum. Flow can level off, but it can never fall, whatever permeability law is used. The paper's own model is a special case of this. So compaction alone is ruled out, not merely unfitted.

**3. The lower flow at high pressure is set early and then holds.** Late in the shot, flow is still rising at 2–6 bar and is flat at 7 bar and above. No pressure shows a measurable fall in flow during the shot, so if fines clog the puck progressively, the effect is too small to detect in this data. The lower flow at high pressure appears to be in place early.

**4. Water takes longest to get through at both low and high pressure.** Time from stable pressure to the first sustained drip:

- 25.5 s at 1 bar
- about 11 s at 3.5 bar
- 12–13 s at 4–6 bar
- 18 s at 13 bar

The slower wetting at high pressure suggests the extra resistance is already present during wetting. The delay also includes the time water takes to reach the cup, so it cannot show where in the puck the resistance sits. Fitted to wetting time alone, compaction laws put the fastest wetting at about 5.1–5.7 bar, close to the 6-bar flow peak.

**5. A useful empirical model exists, but it is not yet a mechanism.** On held-out pressures, the best simple model beats a smooth quadratic fit: 0.211 vs 0.294 g/s error. It combines whole-puck compaction set by the applied pressure, gradual loosening as coffee dissolves, and trapped air that shrinks under pressure. But it:

- falls about three times too steeply at high pressure;
- peaks at 8 bar (interval 7–8 bar) rather than 6;
- needs a compaction setting that disagrees with the one implied by wetting times.

## What we ruled out

| Idea | Why it fails here |
|---|---|
| Local, layer-by-layer compaction (including the paper's model) | Mathematically cannot make flow fall (point 2) |
| Fines gradually jamming the puck at high flow | No measurable fall in flow during the shot (point 3). |
| Grains swelling shut before water breaks through | Even using each brew's measured wetting time, still overpredicts low-pressure flow by about 0.4 g/s |
| One fixed puck state explaining both wetting time and flow | Wetting time and flow need different compaction settings (point 5) |

A caution on one experiment: the paper's stop–restart puck flowed faster after restarting. The authors attribute this to backflow through the machine's valve cracking the puck. It is evidence of damage, not of how the puck behaves in a normal shot, and we no longer use it as a test.

## What is still open

- **Session drift.** Brew order, dates and how each pressure was set are being requested from the authors.
- **Depth.** One untested hypothesis is that resistance builds up layer by layer as the wetting front moves down, which a single-number model cannot represent. The Espresso Whole-Pull solver already tracks the wetting front and compaction, so it could test this. That is a separate decision.
- **Low-pressure suppression.** Trapped air explains about half of why flow is lower than expected at 1–3.5 bar.

## Limits

- One machine, one coffee, one grind.
- All analyses are retrospective, on data the models had already seen during development.
- Uncertainty intervals include brew-to-brew and fitting variation, but not unknown protocol effects.
- These are findings about this dataset, not universal espresso behaviour.
