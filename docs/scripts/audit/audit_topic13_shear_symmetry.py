"""Record conditional selection rules without changing material closure."""

import hashlib
import json
from pathlib import Path

import numpy as np

from docs.core.uet_shear_symmetry import constraints, e2_group, pump_doublet

ROOT = Path(__file__).resolve().parents[3]


def main():
    linear, quadratic = constraints()
    linear_rank = int(np.linalg.matrix_rank(linear, tol=1e-10))
    quadratic_rank = int(np.linalg.matrix_rank(quadratic, tol=1e-10))
    files = ['docs/core/uet_shear_symmetry.py',
             'docs/core/test/test_topic13_shear_symmetry.py',
             'docs/core/T13_MATTER_STRAIN_SUSCEPTIBILITY_MATCH.md',
             'docs/core/07_artifacts/correspondence/uet_equation_correspondence_registry_topic13_shear_symmetry_addendum.json',
             str(Path(__file__).relative_to(ROOT)).replace('\\', '/')]
    artifact = dict(
        major_result_id='T13_SCALAR_SHEAR_SELECTION_RULE', topic='0.13',
        closure_level='CLOSED_FOR_LANE', verification_status='CONDITIONAL_ALGEBRA_ONLY',
        assumptions=['Phi transforms as A1g in this proposed material map',
                     'Unbroken material point-group symmetry; Gamma E2g doublet',
                     'Local linear force and symmetric quadratic potential truncation',
                     'No directional external source in scalar-only case'],
        what_is_closed=['Scalar-only linear coherent-shear forcing excluded under assumptions',
                        'Scalar quadratic coupling and directional pump channel remain allowed'],
        equation_or_mapping='l=0; H=h*I; Phi*(s_1^2+s_2^2) is invariant',
        units={'representation': '1', 's': 'm'}, derivation_class='conditional_group_algebra',
        observable='coherent mean versus invariant quadratic mode channel', data_role='NO_DATA_CALIBRATION',
        linear_rank=linear_rank, invariant_linear_dimension=2-linear_rank,
        quadratic_rank=quadratic_rank, invariant_quadratic_dimension=3-quadratic_rank,
        linear_singular_values=np.linalg.svd(linear, compute_uv=False).tolist(),
        quadratic_singular_values=np.linalg.svd(quadratic, compute_uv=False).tolist(),
        group_average_residual=float(np.max(abs(sum(e2_group())/12))),
        equal_intensity_opposite_pump_doublets=[pump_doublet([1, 0]).tolist(), pump_doublet([0, 1]).tolist()],
        original_mass_source_rejected=False, physical_Phi_identification=False,
        open_blockers=['material representation match', 'independent eta and normalization',
                       'pump tensor and bath/occupation dynamics'],
        dependency_unlocked=['choice of coherent versus thermal research observable only'],
        full_core_unlock=False, claim_promotion=False,
        evidence_hashes={p: hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in files},
        claim_boundary='Not a universal no-go, E2g source identification, thermalization proof or alpha calibration.',
    )
    out = ROOT/'docs/core/07_artifacts/topic13/t13_shear_symmetry_audit.json'
    out.write_text(json.dumps(artifact, indent=2, allow_nan=False)+'\n', encoding='utf-8')
    print(json.dumps({k: artifact[k] for k in ('invariant_linear_dimension', 'invariant_quadratic_dimension', 'group_average_residual')}))
    if linear_rank != 2 or quadratic_rank != 2:
        raise RuntimeError('selection-rule verification failed')


if __name__ == '__main__':
    main()
