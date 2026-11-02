"""Independent SD02 pressure/tensor/domain checks; no material benchmarks."""
from fractions import Fraction as F
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('sd02_response', HERE/'Research_Fluid_Core_O2_Stationary_Source_Response.py')
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)


class SourceResponseTests(unittest.TestCase):
    def test_independent_stationary_pressure_and_cross_derivatives(self):
        c = {k: m.rational(v) for k, v in json.loads(m.CONTRACT.read_text()).items()
             if k in ('A', 'B', 'D', 'l', 'q', 'constant', 'source')}
        def independent_pressure(s):
            a, b = s
            v0 = a+2*b+c['l'][0]; v1 = -a+b+c['l'][1]
            held = -2*a*a-a*b-F(3,2)*b*b+c['q'][0]*a+c['q'][1]*b+c['constant']
            return -held+(2*v0*v0-2*v0*v1+3*v1*v1)/10
        for s in [c['source'], [F(3,7), F(-4,9)], [F(0), F(1,5)]]:
            self.assertEqual(m.pressure(c, s), independent_pressure(s))
            a, b = s; v0 = a+2*b+c['l'][0]; v1 = -a+b+c['l'][1]
            self.assertEqual(m.stationary(c, s), [(-2*v0+v1)/5, (v0-3*v1)/5])
        # Independently expanded B^T A^-1 B = [[7,2],[2,7]]/5.
        chi, relaxation = m.response(c)
        self.assertEqual(relaxation, [[F(7,5), F(2,5)], [F(2,5), F(7,5)]])
        self.assertEqual(chi, [[F(27,5), F(7,5)], [F(7,5), F(22,5)]])
        self.assertNotEqual(chi, m.scale(c['D'], -1))

    def test_independent_tensor_coordinate_Hessian(self):
        coupling = F(1,100); full = m.tensor_components(coupling)
        # V2=lambda/4*(a^2+6ab+b^2-4c^2): symmetric Sigma=(2Va,2Vb,Vc).
        for variation in [[[F(2), F(3)], [F(3), F(-1)]], [[F(0), F(1)], [F(1), F(0)]]]:
            a, b, off = variation[0][0], variation[1][1], variation[0][1]
            expected = [[coupling*(a+3*b), -2*coupling*off], [-2*coupling*off, coupling*(3*a+b)]]
            self.assertEqual(m.tensor(variation, coupling), expected)
            contracted = [[sum(full[i][j][k][l]*variation[k][l] for k in range(2) for l in range(2)) for j in range(2)] for i in range(2)]
            self.assertEqual(contracted, expected)
        for i in range(2):
            for j in range(2):
                for k in range(2):
                    for l in range(2):
                        self.assertEqual(full[i][j][k][l], full[k][l][i][j])
                        self.assertEqual(full[i][j][k][l], full[j][i][k][l])

    def test_quotient_compatibility_and_rejection(self):
        a = [[F(2), F(0)], [F(0), F(0)]]; b = [[F(3), F(1)], [F(0), F(0)]]
        derivative = m.quotient_response(a, b, [0])
        self.assertEqual(derivative, [[F(-3,2), F(-1,2)], [F(0), F(0)]])
        self.assertEqual(m.add(m.mm(a, derivative), b), [[0, 0], [0, 0]])
        with self.assertRaises(ValueError):
            m.inverse(a)
        with self.assertRaises(ValueError):
            m.quotient_response(a, [[F(3), F(1)], [F(1), F(0)]], [0])
        with self.assertRaises(ValueError):
            m.quotient_response([[F(2), F(0)], [F(0), F(1)]], b, [0])
        with self.assertRaises(ValueError):
            m.quotient_response(a, b, [1])

    def test_fresh_scope_and_fail_closed_inputs(self):
        first = m.audit(); self.assertEqual(first, m.audit())
        self.assertEqual(first['status'], 'PASS_CONDITIONAL_STATIONARY_SOURCE_DERIVATION_ONLY')
        self.assertEqual(first['check_count'], first['passing_check_count'])
        self.assertFalse(first['interacting_state_computed'])
        self.assertFalse(first['full_pair_space_external_vertex_computed'])
        self.assertFalse(first['new_benchmark_expansion'])
        self.assertTrue(all(v is False for v in first['admission'].values()))
        self.assertTrue(all(v == 'NOT_STARTED' for v in first['method_gate'].values()))
        for path, digest in first['input_hashes'].items():
            self.assertEqual(m.sha(m.ROOT/path), digest)
        canonical = json.loads(m.CONTRACT.read_text())
        tmp = m.ROOT/'tmp'; tmp.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=tmp) as folder:
            self.assertTrue(Path(folder).resolve().is_relative_to(tmp.resolve()))
            path = Path(folder)/'changed.json'
            for key, value in [('new_benchmark_expansions_authorized', True), ('lambda', '1/200')]:
                data = dict(canonical); data[key] = value; path.write_text(json.dumps(data))
                failed = m.audit(path)
                self.assertEqual(failed['status'], 'STATIONARY_SOURCE_DIAGNOSTIC_FAIL')
                self.assertEqual(failed['derived_controls'], {})
        target = m.ROOT/next(iter(canonical['prelocked_input_hashes'])); real = m.sha
        with patch.object(m, 'sha', side_effect=lambda p: '0'*64 if Path(p) == target else real(p)):
            failed = m.audit()
        self.assertEqual(failed['status'], 'STATIONARY_SOURCE_DIAGNOSTIC_FAIL')
        self.assertEqual(failed['derived_controls'], {})


if __name__ == '__main__':
    unittest.main()
