"""SD03 independent ensemble, total-current, source-unit and scope regression."""
from fractions import Fraction as F
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('sd03',HERE/'Research_Fluid_Material_Frame_EOS_Handoff.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)


class MaterialFrameTests(unittest.TestCase):
    def test_independent_fixed_pressure_path_and_entropy_derivative(self):
        T,mu,cross=F(1,2),F(1),F(1,4);n=F(9,8);S=F(3,4)
        e=m.eos(T,mu,cross);self.assertEqual(e['cp'],F(40,81))
        mu1=F(-2,3);mu2=F(-80,81)
        def raw_pressure(delta):
            a=T+delta;b=mu+mu1*delta+mu2*delta*delta/2
            return (a*a+b*b)/2+cross*a*b
        for h in [F(1,7),F(1,11)]:
            derivatives=[];curvatures=[]
            for step in [h,h/2]:
                derivatives.append((raw_pressure(step)-raw_pressure(-step))/(2*step))
                curvatures.append((raw_pressure(step)-2*raw_pressure(F(0))+raw_pressure(-step))/step**2)
            self.assertEqual((4*derivatives[1]-derivatives[0])/3,F(0))
            self.assertEqual((4*curvatures[1]-curvatures[0])/3,F(0))
            # Along the independent linear tangent n and S are affine.
            nd=mu1+cross;sd=1+cross*mu1
            difference=((S+h*sd)/(n+h*nd)-(S-h*sd)/(n-h*nd))/(2*h)
            self.assertEqual(T*difference*(n*n-h*h*nd*nd)/(n*n),e['cp'])
        self.assertNotEqual(F(10,27),e['cp'])
        for offset in [F(-3,10),F(2,5)]:
            aprime=1+2*offset*cross+offset*offset;bprime=cross+offset
            self.assertEqual(m.heat_capacity(T,n,S+offset*n,aprime,bprime,F(1)),e['cp'])
        with self.assertRaises(ValueError):
            m.eos(T,-cross*T)

    def test_total_current_reference_and_linear_frame(self):
        T,mu,n,S=F(1,2),F(1),F(9,8),F(3,4);h=F(4,3);w=F(3,2)
        JN=[F(1,7),F(-2,9)];JE=[F(3,5),F(2,7)];u=[F(1,23),F(-1,29)]
        q=[e-h*j for e,j in zip(JE,JN)];entropy=[S*v+(e-mu*j)/T for v,e,j in zip(u,JE,JN)]
        for offset in [F(-3,10),F(2,5)]:
            transformed=[(S+offset*n)*v+(e-(mu-offset*T)*j)/T for v,e,j in zip(u,JE,JN)]
            expected=[s+offset*(n*v+j) for s,v,j in zip(entropy,u,JN)]
            self.assertEqual(transformed,expected)
            self.assertNotEqual(transformed,[s+offset*j for s,j in zip(entropy,JN)])
        shift=[F(1,13),F(-1,17)]
        shiftedN=[j-n*v for j,v in zip(JN,shift)];shiftedE=[e-w*v for e,v in zip(JE,shift)]
        self.assertEqual(m.heat_current(shiftedE,shiftedN,h),q)
        self.assertNotEqual(m.heat_current(shiftedE,shiftedN,mu),m.heat_current(JE,JN,mu))
        eckart_entropy=[S*(v+j/n)+heat/T for v,j,heat in zip(u,JN,q)]
        self.assertEqual(entropy,eckart_entropy)

    def test_independent_covariance_gradient_and_unit_map(self):
        r,T,s,cp=F(3,5),F(1,2),F(2,3),F(40,81);b=F(27,40)
        # Direct derivatives of b=(r/(1-r))*T*s^2/cp, without log-gradient helper.
        db=[T*s*s/(cp*(1-r)**2),r*s*s/((1-r)*cp),2*r*T*s/((1-r)*cp),-r*T*s*s/((1-r)*cp*cp)]
        loading=[F(1,100),F(-1,80),F(1,60),F(-1,70)];d=[F(1,10000),F(1,12000),F(1,14000),F(1,16000)]
        covariance=[[loading[i]*loading[j]+(d[i] if i==j else 0) for j in range(4)] for i in range(4)]
        expected=(sum(a*v for a,v in zip(db,loading))**2+sum(a*a*v for a,v in zip(db,d)))/(4*b*b)
        self.assertEqual(m.relative_speed_variance(r,T,s,cp,covariance),expected)
        self.assertNotEqual(expected,sum(db[i]**2*covariance[i][i] for i in range(4))/(4*b*b))
        E0,Th,mass=F(5),F(11),F(3,7);self.assertEqual(E0/(Th*mass)*cp,F(1400,2673))
        for args in [(F(0),T,s,cp),(F(1),T,s,cp),(r,T,s,F(-1))]:
            with self.assertRaises(ValueError):m.reduced_speed_squared(*args)

    def test_provenance_archived_failure_and_false_scope(self):
        a=m.audit();self.assertEqual(a,m.audit());self.assertEqual(a['status'],'PASS_CONDITIONAL_MATERIAL_FRAME_EOS_HANDOFF_ONLY')
        self.assertEqual(a['check_count'],a['passing_check_count']);self.assertTrue(all(v is None for v in a['physical_scales'].values()))
        self.assertFalse(a['physical_covariance_assigned']);self.assertFalse(a['physical_heat_current_computed']);self.assertFalse(a['new_benchmark_expansion'])
        self.assertTrue(all(v is False for v in a['admission'].values()));self.assertTrue(all(v=='NOT_STARTED' for v in a['method_gate'].values()))
        first=json.loads((m.ROOT/m.TOPIC/'Result/previews/fluid_material_frame_eos_first_failure.json').read_text())
        self.assertEqual(first['status'],'MATERIAL_FRAME_HANDOFF_DIAGNOSTIC_FAIL');self.assertEqual(first['passing_check_count'],154)
        failures=[v['name'] for v in first['checks'] if not v['passed']];self.assertEqual(len(failures),2);self.assertTrue(all(v.startswith('entropy_current_reference_transform:') for v in failures))
        for path,digest in a['input_hashes'].items():self.assertEqual(m.sha(m.ROOT/path),digest)
        canonical=json.loads(m.CONTRACT.read_text());tmp=m.ROOT/'tmp';tmp.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=tmp) as folder:
            self.assertTrue(Path(folder).resolve().is_relative_to(tmp.resolve()));path=Path(folder)/'changed.json'
            for key,value in [('new_benchmark_expansions_authorized',True),('physical_scales',dict(canonical['physical_scales'],E0='5'))]:
                data=dict(canonical);data[key]=value;path.write_text(json.dumps(data));failed=m.audit(path)
                self.assertEqual(failed['status'],'MATERIAL_FRAME_HANDOFF_DIAGNOSTIC_FAIL');self.assertEqual(failed['conditional_controls'],{})
        target=m.ROOT/next(iter(canonical['prelocked_input_hashes']));real=m.sha
        with patch.object(m,'sha',side_effect=lambda p:'0'*64 if Path(p)==target else real(p)):
            failed=m.audit()
        self.assertEqual(failed['status'],'MATERIAL_FRAME_HANDOFF_DIAGNOSTIC_FAIL');self.assertEqual(failed['conditional_controls'],{})


if __name__=='__main__':unittest.main()
