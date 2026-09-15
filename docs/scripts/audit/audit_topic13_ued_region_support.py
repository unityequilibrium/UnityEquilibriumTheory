"""Source-coordinate strip diagnostic, without smoothing or population inference."""
import json
from pathlib import Path

import numpy as np

from docs.scripts.audit.audit_topic13_ued_mask_support import support_signals
from docs.scripts.audit.audit_topic13_ued_source_acquisition import digest

ROOT = Path(__file__).resolve().parents[3]


def region_mask(shape, origin, calibration, peak_distance):
    if len(shape) != 2 or calibration <= 0 or peak_distance <= 0:
        raise ValueError('positive source geometry required')
    y, x = np.indices(shape)
    kx = calibration*(x-origin[1])
    ky = calibration*(y-origin[0])
    center = calibration*peak_distance
    # Author notebook cells 7-8: +/-0.5 inverse A strip, +/-0.1 b around peak.
    b = 4*np.pi/(np.sqrt(3)*2.46)
    return (abs(kx) < .5) & (abs(ky-center) < .1*b)


def main():
    inventory_path = ROOT/'docs/core/07_artifacts/topic13/t13_ued_numeric_inventory_audit.json'
    exports_path = ROOT/'docs/core/07_artifacts/topic13/t13_ued_mask_support_audit.json'
    inventory = json.loads(inventory_path.read_text())
    exports = json.loads(exports_path.read_text())
    for source in (inventory, exports):
        for relative, expected in source['evidence_hashes'].items():
            if digest(ROOT/relative) != expected:
                raise ValueError('stale evidence: '+relative)
    notebook = ROOT/'docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/raw/ued_data_paper_7f7036b.ipynb'
    cells = json.loads(notebook.read_text(encoding='utf-8'))['cells']
    if 'w = 0.5' not in ''.join(cells[8]['source']) or 'a= 2.46' not in ''.join(cells[2]['source']):
        raise ValueError('source geometry convention changed')
    rows = []
    for table in inventory['tables']:
        stacks = {}
        for role in ('imgON', 'imgOFF'):
            arrays = []
            for row in table['rows']:
                entry = exports['array_exports'][row[role]['sha256']]
                path = ROOT/entry['path']
                if digest(path) != entry['sha256']:
                    raise ValueError('export hash mismatch')
                arrays.append(np.load(path, allow_pickle=False))
            stacks[role] = np.stack(arrays)
        region = region_mask(stacks['imgON'].shape[1:], table['source_zero_order_position'],
                             table['calibration_inverse_angstrom_per_pixel'], table['source_peak_distance_pixels'])
        delay = np.array([r['delay_ps'] for r in table['rows']])
        common, _, signals = support_signals(stacks['imgON'][:, region][:, None, :],
                                            stacks['imgOFF'][:, region][:, None, :], delay < -.5)
        dt = np.diff(delay)
        rows.append(dict(member=table['member'], geometric_pixels=int(region.sum()),
                         common_pixels=int(common.sum()), delay_ps=delay.tolist(), signals=signals,
                         delay_step_range_ps=[float(dt.min()), float(dt.max())],
                         all_region_pixels_common=bool(common.all())))
    evidence = [inventory_path, exports_path, notebook, Path(__file__),
                ROOT/'docs/core/test/test_topic13_ued_region_support.py']
    result = dict(major_result_id='T13_UED_SOURCE_STRIP_SUPPORT', topic='0.13', closure_level='PARTIAL',
                  what_is_closed=['Source-coordinate strip extracted without smoothing or filling'],
                  equation_or_mapping='Whole-strip ON/OFF ratio with paired and common masks; baseline delay < -0.5 ps',
                  units={'momentum': 'inverse angstrom', 'ratio': '1', 'delay': 'ps'},
                  derivation_class='source_coordinate_detector_diagnostic', observable='strip-integrated diffraction ratio',
                  data_role='EXTERNAL_DATA_DIAGNOSTIC', verification_status='REGION_EXTRACTED_INVERSION_OPEN',
                  region_policy={'source_cells': [2, 7, 8], 'kx_halfwidth': .5, 'ky_halfwidth_b': .1,
                                 'bragg_exclusion': False, 'selection_uses_signal': False,
                                 'smoothing': False, 'fit': False, 'missing_value_fill': False},
                  source_processing_caution='Cell 6 applies Gaussian sigma=1 to stacked images; historical software axis semantics and temporal effects need review before time inference.',
                  results=rows, open_blockers=['Bragg and diffuse mixture', 'branch-resolved scattering weights and rank',
                    'same-irrep does not identify phonon branch', 'preprocessing covariance', 'independent Phi coupling'],
                  full_core_unlock=False, claim_promotion=False,
                  dependency_unlocked=['source-region forward-map design only'],
                  evidence_hashes={str(p.relative_to(ROOT)).replace('\\', '/'): digest(p) for p in evidence},
                  claim_boundary='Not reproduction of smoothed author figure, pure diffuse intensity, phonon population, relaxation rate or thermometer.')
    (ROOT/'docs/core/07_artifacts/topic13/t13_ued_region_support_audit.json').write_text(json.dumps(result, indent=2, allow_nan=False)+'\n')
    print(json.dumps([dict(member=r['member'], pixels=r['geometric_pixels'], common=r['common_pixels'],
                           difference=r['signals']['support_choice_max_difference'], delay_step=r['delay_step_range_ps']) for r in rows], indent=2))


if __name__ == '__main__':
    main()
