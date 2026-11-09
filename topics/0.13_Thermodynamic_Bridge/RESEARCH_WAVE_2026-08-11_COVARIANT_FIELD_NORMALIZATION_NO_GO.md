# Topic 13 Research Wave: Covariant Field-Normalization Identifiability

MAJOR_RESULT_CLOSURE:
`T13_COVARIANT_FIELD_NORMALIZATION_IDENTIFIABILITY_NO_GO` is `CLOSED_FOR_LANE`.

WHAT_IS_ACTUALLY_CLOSED:
- The current covariant response-scalar action has a continuous field-coordinate rescaling that preserves the action sector and any proportional normalized coordinate.
- The rescaling makes a covariant-to-normalized field scale non-identifiable while `Z_Phi`, `m_Phi^2`, `lambda_Phi`, and `xi_Phi` are not source-locked physical quantities.
- Setting a canonical kinetic coefficient is a coordinate convention. It does not create a physical amplitude, a system-specific SI energy density, `e0`, or `alpha_Phi_K`.

WHAT_REMAINS_OPEN:
- A declared `Phi_normalized` mapping with an ontology-preserving coarse-graining rule is absent.
- A source-locked field residue or response-observable amplitude is absent.
- A system-specific SI coefficient and energy-density contract is absent.
- Base `Phi -> Phi_E`, `e0`, numeric `C_src(T)`, independent `alpha_Phi_K`, beta, EOS, transport, SK/KMS, entropy current, and dissipative balance remain open.

DEPENDENCY_UNLOCKED:
None. The no-go prevents an invalid action-default calibration but does not unlock the full thermal bridge, curved 3+1, or Gravity.

STATUS:
`PASS_SCOPED_NO_GO_COVARIANT_FIELD_NORMALIZATION` for the identifiability lane. Full Topic 13 remains `BLOCKED_OPEN_T13_FULL_BRIDGE` and `PARTIAL`.

WHAT_CHANGED:
Added a deterministic action-sector rescaling witness, a machine-readable no-go artifact, regression coverage, and a gate/register/dependency integration record.

EQUATION_OR_MAPPING:
For `delta_phi' = s delta_phi`, the existing scalar sector remains invariant under

```text
Z_Phi' = Z_Phi / s^2
m_Phi^2' = m_Phi^2 / s^2
lambda_Phi' = lambda_Phi / s^4
xi_Phi' = xi_Phi / s^2
rho_*' = rho_*
Phi_scale' = s Phi_scale
```

Thus `Phi_normalized = delta_phi/Phi_scale` remains unchanged. This proves only that the current action cannot supply the missing field scale by itself. The conditional thermal relation remains

```text
Delta_Tq = (e0/C_src) Phi_E
```

after a separate base `Phi -> Phi_E` derivation.

VERIFICATION:
Run:

```powershell
.venv\Scripts\python.exe docs\scripts\audit\audit_topic13_covariant_field_normalization_identifiability.py
.venv\Scripts\python.exe docs\scripts\audit\sync_topic13_covariant_field_normalization_into_gates.py
.venv\Scripts\python.exe -m pytest docs/core/test/test_topic13_covariant_field_normalization_identifiability.py docs/core/test/test_topic13_covariant_field_normalization_integration.py -q
```

The audit uses one deterministic algebraic witness only. It reads no TTG target, performs no fitting, emits no numeric `e0` or `alpha_Phi_K`, and does not access Xie 2026.

CONTROLLING_BLOCKER:
`physical_field_normalization_observable_and_SI_coefficient_provenance_missing`.

NEXT_ACTION:
Obtain either a source-locked covariant field residue/response-observable amplitude plus a system-specific SI action contract, or an independent non-TTG `alpha_Phi_K` calibration record. Then derive the base `Phi -> Phi_E` relation without using the locked holdout.

CLAIM_BOUNDARY:
This is a structural no-go for the current natural-unit scalar implementation. It does not show that physical normalization is impossible, does not identify `Phi` with temperature or heat flux, does not promote `R_gen`, and does not close Topic 13 or UET globally.
