"""Independent diagram, Ward, routing and scaling tests for the current vertex."""
from dataclasses import replace
from math import pi
import numpy as np
import pytest
from docs.core.uet_o2_finite_density_charged_vertex import charged_euclidean_inverse
from docs.scripts.audit import audit_topic13_charged_one_loop_current_vertex as a

CFG=a.CFG


@pytest.mark.parametrize("q,mu,nP,nQ,pz,Qz",[
    (1,.2,1,1,.3,.4),(-1,.2,1,1,.3,.4),(1,-.2,2,1,-.2,.5),(1,0.,1,2,.4,-.3)])
def test_residue_triangle_against_direct_matsubara(q,mu,nP,nQ,pz,Qz):
    r=a.direct_sum_witness(q=q,mu=mu,nP=nP,nQ=nQ,pz=pz,Qz=Qz)
    assert r["relative_error"]<1e-9
    assert np.linalg.norm(r["numeric"])>0


def test_documented_routing_is_legacy_plus_i_mu_propagator():
    T=.25; P0=2*pi*T; K0=4*pi*T; mu=.2; q=1; p=.3; k=.7; c=.23
    momentum=np.sqrt(k*k+p*p-2*k*p*c)
    direct=(P0-K0+1j*q*mu)**2+momentum**2+CFG.mass**2
    legacy=charged_euclidean_inverse(P0-K0,momentum,q*mu,CFG.mass)
    assert direct==legacy


@pytest.mark.parametrize("T,q,nP,nQ,pz,Qz",[
    (.25,1,1,1,.3,.4),(.25,-1,1,1,.3,.4),(.25,1,2,1,-.2,.5),(.5,1,1,2,.4,-.3)])
def test_explicit_full_vertex_satisfies_ward(T,q,nP,nQ,pz,Qz):
    r=a.current_vertex(T,nP,nQ,pz,Qz,q)
    assert r["Ward_relative_error"]<2e-8
    assert r["bath_transversality_relative"]<2e-8
    assert np.linalg.norm(r["mixed_thermal_triangle"])>0
    assert np.linalg.norm(r["mixed_vacuum_and_counterterm_vertex"])>0
    assert "P-K" in r["routing"] and "legacy convention" in r["routing"]


@pytest.mark.parametrize("q",[-1,1])
def test_mixed_thermal_triangle_matches_self_energy_difference(q):
    T=.25; P0=2*pi*T; Q0=P0; p=.3; Q=.4; mu=.2
    triangle=CFG.cubic**2*a.integrate_vertex_integrand(
        a.mixed_triangle_integrand,T,q,P0,Q0,p,Q,mu,order_radial=96,order_angle=48)
    before=a.mixed_thermal_self_energy(P0,p,T,q,mu,order_radial=96,order_angle=48)
    after=a.mixed_thermal_self_energy(P0+Q0,p+Q,T,q,mu,order_radial=96,order_angle=48)
    assert np.array([Q0,Q])@triangle==pytest.approx(q*(after-before),rel=1e-9,abs=1e-13)


@pytest.mark.parametrize("q",[-1,1])
def test_vacuum_triangle_and_counterterm_match_subtracted_self_energy(q):
    T=.25; P0=2*pi*T; Q0=P0; p=.3; Q=.4; mu=.2
    vertex=a.vacuum_vertex(P0,Q0,p,Q,q,mu)
    before=a.vacuum_self_energy(P0,p,q,mu)
    after=a.vacuum_self_energy(P0+Q0,p+Q,q,mu)
    assert np.array([Q0,Q])@vertex==pytest.approx(q*(after-before),rel=1e-10,abs=1e-13)


def test_bath_diagram_is_transverse_by_continuum_shift_not_projection():
    T=.25; Q0=2*pi*T; Q=.4; mu=.2
    errors=[]
    for nr,na in ((64,32),(96,48),(128,64)):
        vertex=a.integrate_vertex_integrand(
            a.bath_triangle_integrand,T,Q0,Q,mu,order_radial=nr,order_angle=na)
        errors.append(abs(np.array([Q0,Q])@vertex)/(np.linalg.norm([Q0,Q])*np.linalg.norm(vertex)))
    assert max(errors)<1e-10


def test_response_relaxation_changes_bath_coefficient_without_changing_ward():
    r=a.current_vertex()
    tree=-4*CFG.coupling
    response_part=CFG.cubic**2/(r["Q0"]**2+r["Qz"]**2+CFG.response_mass_sq)
    assert r["bath_coefficient"]==pytest.approx(tree+response_part)
    assert response_part>0
    assert r["bath_coefficient"]!=tree
    assert abs(np.array([r["Q0"],r["Qz"]])@r["response_relaxed_bath_triangle"])<1e-12


def test_zero_response_coupling_removes_mixed_and_mean_terms_not_o2_bath():
    cfg=replace(CFG,response_coupling=0.)
    r=a.current_vertex(cfg=cfg)
    assert np.linalg.norm(r["mixed_thermal_triangle"])==0
    assert np.linalg.norm(r["mixed_vacuum_and_counterterm_vertex"])==0
    assert r["bath_coefficient"]==-4*cfg.coupling
    assert np.linalg.norm(r["response_relaxed_bath_triangle"])>0
    assert r["Ward_relative_error"]<2e-8


def test_charge_conjugation():
    plus=a.current_vertex(q=1,mu=.2)
    minus=a.current_vertex(q=-1,mu=-.2,nP=-1,nQ=-1,pz=-.3,Qz=-.4)
    for key in ("bare","mixed_thermal_triangle","mixed_vacuum_and_counterterm_vertex","total"):
        assert minus[key]==pytest.approx(np.conjugate(plus[key]),rel=2e-10,abs=1e-12)


def test_natural_energy_covariance():
    scale=2.
    cfg=replace(CFG,mass_squared=CFG.mass_squared*scale**2,
        response_mass_squared=CFG.response_mass_squared*scale**2,
        response_coupling=CFG.response_coupling*scale)
    base=a.current_vertex()
    new=a.current_vertex(T=.25*scale,pz=.3*scale,Qz=.4*scale,mu=.2*scale,cfg=cfg)
    for key in ("bare","mixed_thermal_triangle","response_relaxed_bath_triangle",
                "mixed_vacuum_and_counterterm_vertex","total"):
        assert new[key]==pytest.approx(base[key]*scale,rel=2e-9,abs=1e-12)


@pytest.mark.parametrize("kwargs",[
    {"T":0.},{"q":0},{"mu":1.},{"nP":True},{"nQ":0},{"order_radial":1},{"order_angle":1}])
def test_invalid_domains(kwargs):
    with pytest.raises(ValueError):
        a.current_vertex(**kwargs)
