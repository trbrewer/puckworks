# Invalid versus incomplete evidence

Missing an otherwise optional measurement for an authorized relevant comparator, missing required uncertainty on otherwise closed evidence, or partial applicable-gate coverage is legitimate incompleteness and retains existing `UNRESOLVED` semantics. An authorized universe with no scientifically relevant matched apparatus comparator remains `NOT_EVALUATED`.

Dangling, duplicate, wrong-type, stale, cross-context, unauthorized, orphan, extraneous, noncanonical, or provenance-mismatched records are invalid. They terminate production/verification with a structured `ValueError` reason category and cannot be downgraded to a scientific state.
