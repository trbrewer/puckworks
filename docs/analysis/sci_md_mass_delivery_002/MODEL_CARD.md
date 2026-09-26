# Recipe-conditioned mass-coordinate delivery (research only)

Card before implementation. G1 / NO_GOVERNING_PHYSICS_CHANGE. This is a direct
observational regression of absolute fraction TDS, not registered production
physics. Inputs are cumulative measured beverage mass b (kg), constant nominal
programmed temperature T_set_K (K), and source_flow_setting_code (dimensionless,
source-specific design instruction). Temperature is not local puck temperature.

xT=(T_set_K-362.15)/9; xF=source_flow_setting_code-2.
L(z,h)=z exp(h)/(1-z+z exp(h)), with exact L(0,h)=0, L(1,h)=1,
L(z,0)=z. Evaluate stably. c0=L(c_ref,aT*xT+aF*xF);
k=10000 L(k_ref/10000,dT*xT+dF*xF); q(b)=c0 exp(-(k*b)^p).
Bounds: c_ref [0,1], k_ref [0,10000] kg^-1, p [.25,4], each slope [-3,3].
These are computational bounds, not measured physical priors. MT fixes aF,dF=0;
MF fixes aT,dT=0; MTF is primary with all four slopes active.
Seven-coefficient M0 representation uses unchanged historical c0,k,p and zero
slopes, with original artifact/hash in its fit identity; the 001 schema and
artifact remain untouched. All compact curves reuse the 001 integration kernel.

SETTING_AWARE_EMPIRICAL has five bounded [0,1] piecewise-linear concentration
profiles at center, negative/positive temperature and negative/positive flow.
Exact hat integrals and fixed triangle weights (1-|xT|-|xF|, |xT|, |xF|)
interpolate the center and signed-axis curves. No monotonicity or hull fallback.
Positive-width average TDS=100*S/(b1-b0); zero width S=0, average undefined.
Conditional solute-to-stop-mass is an integral, not mass-attainment prediction.

Domain: [0, final FIT maximum 0.0635064 kg] times |xT|+|xF|<=1.
This product-domain assumption is not complete joint observational coverage.
Report each condition's extent and borrowed shape beyond its observed extent.
Variable settings/ramps are unsupported. No extrapolation or prediction clipping.

No flow, pressure, shot-duration, mass-attainment, inventory, residual inventory,
grinder-transfer, universal-coefficient or physical-mechanism prediction. No
causal interpretation of recipe coefficients. SOURCE_INTERNAL; TARGET_EXPOSED;
RETROSPECTIVE_MODEL_DEVELOPMENT_COMPARISON; PHYSICAL_VALIDATION=NOT_ESTABLISHED.
Task choice was informed by exposed predecessor results; excluding March
chemistry from fitting does not make March newly blind. Source-derived models
and tables: Pannusch/Schmieder, Mendeley 10.17632/y2tz67f6ry.1, CC-BY-NC-3.0,
distinct from first-party code licensing. No production adoption or successor.
