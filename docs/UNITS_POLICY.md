# Units policy (P1.1)

Puckworks is **SI internally**. Every quantity crossing a public contract boundary is in SI unless
its field/name says otherwise:

| quantity | SI unit |
|---|---|
| pressure | pascal (Pa) |
| length / depth / radius | metre (m) |
| time | second (s) |
| mass | kilogram (kg) |
| temperature | kelvin (K) |
| porosity / share / extraction fraction | dimensionless in [0, 1] |
| flow rate | kg/s (mass) — g/s only at a machine/export boundary, named accordingly |

## The one machine-facing exception: bar-gauge pressure

Espresso machines report **bar-gauge overpressure**. That unit appears ONLY at input/output
boundaries and is named so it cannot be confused with Pa:

- `pressure_pa`, `absolute_pressure_pa`, `p_m` (Pa) — internal/SI;
- `P_of_t` and other machine/export fields carry **bar-gauge** and say so in their comment.

Convert at the boundary with `puckworks.validate.bar_gauge_to_pa` / `pa_to_bar_gauge`
(`1 bar = 100000 Pa`). Never mix the two in one expression.

### The factor-of-100000 guard

A bar value (~9) accidentally used where Pa (~9e5) is expected is the classic error. Guard inputs
at boundaries with `is_plausible_pressure_pa` / `assert_pressure_pa` — a shot pressure in Pa is
O(1e5–1.2e6); anything below ~1e4 Pa is almost certainly bar (off by ~1e5). `tests/test_validate.py`
carries the regression.

## Boundary validation (opt-in, additive)

`puckworks.validate` provides early-failing checks with actionable messages — `require_finite`,
`require_positive`, `require_nonnegative`, `require_fraction`, `require_monotonic_increasing`,
`require_aligned`, `require_ndim`, `require_closure` — and a versioned `Trace` structure
(`time` + `channels` + `units`, missing samples as `nan`, never silently dropped) to replace
free-form trace dicts where a caller chooses to. Importing the module changes no numerical
behaviour; adopt it at a boundary, not by rewriting numerical kernels.

## Changing an existing pressure field

The pressure naming is a **confirmed ambiguity to audit**, not licence to change numbers. Before
renaming/converting any pressure field: trace every caller, add an adapter + deprecation, and prove
with a regression test that existing valid inputs are numerically unchanged.

## Controlled vocabularies

Finite categorical fields use controlled values, e.g. flow closures are `poroelastic` / `ck`
(`validate.CLOSURES` / `validate.Closure`); validate with `require_closure`.

## Serialization

Public JSON schemas are versioned (`schema_version`). Add fields; never repurpose them. Provide a
reader/migration for any already-published schema (`contracts.SCHEMA_VERSION`,
`Trace.schema_version`, the evidence-graph and status schema versions).
