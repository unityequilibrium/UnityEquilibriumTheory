"""Audit admissibility, never apply a cross-model phonon correction."""

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT/'docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research'
ART = ROOT/'docs/core/artifacts'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def assess(source, mode):
    rows = source['rows']
    spacing = float(mode['primitive_lattice_angstrom'][2][2])/2
    reference = rows['reference_spacing']['value']
    gamma = rows['fixed_plane_gamma']['value']
    # Derivative of the published power law at its own reference state only.
    derivative = -6*gamma
    return {
        'source_state_log_squared_energy_strain_derivative': derivative,
        'fit_error_only_derivative_uncertainty': 6*rows['fixed_plane_gamma']['uncertainty'],
        'MP48_spacing_angstrom': spacing,
        'source_reference_spacing_angstrom': reference,
        'MP48_strain_relative_to_source_reference': spacing/reference-1,
        'above_compressive_reference': spacing > reference,
        'full_fit_domain_membership': 'OUTSIDE' if spacing > reference else 'NOT_ESTABLISHED',
        'cross_model_transfer_allowed': False,
        'corrected_MP48_frequency': None,
        'physical_D_tensor': None,
        'alpha_Phi_K': None,
    }


def main():
    source_path = DATA/'sun_2017_interlayer_strain_source_package.json'
    mode_path = ART/'t13_mp48_interlayer_mode_residue_audit.json'
    source = json.loads(source_path.read_text(encoding='utf-8'))
    mode = json.loads(mode_path.read_text(encoding='utf-8'))
    raw = ROOT/source['raw_path']
    if digest(raw) != source['sha256']:
        raise ValueError('source PDF hash mismatch')
    for relative, expected in mode['evidence_hashes'].items():
        if digest(ROOT/relative) != expected:
            raise ValueError('stale mode evidence: '+relative)
    result = assess(source, mode)
    artifact = dict(
        major_result_id='T13_INDEPENDENT_AXIAL_STRAIN_SOURCE_TRANSFER_BOUNDARY',
        topic='0.13', closure_level='PARTIAL',
        what_is_closed=['Independent published-model axial strain route located; direct MP48 transfer is not admissible.'],
        equation_or_mapping='At source reference strain: d ln(nu^2)/d epsilon_zz=-6*gamma',
        units={'log_squared_energy_strain_derivative': '1'},
        derivation_class='derivative_of_published_fit_not_microscopic_UET_derivation',
        observable='source-model shear spectral strain sensitivity',
        data_role=source['data_role'], verification_status='SOURCE_JOIN_CHECKED_TRANSFER_BLOCKED',
        result=result,
        open_blockers=['same-state strained force constants', 'model uncertainty', 'UET mode/normalization'],
        dependency_unlocked=[], full_core_unlock=False, claim_promotion=False,
        source_row_hashes={key: hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()
                           for key, value in source['rows'].items()},
        evidence_hashes={str(p.relative_to(ROOT)).replace('\\', '/'): digest(p)
                         for p in (source_path, mode_path, raw, Path(__file__))},
        claim_boundary='No frequency correction, physical D/alpha, external validation or holdout access.',
    )
    (ART/'t13_interlayer_strain_transfer_audit.json').write_text(
        json.dumps(artifact, indent=2, allow_nan=False)+'\n', encoding='utf-8')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
