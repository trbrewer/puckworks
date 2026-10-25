# Exact necessary-shape calculation

All arithmetic determining feasibility, positivity, hull membership, weights and
objectives uses `fractions.Fraction` parsed from authoritative log strings.
Decimals and mg/L conversions are displays, except the explicitly directed
multiplicative enclosures reused from the accepted #364 helper.

## Model implication and its strict converse failure

For extraction r, c_r(V)=A_r exp(−k_r V), A_r>0, k_r>=0 constant throughout
collection. Integrating over [nw,(n+1)w] and dividing by w=5 mL gives
cbar_r,n=B_r q_r^n, where q_r=exp(−k_r w) in (0,1] and
B_r=A_r(1−q_r)/(k_r w)>0; at k_r=0, B_r=A_r. A fixed positive-weight
aggregate over the same extractions has C_n=sum_r a_r q_r^n, a_r>0.
For the four-extraction arithmetic mean, a_r=B_r/4. More components enlarge
this family; no component count, amplitude or rate is fitted here.

Every term is positive and nonincreasing. Expansion and pairing yield

```
C_n C_(n+2) − C_(n+1)^2
  = sum_(r<s) a_r a_s (q_r q_s)^n (q_r−q_s)^2 >= 0.
```

Consequently y_n=log10(C_n/(1 mg/L)) is nonincreasing and convex:
y_(i+1)<=y_i and y_i−2y_(i+1)+y_(i+2)>=0. For ordered nonuniform
coordinates the corresponding requirement is nondecreasing secant slopes.
Supported subsets retain original x values, including gaps.

The converse fails. Concentrations (100,10,1,1), with logs (2,1,0,0), satisfy
both relaxed constraints. Equality in the first log-convexity relation forces
all positive mixture components to share q=0.1, which would require the fourth
concentration to be 0.1. Thus a zero relaxed cost is only necessary-shape
compatibility, not a mixture witness or a four-extraction reconstruction.

## Greatest sequence and exact optimum

For each original supported interval [l_i,u_i], define v_i=min_(j<=i)u_j.
Store p_i as the earliest original supported index attaining that minimum.
Nonincrease implies y_i<=y_j<=u_j for j<=i; hence any feasible y below u is
below v. Conversely v<=u. This proves equivalence of the upper constraints
within the nonincreasing family.

Take the lower convex hull of (x_i,v_i). Remove a middle point whenever its
incoming slope is greater than or equal to its outgoing slope; collinear runs
retain endpoints only. Interpolate linearly between adjacent hull anchors to
obtain h at every original supported coordinate. Since v is nonincreasing,
each hull slope is nonpositive; the hull construction makes slopes strictly
increasing between retained segments. Thus h is nonincreasing and convex and
h<=v<=u. Any other convex sequence f<=v lies below the chord between each two
hull anchors: f_i<=alpha*f_a+beta*f_b<=alpha*v_a+beta*v_b=h_i. Therefore h is
the greatest nonincreasing convex sequence below u, pointwise.

The uniform upper expansion u+epsilon shifts all prefix minima and the greatest
sequence to h+epsilon. Lower feasibility requires l_i−epsilon<=h_i+epsilon,
so necessarily

```
epsilon_LC = max(0, max_i (l_i−h_i)/2).
```

Choosing y=h+epsilon_LC satisfies every expanded original interval and both
shape constraints, proving sufficiency. Its exact maximum interval distance
equals epsilon_LC. If epsilon=0 the witness lies in every original interval;
if positive, an attaining lower constraint has distance epsilon. No floating
tolerance decides whether it is positive.

At each tied controlling i, let a,b be its neighboring hull anchors. Use
alpha=(x_b−x_i)/(x_b−x_a), beta=(x_i−x_a)/(x_b−x_a). For a hull-anchor control
set a=b=i and alpha=1,beta=0. Then every feasible expanded witness obeys

```
l_i−epsilon <= y_i <= alpha*y_a+beta*y_b
  <= alpha*y_(p_a)+beta*y_(p_b)
  <= alpha*u_(p_a)+beta*u_(p_b)+epsilon,
2*epsilon >= l_i−alpha*u_(p_a)−beta*u_(p_b).
```

The middle inequality uses p_a<=a, p_b<=b and monotonicity. Weights use the
HULL-ANCHOR coordinates, never prefix-source coordinates; prefix sources can
repeat. Every tied constraint is retained; epsilon=0 also retains NONNEGATIVITY.
One supported point has h=u and zero cost. Two points need only nonincrease;
there is no curvature constraint. No supported points have no numerical verdict.

## Independent check and LP

`puckworks.analysis.matias2023_aggregation_check` imports neither this hull
producer nor its optimization routine. It reads the original CSV and serialized
witness/certificates, checks original expanded intervals and secant inequalities,
nearest readings, signed residuals, provenance, hull-anchor coordinates, weights,
prefix implications and all tied lower bounds. Primal cost equal to a valid lower
bound proves the optimum independently of the construction algorithm. Checking
submitted hull data is direct constraint checking, not rerunning a hull producer.

The separate numerical cross-check specifies this epigraph LP:

```
minimize epsilon
 y_i − epsilon <= u_i
−y_i − epsilon <= −l_i
 y_(i+1) − y_i <= 0
 (y_(i+1)−y_i)/(x_(i+1)−x_i)
   − (y_(i+2)−y_(i+1))/(x_(i+2)−x_(i+1)) <= 0
 epsilon >= 0; every y_i unbounded in sign.
```

SciPy HiGHS checks all four source layers and a small representative fixture set.
The 1e−9 comparison tolerance is numerical QA only, not scientific acceptance or
exact certification. The exact checker uses rational equality.

All eight original consecutive triples are reported per layer, with
lower=l_i−2u_(i+1)+l_(i+2), upper=u_i−2l_(i+1)+u_(i+2).
Upper<0 excludes locally; upper>=0 is only local non-exclusion. Overlapping
triples may require incompatible readings. For x=(0,1,2,3),
l=(0,−1/2,−3,−3), u=(0,−1/2,0,−3), both upper curvatures are nonnegative
(1,5/2), while epsilon=1/4, attained by (1/4,−3/4,−7/4,−11/4).
Missing original triples are unsupported; subsets never renumber coordinates.

## Uncertainty and support quantifiers

N uses [z,z]; G uses [G_lower,G_upper]; P_outer uses [L_minus,U_plus]; valid
P_inner uses [L_plus,U_minus]. Center support is required for N/G; endpoint
support is required for P. Recovered, covered-but-recovered and clipped-but-recovered
features qualify. A missing endpoint is not inferred. Missing slots stay in all
support/witness tables. Invalid/nonfinite inputs and reversed outer intervals
are SOURCE_INPUT_INVALID; an empty inner construction is INNER_UNAVAILABLE,
not positive discrepancy. No supported observations are SOURCE_SUPPORT_FAILURE.
Incomplete qualified support is SUBSET_LOWER_BOUND_ONLY; it can give an exclusion
on those observations, but neither a complete ten-point optimum nor a full witness.
Zero subset cost does not establish full-cohort compatibility. An exact checking
failure is CHECK_FAILURE; failed numerical agreement is NUMERICAL_CHECK_FAILURE.

G/P rectangles relax shared graphical calibration. Favorable marginal readings
need not be jointly realizable. Graphical recovery, reported SE and unknown assay
error are distinct. For every admissible endpoint realization, set inclusion gives

```
epsilon_LC,Pouter <= epsilon_LC,realized <= epsilon_LC,Pinner,
epsilon_mixture,realized >= epsilon_LC,realized >= epsilon_LC,Pouter.
```

The inner relaxed optimum is NOT a mixture upper bound. Inner positivity alone
does not exclude mixtures for all endpoint realizations. M_LC=10^epsilon_LC is
not an exact best-fit factor for four or arbitrary mixtures. A positive qualified
outer relaxed optimum excludes the necessary shape, and hence mixtures, under
the contract. Zero only establishes necessary-shape compatibility. No confidence
level, equivalence test, practical threshold, independent replication or
"amount explained by aggregation" interpretation is introduced.
