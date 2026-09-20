"""Leave a full reciprocal-radius shell out of baseline registration fits."""
from hashlib import sha256
import json
from pathlib import Path
import sys
import numpy as np

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT))
from docs.scripts.audit.audit_topic13_baseline_registration_models import fit_map,predict


def shell_transfer(nominal,observed,shells,kind):
    nominal=np.asarray(nominal);observed=np.asarray(observed);shells=np.asarray(shells)
    if shells.shape!=(len(nominal),):raise ValueError('one shell per peak required')
    rows=[]
    for shell in np.unique(shells):
        test=shells==shell;train=~test
        params=fit_map(nominal[train],observed[train],kind)
        residual=observed[test]-predict(nominal[test],params,kind)
        norms=np.linalg.norm(residual,axis=1)
        rows.append(dict(shell=int(shell),training_indices=np.flatnonzero(train).tolist(),
            excluded_indices=np.flatnonzero(test).tolist(),residual_yx=residual.tolist(),
            rms_pixels=float(np.sqrt(np.mean(norms**2))),max_pixels=float(norms.max())))
    return rows


def main():
    source_path=ROOT/'docs/core/07_artifacts/topic13/t13_multibragg_positions.json'
    source=json.loads(source_path.read_text())
    for e in source['evidence_artifacts']:
        if sha256((ROOT/e['path']).read_bytes()).hexdigest()!=e['sha256']:raise ValueError('upstream drift')
    rows=[]
    for table in source['rows']:
        p=np.array([v['nominal_yx'] for v in table['probes']])
        g=np.array([v['G'] for v in table['probes']]);shells=g[:,0]**2+g[:,1]**2+g[:,0]*g[:,1]
        norms=np.array([v['momentum_norm'] for v in table['probes']])
        np.testing.assert_allclose(norms**2/norms.min()**2,shells,rtol=1e-12,atol=1e-12)
        result={}
        for radius in ('4','8'):
            if any(v['radii'][radius]['status']!='MEASURED_NOT_CALIBRATED' for v in table['probes']):raise ValueError('incomplete peak set')
            observed=np.array([v['radii'][radius]['centroid_yx'] for v in table['probes']])
            result[radius]={kind:shell_transfer(p,observed,shells,kind) for kind in ('translation','similarity','affine')}
        rows.append(dict(member=table['member'],shell_labels=shells.tolist(),by_radius=result))
    files=[source_path,Path(__file__),ROOT/'docs/scripts/audit/audit_topic13_baseline_registration_models.py',ROOT/'docs/core/test/test_topic13_registration_shell_transfer.py']
    artifact=dict(major_result_id='T13_BASELINE_REGISTRATION_SHELL_TRANSFER',topic='0.13',closure_level='PARTIAL',
        what_is_closed='Excluded-shell transfer residuals recorded without same-radius training peers',
        equation_or_mapping='Fit baseline coordinate map on two radial shells, predict the third; shell=h^2+k^2+hk',
        units='residual pixels; shell dimensionless',derivation_class='internal grouped validation of baseline empirical maps',
        observable='baseline centroid map transfer',data_role='EXTERNAL_BASELINE_DIAGNOSTIC',rows=rows,
        verification_status='GROUPED_TRANSFER_RECORDED',controlling_blocker='centroid_shape_bias_and_physical_registration_uncertainty',
        open_blockers=['source_symmetrization','centroid_background_model','finite_patch_response','UET_normalization'],
        dependency_unlocked=[],full_core_unlock=False,global_claim_promotion=False,
        claim_boundary='Excluded shells remain in the same processed image, not independent experiments or statistical error bounds. No image correction, thermal fit or holdout.',
        evidence_artifacts=[dict(path=p.relative_to(ROOT).as_posix(),sha256=sha256(p.read_bytes()).hexdigest()) for p in files])
    (ROOT/'docs/core/07_artifacts/topic13/t13_registration_shell_transfer.json').write_text(json.dumps(artifact,indent=2,allow_nan=False)+'\n')
    print(json.dumps([dict(member=r['member'],radii={rad:{kind:[v['rms_pixels'] for v in vals] for kind,vals in models.items()} for rad,models in r['by_radius'].items()}) for r in rows]))


if __name__=='__main__':main()
