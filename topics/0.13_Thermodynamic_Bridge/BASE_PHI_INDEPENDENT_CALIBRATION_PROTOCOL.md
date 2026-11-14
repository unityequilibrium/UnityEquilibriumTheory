# Topic 13 Base-Phi Independent Calibration Protocol

MAJOR_RESULT_CLOSURE: `OPEN` -- this is an evidence requirement, not a calibration result.

WHAT_IS_ACTUALLY_CLOSED: An admissible route to identify base `Phi` amplitude is specified: one independent source must supply matched SI energy/response amplitude, base-`Phi` amplitude, units, uncertainties, preprocessing, row identities, and hashes.

WHAT_REMAINS_OPEN: No paired base-`Phi`/SI-observable record is currently available. `Phi_E` remains a separate energy-response coordinate.

DEPENDENCY_UNLOCKED: None until a record passes the stated checks.

STATUS: `OPEN_INDEPENDENT_BASE_PHI_CALIBRATION_REQUIRED`

WHAT_CHANGED: The protocol prohibits choosing `alpha_Phi_K` or the base-`Phi -> Phi_E` scale from a TTG target curve, residual, or Xie 2026.

EQUATION_OR_MAPPING:

```text
Phi_E = Delta_u / e0
Phi_E = s_material * Phi_base
alpha_Phi_K = (e0 / c_v) * s_material
```

VERIFICATION: Require a preregistered independent calibration source, matched material/state/geometry, SI and base-`Phi` amplitudes with uncertainty, full provenance, and an audit that calibration did not read Xie 2026.

CONTROLLING_BLOCKER: `independent_paired_base_Phi_amplitude_and_SI_observable_record_missing`

NEXT_ACTION: Acquire a permitted paired measurement and run the preregistered calibration without post-inspection tuning.

CLAIM_BOUNDARY: No numerical scale, fit, prediction, external validation, or Full Topic 13 closure is produced by this protocol.
