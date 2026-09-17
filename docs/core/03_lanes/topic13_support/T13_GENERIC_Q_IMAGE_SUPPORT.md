# Generic-q support in archived detector images

MAJOR_RESULT_CLOSURE: PARTIAL; actual common finite image support preserves conditional ideal target observability.
WHAT_IS_ACTUALLY_CLOSED: Both archived pump datasets retain21 or22 of24 candidate basal footprints at each of four generic q. Restricting the ideal operator to those rows preserves rank8 and local-target identifiability for both mirrored coordinate alternatives, all16 cases.
WHAT_REMAINS_OPEN: Full reciprocal indexing, distortion/strain/orientation uncertainty, physical intensity response, covariance, elastic separation and UET normalization.
DEPENDENCY_UNLOCKED: None; full_core_unlock=false. Existing-image reciprocal indexing is now a concrete next action rather than immediate new-data acquisition.
STATUS: ACTUAL_MASK_SUPPORT_WITH_CONDITIONAL_IDEAL_OPERATOR.
WHAT_CHANGED: Hash-checked exported arrays read with allow_pickle=false; source origin/calibration used for fixed footprints; ideal operator retested after support restriction. No signal inversion or intensity-driven selection.
EQUATION_OR_MAPPING: Rotate model G100 to source positive detector y; retain both x reflections; detector center=source origin+(Q_y,Q_x)/calibration. Pixel centers within1.5 pixels on each axis form a fixed footprint.
VERIFICATION: Five support/target tests PASS; all archived ON/OFF rows participate in common finite masks;16 restricted operators remain target-identifiable. Source and array hashes checked; foundation audit PASS/foundation BLOCKED.
CONTROLLING_BLOCKER: full_reciprocal_indexing_and_detector_weighted_identifiability.
NEXT_ACTION: Check multiple noncollinear Bragg centroids against this candidate map and quantify geometry uncertainty. Then evaluate physical response/covariance and finite-patch integration before extracting a target signal.
CLAIM_BOUNDARY: Pixel availability plus ideal rank is not an experimentally calibrated inversion. One-vector alignment and mirror alternatives do not establish complete orientation. No alpha, population, heat, temperature or full-topic promotion.

## Actual support outcome

The source is the existing processed400nm and800nm records. A footprint is retained only if it lies inside the image and every pixel in it is finite in every ON and OFF frame of that record. No absent value is filled. The footprint size is a declared diagnostic choice, not an optimized aperture or physical resolution claim.

| Reduced q | Full finite rows out of24, each dataset and mirror |
| --- | --- |
| (.07,.113,0) | 22 |
| (.173,.097,0) | 22 |
| (.23,.19,0) | 21 |
| (.3,.12,0) | 21 |

The source first-peak momentum is2.94926726 inverse angstrom and the model G100 magnitude is2.94936993 inverse angstrom. This close radial correspondence alone does not verify other Bragg indices, detector handedness, strain, distortion or material equivalence. The model lattice scale is retained, not fitted to these numbers.

For each retained row set, the ideal point response is recomputed at the same q and G and the local target is tested against its row space. All16 cases remain identifiable numerically with rank8. This is stronger than counting rows, but weaker than testing a real finite-pixel detector response: aperture integration, covariance and source preprocessing remain unmodeled.

The source images were symmetry processed; different patches therefore need not be statistically independent. Equal support under the two mirrors neither establishes handedness nor doubles the number of independent observations. The two pump datasets are not merged as one shared population state.

## Next decision

There is no demonstrated need to acquire a new tilted dataset merely because the old symmetry-line diagnostic was rank-deficient. Existing generic-q regions survive the archived masks. The actionable bottleneck is now indexing those regions accurately and obtaining an honest uncertainty/response model. If those checks fail, the complementary-geometry route remains available, but cannot be assumed necessary in advance.

Evidence: `artifacts/t13_generic_q_image_support.json`, including all patch coordinates, retained rows, conditional tests, upstream hashes and every array-export hash. Raw images remain local-only; only derived support metadata is committed.
