"""Small real-data readout-domain diagnostic; never a physical rejection test."""
from __future__ import annotations
import argparse
import csv
from fractions import Fraction as Q
import hashlib
import io
import json
from pathlib import Path
import shutil
import sys
import zlib

ROOT=Path(__file__).resolve().parents[5]
sys.path.insert(0,str(ROOT))
from docs.scripts.audit.audit_calculation_completeness import artifact_metadata,load_json

BASE='docs/topics/0.13_Thermodynamic_Bridge/'
MANIFEST=BASE+'Data/03_Research/dhiman_2026_fig3c_readout_manifest.json'
CONTRACT=BASE+'calculation_contracts/readout_admission.json'
OUTPUT='docs/core/07_artifacts/topic13/t13_readout_admission.json'


def parse_rows(text):
    rows=list(csv.reader(io.StringIO(text)))
    if rows[:3]!=[['sep=', ''],['Fig 3 (panel c) Experiment'],['detuning Delta','S21 absolute']]:
        raise ValueError('unexpected member schema; do not infer new columns')
    values=[]
    for row in rows[3:]:
        if len(row)!=2 or any(not token.strip() for token in row):
            raise ValueError('missing or malformed observation')
        values.append(tuple(Q(token) for token in row))
    if not values:
        raise ValueError('no observations')
    return values


def gain_enclosure(values,lower):
    """Optimistic closed range m_i=g*t_i+e_i, lower<=t_i<=1.

    This optimizes a necessary envelope, not a cavity fit or adopted gain/noise.
    Detuning/order constraints are relaxed, so compatibility is not sufficient.
    """
    if not values or not 0<=lower<=1 or min(values)<0 or max(values)<=0:
        raise ValueError('need nonnegative magnitudes with a positive maximum and 0<=lower<=1')
    lo,hi=min(values),max(values)
    gap=lower*hi-lo
    error=max(Q(0),gap/(1+lower))
    optimizer=(hi+lo)/(1+lower) if gap>0 else hi
    return {'closed_envelope_gain_only_possible':gap<=0,
            'noiseless_gain_lower_bound':str(hi),
            'noiseless_gain_upper_bound':str(lo/lower) if lower else None,
            'largest_lower_ratio_allowing_noiseless_gain':str(lo/hi),
            'unit_gain_minimum_uniform_amplitude_error':str(max(Q(0),hi-1,lower-lo)),
            'optimistic_minimum_uniform_amplitude_error':str(error),
            'envelope_optimizer_NOT_adopted_gain':str(optimizer),
            'applied_gain_correction':False,'estimated_noise_distribution':False,
            'boundary':'necessary closed-envelope compatibility, not a fit, physical uncertainty estimate or sufficient detuning/stability test'}


def profile(rows,internal,external):
    if internal<0 or external<=0:
        raise ValueError('outside central passive hanger domain')
    if not rows or any(m<0 for _,m in rows):
        raise ValueError('absolute magnitude must be nonnegative')
    lower=internal/(internal+external)
    counts={'below_central_ideal_minimum':0,'inside_central_ideal_domain':0,
            'at_or_above_unit_magnitude':0}
    for _,m in rows:
        key=('below_central_ideal_minimum' if m<lower else
             'at_or_above_unit_magnitude' if m>=1 else 'inside_central_ideal_domain')
        counts[key]+=1
    return {'rows':len(rows),'columns':2,'missing_fields':0,
            'duplicate_detuning_count':len(rows)-len({x for x,_ in rows}),
            'exact_duplicate_row_count':len(rows)-len(set(rows)),
            'magnitude_min':str(min(m for _,m in rows)),
            'magnitude_max':str(max(m for _,m in rows)),
            'central_ideal_minimum_magnitude':str(lower),
            'central_ideal_minimum_squared':str(lower*lower),
            'domain_counts':counts,'clipped_or_dropped_rows':0,
            'global_gain_enclosure':gain_enclosure([m for _,m in rows],lower),
            'boundary':'central rounded calibration domain only; inside-domain is not physical admission, outside-domain is not theory rejection'}


def calculate():
    manifest=load_json(ROOT/MANIFEST)
    text=(ROOT/manifest['local']['path']).read_text(encoding='utf-8').replace('\r\n','\n').replace('\r','\n')
    normalized=text.encode('utf-8'); upstream=text.replace('\n','\r\n').encode('utf-8')
    source=manifest['source']
    if hashlib.sha256(normalized).hexdigest()!=manifest['local']['normalized_text_sha256']:
        raise ValueError('local input identity changed')
    if (len(upstream)!=source['member_bytes'] or hashlib.sha256(upstream).hexdigest()!=source['member_sha256']
            or f'{zlib.crc32(upstream)&0xffffffff:08x}'!=source['member_crc32']):
        raise ValueError('normalized working copy does not reconstruct verified upstream member')
    c=manifest['calibration']
    result=profile(parse_rows(text),Q(c['kappa_internal_over_2pi_MHz']),Q(c['kappa_external_over_2pi_MHz']))
    return {'status':'PROCESSED_MAGNITUDE_NOT_ADMITTED_FOR_POINTWISE_STATIC_INVERSE',
            'profile':result,'source_member_sha256':source['member_sha256'],
            'normalized_working_copy_sha256':manifest['local']['normalized_text_sha256'],
            'input_crc_reconstruction_verified':True,'source_working_point':c['working_point'],
            'physical_acceptance':False,'theory_rejection':False,'physical_residual_rows_scored':0,
            'new_held_out_rows':False,'unknown_effects_assigned_zero':False,
            'controller':'admit gain/mismatch and correlated noise/calibration/averaging error model before any physical residual; do not clip or select rows to pass',
            'claim_boundary':'exploratory data/readout-domain diagnostic, not bad-data finding, measured rejection, UET identification or external validation'}


def record():
    return {**calculate(),**artifact_metadata(load_json(ROOT/CONTRACT),ROOT),
            'generator_path':Path(__file__).relative_to(ROOT).as_posix(),
            'evidence_class':'EXPOSED_PROCESSED_DATA_READOUT_DIAGNOSTIC'}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    mode=parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--emit',action='store_true'); mode.add_argument('--check',action='store_true')
    args=parser.parse_args(); text=json.dumps(record(),ensure_ascii=False,indent=2,allow_nan=False)+'\n'
    path=ROOT/OUTPUT
    if args.emit:
        if shutil.disk_usage(ROOT).free<100*1024*1024:
            raise SystemExit('Insufficient free space')
        path.write_text(text,encoding='utf-8',newline='\n')
    elif not path.exists() or path.read_text(encoding='utf-8')!=text:
        raise SystemExit('Missing/drifted diagnostic; check is read-only')
    print('READOUT_DOMAIN_DIAGNOSTIC; no physical residual score or theory rejection')


if __name__=='__main__':
    main()
