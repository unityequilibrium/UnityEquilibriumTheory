"""Independent variation, provenance, negative scope and stationary tradeoff tests."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from fractions import Fraction as F
from unittest.mock import patch

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('gapless_functional',HERE/'Research_Fluid_Core_O2_Gapless_Functional.py')
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

class GaplessFunctionalTests(unittest.TestCase):
    def test_fresh_provenance_and_claim_boundary(self):
        first=m.audit();second=m.audit()
        self.assertEqual(first,second)
        self.assertEqual(first['status'],'PASS_CONDITIONAL_GHF_FUNCTIONAL_ALGEBRA_ONLY')
        self.assertEqual(first['check_count'],first['passing_check_count'])
        self.assertTrue(all(v is False for v in first['admission'].values()))
        self.assertTrue(all(v=='NOT_STARTED' for v in first['method_gate'].values()))
        self.assertEqual(len(first['source_inventory']),3)
        self.assertFalse(first['temperature_integrals_executed'])
        self.assertFalse(first['external_source_vertex_computed'])
        self.assertTrue(all(i['residual_term_count']==0 for i in first['polynomial_identities']))
        for name,digest in first['input_hashes'].items():
            self.assertEqual(m.sha(m.ROOT/name),digest)
            self.assertNotIn('\\',name)
        archived=json.loads((m.ROOT/m.TOPIC/'Result/previews/fluid_core_o2_gapless_functional_first_execution.json').read_text(encoding='utf-8'))
        self.assertEqual(archived['check_count'],186)
        original_inputs={k.replace('\\','/'):v for k,v in archived['input_hashes'].items()}
        source=m.ROOT/m.TOPIC/'Result/previews/core_o2_gapless_functional_first_verifier.py.txt'
        self.assertEqual(m.sha(source),original_inputs[(HERE/'Research_Fluid_Core_O2_Gapless_Functional.py').relative_to(m.ROOT).as_posix()])

    def test_independent_variation_and_extra_rotation(self):
        # Extra exact polynomial point tests implementation, not a new material state.
        a,b,c=F(2,9),F(1,7),F(1,17);coupling=F(3,100);q=[[a,c],[c,b]]
        phi=[F(2,3),F(-3,7)];d=F(-7,13)
        def raw_v(qcoords):
            x,y,z=qcoords
            return coupling*F(1,4)*(x*x+6*x*y+y*y-4*z*z)
        sigma=m.self_energy(q,coupling)
        for coord,i,j,factor in [(0,0,0,2),(1,1,1,2),(2,0,1,1)]:
            step=F(2,13);plus=[a,b,c];minus=[a,b,c];plus[coord]+=step;minus[coord]-=step
            self.assertEqual(factor*(raw_v(plus)-raw_v(minus))/(2*step),sigma[i][j])
        def raw_field(p):
            u,v=p;x=u*u+v*v
            return d*x/2+coupling*x*x/4+coupling*x*(a+b)/2+coupling*(a*u*u+2*c*u*v+b*v*v)+raw_v([a,b,c])
        h=m.mean_residual(phi,q,d,coupling)
        for index in range(2):
            derivatives=[]
            for step in [F(2,13),F(1,13)]:
                plus=list(phi);minus=list(phi);plus[index]+=step;minus[index]-=step
                derivatives.append((raw_field(plus)-raw_field(minus))/(2*step))
            self.assertEqual((4*derivatives[1]-derivatives[0])/3,h[index])
        r=[[F(5,13),F(-12,13)],[F(12,13),F(5,13)]]
        rq=m.multiply(m.multiply(r,q),m.transpose(r));rp=m.matvec(r,phi)
        self.assertTrue(m.equal(m.inverse_block(rp,rq,d,coupling),m.multiply(m.multiply(r,m.inverse_block(phi,q,d,coupling)),m.transpose(r))))
        self.assertTrue(m.equal(m.ward_defect(rp,rq,d,coupling),[0,0]))
        self.assertFalse(m.equal(m.ward_defect(phi,q,d,coupling,0),[0,0]))
        self.assertFalse(m.equal(m.ward_defect(phi,q,d,coupling,F(1,2)),[0,0]))

    def test_original_stationarity_is_not_inherited(self):
        coupling=F(1,100);mu=F(32,25);mass=F(1);ip=F(1,20)
        for im in [F(-1,100),F(0),F(1,100)]:
            x=(mu*mu-mass-coupling*(2*ip+im))/coupling
            y=mass+2*coupling*x+2*coupling*ip
            old_d=coupling*x+coupling*im;new_d=coupling*x-coupling*im
            self.assertEqual(y-new_d-mu*mu,0)
            self.assertEqual(y-old_d-mu*mu,-2*coupling*im)
            old_dyson_residual=new_d-coupling*x-coupling*im
            self.assertEqual(old_dyson_residual,-2*coupling*im)
            self.assertEqual(old_d==new_d,im==0)
            self.assertEqual(mass-mu*mu+coupling*x+coupling*(2*ip+im),0)

    def test_fail_closed_scope_and_stale_source(self):
        canonical=json.loads(m.CONTRACT.read_text(encoding='utf-8'))
        mutations=[('external_source_vertex',True),('physical_heat_current',True)]
        temp_root=m.ROOT/'tmp';temp_root.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=temp_root) as folder:
            self.assertTrue(Path(folder).resolve().is_relative_to(temp_root.resolve()))
            path=Path(folder)/'contract.json'
            for key,value in mutations:
                data=json.loads(json.dumps(canonical));data['admission'][key]=value;path.write_text(json.dumps(data),encoding='utf-8')
                result=m.audit(path)
                self.assertEqual(result['status'],'GAPLESS_FUNCTIONAL_DIAGNOSTIC_FAIL')
                self.assertEqual(result['off_shell_controls'],[])
                self.assertTrue(all(x is False for x in result['admission'].values()))
            data=json.loads(json.dumps(canonical));data['configuration']['lambda_paper_over_lambda_here']=1;path.write_text(json.dumps(data),encoding='utf-8')
            self.assertEqual(m.audit(path)['status'],'GAPLESS_FUNCTIONAL_DIAGNOSTIC_FAIL')
        target=m.ROOT/canonical['source_module_paths'][0];real_sha=m.sha
        with patch.object(m,'sha',side_effect=lambda p:'0'*64 if Path(p)==target else real_sha(p)):
            result=m.audit()
        self.assertEqual(result['status'],'GAPLESS_FUNCTIONAL_DIAGNOSTIC_FAIL')
        self.assertEqual(result['polynomial_identities'],[])
        self.assertEqual(result['source_inventory'],[])

if __name__=='__main__':
    unittest.main()
