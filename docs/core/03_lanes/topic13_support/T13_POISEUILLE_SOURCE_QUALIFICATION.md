# Phonon transport source qualification, 2026-09-10

MAJOR_RESULT_CLOSURE: PARTIAL; alternate source role identified, no new numeric physical input accepted.

WHAT_IS_ACTUALLY_CLOSED: Huang et al. (2023), DOI10.1038/s41467-023-37380-5, describes graphite ribbons with both natural and purified isotope compositions. Its Methods use literature specific heat in a finite-element extraction of in-plane conductivity. Separate BTE calculations use harmonic/third-order force constants from Quantum ESPRESSO and ShengBTE. Data availability directs readers to request data from corresponding authors. No numeric force-constant or C_src package was acquired in this pass. [Primary article, Methods and Data availability](https://www.nature.com/articles/s41467-023-37380-5).

WHAT_REMAINS_OPEN: Permissioned numeric arrays, mode/mesh indexing, units, source uncertainty and match to the intended TTG material/state. The theory's finite-width geometry and boundary assumptions need an explicit correspondence, not a material-name substitution.

DEPENDENCY_UNLOCKED: Targeted source-request qualification only; no physical dependency unlock.

STATUS: SOURCE_ROLE_IDENTIFIED_NUMERIC_INPUT_NOT_ACQUIRED.

WHAT_CHANGED: Added this source qualification and a separate holdout exposure declaration. No equation, parameter, fit, threshold or numeric research artifact changed.

EQUATION_OR_MAPPING: Imported specific heat -> conductivity extraction is not independent evidence for that same specific heat. This is an inference about validation independence, not a claim that the publication's method is invalid. A standard-physics conductivity extraction also cannot become a UET Kubo record without the required microscopic/observable mapping.

VERIFICATION: Read primary Methods, Data availability and reference33 identifying Guo et al., Phys.Rev.B104,075450(2021), as the detailed modeling route. Compared the source role with t13_full_closure_minimal_input_contract.json and t13_independent_csrc_acceptance_contract.json. No new scientific verifier or experiment was run for this literature-only result.

CONTROLLING_BLOCKER: Missing numeric acquisition and material-state correspondence. Neither article access nor a reported conductivity supplies the independent base-Phi SI anchor.

NEXT_ACTION: If pursuing this route, request second/third-order force constants, structure/masses, q-mesh weights, scattering records, uncertainty and redistribution terms; separately establish material/state match. Do not rerun image fits as a substitute for these inputs. No author contacted and no request sent in this pass.

CLAIM_BOUNDARY: Literature qualification only, not source-package closure, C_src acceptance, independent alpha, transport match or Full Topic13 promotion. Historical xie_2026_accessed=false artifacts must not be interpreted as a current statement that no public summary has ever been exposed; see T13_HOLDOUT_EXPOSURE_2026_09_10.json.
