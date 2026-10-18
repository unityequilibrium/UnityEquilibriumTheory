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


def finite_layer_projection(n):
    """Conditional free-chain geometry, unit layer mass/area; no graphite fit."""
    import numpy as np
    if not isinstance(n,int) or isinstance(n,bool) or n<2:
        raise ValueError('at least two identical layers required')
    e=np.cos((n-1)*(2*np.arange(1,n+1)-1)*np.pi/(2*n))
    na,nb=(n+1)//2,n//2
    r=np.array([1/na if j%2==0 else -1/nb for j in range(n)])
    lap=np.zeros((n,n))
    for j in range(n-1):
        lap[j,j]+=1;lap[j+1,j+1]+=1
        lap[j,j+1]-=1;lap[j+1,j]-=1
    value=4*np.cos(np.pi/(2*n))**2
    residual=float(np.max(np.abs(lap@e-value*e)))
    if residual>1e-12 or abs(float(e.sum()))>1e-12:
        raise ValueError('free-ended eigenvector or translation orthogonality failed')
    norm=float(e@e); projection=float(r@e)
    eta=projection**2/(float(r@r)*norm)
    return {'layers':n,'profile':e.tolist(),'eigenpair_roundoff':residual,
            'centroid_projection':projection,'rigid_mass_per_layer_mass':na*nb/n,
            'pole_mass_per_layer_mass':norm/projection**2,'rigid_overlap_fraction':eta,
            'frequency_over_bulk':float(np.cos(np.pi/(2*n))),
            'conditional_equal_layer_basal_observer_ratio':str(Q(na*nb,na*na+nb*nb-na*nb)),
            'observer_admitted':False,'uet_field_map_admitted':False}


def finite_layer_observer(n,t,phase=None):
    """Conditional full kinematic intensity; Taylor bounds are analytic, not grid claims."""
    import math
    import numpy as np
    if phase is None: phase=2*math.pi/3
    if not math.isfinite(t) or not math.isfinite(phase):
        raise ValueError('finite displacement phase and layer phase required')
    p=finite_layer_projection(n)
    b=np.array(p['profile'])/p['centroid_projection']
    c=np.array([1 if j%2==0 else np.exp(-1j*phase) for j in range(n)])
    base=c.sum();den=float(abs(base)**2)
    if abs(base)<=1e-12*n:
        raise ValueError('near-extinct baseline cannot be normalized at declared precision')
    delta=b[:,None]-b[None,:]
    weights=c[:,None]*c.conjugate()[None,:]
    derivatives=[float(np.real(np.sum(weights*(-1j*delta)**k))/den) for k in (1,2,3)]
    intensity=float(abs(np.sum(c*np.exp(-1j*t*b)))**2/den)
    pair=float(np.real(np.sum(weights*np.exp(-1j*t*delta)))/den)
    if abs(intensity-pair)>1e-12: raise ValueError('amplitude/pair observer mismatch')
    b2=float(np.sum(delta**2)/(2*den))
    b4=float(np.sum(delta**4)/(24*den))
    linear=1+derivatives[0]*t
    cubic=linear+derivatives[1]*t*t/2+derivatives[2]*t*t*t/6
    if abs(intensity-linear)>b2*t*t+1e-12 or abs(intensity-cubic)>b4*t**4+1e-12:
        raise ValueError('analytic observer envelope failed implementation check')
    return {'layers':n,'t':t,'intensity':intensity,'derivatives_at_zero':derivatives,
            'linear_error':abs(intensity-linear),'linear_bound_coefficient':b2,
            'cubic_error':abs(intensity-cubic),'cubic_bound_coefficient':b4,
            'leading_detector_cubic_ratio':derivatives[2]/(24*derivatives[0]**3) if abs(derivatives[0])>1e-12 else None,
            'physical_displacement_or_error_budget_assigned':False}


def two_order_third(first,second,k1,k3):
    """Cubic observer-order inversion; geometry/transfer assumptions must be admitted."""
    if k1==0 or k3==0: raise ValueError('two-order cubic map is singular')
    return (8*first+second)/(6*k1),-(2*first+second)/(6*k3)


def source_geometry(h,k,n=9):
    """Source four-atom basal convention; not a measured sample orientation."""
    import cmath
    import math
    if any(not isinstance(v,int) or isinstance(v,bool) for v in (h,k)):
        raise ValueError('integer basal reciprocal indices required')
    fa=1+cmath.exp(-2j*math.pi*(h+2*k)/3)
    fb=1+cmath.exp(-2j*math.pi*(2*h+k)/3)
    ratio=fb/fa;phase=-cmath.phase(ratio)
    g=(2*math.pi*h,2*math.pi*(h+2*k)/math.sqrt(3))
    obs=finite_layer_observer(n,0.,phase)
    k1,k2,k3=obs['derivatives_at_zero']
    return {'hk':[h,k],'layers':n,'layer_phase':phase,'layer_factor_ratio_abs':abs(ratio),
            'G_times_a':list(g),'linear_row_wrt_article_P':[-k1*v for v in g],
            'coherent_reference_second_derivative':k2,
            'sample_geometry_measured':False}


def divided_cubic(a1,a2,a3,b2):
    """Derivative coefficients of N/(1+b2*q^2/2) through third order."""
    return a1,a2-b2,a3-3*a1*b2


def division_omission_bound(magnitude,rho):
    if magnitude<0 or not 0<=rho<1:
        raise ValueError('nonnegative magnitude and divisor radius below one required')
    return magnitude*rho/(1-rho)


def shared_divisor_ratios(values):
    """Only positive simultaneous normalized intensity traces, not harmonic coefficients."""
    import math
    if len(values)!=3 or any(not math.isfinite(v) or v<=0 for v in values):
        raise ValueError('three finite positive normalized intensities required')
    return values[0]/values[1],values[2]/values[1]


def linear_common_reconstruct(values,scale):
    """Exact inversion of LINEAR observer plus unknown common divisor only."""
    shared_divisor_ratios(values)
    if scale<=0: raise ValueError('positive known observer scale required')
    divisor=3/sum(values)
    corrected=tuple((divisor*v-1)/scale for v in values)
    return (*reconstruct(corrected),divisor)


def quotient_error_bound(a,b,ea,eb):
    import math
    if any(not math.isfinite(v) for v in (a,b,ea,eb)) or min(ea,eb)<0 or abs(b)<=eb:
        raise ValueError('finite joint errors and denominator separated from zero required')
    return (ea+abs(a/b)*eb)/(abs(b)-eb)


def full_ratio_observer(n,pa,pb):
    import math
    geometry=[source_geometry(h,k,n) for h,k in ((1,0),(0,1),(-1,1))]
    intensities=[]
    for p in geometry:
        t=-p['G_times_a'][0]*pa-p['G_times_a'][1]*pb
        intensities.append(finite_layer_observer(n,t,p['layer_phase'])['intensity'])
    rows=[p['linear_row_wrt_article_P'] for p in geometry]
    jac=[[rows[i][j]-rows[1][j] for j in (0,1)] for i in (0,2)]
    determinant=jac[0][0]*jac[1][1]-jac[0][1]*jac[1][0]
    f=float(Q(((n+1)//2)*(n//2),((n+1)//2)**2+(n//2)**2-((n+1)//2)*(n//2)))
    expected=24*math.pi**2*math.sqrt(3)*f*f
    if abs(determinant-expected)>1e-10:raise ValueError('ratio Jacobian identity failed')
    return {'layers':n,'P':[pa,pb],'intensities':intensities,
            'ratios':list(shared_divisor_ratios(intensities)),
            'baseline_ratio_jacobian_determinant':determinant,
            'common_applied_divisor_cancels':True,'actual_processing_identity_admitted':False}


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
            'finite_layer_material_projection':[finite_layer_projection(n) for n in (2,3,4,9)],
            'full_observer_controls':[finite_layer_observer(9,t) for t in (0.,-.001,.001,-.01,.01,-.1,.1)],
            'source_geometry_checks':[source_geometry(h,k) for h,k in ((1,0),(0,1),(-1,1),(2,0),(1,1))],
            'full_record_invariant_controls':[full_ratio_observer(9,*p) for p in ((0.,0.),(.0001,-.0002),(-.0001,.0002))],
            'shared_reference_cubic_ambiguity':{'true_material_third':'0',
                'inferred_third_with_unmodeled_divisor':str(two_order_third(
                    (Q(-3)-3*Q(2)*Q(1,10))*Q(1,100000),
                    (-8*Q(-3)+6*Q(2)*Q(1,10))*Q(1,100000),Q(2),Q(-3))[0]),
                'role':'rational counterexample, not physical bias estimate',
                'requires_undivided_reference_and_correction_bound':True,
                'requirement_scope':'processed-third-only inference; full-trace common-divisor invariant is an alternative sufficient observer packet'},
            'processed_third_only_null_direction':{'variables':['B','C','E=b2*C'],
                'null_vector':[3,0,1],
                'scope':'cubic processed third amplitudes, uncalibrated common divisor and free C; not full-record no-go',
                'more_same_processed_orders_sufficient':False},
            'two_order_candidate':{'orders':[1,2],'phase_pair':'plus/minus 2*pi/3',
                'material_third_formula':'(8*Y3_first+Y3_second)/(6*K1)',
                'joint_error_bound':'(8*E_first+E_second)/(6*abs(K1)) plus coefficient uncertainty',
                'physical_geometry_or_records_admitted':False},
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
