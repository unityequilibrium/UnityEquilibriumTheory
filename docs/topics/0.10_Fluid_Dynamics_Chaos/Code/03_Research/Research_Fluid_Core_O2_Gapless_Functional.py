"""SD01: exact conditional gHF functional algebra; no thermal integral/state.

The approximation-functional correction is phenomenological.  This verifier
checks its variation and static algebra, not an admitted microscopic operator.
"""
from __future__ import annotations
import argparse
import ast
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
TOPIC = Path('docs/topics/0.10_Fluid_Dynamics_Chaos')
CONTRACT = ROOT / TOPIC / 'Data/03_Research/fluid_core_o2_gapless_functional_contract.json'
OUTPUT = ROOT / TOPIC / 'Result/artifacts/fluid_core_o2_gapless_functional_audit.json'
CONTRACT_SHA = '981d26cdb0d1d371d14401ed7f85ad4da04ea4b9bcdcede0c1f1ad757d229a20'
# Polynomial coordinates: d=m^2-mu^2, lambda, Q11,Q22,Q12,phi1,phi2,t.
NV = 8

class Poly:
    """Sparse exact rational polynomial; coefficient cancellation is internal."""
    def __init__(self, terms=None):
        self.terms = {k: F(v) for k, v in (terms or {}).items() if v}
    @staticmethod
    def scalar(value):
        return value if isinstance(value, Poly) else Poly({(0,)*NV: F(value)})
    @staticmethod
    def variable(index):
        exponents = [0]*NV
        exponents[index] = 1
        return Poly({tuple(exponents): F(1)})
    def __add__(self, other):
        terms = dict(self.terms)
        for key, value in self.scalar(other).terms.items():
            terms[key] = terms.get(key, F(0)) + value
        return Poly(terms)
    __radd__ = __add__
    def __neg__(self):
        return Poly({k: -v for k, v in self.terms.items()})
    def __sub__(self, other):
        return self + -self.scalar(other)
    def __rsub__(self, other):
        return self.scalar(other) + -self
    def __mul__(self, other):
        terms = {}
        for a, av in self.terms.items():
            for b, bv in self.scalar(other).terms.items():
                key = tuple(x+y for x, y in zip(a,b))
                terms[key] = terms.get(key, F(0)) + av*bv
        return Poly(terms)
    __rmul__ = __mul__
    def __pow__(self, power):
        if not isinstance(power, int) or power < 0:
            raise ValueError('nonnegative polynomial powers only')
        result = self.scalar(1)
        for _ in range(power):
            result = result*self
        return result
    def __eq__(self, other):
        return self.terms == self.scalar(other).terms
    def derivative(self, index):
        terms = {}
        for key, value in self.terms.items():
            if key[index]:
                exponents = list(key)
                exponents[index] -= 1
                terms[tuple(exponents)] = value*key[index]
        return Poly(terms)

def transpose(a):
    return [list(row) for row in zip(*a)]
def multiply(a,b):
    return [[sum(a[i][k]*b[k][j] for k in range(2)) for j in range(2)] for i in range(2)]
def matvec(a,v):
    return [sum(a[i][j]*v[j] for j in range(2)) for i in range(2)]
def scale(a,s):
    return [[s*x for x in row] for row in a]
def equal(a,b):
    if isinstance(a,list):
        return isinstance(b,list) and len(a)==len(b) and all(equal(x,y) for x,y in zip(a,b))
    return a==b

def potential(q, coupling, interpolation=1):
    a,b,c = q[0][0],q[1][1],q[0][1]
    tr = a+b
    tr_square = a*a+b*b+2*c*c
    hartree = coupling*F(1,4)*(tr*tr+2*tr_square)
    correction = -coupling*F(1,2)*(2*tr_square-tr*tr)
    return hartree + interpolation*correction

def self_energy(q,coupling,interpolation=1):
    tr = q[0][0]+q[1][1]
    return [[coupling*((tr if i==j else 0)+2*q[i][j])
             +interpolation*coupling*((2*tr if i==j else 0)-4*q[i][j])
             for j in range(2)] for i in range(2)]

def field_potential(phi,q,d,coupling,interpolation=1):
    # Fixed-Q mean-field part; V2 has no explicit phi dependence at fixed G.
    x = sum(p*p for p in phi)
    phi_q_phi = sum(phi[i]*q[i][j]*phi[j] for i in range(2) for j in range(2))
    return (F(1,2)*d*x+F(1,4)*coupling*x*x
            +F(1,2)*coupling*x*(q[0][0]+q[1][1])
            +coupling*phi_q_phi+potential(q,coupling,interpolation))

def mean_residual(phi,q,d,coupling):
    x = sum(p*p for p in phi)
    qphi = matvec(q,phi)
    return [(d+coupling*x+coupling*(q[0][0]+q[1][1]))*phi[i]
            +2*coupling*qphi[i] for i in range(2)]

def inverse_block(phi,q,d,coupling,interpolation=1):
    x = sum(p*p for p in phi)
    sigma = self_energy(q,coupling,interpolation)
    return [[((d+coupling*x) if i==j else 0)+2*coupling*phi[i]*phi[j]+sigma[i][j]
             for j in range(2)] for i in range(2)]

def ward_defect(phi,q,d,coupling,interpolation=1):
    jphi = [-phi[1],phi[0]]
    h = mean_residual(phi,q,d,coupling)
    left = matvec(inverse_block(phi,q,d,coupling,interpolation),jphi)
    return [left[0]+h[1],left[1]-h[0]]

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
def encode(value):
    if isinstance(value,F): return str(value)
    if isinstance(value,dict): return {k:encode(v) for k,v in value.items()}
    if isinstance(value,list): return [encode(v) for v in value]
    return value

def audit(contract_path=CONTRACT):
    canonical = json.loads(CONTRACT.read_text(encoding='utf-8'))
    contract_path = Path(contract_path)
    data = json.loads(contract_path.read_text(encoding='utf-8'))
    checks=[]; cases=[]; witnesses=[]; inventory=[]; identities=[]
    def check(name,passed):
        checks.append({'name':name,'passed':bool(passed)})
    all_paths = set(canonical['prelocked_source_hashes']) | {
        (TOPIC/'Data/03_Research/fluid_core_o2_gapless_functional_contract.json').as_posix(),
        canonical['prior_method_artifact'],Path(__file__).relative_to(ROOT).as_posix()}
    prior = json.loads((ROOT/canonical['prior_method_artifact']).read_text(encoding='utf-8'))
    all_paths.update(prior['input_hashes'])
    archive_source = TOPIC/'Result/previews/core_o2_gapless_functional_first_verifier.py.txt'
    archive_result = TOPIC/'Result/previews/fluid_core_o2_gapless_functional_first_execution.json'
    all_paths.update([archive_source.as_posix(),archive_result.as_posix()])
    def finish():
        passed = all(x['passed'] for x in checks)
        result = {
          'schema_version':'t010-gapless-functional-audit-v1',
          'date':'2026-10-05','date_role':'audit_wave_version_not_run_timestamp',
          'status':'PASS_CONDITIONAL_GHF_FUNCTIONAL_ALGEBRA_ONLY' if passed else 'GAPLESS_FUNCTIONAL_DIAGNOSTIC_FAIL',
          'check_count':len(checks),'passing_check_count':sum(x['passed'] for x in checks),'checks':checks,
          'input_hashes':{p:sha(ROOT/p) for p in sorted(all_paths) if (ROOT/p).is_file()},
          'evaluated_contract_hash':sha(contract_path),
          'polynomial_identities':identities,'off_shell_controls':cases,'stationary_witnesses':witnesses,
          'source_inventory':inventory,
          'method_gate':{k:'NOT_STARTED' for k in canonical['method_gate']},
          'admission':{k:False for k in canonical['admission']},
          'unit_powers':{'phi':1,'Q':2,'V2':4,'Sigma':2,'K':2,'h':3},
          'approximation_functional_changed':True,'original_Core_action_edited':False,
          'temperature_integrals_executed':False,'full_condensed_interacting_state_computed':False,
          'whole_Core_runtime_executed':False,'external_source_vertex_computed':False,
          'formal_verification':False,'external_math_review':False,
          'physical_heat_current_matched':False,'physical_material_frame_admitted':False,
          'physical_J04_executed':False,'physical_J05_executed':False,'physical_J06_executed':False,
          'claim_promotion':False,'dependency_unlock':False,'parameters_fitted':False,'thresholds_relaxed':False,
          'physical_controller':canonical['physical_controller'],
          'controlling_measured_blocker':canonical['candidate_controller'],
          'method_controller':canonical['method_controller'],
          'scope':'exact internal polynomial/Fraction diagnostics and source AST inventory; no integral state, renormalization or dynamic vertex',
          'notes':['Q_ab is a coincident tadpole matrix, not UET Q=DtPhi.',
                   'The modified approximation functional is phenomenological; classical Core action is unchanged.',
                   'Static Goldstone consistency is not local/dynamic Ward, material heat or source response admission.',
                   'All ten method obligations remain NOT_STARTED.']}
        return encode(result)
    check('canonical_contract_prelocked_hash',sha(CONTRACT)==CONTRACT_SHA)
    check('evaluated_contract_matches_preregistration',data==canonical)
    check('all_sixteen_admissions_false',len(data.get('admission',{}))==16 and all(v is False for v in data.get('admission',{}).values()))
    check('all_ten_method_gates_not_started',len(data.get('method_gate',{}))==10 and all(v=='NOT_STARTED' for v in data.get('method_gate',{}).values()))
    check('no_temperature_integral',data.get('configuration',{}).get('temperature_integrals_executed') is False)
    for name,expected in canonical['prelocked_source_hashes'].items():
        check('prelocked_source:'+name,(ROOT/name).is_file() and sha(ROOT/name)==expected)
    check('prior_156_control_boundary',prior['check_count']==156 and prior['passing_check_count']==156 and prior['status']=='PASS_SOURCE_BRANCH_CONDITIONAL_ALGEBRA_ONLY')
    for name,expected in prior['input_hashes'].items():
        check('prior_input:'+name,(ROOT/name).is_file() and sha(ROOT/name)==expected)
    if not all(x['passed'] for x in checks): return finish()
    first = json.loads((ROOT/archive_result).read_text(encoding='utf-8'))
    original_path = Path(__file__).relative_to(ROOT).as_posix()
    first_inputs = {k.replace(chr(92),'/'):v for k,v in first['input_hashes'].items()}
    check('first_186_execution_retained',first['check_count']==186 and first['passing_check_count']==186 and first['status']=='PASS_CONDITIONAL_GHF_FUNCTIONAL_ALGEBRA_ONLY')
    check('first_source_identity_retained',sha(ROOT/archive_source)==first_inputs[original_path])
    if not all(x['passed'] for x in checks): return finish()
    # Source inspection only; no import/execution of Core modules or transport lane.
    classes = ['EnergyMomentumConservingBSState','ChargeConservingLadderResponseState','KineticCollisionState']
    required = [['microscopic_bethe_salpeter_match_completed','microscopic_sk_kms_match_completed','physical_kubo_coefficient_emitted'],['physical_kubo_coefficient_emitted'],['physical_kubo_coefficient_emitted']]
    for index,name in enumerate(canonical['source_module_paths']):
        tree=ast.parse((ROOT/name).read_text(encoding='utf-8'))
        cls=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name==classes[index])
        false_fields=[n.target.id for n in cls.body if isinstance(n,ast.AnnAssign) and isinstance(n.target,ast.Name) and isinstance(n.value,ast.Constant) and n.value.value is False]
        check('source_non_admission:'+name,all(n in false_fields for n in required[index]))
        definitions={n.name:hashlib.sha256(ast.dump(n,include_attributes=False).encode()).hexdigest() for n in tree.body if isinstance(n,(ast.ClassDef,ast.FunctionDef))}
        inventory.append({'path':name,'role':'AST_inventory_only_not_kernel_reuse','false_fields':false_fields,'definition_hashes':definitions,'runtime_executed':False})
        if index==2:
            helper=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='_normal_state_inputs')
            messages=[n.value for n in ast.walk(helper) if isinstance(n,ast.Constant) and isinstance(n.value,str)]
            check('strict_normal_branch_guard','kinetic collision lane requires a strict normal branch' in messages)
            check('mu_below_mass_guard','normal branch requires chemical potential below the mass' in messages)
    if not all(x['passed'] for x in checks): return finish()
    d,l,a,b,c,u,v,t = [Poly.variable(i) for i in range(NV)]
    q=[[a,c],[c,b]];phi=[u,v]
    homogeneous=field_potential(phi,q,d,l,1)
    correction=potential(q,l,1)-potential(q,l,0)
    for i,coordinate in enumerate([5,6]):
        residual=homogeneous.derivative(coordinate)-mean_residual(phi,q,d,l)[i]
        check('general_mean_field_variation:'+str(i),residual==0)
        identities.append({'name':'mean_field_variation:'+str(i),'residual_term_count':len(residual.terms)})
        check('correction_fixed_Q_mean_independence:'+str(i),correction.derivative(coordinate)==0)
    for method in [0,1]:
        value=potential(q,l,method);sigma=self_energy(q,l,method)
        for coord,i,j,factor in [(2,0,0,2),(3,1,1,2),(4,0,1,1)]:
            residual=factor*value.derivative(coord)-sigma[i][j]
            check(f'polynomial_variation:{method}:{coord}',residual==0)
            identities.append({'name':f'variation:{method}:{coord}','residual_term_count':len(residual.terms)})
    for i,residual in enumerate(ward_defect(phi,q,d,l,1)):
        check('general_static_Ward:'+str(i),residual==0)
        identities.append({'name':'static_Ward:'+str(i),'residual_term_count':len(residual.terms)})
    jq=[-v,u]
    traceless=[[2*a-(a+b),2*c],[2*c,2*b-(a+b)]]
    expected=[2*l*(1-t)*x for x in matvec(traceless,jq)]
    for i,(got,want) in enumerate(zip(ward_defect(phi,q,d,l,t),expected)):
        residual=got-want;check('general_interpolation_defect:'+str(i),residual==0)
        identities.append({'name':'interpolation_defect:'+str(i),'residual_term_count':len(residual.terms)})
    check('general_omission_negative_detected',not equal(ward_defect(phi,q,d,l,0),[0,0]))
    check('general_half_correction_negative_detected',not equal(ward_defect(phi,q,d,l,F(1,2)),[0,0]))
    # A nonzero cross-Hessian makes frozen and relaxed Schur responses distinct.
    # This is a symbolic chain-rule obligation, not an evaluated Gamma_GG inverse.
    check('frozen_external_identification_rejected',u*v!=0 and canonical['admission']['external_source_vertex'] is False)
    config=canonical['configuration'];coupling=F(config['lambda_here']);mass=F(config['mass_squared']);mu=F(config['mu_charge']);delta=mass-mu*mu
    check('paper_N_normalization',F(config['lambda_paper_over_lambda_here'],config['N'])==1)
    rotation=[[F(x) for x in row] for row in canonical['verification']['rotation']]
    check('rational_rotation_orthogonal',equal(multiply(rotation,transpose(rotation)),[[1,0],[0,1]]))
    for index,point in enumerate(canonical['verification']['off_shell']):
        field=[F(x) for x in point['phi']];qa,qb,qc=[F(x) for x in point['Q']];matrix=[[qa,qc],[qc,qb]]
        for method in [0,1]:
            sigma=self_energy(matrix,coupling,method)
            for step_token in canonical['verification']['variation_steps']:
                step=F(step_token)
                for coord,i,j,factor in [(0,0,0,2),(1,1,1,2),(2,0,1,1)]:
                    plus=[qa,qb,qc];minus=[qa,qb,qc];plus[coord]+=step;minus[coord]-=step
                    pq=[[plus[0],plus[2]],[plus[2],plus[1]]];mq=[[minus[0],minus[2]],[minus[2],minus[1]]]
                    derivative=(potential(pq,coupling,method)-potential(mq,coupling,method))/(2*step)
                    check(f'central_variation:{index}:{method}:{step_token}:{coord}',factor*derivative==sigma[i][j])
        rq=multiply(multiply(rotation,matrix),transpose(rotation));rp=matvec(rotation,field)
        check('mean_rotation:'+str(index),equal(mean_residual(rp,rq,delta,coupling),matvec(rotation,mean_residual(field,matrix,delta,coupling))))
        check('inverse_rotation:'+str(index),equal(inverse_block(rp,rq,delta,coupling),multiply(multiply(rotation,inverse_block(field,matrix,delta,coupling)),transpose(rotation))))
        check('potential_rotation:'+str(index),potential(rq,coupling)==potential(matrix,coupling))
        check('static_Ward_point:'+str(index),equal(ward_defect(field,matrix,delta,coupling),[0,0]))
        wrong=-4*coupling*qc
        check('off_diagonal_factor_negative:'+str(index),wrong!=self_energy(matrix,coupling)[0][1])
        for method in [0,F(1,2)]:check(f'coefficient_negative:{index}:{method}',not equal(ward_defect(field,matrix,delta,coupling,method),[0,0]))
        energy=canonical['verification']['energy_scale'];sq=scale(matrix,energy**2);sp=[energy*x for x in field];sd=energy**2*delta
        check('unit_V2:'+str(index),potential(sq,coupling)==energy**4*potential(matrix,coupling))
        check('unit_Sigma:'+str(index),equal(self_energy(sq,coupling),scale(self_energy(matrix,coupling),energy**2)))
        check('unit_K:'+str(index),equal(inverse_block(sp,sq,sd,coupling),scale(inverse_block(field,matrix,delta,coupling),energy**2)))
        check('unit_h:'+str(index),equal(mean_residual(sp,sq,sd,coupling),[energy**3*x for x in mean_residual(field,matrix,delta,coupling)]))
        cases.append({'phi':field,'Q':matrix,'Sigma_H':self_energy(matrix,coupling,0),'Sigma_g':self_energy(matrix,coupling),'Ward_g':ward_defect(field,matrix,delta,coupling),'Ward_omitted':ward_defect(field,matrix,delta,coupling,0),'Ward_half_correction':ward_defect(field,matrix,delta,coupling,F(1,2))})
    ip=F(canonical['verification']['stationary_witness']['I_plus'])
    for token in canonical['verification']['stationary_witness']['I_minus']:
        im=F(token);x=(mu*mu-mass-coupling*(2*ip+im))/coupling
        y=mass+2*coupling*x+2*coupling*ip;dg=coupling*x-coupling*im;dh=coupling*x+coupling*im
        mean=delta+coupling*x+coupling*(2*ip+im);goldstone=y-dg-mu*mu
        original=[y+dg-mu*mu-2*coupling*x,y-mass-2*coupling*x-2*coupling*ip,dg-coupling*x-coupling*im]
        check('stationary_mean:'+token,mean==0)
        check('modified_static_Goldstone:'+token,goldstone==0)
        check('synthetic_radial_positive:'+token,x>0 and 2*coupling*(x-im)>0)
        check('original_residual_tradeoff:'+token,equal(original,[-2*coupling*im,0,-2*coupling*im]))
        check('old_stationary_Goldstone_defect:'+token,y-dh-mu*mu==-2*coupling*im)
        witnesses.append({'I_plus':ip,'I_minus':im,'rho_squared':x,'Y':y,'D_g':dg,'D_H':dh,'mean_residual':mean,'Goldstone_g':goldstone,'original_Hartree_residuals_at_gHF':original,'synthetic_tadpoles':True,'temperature_integral_solved':False})
    return finish()

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--contract-json',type=Path,default=CONTRACT)
    parser.add_argument('--output',type=Path,default=OUTPUT)
    args=parser.parse_args()
    result=audit(args.contract_json)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(result['status'],str(result['passing_check_count'])+'/'+str(result['check_count']))
    return 0 if result['status'].startswith('PASS_') else 1

if __name__=='__main__':
    raise SystemExit(main())
