# Research Wave: Calorine/Zenodo PBTE Numeric C_src Reproduction (2026-08-14)

MAJOR_RESULT_CLOSURE: CLOSED_FOR_LANE
WHAT_IS_ACTUALLY_CLOSED: T13_CALORINE_ZENODO_NEP_BTE_NUMERIC_REPRODUCTION. The public Calorine/Zenodo graphite NEP input was rerun with a fixed 4x4x2 force-constant state. The latest 8x8x4 to 10x10x5 q-mesh pair has maximum relative C_src change 0.0023908135.
WHAT_REMAINS_OPEN: Ding material/state equivalence, source-grade uncertainty, Ding C_src acceptance, alpha_Phi_K, non-circular bridge/beta, EOS/transport/KMS/entropy, and dimensional Phi mapping.
DEPENDENCY_UNLOCKED: Candidate numeric reproduction lane only.
STATUS: PASS_SCOPED_CALORINE_NUMERIC_C_SRC_REPRODUCTION.
WHAT_CHANGED: Added source package, persistent summaries and HDF5 outputs, machine-readable audit, full-gate source-package projection, registry sync, and regression tests.
EQUATION_OR_MAPPING: C_src(T) = [sum_q w_q sum_mu c_qmu(T)] / [sum_q w_q V_primitive], with SI conversion from eV K^-1 per mode per primitive cell to J m^-3 K^-1. No Phi or alpha mapping is inferred.
VERIFICATION: Source hashes, archived payloads, unit conversion, fixed force constants, latest mesh preflight, no-fit, and holdout audit pass.
CONTROLLING_BLOCKER: ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing.
NEXT_ACTION: Resolve material/state equivalence and source-grade uncertainty against the independent C_src acceptance contract.
CLAIM_BOUNDARY: Candidate harmonic/RTA PBTE reproduction only; not Ding validation, alpha calibration, TTG prediction, external validation, or Full Topic 13 closure.
EVIDENCE_HASHES: package 2672a3fe2d60e564c7e9c4eff17944f5db4d3ff62bc20be32960912fe48500ca; audit 822a736824feff7223a6290734eb21a3891950eaa16af39b3864a83ecd72f135; full gate 4638941a2d1387df91048905a255f4641a35b83fea753a0b52086d11120aaa07; register b5bf4ceef12b075474c784874dcfc5ef0519176edc694629eb57c92ebe437a7c; dependency 8f426f75c104912b68a086ef560f9a63ae9b4ec4e75ae9666ef829231f4caf1d.
