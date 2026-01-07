"""
FIND THE BUG: Try to break valid parameters!
หา case ที่ควรถูกแต่ดันพัง
"""
import sys
import numpy as np
sys.path.insert(0, '.')

from uet_core.solver import run_case, StrictSettings

print('='*80)
print('BUG HUNTER: Find cases that SHOULD work but FAIL!')
print('='*80)
print()

rng = np.random.default_rng(999)

# Edge cases with VALID params that might still break
test_cases = [
    # Extreme but valid
    {'name': 'EXTREME_a', 'a': -1000, 'delta': 1, 's': 0, 'kappa': 0.5, 'beta': 0.5,
     'dt': 0.01, 'T': 1.0, 'N': 32, 'reason': 'a very negative'},
    
    {'name': 'EXTREME_delta_high', 'a': -1, 'delta': 1000, 's': 0, 'kappa': 0.5, 'beta': 0.5,
     'dt': 0.01, 'T': 1.0, 'N': 32, 'reason': 'delta very large'},
    
    {'name': 'EXTREME_s', 'a': -1, 'delta': 1, 's': 100, 'kappa': 0.5, 'beta': 0.5,
     'dt': 0.01, 'T': 1.0, 'N': 32, 'reason': 's (bias) very large'},
    
    {'name': 'TINY_kappa', 'a': -1, 'delta': 1, 's': 0, 'kappa': 0.0001, 'beta': 0.5,
     'dt': 0.01, 'T': 1.0, 'N': 32, 'reason': 'kappa almost zero'},
    
    {'name': 'HUGE_beta', 'a': -1, 'delta': 1, 's': 0, 'kappa': 0.5, 'beta': 100,
     'dt': 0.01, 'T': 1.0, 'N': 32, 'reason': 'beta very large coupling'},
    
    # Time-related edge cases
    {'name': 'TINY_dt', 'a': -1, 'delta': 1, 's': 0, 'kappa': 0.5, 'beta': 0.5,
     'dt': 0.0001, 'T': 0.1, 'N': 32, 'reason': 'very small timestep'},
    
    {'name': 'LARGE_dt', 'a': -1, 'delta': 1, 's': 0, 'kappa': 0.5, 'beta': 0.5,
     'dt': 0.5, 'T': 2.0, 'N': 32, 'reason': 'very large timestep'},
    
    {'name': 'LONG_T', 'a': -1, 'delta': 1, 's': 0, 'kappa': 0.5, 'beta': 0.5,
     'dt': 0.01, 'T': 100.0, 'N': 32, 'reason': 'very long simulation'},
    
    # Grid-related
    {'name': 'TINY_N', 'a': -1, 'delta': 1, 's': 0, 'kappa': 0.5, 'beta': 0.5,
     'dt': 0.01, 'T': 1.0, 'N': 4, 'reason': 'very coarse grid'},
    
    {'name': 'LARGE_N', 'a': -1, 'delta': 1, 's': 0, 'kappa': 0.5, 'beta': 0.5,
     'dt': 0.01, 'T': 1.0, 'N': 128, 'reason': 'fine grid'},
    
    # Combination attacks
    {'name': 'CHAOS_1', 'a': -100, 'delta': 100, 's': 50, 'kappa': 0.01, 'beta': 50,
     'dt': 0.1, 'T': 5.0, 'N': 16, 'reason': 'chaos combination 1'},
    
    {'name': 'CHAOS_2', 'a': -0.001, 'delta': 0.001, 's': 0, 'kappa': 100, 'beta': 0.001,
     'dt': 0.001, 'T': 0.1, 'N': 64, 'reason': 'chaos combination 2'},
]

fail_count = 0
pass_count = 0
bugs_found = []

for tc in test_cases:
    print(f"Test: {tc['name']}")
    print(f"  Reason: {tc['reason']}")
    print(f"  Params: a={tc['a']}, delta={tc['delta']}, s={tc['s']}")
    print(f"  Params: kappa={tc['kappa']}, beta={tc['beta']}")
    print(f"  Time: dt={tc['dt']}, T={tc['T']}, N={tc['N']}")
    print()
    print(f"  EXPECTED: PASS (all params are valid!)")
    print()
    
    config = {
        'case_id': tc['name'],
        'model': 'C_I',
        'domain': {'L': 10.0, 'dim': 2, 'bc': 'periodic'},
        'grid': {'N': int(tc['N'])},
        'time': {
            'dt': tc['dt'],
            'T': tc['T'],
            'max_steps': 2000,
            'tol_abs': 1e-8,
            'tol_rel': 1e-8,
            'backtrack': {'factor': 0.5, 'max_backtracks': 20}
        },
        'params': {
            'potC': {'type': 'quartic', 'a': tc['a'], 'delta': tc['delta'], 's': tc['s']},
            'potI': {'type': 'quartic', 'a': tc['a'], 'delta': tc['delta'], 's': tc['s']},
            'beta': tc['beta'],
            'kC': tc['kappa'],
            'kI': tc['kappa'],
            'MC': 1.0,
            'MI': 1.0
        }
    }
    
    try:
        summary, _ = run_case(config, rng, StrictSettings())
        status = summary.get('status', 'UNKNOWN')
        fail_reasons = summary.get('fail_reasons', [])
        Omega0 = summary.get('Omega0', 0)
        OmegaT = summary.get('OmegaT', 0)
        V = Omega0 - OmegaT if not (np.isnan(Omega0) or np.isnan(OmegaT)) else float('nan')
        backtracks = summary.get('dt_backtracks_total', 0)
        
        print(f"  ACTUAL:")
        print(f"    Status: {status}")
        print(f"    Fail reasons: {fail_reasons}")
        print(f"    Omega0 = {Omega0:.2e}")
        print(f"    OmegaT = {OmegaT:.2e}")
        print(f"    Value = {V:.2e}")
        print(f"    Backtracks: {backtracks}")
        
        if status == 'FAIL':
            print(f"    *** BUG FOUND! Should PASS but FAILED! ***")
            fail_count += 1
            bugs_found.append(tc['name'])
        elif status == 'WARN':
            print(f"    [WARN] Partial issue")
            pass_count += 1
        else:
            print(f"    [OK] Passed as expected")
            pass_count += 1
            
    except Exception as e:
        print(f"  ACTUAL:")
        print(f"    ERROR: {e}")
        print(f"    *** BUG FOUND! Should PASS but CRASHED! ***")
        fail_count += 1
        bugs_found.append(tc['name'])
    
    print()
    print('-'*80)
    print()

print('='*80)
print('SUMMARY')
print('='*80)
print(f"Passed as expected: {pass_count}/{len(test_cases)}")
print(f"BUGS FOUND (should pass but failed): {fail_count}/{len(test_cases)}")
print()
if bugs_found:
    print("BUG CASES:")
    for bug in bugs_found:
        print(f"  - {bug}")
    print()
    print("GOTCHA! Found potential issues with valid params!")
else:
    print("No bugs found :( Theory seems too robust!")
print('='*80)
