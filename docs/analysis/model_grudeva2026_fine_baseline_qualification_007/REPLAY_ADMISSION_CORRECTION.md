# 007 accepted-state admission correction

This separately frozen 007 rule supplements the original failed receipt; it does
not change it. G1 / NO_GOVERNING_PHYSICS_CHANGE. Physical validation remains
NOT_ESTABLISHED. The correction is limited to accepted-state consistency of the
pinned SciPy BDF dense interpolator. Persistence, live/offline fidelity, event
consistency, observer mathematics, interval selection, support, masks and every
scientific accuracy gate remain unchanged. No solver invocation is permitted.

## Cause and scope

Pinned SciPy 1.18.1 builds `t_shift = t_end - h * arange(order)` and
`denom = h * (1 + arange(order))` in binary64. Its differences represent the
Newton polynomial in an equally spaced time coordinate. The step routine may
change order and rescale differences before producing dense output; consequently
the dense `h` can differ from the just-completed interval length. The original
BDF `OdeSolution` selects the following interval at interior accepted times
(`alt_segment=True`, recorded `side=right`). None of these choices is changed.
The upstream [OdeSolution documentation](https://docs.scipy.org/doc/scipy/reference/generated/scipy.integrate.OdeSolution.html)
describes the alternative selection. The actual pinned local source hashes,
rather than the moving documentation version, control this assessment.

At small h relative to absolute time, rounding the shifts need not be small
relative to h. The original fixed absolute accepted-state test conflates this
coordinate error with coefficient inconsistency. Exact stored-polynomial
arithmetic and independent Decimal diagnostics establish that the observed
excess already exists in the stored-coordinate polynomial. The correction does
not assume accurate coefficients: it retains the original bound for the
same-coefficient polynomial with exact time coordinates, independently of the
coordinate and evaluation bounds below. It makes no claim about unrecorded BDF
coefficient operations or continuum accuracy.

## Exact certificate, frozen before its assessment

Retain the original accepted-state gate T = 8 * ALGEBRA for every capture. A
passing original gate needs no recalculation. An accepted-state failure can pass
only when an exhaustive identity-bound scan supplies every exceeding location,
and every location meets this certificate. Events retain the original test.
Unknown failures and missing certificates fail admission.

For the selected order q, endpoint e, recorded dense h, coefficients D_j and
accepted time t, interpret each binary64 value as an exact rational. Verify the
stored shifts and denominators bit-for-bit against the pinned NumPy/SciPy
construction. Let b_sj be the exact Newton basis product using stored shifts and
denominators, and b_ij the exact product using e - j*h and (j+1)*h with no
coordinate rounding. Define P_s = D_0 + sum D_j*b_sj and P_i analogously.

The independently determined coordinate bound is

    C = sum_j |D_j| * |b_sj - b_ij|.

It bounds |P_s - P_i| by the triangle inequality, works at zero factors, and
scales with the actual time, h, order and coefficients. It is not chosen from
the accepted-state discrepancy or its maximum.

Let p_fj be the exact rational representation of each factor produced by the
unchanged binary64 subtraction/division/cumulative-product evaluator. Define

    E_basis = sum_j |D_j| * |p_fj - b_sj|
    S = |D_0| + sum_j |D_j * p_fj|
    u = 2^-53, eta = 2^-1074, n = 2*q + 2
    gamma_n = n*u/(1-n*u)
    E = E_basis + gamma_n*S + n*eta/(1-n*u).

The last two terms conservatively bound the remaining dot product and D_0
addition under round-to-nearest binary64 with gradual underflow. There are at
most q multiplications, q-1 sums and one final addition; n includes two extra
operations. Fused multiply-add requires fewer roundings and is covered. Exact
factor differences include subtraction/division/product rounding, including
underflow. Finite factors and a sum-of-absolute-products overflow guard are
mandatory. The implementation checks the active rounding mode and runtime bit-pattern probes for gradual underflow and denormal-input preservation (rejecting FTZ/DAZ). No numerical
bound is computed from the observed accepted-state maximum.

All of the following exact rational inequalities must hold:

- |P_i - y_accepted| <= T (unchanged coefficient-consistency allowance);
- |y_native - P_s| <= E (independent evaluation-rounding check);
- |P_s - P_i| <= C;
- |y_native - y_accepted| <= T + C + E.

Decimally rendered numbers are reporting conveniences, never decision inputs.
No values are snapped, no interval is switched, and P_i replaces no scientific
observation. The original native reconstruction remains the value audited and
compared. Original live/offline fidelity receipts remain mandatory. A new
certificate is an additional admission record, not a forged PASS in old metadata.

The same disjunction applies to the reused 006 baseline, completed continuation
pilot, observed repeat, modes_fine, time_fine, bed_fine and combined captures.
The unobserved control has no dense capture and retains its exact public-Result
neutrality gate. Previously passing evidence is reused through its original
bindings. Original 005/006 dispositions do not change.

## Execution and review

The diagnostic implementation/PLAN and its completed ledger are preserved at
their original hashes and an external snapshot of the prior controller source. The small correction invocation reuses the serial
controller with an explicit contract, stage table and ledger directory; no
scientific source is patched. Its worker verifies exact stage, contract, lock,
parent identity, environment and source bindings. No deadline, memory ceiling or
invocation quota is introduced. Machine-safety monitoring remains active.

Manufactured regressions must reject coefficient errors, wrong coordinates,
wrong reconstructed values, nonfinite/unsupported input and stage mismatches;
cover zero factors, cancellation, state/time scaling and subnormal values; and
show a coordinate-rounding case without using canonical scientific arrays.
Independent review must approve this contract and implementation before the
certificate is assessed. Final review covers the actual result and exact head.
