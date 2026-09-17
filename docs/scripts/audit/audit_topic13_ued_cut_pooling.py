"""Audit source pooling and cross-cut metadata, not estimate physical noise."""
import json
from pathlib import Path
from docs.scripts.audit.audit_topic13_ued_source_acquisition import digest

ROOT = Path(__file__).resolve().parents[3]


def differences(a, b, columns):
    if len(a) != len(b) or not a: raise ValueError('unpaired or empty cuts')
    if any(x['LTS_position'] != y['LTS_position'] or x['Delay_ps'] != y['Delay_ps'] for x,y in zip(a,b)):
        raise ValueError('stage/delay alignment missing')
    result = {}
    for column in columns:
        delta = [abs(x[column]-y[column]) for x,y in zip(a,b)]
        if max(delta): result[column] = dict(differing_rows=sum(d != 0 for d in delta), maximum_absolute_difference=max(delta))
    return result


def main():
    source = ROOT/'docs/core/07_artifacts/topic13/t13_ued_source_acquisition_audit.json'
    structure = ROOT/'docs/core/07_artifacts/topic13/t13_ued_raw_structure_audit.json'
    for p in (source, structure):
        for file, h in json.loads(p.read_text())['evidence_hashes'].items():
            if digest(ROOT/file) != h: raise ValueError('stale evidence')
    notebook = ROOT/'docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/raw/ued_treat_pickle_7f7036b.ipynb'
    cell = ''.join(json.loads(notebook.read_text())['cells'][1]['source'])
    tokens = ['glob.glob(', 'for file in file_list:', "input_df['imagesON']", 'imgON_raw = np.sum(np.array(imgON), axis=0)',
              'imgOFF_raw = np.sum(np.array(imgOFF), axis=0)', "df1 = input_df.drop('imagesOFF', axis=1)", "df1['LTS_position']", 'delay[t0_num-1]']
    if not all(t in cell for t in tokens): raise ValueError('reviewed pooling source changed')
    tables = json.loads(structure.read_text())['tables']
    a,b = tables[:2]
    if not a['member'].endswith('400nm_cut1.pickle') or not b['member'].endswith('400nm_cut2.pickle'):
        raise ValueError('cut identity changed')
    delta = differences(a['rows'],b['rows'],a['columns'][:19])
    files = [source,structure,notebook,Path(__file__),ROOT/'docs/core/test/test_topic13_ued_cut_pooling.py']
    artifact = dict(major_result_id='T13_CUT_POOLING_PROVENANCE_BOUNDARY',topic='0.13',closure_level='PARTIAL',
        what_is_closed=['Published processing sums cuts before processing; raw metadata differences retained explicitly'],
        equation_or_mapping='Source image sum across files; last input table supplies stage-derived time axis',
        units='Raw metadata units retained as unverified except explicit source labels; differences are not uncertainties',
        derivation_class='SOURCE_CODE_AND_DATA_AUDIT',observable='acquisition metadata',data_role='SOURCE_PROVENANCE',
        verification_status='POOLING_IDENTIFIED_INDEPENDENCE_UNVERIFIED',
        cross_cut_differences=delta,source_locator='treat_pickle.ipynb cell 1 at 7f7036bfda28f9330f19b40e57f4edf464b67d64',
        source_pooling=dict(operation='sum across files',independence_check_present=False,
                            exposure_weighting_present=False,last_input_supplies_time_axis=True,
                            actual_cut_time_axes_equal=True,scope='reviewed import/pooling cell only'),
        open_blockers=['pre-sorted acquisition/aggregation procedure', 'cut independence and drift contribution',
                       'detector gain/noise and sensor calibration', 'independent Phi coupling'],
        next_action='Keep cuts separate for sensitivity; obtain pre-sorting/DAQ provenance before constructing covariance or physical temperature calibration',
        dependency_unlocked=['cut-resolved sensitivity only'],full_core_unlock=False,claim_promotion=False,
        evidence_hashes={str(p.relative_to(ROOT)).replace('\\','/'):digest(p) for p in files},
        claim_boundary='Metadata differences do not prove physical drift or invalidate the experiment. Summed images are not independent frames. No covariance estimate, holdout, fitted alpha or thermal claim.')
    (ROOT/'docs/core/07_artifacts/topic13/t13_ued_cut_pooling_audit.json').write_text(json.dumps(artifact,indent=2)+'\n')
    print(json.dumps(delta,indent=2))


if __name__ == '__main__': main()
