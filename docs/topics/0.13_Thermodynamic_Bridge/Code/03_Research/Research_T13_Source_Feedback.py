"""Formal source-feedback counterexample and header-only source admission.

No archive download, numerical experimental rows, trajectory or physical score.
"""
from __future__ import annotations
import argparse
from fractions import Fraction as Q
import hashlib
from itertools import permutations
import json
from pathlib import Path
import re
import shutil
import sys

ROOT=Path(__file__).resolve().parents[5]
sys.path.insert(0,str(ROOT))
from docs.scripts.audit.audit_calculation_completeness import artifact_metadata,load_json

SOURCE="docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/source_feedback_protocol_references.json"
CONTRACT="docs/topics/0.13_Thermodynamic_Bridge/calculation_contracts/source_feedback.json"
OUTPUT="docs/core/07_artifacts/topic13/t13_source_feedback.json"


def incident_source_coefficients(k,beta,a,detuning,g):
    if k<=0 or beta<0 or a<=0 or g<=0:
        raise ValueError('outside positive-stiffness declared comparator domain')
    d=a*a+detuning*detuning
    return (k*d,2*k*detuning*g,k*g*g+beta*d,2*beta*detuning*g,beta*g*g)


def evaluate_source(coefficients,x):
    return sum(c*x**j for j,c in enumerate(coefficients,1))


def characteristic_coefficients(a,gamma,w2,c,g,n,delta):
    if min(a,gamma,w2,c,g)<=0 or n<0:
        raise ValueError('invalid local stability inputs')
    d=a*a+delta*delta
    return (gamma+2*a,w2+2*a*gamma+d,2*a*w2+gamma*d,w2*d+2*c*g*n*delta)


def hurwitz(coeffs):
    a1,a2,a3,a4=coeffs
    h2=a1*a2-a3
    h3=a3*h2-a1*a1*a4
    return h2,h3,all(x>0 for x in (*coeffs,h2,h3))


def drift_matrix(a,gamma,w2,c,g,delta,ar,ai):
    return ((Q(0),Q(1),Q(0),Q(0)),(-w2,-gamma,2*c*ar,2*c*ai),
            (-g*ai,Q(0),-a,-delta),(g*ar,Q(0),delta,-a))


def determinant(matrix):
    if len(matrix)!=4 or any(len(r)!=4 for r in matrix):
        raise ValueError('this exact control is only a 4x4 determinant')
    result=Q(0)
    for perm in permutations(range(4)):
        inversions=sum(perm[i]>perm[j] for i in range(4) for j in range(i+1,4))
        term=Q(-1 if inversions%2 else 1)
        for i in range(4):
            term*=matrix[i][perm[i]]
        result+=term
    return result


def check_characteristic_at_fixed_point(x,ar,ai):
    a,gamma,w2,c,g=Q(3,4),Q(10),Q(1),Q(1),Q(1)
    n=ar*ar+ai*ai
    if n!=x or a*ai!=x*ar:
        raise ValueError('quadratures do not describe the declared fixed point')
    j=drift_matrix(a,gamma,w2,c,g,x,ar,ai)
    a1,a2,a3,a4=characteristic_coefficients(a,gamma,w2,c,g,n,x)
    # Degree <=4; five distinct exact values certify this fixed-point polynomial.
    for s in map(Q,(-1,0,1,2,3)):
        matrix=[[s*int(i==k)-j[i][k] for k in range(4)] for i in range(4)]
        if determinant(matrix)!=s**4+a1*s**3+a2*s**2+a3*s+a4:
            raise ValueError('characteristic polynomial differs from actual drift matrix')
    if not hurwitz((a1,a2,a3,a4))[2]:
        raise ValueError('fixed point not certified stable')
    return 5


def transmission_components(a,port,delta):
    if not 0<port<=a:
        raise ValueError('need declared passive hanger port convention')
    d=a*a+delta*delta
    return 1-port*a/d,-port*delta/d


def infer_occupation(a,port,input_flux,magnitude_squared):
    """Stationary calibrated inverse, not an arbitrary magnitude normalization."""
    if not 0<port<=a or input_flux<0 or not 0<=magnitude_squared<1:
        raise ValueError('invalid calibrated single-pole inverse domain')
    d=port*(2*a-port)/(1-magnitude_squared)
    if d<a*a:
        raise ValueError('magnitude incompatible with declared transfer; do not clip')
    return input_flux*(1-magnitude_squared)/(2*a-port),d-a*a


def infer_complex_port(port,tr,ti):
    if port<=0:
        raise ValueError('port must be positive')
    denominator=(1-tr)**2+ti*ti
    if denominator==0:
        raise ValueError('no finite inverse at unit transmission')
    return port*(1-tr)/denominator,-port*ti/denominator


def mismatch_magnitude_squared(a,magnitude,cosine,sine,delta):
    """Explicit complex circle coefficient; not equated to input-port coupling."""
    if a<=0 or magnitude<=0 or cosine*cosine+sine*sine!=1:
        raise ValueError('need calibrated positive rates and exact phase convention')
    return 1+(magnitude*magnitude-2*magnitude*a*cosine+2*magnitude*delta*sine)/(a*a+delta*delta)


def mechanical_kerr(g0,omega,gamma):
    """Native stationary Eq.20; coefficients must be independently calibrated."""
    if g0<0 or omega<=0 or gamma<0:
        raise ValueError('outside declared native rate domain')
    return 2*g0*g0*omega/(omega*omega+gamma*gamma/4)


def phase_free_native_residual(a,port,input_flux,magnitude_squared,detuning,effective_kerr):
    """Necessary condition only: no latent sign selected or physical score issued."""
    n,delta2=infer_occupation(a,port,input_flux,magnitude_squared)
    return (detuning+effective_kerr*n)**2-delta2


def general_phase_free_constraints(n,a,magnitude,cosine,sine,detuning,effective_kerr,intensity,r):
    """Evaluate simultaneous latent-n constraints; NOT a global feasibility solver."""
    if n<0 or a<=0 or magnitude<=0 or intensity<=0 or r<0 or cosine*cosine+sine*sine!=1:
        raise ValueError('invalid stationary complex-transfer candidate')
    delta=detuning+effective_kerr*n
    first=n*(a*a+delta*delta)-intensity
    second=(intensity*(r-1)-n*(magnitude*magnitude-2*magnitude*a*cosine+2*magnitude*detuning*sine)
            -2*magnitude*effective_kerr*sine*n*n)
    return first,second


def shared_scale_polynomial(a,port,relative_power,r,detuning):
    """Ascending coefficients in b=K_eff*C/(2*a-port), flux=C*relative_power.

    relative_power denotes linear relative photon flux, not unconverted watts/dBm.
    Conditional real-port stationary law; C is one common positive source scale.
    Exact controls only, not a rounded-data hypothesis test.
    """
    if relative_power<=0:
        raise ValueError('positive relative input power required')
    _,delta2=infer_occupation(a,port,Q(1),r)
    x=relative_power*(1-r)
    return (detuning*detuning-delta2,2*detuning*x,x*x)


def _trim_polynomial(p):
    p=list(map(Q,p))
    while p and p[-1]==0:
        p.pop()
    return tuple(p)


def _polynomial_remainder(a,b):
    a=list(_trim_polynomial(a)); b=_trim_polynomial(b)
    if not b:
        raise ValueError('zero polynomial divisor')
    while len(a)>=len(b):
        scale=a[-1]/b[-1]; offset=len(a)-len(b)
        for i,value in enumerate(b):
            a[i+offset]-=scale*value
        a=list(_trim_polynomial(a))
    return tuple(a)


def common_real_quadratic_candidate(polynomials):
    """Exact rational gcd decision, not a joint-uncertainty feasibility solver."""
    if not polynomials:
        raise ValueError('at least one declared row required')
    g=()
    for p in polynomials:
        p=_trim_polynomial(p)
        if len(p)>3:
            raise ValueError('only degree-at-most-two constraints supported')
        while p:
            g,p=p,_polynomial_remainder(g,p)
        if g:
            g=tuple(c/g[-1] for c in g)
    if not g:
        return (),True  # Every constraint was zero: no information, not validation.
    if len(g)==1:
        return g,False
    if len(g)==2:
        return g,True
    return g,g[1]*g[1]-4*g[2]*g[0]>=0


def inspect_curated_headers(source):
    rows=[]
    for item in source['headers']:
        text=item['header']
        if hashlib.sha256(text.encode('utf-8')).hexdigest()!=item['raw_header_sha256']:
            raise ValueError('curated raw header identity changed')
        lines=text.splitlines()
        if len(lines)!=3 or not lines[0].startswith('sep='):
            raise ValueError('exactly three source header lines required, no numeric rows')
        delimiter=lines[0][4:]
        columns=lines[2].split(delimiter)
        if columns!=['detuning Delta','S21 absolute']:
            raise ValueError('source schema changed; new protocol review required')
        if item['numeric_rows_decoded']!=0 or item['whole_member_crc_verified']:
            raise ValueError('header-only scope changed; review actual source role')
        rows.append({'member':item['member'],'role':'experiment' if 'Experiment' in lines[1] else 'simulation',
                     'delimiter':delimiter,'columns':columns,'header_identity_verified':True,
                     'whole_member_crc_verified':False})
    if {r['role'] for r in rows}!={'experiment','simulation'}:
        raise ValueError('experiment/simulation distinction lost')
    return rows


def inspect_follow_up_headers(source):
    """Classify declared products, never infer numeric payload or missing data globally."""
    review=source['follow_up_header_review']
    if review['numeric_rows_decoded']!=0 or review['whole_member_crc_verified']:
        raise ValueError('follow-up source role changed; full-data review required')
    counts={}; rows=[]; mismatch=[]
    for item in review['headers']:
        text=item['header']
        if hashlib.sha256(text.encode('utf-8')).hexdigest()!=item['sha256']:
            raise ValueError('follow-up header identity changed')
        lines=text.splitlines()
        if len(lines)!=3 or lines[0]!='sep=,':
            raise ValueError('only the declared three-line comma header is admitted')
        cols=lines[2].split(',')
        if 'P_d dBm from n_c' in cols:
            kind='DERIVED_CALIBRATION_POWER_NOT_INDEPENDENT_PAIR'
        elif cols[0]=='first author':
            kind='LITERATURE_COMPARISON_TABLE'
        elif any('fourier of ' in c for c in cols):
            kind='FOURIER_STATE_PROVENANCE_AND_COMPLEX_REPRESENTATION_UNRESOLVED'
        elif 'stable/unstable' in cols or 'stable or unstable' in cols:
            kind='DECLARED_FIXED_POINT_MODEL_PRODUCT'
        elif 'S_ww data' in cols and 'S_ww fit' in cols:
            kind='CALIBRATION_SPECTRUM_WITH_MODEL_FIT'
        elif cols[0]=='freq' and any(c.startswith('S21 absolute') for c in cols):
            kind='MAGNITUDE_FREQUENCY_SWEEP_NOT_DECLARED_TIME_TRACE'
        else:
            raise ValueError('new source schema needs an explicit product-role review')
        counts[kind]=counts.get(kind,0)+1
        folder=re.search(r'Figure_(\d+)/',item['member'])
        embedded=re.search(r'Fig (\d+)',lines[1])
        if folder and embedded and folder.group(1)!=embedded.group(1):
            mismatch.append(item['member'])
        rows.append({'member':item['member'],'role':kind,'header_identity_verified':True})
    if len(rows)!=15:
        raise ValueError('candidate inventory changed; do not reuse the old coverage statement')
    return {'selected_headers':len(rows),'roles':counts,'members':rows,
            'folder_comment_binding_review':mismatch,
            'independent_validation_of_derived_power_pair':False,
            'boundary':'selected declared schemas only; Fourier complex payload and every other archive member remain unassessed'}


def calculate(source):
    coeffs=incident_source_coefficients(Q(1),Q(0),Q(3,4),Q(0),Q(1))
    if coeffs!=(Q(9,16),Q(0),Q(1),Q(0),Q(0)):
        raise ValueError('linear-spring apparent-cubic identity failed')
    # Positive coefficient certificates in t=x^2; proof derives them for all t>=0.
    h2=(Q(5867,32),Q(3,2))
    h3=(Q(315375,256),Q(11579,8),Q(15))
    for t in (Q(0),Q(1,4),Q(1)):
        cs=(Q(23,2),Q(265,16)+t,Q(57,8)+10*t,Q(9,16)+3*t)
        observed=hurwitz(cs)
        if observed[0]!=h2[0]+h2[1]*t or observed[1]!=sum(v*t**i for i,v in enumerate(h3)):
            raise ValueError('Hurwitz polynomial certificate failed')
    count=check_characteristic_at_fixed_point(Q(1),Q(3,5),Q(4,5))
    count+=check_characteristic_at_fixed_point(Q(9,16),Q(3,5),Q(9,20))
    a,port,flux=Q(3,4),Q(1,2),Q(25,8)
    tr,ti=transmission_components(a,port,Q(1))
    occupation,delta2=infer_occupation(a,port,flux,tr*tr+ti*ti)
    if occupation!=1 or delta2!=1 or infer_complex_port(port,tr,ti)!=(a,Q(1)):
        raise ValueError('conditional source/readout inversion failed')
    mismatch_candidates=(Q(0),Q(-16,7))
    if any(mismatch_magnitude_squared(Q(1),Q(1,2),Q(3,5),Q(4,5),d)!=Q(13,20) for d in mismatch_candidates):
        raise ValueError('complex mismatch ambiguity witness failed')
    keff=Q(3,4)+mechanical_kerr(Q(1,2),Q(1),Q(2))
    resonant=phase_free_native_residual(a,port,Q(25,8),Q(17,25),Q(0),keff)
    detuned=phase_free_native_residual(a,port,Q(45,8),Q(37,45),Q(1,2),keff)
    wrong=phase_free_native_residual(a,port,Q(45,8),Q(37,45),Q(1,2),-keff)
    if (resonant,detuned,wrong)!=(Q(0),Q(0),Q(-2)):
        raise ValueError('phase-free detuned control failed')
    if general_phase_free_constraints(Q(1),Q(1),Q(1,2),Q(3,5),Q(4,5),Q(-1),Q(1),Q(1),Q(13,20))!=(0,0):
        raise ValueError('general complex-transfer constraints failed')
    shared_rows=(shared_scale_polynomial(a,port,Q(25,8),Q(17,25),Q(0)),
                 shared_scale_polynomial(a,port,Q(45,8),Q(37,45),Q(1,2)))
    common,exists=common_real_quadratic_candidate(shared_rows)
    incompatible=shared_scale_polynomial(a,port,Q(25,4),Q(17,25),Q(0))
    rejected,rejected_exists=common_real_quadratic_candidate((shared_rows[0],incompatible))
    if (common,exists,rejected,rejected_exists)!=((Q(-1),Q(1)),True,(Q(1),),False):
        raise ValueError('shared source-scale discrimination failed')
    return {'status':'STABLE_SOURCE_FEEDBACK_COUNTEREXAMPLE_AND_HEADER_ADMISSION',
        'linear_spring_apparent_source_polynomial':[str(c) for c in coeffs],
        'true_mechanical_duffing':'0','source_corrected_law':'hbar*G*n=k*x; incident power is not internal occupation',
        'all_t_nonnegative_stability_certificate':{'H2':[str(x) for x in h2],'H3':[str(x) for x in h3],
            'boundary':'local linear stability of declared mathematical branch, not global or real-apparatus validation'},
        'jacobian_polynomial_exact_controls':count,
        'inverse_control':{'transmission_real':str(tr),'transmission_imag':str(ti),'magnitude_squared':str(tr*tr+ti*ti),
            'recovered_occupation':str(occupation),'magnitude_only_detuning_candidates':['-1','1'],'complex_recovered_detuning':'1'},
        'complex_mismatch_control':{'magnitude_squared':'13/20','detuning_candidates':['0','-16/7'],
            'occupation_candidates':['1','49/305'],'boundary':'abstract calibrated transfer, not measured data; circle coefficient magnitude need not equal drive coupling'},
        'phase_free_native_controls':{'K_eff':str(keff),'resonant_residual':str(resonant),
            'detuned_residual':str(detuned),'wrong_sign_detuned_residual':str(wrong),
            'boundary':'necessary condition under independent calibration; no unique state reconstruction or measured acceptance',
            'complex_mismatch':'simultaneous latent-n constraints defined, not a global joint-uncertainty solver'},
        'shared_source_scale_controls':{'consistent_gcd':[str(x) for x in common],
            'consistent_common_real_candidate':exists,'inconsistent_gcd':[str(x) for x in rejected],
            'inconsistent_common_real_candidate':rejected_exists,
            'identified_combination':'b=K_eff*C/(2*a-port); K_eff and absolute flux scale C not separately identified',
            'boundary':'exact rational controls, independently known real-port transfer and relative input; no measured rejection or error-bound claim'},
        'inspected_headers':inspect_curated_headers(source),
        'follow_up_header_review':inspect_follow_up_headers(source),
        'archive_readme_delimiter':source['data_record']['readme']['advertised_separator'],
        'member_level_delimiter_precedence':True,
        'admission':source['admission'],'physical_acceptance':False,'numeric_rows_scored':0,
        'numeric_rows_decoded':0,'new_UET_terms':0,'large_archive_download':False,
        'claim_boundary':'ordinary comparator source-feedback/protocol result; no UET material map, intrinsic nonlinearity measurement or unique theory validation'}


def record():
    return {**calculate(load_json(ROOT/SOURCE)),**artifact_metadata(load_json(ROOT/CONTRACT),ROOT),
            'generator_path':Path(__file__).relative_to(ROOT).as_posix(),'evidence_class':'FORMAL_PROTOCOL_AND_HEADER_METADATA_ONLY'}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    mode=p.add_mutually_exclusive_group(required=True)
    mode.add_argument('--emit',action='store_true'); mode.add_argument('--check',action='store_true')
    args=p.parse_args(); text=json.dumps(record(),ensure_ascii=False,indent=2,allow_nan=False)+'\n'; path=ROOT/OUTPUT
    if args.emit:
        if shutil.disk_usage(ROOT).free<100*1024*1024:
            raise SystemExit('Insufficient free space')
        path.write_text(text,encoding='utf-8',newline='\n')
    elif not path.exists() or path.read_text(encoding='utf-8')!=text:
        raise SystemExit('Missing/drifted evidence; check does not write')
    print('STABLE_SOURCE_FEEDBACK_COUNTEREXAMPLE_AND_HEADER_ADMISSION; no physical score')


if __name__=='__main__':
    main()
