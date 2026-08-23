def nested_difference(parent, nested, tolerance=1e-12):
    contrast=parent-nested
    closure=parent-(nested+contrast)
    if abs(closure)>tolerance: raise ValueError("nested residual does not close")
    return {"parent_response":parent,"nested_response":nested,"component_contrast":contrast,
            "closure_error":closure,"numerical_tolerance":tolerance,"nested":True,
            "decomposition_method":"NESTED_DIFFERENCE","causal_eligibility":True}

def attribution(*, nested, causal_share=None):
    if not nested and causal_share is not None: raise ValueError("non-nested comparison cannot carry causal share")
    return "NESTED_DIFFERENCE" if nested else "NONADDITIVE_ATTRIBUTION"
