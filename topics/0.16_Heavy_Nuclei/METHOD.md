# Method

## Problem Target

This topic tests whether UET information-saturation language can be mapped onto heavy-nuclei binding and fission diagnostics in an auditable way. The current target is a structured benchmark package, not a full first-principles nuclear theory.

## Evidence Lanes

| Lane | Code path | Current status |
| :-- | :-- | :-- |
| SEMF / UET bridge | `Code/01_Engine/Engine_Heavy_Nuclei.py` | reviewed heuristic bridge; currently equals SEMF baseline |
| Fission sanity check | `Code/03_Research/Research_Fission.py` | primary artifact, expected `WARN` |
| Heavy binding comparison | `Code/03_Research/Research_Heavy_Binding.py` | secondary AME subset comparison, needs artifact rows |
| Stability valley / island | `Code/02_Proof/Proof_Stability_Valley.py` | open lane, not primary evidence |

## Variable Framing

| Variable | Meaning | Unit convention | Current role |
| :-- | :-- | :-- | :-- |
| `Z` | proton number | count | isotope identity |
| `N` | neutron number | count | isotope identity |
| `A` | mass number | count | isotope identity and SEMF scale |
| `BE` | total binding energy | MeV in engine; keV or MeV in datasets | verifier metric |
| `a_V`, `a_S`, `a_C`, `a_A`, `a_P` | SEMF coefficients | MeV | bridge coefficients |
| `Q_bridge` | fission energy sanity value | MeV | primary artifact metric |

## Primary Verification Method

1. Load AME2020 heavy-nuclei working copy.
2. Compute U-235 bridge binding energy from `Engine_Heavy_Nuclei.py`.
3. Compare U-235 bridge binding to AME2020 U-235 binding checkpoint.
4. Compute Ba-141 and Kr-92 fragment binding energies from the same bridge.
5. Check whether bridge fission energy is exothermic and within `[100, 250] MeV`.
6. Write artifact status `WARN` when these checks pass but source-locked fragment masses are absent.

## Assumptions

- The UET bridge currently interprets SEMF-like liquid-drop terms; it is not yet an independent derivation.
- Fragment estimates are bridge outputs, not AME2020 source-locked values.
- The U-235 binding checkpoint is useful but too narrow to validate the full model.

## Domain of Validity

- Internal fission sanity check and selected heavy-nuclei binding diagnostics.
- Claim Class C/D boundary language only.

## Excluded Cases

- Evaluated U-235 fission-energy validation.
- Island-of-stability prediction.
- Complete nuclear-stability and decay theory.
- External replication or peer-reviewed validation.

## Dependency Policy

- `0.5_Nuclear_Binding_Hadrons`, `0.17_Mass_Generation`, `0.21_Yang_Mills_Mass_Gap`, `0.23_Unity_Scale_Link`, and `0.0_Grand_Unification` may cite this topic only with explicit SEMF-bridge and missing-fragment limitations.
