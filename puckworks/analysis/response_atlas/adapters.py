ADAPTER_VERSIONS={"pressure_drop_to_gradient":"2.0.0","scalar_darcy_flux_override":"1.0.0",
                  "flow_area_density":"1.0.0","permeability_to_resistance":"1.0.0"}

def pressure_drop_to_gradient(drop_pa, length_m, *, pressure_reference=None,
                              inlet_node=None, outlet_node=None, viscosity_pa_s=None,
                              density_kg_m3=None, temperature_basis=None,
                              geometry_provenance=None):
    required = (pressure_reference, inlet_node, outlet_node, viscosity_pa_s,
                density_kg_m3, temperature_basis, geometry_provenance)
    if length_m <= 0 or any(v is None for v in required):
        raise ValueError("pressure-gradient adapter requires bed length, differential basis, nodes, properties, temperature, and geometry provenance")
    if pressure_reference != "DIFFERENTIAL" or inlet_node != "BED_INLET" or outlet_node != "BED_OUTLET":
        raise ValueError("pressure-gradient adapter requires BED_INLET-to-BED_OUTLET differential pressure")
    return drop_pa / length_m
