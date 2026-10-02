> Publication copy of the completed study derivation. See [evidence map](EVIDENCE_MAP.csv) for the original identity. Numerical claims below describe prior producer executions, not this documentation task.

# Derivative supplied to the installed ode15s interface

READ source: jamiemfoster/Espresso@79ebefb72446eb706084e2392cab64bf0fad93a2,
`RHS.m:19-67` and `build_mass.m:1-38` (obtain the pinned external source for optional replay). The adapter
supplies J=df/du for M u'=f(u). M is the exact source matrix cast to sparse,
including M2*M1 rather than M1 alone. No inverse mass or residual mass term
is included in J. `linear_jacobian.m` caches only the constant linear stencils;
`rhs_jacobian.m` adds the state-dependent surface derivatives.

Write h=dx, gamma=1/(1-phi_s), D=Deff. Liquid interior row j has columns
j-1,j,j+1 equal to gamma*(D/h²+q/(2h), -2D/h², D/h²-q/(2h)). Its nonlinear
row contributions are gamma*bet_i*dG_i/dl in column j and
gamma*bet_i*dG_i/ds in that population's surface column. These follow directly
from `RHS.m:37-41`; the boundary rows receive no reaction contributions.

The inlet algebraic row has columns 1,2,3 equal to
(3D/(2h)+q, -2D/h, D/(2h)); the outlet row has columns N-2,N-1,N equal to
(1/2,-2,3/2), from `RHS.m:36,43`. Neither boundary row is divided by mass.

For each particle population and each axial site, define
c_(i+1/2)=4*pi*((x_i+x_(i+1))/2)^2*Ds/h. Each interior radial row has
(c_(i-1/2), -(c_(i-1/2)+c_(i+1/2)), c_(i+1/2)); the centre row is
(-c_(3/2),c_(3/2)), and the surface diffusion row is
(c_(N-1/2),-c_(N-1/2)). These are the two flux differences in
`RHS.m:49-54,61-66`. The surface row also receives
-4*pi*beta*Qi*(dGi/dl,dGi/ds) in its own liquid/surface columns.
Surface indices are N+j*N (fine) and N+N*N+j*N (coarse), j=1..N.

For G=K*(1-l)*s*(s-beta*l), the product rule gives

    dG/dl = -K*s*(s-beta*l) - K*beta*s*(1-l)
           = -K*s*(s+beta-2*beta*l)
    dG/ds = K*(1-l)*((s-beta*l)+s)
           = K*(1-l)*(2*s-beta*l).

VERIFIED independently using complex perturbations of the unexpanded polynomial,
then directional central differences of the ORIGINAL complete RHS (not another
copy of the Jacobian algebra). The latter covers both algebraic rows, interior
liquid and radial stencils, and both particle populations; see `verify_sparse.m`
and `jacobian_differences.csv`. Coarse differences show truncation error, and
h=1e-7 shows more cancellation than h=1e-5. The selection of the better of the
last two h values was declared beforehand in `CONTRACT.md`, not changed after
inspection. These are numerical implementation checks, not new model physics.
