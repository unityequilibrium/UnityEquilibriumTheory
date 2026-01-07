"""
ULTIMATE STRESS TEST: Break the theory at all costs!
ทำยังไงก็ได้ให้มันพัง!
"""
import sys
import numpy as np
import gc
sys.path.insert(0, '.')

from uet_core.solver import run_case, StrictSettings

print('='*80)
print('ULTIMATE STRESS TEST: BREAK IT!')
print('='*80)
print()

# Attack vectors
attacks = [
    # 1. Precision attacks
    {'name': 'TINY_VALUES', 'a': -1e-15, 'delta': 1e-15, 's': 0, 'kappa': 1e-15, 'beta': 1e-15,
     'dt': 0.01, 'T': 1.0, 'N': 32, 'reason': 'Near-zero values'},
    
    {'name': 'HUGE_VALUES', 'a': -1e10, 'delta': 1e10, 's': 0, 'kappa': 1e10, 'beta': 1e10,
     'dt': 0.01, 'T': 0.001, 'N': 32, 'reason': 'Huge values'},
    
    # 2. Ratio attacks
    {'name': 'RATIO_EXTREME_1', 'a': -1e-10, 'delta': 1e10, 's': 0, 'kappa': 0.5, 'beta': 0.5,
     'dt': 0.01, 'T': 1.0, 'N': 32, 'reason': 'delta/a ratio = 1e20'},
    
    {'name': 'RATIO_EXTREME_2', 'a': -1e10, 'delta': 1e-10, 's': 0, 'kappa': 0.5, 'beta': 0.5,
     'dt': 0.01, 'T': 1.0, 'N': 32, 'reason': 'a/delta ratio = 1e20'},
    
    # 3. Stiffness attacks  
    {'name': 'STIFF_1', 'a': -1000000, 'delta': 0.001, 's': 0, 'kappa': 0.001, 'beta': 1000,
     'dt': 0.1, 'T': 1.0, 'N': 32, 'reason': 'Very stiff system'},
    
    {'name': 'STIFF_2', 'a': -0.001, 'delta': 1000000, 's': 0, 'kappa': 1000, 'beta': 0.001,
     'dt': 0.001, 'T': 0.1, 'N': 32, 'reason': 'Inverse stiff'},
    
    # 4. Time attacks
    {'name': 'DT_VS_KAPPA', 'a': -1, 'delta': 1, 's': 0, 'kappa': 1000000, 'beta': 0.5,
     'dt': 1.0, 'T': 10.0, 'N': 32, 'reason': 'dt >> 1/kappa (CFL violation?)'},
    
    {'name': 'MICRO_DT', 'a': -1, 'delta': 1, 's': 0, 'kappa': 0.5, 'beta': 0.5,
     'dt': 1e-10, 'T': 1e-8, 'N': 32, 'reason': 'Microscopic timestep'},
    
    # 5. Grid attacks
    {'name': 'MISMATCH_GRID', 'a': -1, 'delta': 1, 's': 0, 'kappa': 0.0001, 'beta': 0.5,
     'dt': 0.01, 'T': 1.0, 'N': 3, 'reason': 'N=3 (barely a grid)'},
    
    # 6. Asymmetry attacks (different potC vs potI)  
    {'name': 'ASYMMETRIC', 'potC': {'a': -1, 'delta': 1, 's': 0}, 
     'potI': {'a': -1000, 'delta': 0.001, 's': 100}, 'kappa': 0.5, 'beta': 0.5,
     'dt': 0.01, 'T': 1.0, 'N': 32, 'reason': 'Wildly different potentials'},
    
    # 7. Bias attacks
    {'name': 'HUGE_BIAS', 'a': -1, 'delta': 1, 's': 1e10, 'kappa': 0.5, 'beta': 0.5,
     'dt': 0.01, 'T': 1.0, 'N': 32, 'reason': 's = 1e10'},
    
    # 8. Coupling attacks  
    {'name': 'BETA_VS_DELTA', 'a': -1, 'delta': 0.001, 's': 0, 'kappa': 0.5, 'beta': 1e6,
     'dt': 0.01, 'T': 1.0, 'N': 32, 'reason': 'beta >> delta'},
    
    # 9. Edge of validity
    {'name': 'EDGE_DELTA', 'a': -1, 'delta': 1e-15, 's': 0, 'kappa': 0.5, 'beta': 0.5,
     'dt': 0.01, 'T': 1.0, 'N': 32, 'reason': 'delta barely positive'},
    
    {'name': 'EDGE_KAPPA', 'a': -1, 'delta': 1, 's': 0, 'kappa': 1e-15, 'beta': 0.5,
     'dt': 0.01, 'T': 1.0, 'N': 32, 'reason': 'kappa barely positive'},
]

rng = np.random.default_rng(666)
bugs = []
warns = []

for i, tc in enumerate(attacks):
    print(f"[{i+1}/{len(attacks)}] Test: {tc['name']}")
    print(f"  Reason: {tc['reason']}")
    
    # Handle asymmetric case
    if 'potC' in tc:
        potC = tc['potC']
        potI = tc['potI']
    else:
        potC = {'a': tc['a'], 'delta': tc['delta'], 's': tc['s']}
        potI = {'a': tc['a'], 'delta': tc['delta'], 's': tc['s']}
    
    config = {
        'case_id': tc['name'],
        'model': 'C_I',
        'domain': {'L': 10.0, 'dim': 2, 'bc': 'periodic'},
        'grid': {'N': int(tc['N'])},
        'time': {
            'dt': tc['dt'],
            'T': tc['T'],
            'max_steps': 500,
            'tol_abs': 1e-8,
            'tol_rel': 1e-8,
            'backtrack': {'factor': 0.5, 'max_backtracks': 50}
        },
        'params': {
            'potC': {'type': 'quartic', **potC},
            'potI': {'type': 'quartic', **potI},
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
        
        # Check if V < 0 (Omega increased!) - this would be a bug!
        if not np.isnan(Omega0) and not np.isnan(OmegaT):
            V = Omega0 - OmegaT
            omega_increased = V < -1e-6  # Allow tiny tolerance
        else:
            V = float('nan')
            omega_increased = False
        
        backtracks = summary.get('dt_backtracks_total', 0)
        
        print(f"  Status: {status} | V={V:.2e} | BT={backtracks}")
        
        if status == 'FAIL':
            print(f"  *** FAIL! Reasons: {fail_reasons}")
            bugs.append({'name': tc['name'], 'type': 'FAIL', 'reasons': fail_reasons})
        elif omega_increased:
            print(f"  *** BUG! Omega INCREASED! V = {V:.2e}")
            bugs.append({'name': tc['name'], 'type': 'OMEGA_INCREASE', 'V': V})
        elif status == 'WARN':
            warns.append(tc['name'])
            print(f"  [WARN]")
        else:
            print(f"  [OK]")
            
    except Exception as e:
        print(f"  *** CRASH: {str(e)[:50]}")
        bugs.append({'name': tc['name'], 'type': 'CRASH', 'error': str(e)[:100]})
    
    gc.collect()
    print()

print('='*80)
print('FINAL VERDICT')
print('='*80)
print(f"Total attacks: {len(attacks)}")
print(f"BUGS/CRASHES: {len(bugs)}")
print(f"WARNINGS: {len(warns)}")
print()

if bugs:
    print("FOUND ISSUES:")
    for b in bugs:
        print(f"  - {b['name']}: {b['type']}")
    print()
    print("GOTCHA! Theory has weaknesses!")
else:
    print("NO BUGS FOUND :(")
    print("Theory is annoyingly robust...")
    
if warns:
    print(f"\nWarning cases: {warns}")
    
print('='*80)
