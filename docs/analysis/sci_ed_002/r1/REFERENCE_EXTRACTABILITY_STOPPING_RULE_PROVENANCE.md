# Reference-extractability stopping-rule provenance

The R0 rule is preserved for audit but is not promoted. Public paired-analyte papers provide hot-water extraction and recovery/precision evidence; neither prescribes or quantitatively derives 1%, two consecutive fractions, or eight cycles. Those three critical elements are therefore `UNSUPPORTED_DESIGN_CHOICE`, which forces the method-specific blocked disposition.

The statistic is blank-corrected analyte mass in the current fraction divided by cumulative non-negative blank-corrected recovery through that fraction. Raw negative results remain stored; zero substitution is limited to the stopping statistic. `<LOD` and `<LOQ` are censored, and a censored fraction cannot qualify. An above-LOQ fraction outside the validated precision range cannot qualify. Physical extraction continues until both analytes stop or cycle eight; an earlier analyte endpoint is frozen while later fractions remain recorded. Reaching eight without qualification yields `MAXIMUM_REACHED_NOT_QUALIFIED`.

No rule value changed because no alternative commissioning-ready numeric rule could be defended without invention. This is a pre-measurement correction, not post-hoc tuning.
