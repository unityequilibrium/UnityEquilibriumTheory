"""Conditional conservative action audit; not an admitted UET fluid solver.

Spacetime paths test first variations, not stationarity or PDE trajectories.
"""
from __future__ import annotations
import argparse
import ast
import hashlib
import json
from pathlib import Path
from types import SimpleNamespace
import numpy as np
from Research_Fluid_Vector_State_Contract import (
    ROOT, TOPIC, CORE, PeriodicOperators, source_expression, evaluate, rms, relative
)

CONTRACT = TOPIC / "Data/03_Research/fluid_vector_variational_origin_contract.json"
PARENT = TOPIC / "Data/03_Research/fluid_vector_state_research_contract.json"
REGISTRY = ROOT / "docs/core/07_artifacts/correspondence/uet_equation_correspondence_registry_topic10_variational_addendum.json"
CARD = TOPIC / "VECTOR_VARIATIONAL_ORIGIN.md"
OUTPUT = TOPIC / "Result/artifacts/fluid_vector_variational_origin_audit.json"


def locked_field(expression, x, y, t):
    node = ast.parse(expression, mode="eval")
    allowed = (ast.Expression, ast.BinOp, ast.UnaryOp, ast.Name, ast.Load,
               ast.Constant, ast.Call, ast.Add, ast.Sub, ast.Mult, ast.Div,
               ast.USub, ast.UAdd)
    for part in ast.walk(node):
        if not isinstance(part, allowed):
            raise ValueError("unsupported manufactured expression")
        if isinstance(part, ast.Name) and part.id not in ("x", "y", "t", "sin", "cos"):
            raise ValueError("unsupported control symbol")
        if isinstance(part, ast.Call) and not (
            isinstance(part.func, ast.Name) and part.func.id in ("sin", "cos")):
            raise ValueError("only trig calls allowed")
    result = eval(compile(node, "<locked_field>", "eval"), {"__builtins__": {}},
                  dict(x=x, y=y, t=t, sin=np.sin, cos=np.cos))
    return np.broadcast_to(result, np.broadcast_shapes(x.shape, y.shape, t.shape)).copy()


def audit_grid(n, c, rules, expressions):
    op = PeriodicOperators(n)
    t = (np.arange(n)*2*np.pi/n)[:, None, None]
    x, y = op.x[None, :], op.y[None, :]
    ktime = np.fft.fftfreq(n, d=1/n)[:, None, None]
    def dt(a):
        return np.fft.ifft(1j*ktime*np.fft.fft(a, axis=0), axis=0).real
    def field(name):
        return locked_field(rules["fields"][name], x, y, t)
    def integral(a):
        return float(np.mean(a)*(2*np.pi)**3)
    def transport(v, a):
        return dt(a)+op.advection(v, a)
    def vector_transport(v, a):
        return np.stack([transport(v, a[i]) for i in range(2)])
    def density(C, Phi):
        local = evaluate(expressions["local_density"][1], config=c, C=C, Phi=Phi)
        return (local+c.kappa_matter*np.sum(op.gradient(C)**2, axis=0)/2
                +c.kappa_space*np.sum(op.gradient(Phi)**2, axis=0)/2)
    def potentials(C, Phi):
        env=dict(config=c, C=C, Phi=Phi, lap_C=op.laplacian(C),
                 lap_Phi=op.laplacian(Phi))
        return tuple(evaluate(expressions[key][1], **env) for key in ("mu_C", "mu_Phi"))
    h = c.tau_space/c.mobility_space
    def lagrangian(C, Phi, Pi, velocity):
        q = Pi+op.advection(velocity, Phi)
        return c.rho0*np.sum(velocity**2, axis=0)/2+h*q*q/2-density(C, Phi)
    def action(C, Phi, velocity):
        return integral(lagrangian(C, Phi, dt(Phi), velocity))
    checks={}
    details={}
    tol=rules["identity_tolerance"]
    floor=rules["negative_control_floor"]
    def check(name, value, limit=tol):
        checks[name]=dict(metric=float(value), threshold=float(limit),
                          pass_=bool(np.isfinite(value) and value<=limit))
    def sensitive(name, value):
        checks[name]=dict(metric=float(abs(value)), minimum=float(floor),
                          pass_=bool(np.isfinite(value) and abs(value)>floor))
    C,Phi=field("C"),field("Phi")
    u=np.stack([field("u_x"),field("u_y")])
    chi,psi=field("chi"),field("xi_stream")
    xi=np.stack([op.derivative(psi,1),-op.derivative(psi,0)])
    Pi=dt(Phi)
    Q=transport(u,Phi)
    gc,gp=op.gradient(C),op.gradient(Phi)
    muC,muP=potentials(C,Phi)
    du=np.stack([dt(xi[i])+op.advection(u,xi[i])-op.advection(xi,u[i])
                 for i in range(2)])
    dC=-op.advection(xi,C)
    dPhi=chi-op.advection(xi,Phi)
    dQ=transport(u,chi)-op.advection(xi,Q)
    dQchain=dt(dPhi)+np.sum(du*gp,axis=0)+op.advection(u,dPhi)
    check("velocity_divergence",rms(op.divergence(u)))
    check("displacement_divergence",rms(op.divergence(xi)))
    check("reversible_C_path_constraint",rms(transport(u,C)))
    check("linearized_C_constraint",rms(transport(u,dC)+op.advection(du,C)))
    check("variation_endpoints",max(rms(xi[:,0]),rms(chi[0]),rms(dC[0]),rms(dPhi[0])))
    check("material_Q_variation_chain_rule",relative(dQ,dQchain))
    check("Eulerian_material_coordinate",relative(Q,Pi+op.advection(u,Phi)))
    integrand=c.rho0*np.sum(u*du,axis=0)+h*Q*dQ-muC*dC-muP*dPhi
    direct=integral(integrand)
    kinetic=c.rho0*np.sum(u*u,axis=0)/2+h*Q*Q/2
    force=muC*gc+muP*gp
    axi=-c.rho0*vector_transport(u,u)+force-op.gradient(kinetic)
    achi=-h*transport(u,Q)-muP
    ibp=integral(np.sum(axi*xi,axis=0)+achi*chi)
    check("integrated_by_parts_first_variation",relative(direct,ibp))
    sensitive("nonstationary_path_is_informative",direct)
    fd_rows=[]
    for eps in rules["steps"]:
        finite=(action(C+eps*dC,Phi+eps*dPhi,u+eps*du)
                -action(C-eps*dC,Phi-eps*dPhi,u-eps*du))/(2*eps)
        fd_rows.append(dict(step=eps, derivative=finite,
                            normalized_error=relative(finite,direct)))
    check("action_finite_difference_finest",fd_rows[-1]["normalized_error"],
          rules["directional_derivative_tolerance"])
    check("action_finite_difference_improves",
          max(0,fd_rows[-1]["normalized_error"]-fd_rows[0]["normalized_error"]),tol)
    details.update(action=action(C,Phi,u),direct_first_variation=direct,
                   ibp_first_variation=ibp,action_finite_differences=fd_rows)
    # Q transport omission is invisible in integrated kinetic work: it is a
    # periodic divergence. Its negative control must test the local chain rule.
    dQomit=transport(u,chi)
    sensitive("omitted_material_Q_transport_breaks_local_chain",
              rms(dQomit-dQchain))
    check("Q_transport_work_is_periodic_gauge",
          abs(integral(h*Q*op.advection(xi,Q))))
    naive_dQ=dt(chi)+np.sum(du*gp,axis=0)+op.advection(u,chi)
    naive_direct=integral(c.rho0*np.sum(u*du,axis=0)+h*Q*naive_dQ
                          -muC*dC-muP*chi)
    sensitive("omitted_Phi_transport_changes_action_variation",naive_direct-direct)
    details["omitted_Phi_transport_variation_defect"]=naive_direct-direct
    details["omitted_Q_transport_local_defect"]=rms(dQomit-dQchain)
    p=h*Q
    m=c.rho0*u+p*gp
    v=np.broadcast_to(np.asarray(rules["fields"]["velocity_fibre_direction"])[:,None,None,None],
                      u.shape)
    r=field("rate_fibre_direction")
    velocity_pair=integral(np.sum(m*v,axis=0))
    rate_pair=integral(p*r)
    rate_rows=[]
    velocity_rows=[]
    for eps in rules["steps"]:
        velocity_fd=integral((lagrangian(C,Phi,Pi,u+eps*v)
                              -lagrangian(C,Phi,Pi,u-eps*v))/(2*eps))
        rate_fd=integral((lagrangian(C,Phi,Pi+eps*r,u)
                          -lagrangian(C,Phi,Pi-eps*r,u))/(2*eps))
        velocity_rows.append(dict(step=eps,derivative=velocity_fd,
                                  normalized_error=relative(velocity_fd,velocity_pair)))
        rate_rows.append(dict(step=eps,derivative=rate_fd,
                              normalized_error=relative(rate_fd,rate_pair)))
    check("canonical_velocity_derivative",velocity_rows[-1]["normalized_error"],
          rules["directional_derivative_tolerance"])
    check("canonical_scalar_rate_derivative",rate_rows[-1]["normalized_error"],
          rules["directional_derivative_tolerance"])
    naive_m_pair=integral(c.rho0*np.sum(u*v,axis=0))
    sensitive("naive_mechanical_canonical_identification_fails",
              velocity_rows[-1]["derivative"]-naive_m_pair)
    details.update(canonical_velocity_pairing=velocity_pair,
                   mechanical_only_pairing=naive_m_pair,
                   canonical_momentum_defect=velocity_pair-naive_m_pair,
                   velocity_finite_differences=velocity_rows,rate_finite_differences=rate_rows)
    reconstructed_u=(m-p*gp)/c.rho0
    reconstructed_Pi=p/h-op.advection(reconstructed_u,Phi)
    check("Legendre_velocity_inverse",relative(reconstructed_u,u))
    check("Legendre_Eulerian_rate_inverse",relative(reconstructed_Pi,Pi))
    L=lagrangian(C,Phi,Pi,u)
    Hlegendre=np.sum(m*u,axis=0)+p*Pi-L
    Hcanonical=np.sum((m-p*gp)**2,axis=0)/(2*c.rho0)+p*p/(2*h)+density(C,Phi)
    Hreference=kinetic+density(C,Phi)
    check("Hamiltonian_Legendre_definition",relative(Hlegendre,Hcanonical))
    check("Hamiltonian_reference_energy_alignment",relative(Hcanonical,Hreference))
    # Algebraic positivity is in the card. Sampled Hessians are a numeric check,
    # not a PDE stability argument or a substitute for the Schur complement.
    step=max(1,n//8)
    a=np.moveaxis(gp[:,::step,::step,::step],0,-1)
    matrix=np.zeros(a.shape[:-1]+(3,3))
    matrix[...,:2,:2]=c.rho0*np.eye(2)+h*a[..., :,None]*a[...,None,:]
    matrix[...,:2,2]=h*a
    matrix[...,2,:2]=h*a
    matrix[...,2,2]=h
    minimum=float(np.min(np.linalg.eigvalsh(matrix)))
    determinant=np.linalg.det(matrix)
    check("rate_Hessian_determinant",relative(determinant,h*c.rho0**2))
    checks["rate_Hessian_positive"]=dict(metric=minimum,minimum=0,pass_=minimum>0)
    details["rate_Hessian_minimum_eigenvalue"]=minimum
    details["rate_Hessian_sample_count"]=int(np.prod(a.shape[:-1]))
    # Canonical derivative correction is a vector, not a mass identification.
    sensitive("canonical_field_correction_nonzero",rms(m-c.rho0*u))
    for row in checks.values():
        row["pass"]=row.pop("pass_")
    return dict(grid=n,temporal_grid=n,checks=checks,details=details,
                pass_=all(row["pass"] for row in checks.values()))


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--output",type=Path,default=OUTPUT)
    args=parser.parse_args()
    contract=json.loads(CONTRACT.read_text())
    parent=json.loads(PARENT.read_text())
    coefficients=SimpleNamespace(**parent["coefficients"])
    if coefficients.rho0<=0 or coefficients.tau_space<=0 or coefficients.mobility_space<=0:
        raise ValueError("positive constant rate/fluid inertia required")
    expressions={key:source_expression(function,assignment)
                 for key,function,assignment in [
                     ("local_density","matter_space_free_energy","local_density"),
                     ("mu_C","matter_space_chemical_potentials","mu_C"),
                     ("mu_Phi","matter_space_chemical_potentials","mu_Phi")]}
    rows=[audit_grid(n,coefficients,contract["verification"],expressions)
          for n in contract["verification"]["grids"]]
    for row in rows: row["pass"]=row.pop("pass_")
    ok=all(row["pass"] for row in rows)
    inputs=[Path(__file__),CONTRACT,PARENT,REGISTRY,CARD,CORE,
            Path(__file__).with_name("Research_Fluid_Vector_State_Contract.py")]
    output=dict(schema_version="t10-vector-variational-origin-audit-v1",
                status="PASS_CONDITIONAL_VARIATIONAL_REFERENCE_ONLY" if ok else "FAIL_VARIATIONAL_REFERENCE",
                controlling_blocker=contract["controlling_blocker"],
                claim_promotion=False,dependency_unlock=False,physical_uet_operator_admitted=False,
                scope="Spacetime first-variation/fibre audit of a declared action; not an EOM trajectory or formal proof.",
                origin=contract["origin"],admission_gates=contract["admission_gates"],
                reference_check_count=sum(len(row["checks"]) for row in rows),
                thresholds=contract["verification"],grids=rows,
                canonical_source_expressions={key:item[0] for key,item in expressions.items()},
                input_hashes={str(path.relative_to(ROOT)).replace("\\","/"):
                              hashlib.sha256(path.read_bytes()).hexdigest() for path in inputs},
                physical_controller_unchanged=True,
                excluded=["SI calibration","physical material state","dissipative closure",
                          "trajectory/time convergence","Core admission","He-II response","global regularity"])
    args.output.parent.mkdir(parents=True,exist_ok=True)
    with args.output.open("w",encoding="utf-8",newline="\n") as stream:
        stream.write(json.dumps(output,indent=2,allow_nan=False)+"\n")
    failures=[(row["grid"],name) for row in rows for name,item in row["checks"].items()
              if not item["pass"]]
    print(json.dumps(dict(status=output["status"],checks=output["reference_check_count"],failures=failures)))
    return 0 if ok else 1


if __name__=="__main__":
    raise SystemExit(main())
