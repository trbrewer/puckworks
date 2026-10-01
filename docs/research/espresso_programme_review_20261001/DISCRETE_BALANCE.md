> Publication copy of the completed study derivation. See [evidence map](EVIDENCE_MAP.csv) for the original identity. Numerical claims below describe prior producer executions, not this documentation task.

# Discrete balance identity and its scope

**CONFIRMED for the stated functional:** the candidate identity and initial-rate
prediction. **REFINED as a causal explanation:** it predicts a nonzero spatial/
diagnostic imbalance; it does not make every observed finite-tolerance residual a
spatial error, and its initial rate is not a constant loss rate. The original
particle averaging is conservative for the author's shell-volume integral.

All source citations refer to `jamiemfoster/Espresso` commit
`79ebefb72446eb706084e2392cab64bf0fad93a2`, tree
`cb6f42ce893da256d1d6974e724166044e77af94`. One-based indices are used here.

## Functional, units and source map

Let h=1/(N-1), epsilon=1-phi_s, x_j=(j-1)h, axial trapezoid weights
w=(h/2,h,...,h,h/2), and radial shell volumes v from `build_mass.m:3-11`.
For population i at axial site j, s_ij is the radial state scaled by c_s0;
c_j is liquid concentration scaled by c_sat. The state ordering is liquid,
then N fine radial vectors, then N coarse radial vectors (`RHS.m:19-27`).
The dimensionless b_i in this note is geometric area divided by b0, and
Q_i=1/(a_i*b0); beta=c_sat/c_s0 (`define_parameters.m:27-49`).

The author functional is

    M_hat = epsilon * sum_j w_j*c_j
            + sum_i b_i/(4*pi*beta*Q_i) * sum_j w_j*(v^T*s_ij).
    C_hat' = q*c_N.

`checkmass.m:17-41,55-81,93-127` uses exactly these scales and weights. Since
b_i/(3*Q_i)=phi_i and normalized spherical shell weights equal 3*v/(4*pi),
the executed reducer's fine/coarse moments give the same inventory. Direct
checks of all seven retained endpoint/bracket states differ by at most
1.36425e-12 mg ([`functional_equivalence.csv`](balance/functional_equivalence.csv)); no material functional correction
is needed. The author checkmass diagnostic omits explicit boundary flux corrections;
the reported E includes them. Their maximum endpoint difference is 6.12503e-7 mg
in the original tighter run ([`original_reconstruction.csv`](balance/original_reconstruction.csv)).

Dimensional factor is F=V*c_sat*10^6 mg, V=pi*R0^2*L. Dimensionless rates integrate
with respect to t_hat; physical seconds are 33.9*t_hat. Initial soluble inventory
is 4889.334105803382 mg and E(0)=0. None of this specifies measured dry dose or
physical EY. `balance.py` independently reproduces the old unrounded E, cup and
phase inventories within the predeclared 1e-8 mg tolerance.

## Particle blocks telescope

The original particle mass block is B=A*diag(v), where A is source M2 and diag(v)
is source M1 (`build_mass.m:3-31`). Its columns sum to one: at the end,
3/4+1/4=1; the neighbouring column has 1/8+6/8+1/8=1, as do interior columns;
the other end is symmetric. Therefore 1^T*B=v^T. Internal radial flux differences
in `RHS.m:49-54,61-66` telescope, leaving

    v^T*s_ij' = -4*pi*beta*Q_i*G_ij.

After multiplying by the inventory scale, the solid contribution at each axial
site is -b_i*G_ij. Off-diagonal radial averaging does not itself remove soluble
inventory. Original Octave build_mass calls verify the column-sum and weight
identities to 5.99521e-15 and 1.60983e-15 respectively ([`operator_results.json`](balance/operator_results.json)).

## Summing the liquid operator

For j=2,...,N-1, `RHS.m:37-41` gives

    epsilon*c_j' = -q*(c_(j+1)-c_(j-1))/(2*h)
                  + D*(c_(j+1)-2*c_j+c_(j-1))/h^2 + S_j,
    S_j = b1*G1_j+b2*G2_j.

Summing h times the interior equations gives transport terms

    -q/2*(c_N+c_(N-1)-c_1-c_2)
    +D/h*(c_N-c_(N-1)-c_2+c_1).

Interior release cancels the corresponding solid loss. The grain equations still
release at both axial endpoints, while liquid endpoint rows are algebraic rather
than local storage/source equations (`RHS.m:36,43`; `build_mass.m:36-38`). The
trapezoid inventory nevertheless assigns those liquid endpoints h/2 weights.
Adding those storage terms, endpoint solid loss and C_hat'=q*c_N yields

    (M_hat+C_hat)' = A_adv + A_disp + A_end
    A_adv  = q/2*(c_N-c_(N-1)+c_1+c_2)
    A_disp = D/h*(c_N-c_(N-1)-c_2+c_1)
    A_end  = h/2*(epsilon*(c_1'+c_N')-S_1-S_N).

This is a spatial-operator/diagnostic construction effect, involving cancellation
between transport, endpoint release and endpoint storage. It is not simply a
missing positive sink or an experimental boundary loss.

Differentiating the constant-coefficient algebraic constraints gives

    c_1' = (D/h)*(2*c_2'-c_3'/2)/(q+3*D/(2*h))
    c_N' = (4*c_(N-1)'-c_(N-2)')/3.

`operator_checks.m` obtains algebraic coefficients through original RHS basis
calls, uses interior derivatives from original RHS calls, and solves only the
nonsingular N-by-N particle block for independent inventory derivatives. It never
inverts or pseudo-inverts the complete singular matrix. Initial, three nonuniform
boundary-consistent synthetic and thirteen saved states are checked. Saved states
are not projected. The largest identity discrepancy is 1.77688e-14 dimensionless,
against the predeclared 5e-11*(1+sum of absolute component rates) criterion.
Sign, endpoint-weight and unit mutations are rejected. All actual algebraic
residuals are retained in [`operator_checks.csv`](balance/operator_checks.csv) and [`run_statistics.csv`](balance/run_statistics.csv).

## Integrated signs and initial prediction

The source/reducer conventions are

    F_in_total = F*integral[q*c_1-D/h*(-1.5*c_1+2*c_2-0.5*c_3)] dt_hat
    F_out_disp = F*integral[-D/h*(0.5*c_(N-2)-2*c_(N-1)+1.5*c_N)] dt_hat
    E = I0 - M_solid - M_liquid - C_adv - F_out_disp + F_in_total.

Thus each advective, dispersive and endpoint-release contribution to predicted E
is minus F times its signed rate integral. Endpoint storage is integrated exactly
as -F*epsilon*h/2*Delta(c_1+c_N), without differencing output samples. The boundary
correction -F_out_disp+F_in_total is added once. These signs produce the candidate
integrated budget in the task. Actual nonzero constraint fluxes are retained.

At the initial state c=0, s=1, S0=(b1+b2)*K. Interior c'=S0/epsilon, while the
inlet derivative is reduced by its boundary constraint. Consequently

    E_core'(0) = F*h/2*S0*q/(q+3*D/(2*h)).

Original-operator evaluation gives 95.345648956129 mg per scaled time, or
2.812556016405 mg/s. This was calculated, not inserted as an expected target.
It matches the proposed initial prediction but cannot be multiplied by shot time
to infer endpoint loss. The resolved predicted deficit is only 2.207446 mg at
scaled time 1 and 5.366325 mg at 10.

## Evidence boundary

Old N=40 exports retain twelve moment/flux columns, not full u(t). They omit
boundary-neighbour and endpoint particle states. Two diagnostic replays recover
those values, reproducing all old history bytes and endpoint/bracket states
exactly ([`exact_replay_checks.json`](balance/exact_replay_checks.json)). New `boundary_history.csv` files contain
raw returned-state components, not inferred defects. The old N=6 files are full
short trajectories and are not mistaken for N=40 evidence. No full missing
trajectory is fabricated from diagnostic snapshots or RHS trial times.
