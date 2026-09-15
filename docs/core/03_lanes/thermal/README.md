# Thermal lane

This package is the canonical home for thermal-lane support modules that have
an explicit source, calibration, unit, and claim boundary.  The He-4 records
here are source-backed external inputs and standard mappings; their presence
does not promote a UET thermal prediction or close the full Topic 13 lane.

## Members

- `he4_svp_reference.py` — source-locked He-4 saturated-vapour-pressure
  reference functions and calibration rows.
- `he4_o2_response_calibration.py` — local alpha and normalized-field
  calibration derived from the declared He-4 reference rows.
- `he4_o2_si_beta_mapping.py` — state-matched SI scale and normalized beta
  mapping with explicit uncertainty propagation.
- `he4_normal_viscosity_kubo.py` — source-locked normal-component shear
  viscosity record and standard Kubo/KMS/entropy interface.

The root paths remain compatibility shims while consumers migrate to this
package.  Organization migration does not alter the source data, evidence
status, parameter provenance, or physics claim boundary.

- thermal_observable_bridge.py — normalized C-to-temperature proxy with Fourier/Cattaneo controls; the gain remains an open mapping coefficient.
- thermal_source_observable_map.py — TTG observable definitions and an explicit Phi-to-kelvin calibration contract; open calibration returns no physical temperature.

- thermal_dimensional_bridge.py — conditional local-equilibrium Phi-to-kelvin bridge with explicit dimensional inputs; it is not a source-free calibration.
- thermal_energy_response_bridge.py — named Phi_E energy-density response branch with heat-capacity conversion and uncertainty requirements; Phi_E is not the base Phi.
- thermal_phi_e_reference_normalization.py — reference-temperature normalization for the named Phi_E lane; it does not calibrate base Phi.
- thermal_response_beta_contract.py — finite-temperature normalized response-beta contract with explicit unit and non-Landauer boundaries.
