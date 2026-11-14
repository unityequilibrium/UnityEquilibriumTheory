# Topic 13 Research Wave: Tohei Alpha-V/K-T Table Comparator

MAJOR_RESULT_CLOSURE: `CLOSED_FOR_LANE` for `T13_TOHEI_GRAPHITE_ALPHA_V_K_T_TABLE_COMPARATOR`; Full Topic 13 remains `PARTIAL`.
WHAT_IS_ACTUALLY_CLOSED: Tohei et al. Table I is archived as a primary-paper table comparator with an explicit locator. The same QHA calculation reports graphite at 300 K with `alpha_V=19.8e-6 K^-1` and `B0=28.7 GPa`; separately cited experimental table values are `alpha_V=21.9e-6 K^-1` and `B0=33.8 GPa`.
WHAT_REMAINS_OPEN: The table has no row-level uncertainty, its experimental values come from different cited references, and it does not establish a same-specimen Ding TTG state. A source-grade `alpha_V/K_T` correction and direct volumetric heat-capacity route remain open.
DEPENDENCY_UNLOCKED: Numeric graphite comparator lane only; no `Cp-to-Cv`, Ding `C_src`, Phi calibration, transport, Core, Gravity, or Full Topic 13 unlock.
STATUS: `SOURCE_SCREENED_TABLE_COMPARATOR_NO_CLOSURE`; full gate remains `BLOCKED_OPEN_T13_FULL_BRIDGE`/`PARTIAL`.
WHAT_CHANGED: Added the Tohei table comparator package and extended the graphite `alpha_V/K_T` boundary audit and regression without emitting a correction.
EQUATION_OR_MAPPING: `c_p^V-c_v^V=T*alpha_V^2*K_T`; the table values are recorded as comparator rows only, and no numeric correction is calculated.
VERIFICATION: Matched-source boundary audit passed with all checks true; focused regression `2 passed`; source package hash `7a8dfafd8c06145e08194505aeca933b6f90c27e184cf4db45b56d9375b140c9`; boundary audit hash `7f16734e1f78d29154c1652feb3784290ce16923e772fb42230237ea07ab03f1`; no fit, calibration, target data, threshold adjustment, or Xie 2026 holdout access.
CONTROLLING_BLOCKER: `same_grade_alpha_V_and_K_T_missing`, refined here as missing same-state source-grade uncertainty and Ding-regime mapping.
NEXT_ACTION: Obtain a permitted full P-V-T payload or a direct volumetric `c_v`/same-state `Cp` source with units, uncertainty, specimen/state identity, and Ding-regime mapping; do not combine the Tohei calculated pair with its separately cited experimental values.
CLAIM_BOUNDARY: This result is a source-traceable comparator boundary, not a source-grade thermodynamic correction, Ding validation, UET calibration, TTG prediction, external validation, or Full Topic 13 closure.

SOURCE_PACKAGE: `docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/tohei_2006_graphite_alpha_v_kt_table_comparator_source_package.json`
SOURCE_URL: `https://repository.kulib.kyoto-u.ac.jp/items/57c9b94f-09df-4176-8f5e-9490526b9ab8`
