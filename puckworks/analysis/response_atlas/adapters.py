ADAPTER_VERSIONS={"pressure_drop_to_gradient":"1.0.0","scalar_darcy_flux_override":"1.0.0",
                  "flow_area_density":"1.0.0","permeability_to_resistance":"1.0.0"}

def pressure_drop_to_gradient(drop_pa,length_m):
    if length_m <= 0: raise ValueError("positive bed length required")
    return drop_pa/length_m
