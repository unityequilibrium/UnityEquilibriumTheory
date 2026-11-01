"""Existing-action coherent source/preparation distinction; no new Core source."""
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
CONTRACT=BASE+'calculation_contracts/mechanical_source_bridge.json'
OUTPUT='docs/core/07_artifacts/topic13/t13_mechanical_source_bridge.json'


def required_source(chi,acceleration,z,mass_sq,quartic,epsilon,coupling,delta_phi):
    """Inverse residual for a prescribed trajectory, NOT independently known drive."""
    if len(chi)!=2 or len(acceleration)!=2 or z<=0 or quartic<=0 or min(epsilon,coupling)<0:
        raise ValueError('outside declared two-component action domain')
    coefficient=mass_sq+quartic*sum(x*x for x in chi)-epsilon*coupling*delta_phi
    return tuple(z*a+coefficient*x for a,x in zip(acceleration,chi))


def source_free_acceleration(chi,z,mass_sq,quartic,epsilon,coupling,delta_phi):
    force=required_source(chi,(Q(0),Q(0)),z,mass_sq,quartic,epsilon,coupling,delta_phi)
    return tuple(-f/z for f in force)


def stationary_background(mass_effective_sq,quartic,amplitude_sq):
    if quartic<=0 or amplitude_sq<0:
        raise ValueError('positive quartic and nonnegative amplitude required')
    if amplitude_sq==0:
        return (mass_effective_sq,mass_effective_sq)
    if mass_effective_sq+quartic*amplitude_sq!=0:
        raise ValueError('declared nonzero background is not stationary')
    return (2*quartic*amplitude_sq,Q(0))  # longitudinal/transverse Hessian


def current_core_controls():
    import numpy as np
    from docs.core.uet_covariant_response import CovariantResponseConfig
    from docs.core.uet_covariant_matter import (CovariantMatterConfig,matter_on_shell_box,
        matter_eom_residual,reciprocal_interaction_derivatives)
    rc=CovariantResponseConfig(epsilon_nc=.5,phi_equilibrium=0.)
    mc=CovariantMatterConfig(matter_kinetic=1.25,matter_mass_sq=1.,matter_quartic=.75,response_coupling=.6)
    error=0.; count=0
    for phi in (-4.,-1.,0.,1.,4.,8.):
        if not np.array_equal(matter_on_shell_box((0.,0.),phi,rc,mc),np.zeros(2)):
            raise ValueError('production normal-state force is no longer homogeneous')
        for chi in ((.5,-.25),(-.5,.25)):
            exact=source_free_acceleration(tuple(map(Q,chi)),Q(5,4),Q(1),Q(3,4),Q(1,2),Q(3,5),Q(phi))
            actual=-matter_on_shell_box(chi,phi,rc,mc)
            error=max(error,float(np.max(np.abs(actual-np.array([float(v) for v in exact])))))
            if np.max(np.abs(matter_eom_residual(-actual,chi,phi,rc,mc)))>1e-13:
                raise ValueError('flat Box=-acceleration convention drifted')
            a=reciprocal_interaction_derivatives(phi,chi,rc,mc)
            b=reciprocal_interaction_derivatives(phi,tuple(-x for x in chi),rc,mc)
            if a[0]!=b[0] or not np.array_equal(a[1],-b[1]):
                raise ValueError('existing even-source/odd-force parity changed')
            count+=1
    if error>1e-13:
        raise ValueError('exact reduced force differs from current implementation')
    return {'nonzero_epsilon':.5,'nonzero_coupling':.6,'scalar_settings':6,
            'nonzero_state_controls':count,'largest_acceleration_roundoff':error,
            'boundary':'finite implementation controls supplement initial-value uniqueness proof; 1e-13 is a code-roundoff check, not physical tolerance'}


def calculate():
    z,mass,quartic,e,h=Q(5,4),Q(1),Q(3,4),Q(1,2),Q(3,5)
    for phi in map(Q,(-4,-1,0,1,4,8)):
        if source_free_acceleration((Q(0),Q(0)),z,mass,quartic,e,h,phi)!=(0,0):
            raise ValueError('zero-state identity failed')
    witness=required_source((Q(1,2),Q(0)),(Q(-1,3),Q(0)),z,mass,quartic,e,h,Q(2))
    return {'status':'NORMAL_BRANCH_SCALAR_DRIVE_DOES_NOT_SUPPLY_COHERENT_MATTER_FORCE',
            'source_kind':'mass/stiffness modulation, not additive directional force',
            'zero_initial_state_prediction':'chi=0 for arbitrary finite continuous scalar history on interval of unique solution',
            'nonzero_coupling_required_for_controls':True,
            'proof_basis':'polynomial state vector field is locally Lipschitz; zero is a solution; uniqueness, not a time sweep',
            'current_core_controls':current_core_controls(),
            'inverse_residual_example':[str(v) for v in witness],
            'inverse_residual_role':'constructing J from a compared trajectory is a tautological inverse input, not independent pump calibration',
            'nonzero_background_boundary':{'example_hessian':[str(x) for x in stationary_background(Q(-3),Q(3,4),Q(4))],
                'boundary':'different broken-background expansion, not the inherited stable-normal mechanical kernel'},
            'minimum_missing_input':'independently justified conjugate-drive functional OR preparation-to-initial-state map, with mode/projection and matched signed readout/joint errors; a free-ringdown protocol is not the four-drive kernel test',
            'units':{'chi':'E','delta_phi':'E','h':'E','matter_force_or_J':'E^3','conditional_lab_acceleration_drive':'m/s^2'},
            'physical_source_operator_added':False,'physical_test_run':False,'physical_acceptance':False,
            'new_material_parameter':False,'new_data_acquired':False,'new_held_out_rows':False,
            'claim_boundary':'normal homogeneous coherent first-moment source/preparation restriction only; not zero thermal/variance response, no parametric-seed prohibition, no global UET no-go'}


def record():
    return {**calculate(),**artifact_metadata(load_json(ROOT/CONTRACT),ROOT),
            'generator_path':Path(__file__).relative_to(ROOT).as_posix(),
            'evidence_class':'FORMAL_SOURCE_INTERFACE_NOT_PHYSICAL_VALIDATION'}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    group=p.add_mutually_exclusive_group(required=True)
    group.add_argument('--emit',action='store_true'); group.add_argument('--check',action='store_true')
    args=p.parse_args(); text=json.dumps(record(),ensure_ascii=False,indent=2,allow_nan=False)+'\n'; path=ROOT/OUTPUT
    if args.emit:
        if shutil.disk_usage(ROOT).free<100*1024*1024: raise SystemExit('Insufficient free space')
        path.write_text(text,encoding='utf-8',newline='\n')
    elif not path.exists() or path.read_text(encoding='utf-8')!=text:
        raise SystemExit('Missing/drifted evidence; check is read-only')
    print('NORMAL_BRANCH_COHERENT_SOURCE_NOT_SUPPLIED; no physical test')


if __name__=='__main__': main()
