"""Exact prefix preparation/readout controls, not a physical graphite forecast."""
from __future__ import annotations
import argparse
from fractions import Fraction as Q
import json
from pathlib import Path
import shutil
import sys

ROOT=Path(__file__).resolve().parents[5]
sys.path.insert(0,str(ROOT))
from docs.scripts.audit.audit_calculation_completeness import artifact_metadata,load_json
BASE='docs/topics/0.13_Thermodynamic_Bridge/'
CONTRACT=BASE+'calculation_contracts/graphite_preparation_prediction.json'
OUTPUT='docs/core/07_artifacts/topic13/t13_graphite_preparation_prediction.json'


def observe(x,z):
    """x=sqrt(3)*Pa, z=Pb, y=(Icp-1)/(2pi); all dimensionless."""
    return x+z,-2*z,-x+z


def reconstruct(y):
    if len(y)!=3: raise ValueError('three signed intensity channels required')
    return (y[0]-y[2])/2,(y[0]-2*y[1]+y[2])/6


def hidden_state(q,v,a,jerk,z,mass,quartic,g):
    """Model-conditioned exact jet estimator; NOT an independent Phi measurement."""
    if q==0 or g==0 or z<=0 or quartic<=0:
        raise ValueError('outside nonzero-coordinate, coupled, positive-action domain')
    return ((mass+quartic*q*q+z*a/q)/g,
            (2*quartic*q*v+z*(jerk*q-a*v)/(q*q))/g)


def matter_jet(q,v,d,w,z,mass,quartic,g):
    a=-(mass+quartic*q*q-g*d)*q/z
    jerk=-(mass+3*quartic*q*q-g*d)*v/z+g*w*q/z
    return a,jerk


def calculate():
    x,z=Q(2,7),Q(-3,11)
    y=observe(x,z)
    if reconstruct(y)!=(x,z) or sum(y)!=0: raise ValueError('left inverse drift')
    q,v,d,w=Q(2,3),Q(-1,4),Q(3,5),Q(-2,7)
    args=Q(5,4),Q(1),Q(3,4),Q(3,10)
    a,j=matter_jet(q,v,d,w,*args)
    if hidden_state(q,v,a,j,*args)!=(d,w): raise ValueError('state identity drift')
    return {'status':'PREFIX_PREPARATION_CONDITIONALLY_POSSIBLE_PHYSICAL_PACKET_NOT_ADMITTED',
            'observer_rank':2,'observer_closure':'sum(y)=0',
            'full_collinear_state':['q','q_dot','delta_phi','delta_phi_dot'],
            'hidden_state_identity_control':[str(t) for t in (d,w)],
            'uncertainty_policy':'joint state/parameter/observer sets; no unmeasured effects assigned zero',
            'old_four_frequency_kernel_evaluated':False,'physical_forecast_run':False,
            'physical_acceptance':False,'new_core_term':False,'numeric_records_acquired':False,
            'reopen':'same-state correspondence, frozen coefficients, eligible split records, full state and joint source/damping/observer bounds',
            'boundary':'prefix model-conditioned state calibration is not independent Phi observation or unique UET discrimination'}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    g=p.add_mutually_exclusive_group(required=True)
    g.add_argument('--emit',action='store_true');g.add_argument('--check',action='store_true')
    a=p.parse_args()
    r={**calculate(),**artifact_metadata(load_json(ROOT/CONTRACT),ROOT),
       'generator_path':Path(__file__).relative_to(ROOT).as_posix()}
    text=json.dumps(r,ensure_ascii=False,indent=2,allow_nan=False)+'\n'
    path=ROOT/OUTPUT
    if a.emit:
        if shutil.disk_usage(ROOT).free<100*1024*1024: raise SystemExit('Insufficient free space')
        path.write_text(text,encoding='utf-8',newline='\n')
    elif not path.exists() or path.read_text(encoding='utf-8')!=text:
        raise SystemExit('Missing/drifted output; check is read-only')
    print(r['status'])


if __name__=='__main__':main()
