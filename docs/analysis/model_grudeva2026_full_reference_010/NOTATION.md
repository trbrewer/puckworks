# Dimensional notation clarification

The frozen CONTRACT's published-definition line prints
`Q_i=phi_T/(a_i*b_i*)`. The radius in that denominator is dimensional:
the correct typography is **`Q_i=phi_T/(a_i* b_i*)`**, as in article Eq. 21.
Together with Eq. 4, `b_i*=3*phi_i/a_i*`, this gives
`Q_i=phi_T/(3*phi_i)`.

This corrects an omitted star in prose. The implementation, parameter checks,
focused controls and frozen matrix already use `Q_f=5/48` and `Q_b=5/12`.
No equation, parameter, numerical method, threshold or campaign row changed.
The original hash-bound contract remains intact. The retained article text
identified in SOURCE.json was rechecked at Eqs. 4 and 21 for this clarification.
