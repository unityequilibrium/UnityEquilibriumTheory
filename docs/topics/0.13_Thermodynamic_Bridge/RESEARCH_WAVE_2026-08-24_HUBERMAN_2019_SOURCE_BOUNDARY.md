# Research Wave: Huberman 2019 TTG Source Boundary

MAJOR_RESULT_CLOSURE: `CLOSED_FOR_LANE` for `T13_HUBERMAN_2019_TTG_SOURCE_BOUNDARY`.

WHAT_IS_ACTUALLY_CLOSED: The public Huberman 2019 route is source-identified and its PBTE formula/setup layer is recorded. The route is bounded as formula/setup context only; it does not contain an accepted numeric `C_src` package.

WHAT_REMAINS_OPEN: Machine-readable mode-resolved `c_mu(T)`, aggregate `C_src(T)`, raw TTG time series, second- and third-order force constants, source-grade uncertainty, material-state mapping to the 2022 lane, base-Phi amplitude, and `alpha_Phi_K` remain open.

DEPENDENCY_UNLOCKED: Standard PBTE formula/source-boundary lane only. No `C_src`, alpha, physical transport, Core, Gravity, or Full Topic 13 dependency is unlocked.

STATUS: `PASS_SCOPED_HUBERMAN_2019_SOURCE_BOUNDARY_NO_CORE_PAYLOAD`; canonical Full Topic 13 gate remains `BLOCKED_OPEN_T13_FULL_BRIDGE`.

WHAT_CHANGED: Added the source-boundary package and linked audit. Added Huberman 2019 and Ding 2017 force-constant requests to the existing author-request manifest without changing any acceptance status.

EQUATION_OR_MAPPING: `partial_t g_i + v_i dot grad g_i = Q p_i + sum_j W_ij(g_j^0 - g_j)`; `Delta_T_tilde = sum_i(g_i_tilde) / C`; `C = sum_i c_i`. No mapping from source `g_i` or `C` to UET `Phi` or UET `C` is asserted.

VERIFICATION: JSON parsing passed; observed arXiv PDF hash is recorded; source route has no row-level numeric `C_src`, force-constant, raw TTG, or paired base-Phi payload; input-package audit passed with zero accepted packages; closure matrix remains 10 requirements, 36 subresults, 7 blockers, and 0 Core-closed subresults.

CONTROLLING_BLOCKER: `ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing`; independent `alpha_Phi_K`, dimensional SI anchor, and physical Kubo/SK/KMS/entropy inputs remain separate blockers.

NEXT_ACTION: Send one bounded request to the corresponding authors for the 2022 PBTE package and the 2017/2019 force-constant, full-scattering, and TTG response inputs. If a payload arrives, run the fail-closed record contract before any gate promotion.

CLAIM_BOUNDARY: This is a source-availability boundary, not a numeric `C_src` result, not an independent alpha calibration, not a TTG prediction, and not Full Topic 13 or external validation.

EVIDENCE_PATHS: `docs/core/artifacts/t13_huberman_2019_ttg_source_boundary_audit.json`; `docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/huberman_2019_ttg_source_boundary_package.json`; `docs/core/artifacts/t13_closure_input_package_audit.json`; `docs/core/artifacts/t13_topic13_closure_matrix.json`.

EVIDENCE_HASHES: source-boundary audit `FA25C313272A79230263C92BF315510E11842D11070C41D67E41D4CB8F88C3AE`; package `F70FF820EA3CB16023D23BB3FD7D36D6ED486357B8CBC6CEB81BF2FD35492844`; input audit `BDE78DC8381E522CB477559B2B0BCC6C2DA5C834860AFAC1C735F870EA74A546`; matrix `B55AC2FC63CDFF1B9103A1A010B2D33CF47660D01BD0C99B8F512450E4438D7C`.
