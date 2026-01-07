"""
FIX ATTEMPTS: Try to make RATIO_EXTREME_2 pass!
"""
import sys
import numpy as np
sys.path.insert(0, '.')

from uet_core.solver import run_case, StrictSettings

print('='*80)
print('FIX ATTEMPTS: Make RATIO_EXTREME_2 pass!')
print('='*80)
print()
print('Original problem:')
print('  a=-1e10, delta=1e-10 => BLOWUP')
print()

rng = np.random.default_rng(999)

fixes = [
    # Fix 1: Tiny dt
    {'name': 'FIX1_tiny_dt', 'dt': 1e-15, 'T': 1e-10, 'max_steps': 1000,
     'desc': 'Use extremely small dt'},
    
    # Fix 2: More backtracks
    {'name': 'FIX2_more_backtrack', 'dt': 0.01, 'T': 1.0, 'max_steps': 500,
     'max_backtracks': 100, 'desc': 'Allow more backtracks'},
    
    # Fix 3: Tighter tolerance
    {'name': 'FIX3_tight_tol', 'dt': 0.001, 'T': 0.1, 'max_steps': 500,
     'tol_abs': 1e-15, 'tol_rel': 1e-15, 'desc': 'Very tight tolerance'},
    
    # Fix 4: Smaller time window
    {'name': 'FIX4_short_T', 'dt': 1e-12, 'T': 1e-10, 'max_steps': 1000,
     'desc': 'Very short simulation'},
    
    # Fix 5: Scale down a
    {'name': 'FIX5_scale_a', 'a': -1e5, 'delta': 1e-10, 'dt': 0.01, 'T': 1.0,
     'desc': 'Reduce |a| from 1e10 to 1e5'},
    
    # Fix 6: Scale up delta
    {'name': 'FIX6_scale_delta', 'a': -1e10, 'delta': 1e5, 'dt': 0.01, 'T': 1.0,
     'desc': 'Increase delta from 1e-10 to 1e5'},
    
    # Fix 7: Both scaled to same order
    {'name': 'FIX7_balance', 'a': -1e3, 'delta': 1e3, 'dt': 0.01, 'T': 1.0,
     'desc': 'Balance |a| ~ delta'},
    
    # Fix 8: Aggressive backtrack
    {'name': 'FIX8_aggressive_bt', 'dt': 0.01, 'T': 1.0, 'max_steps': 500,
     'backtrack_factor': 0.1, 'max_backtracks': 200, 
     'desc': 'Very aggressive backtracking'},
]

for fix in fixes:
    print(f"Trying: {fix['name']}")
    print(f"  Strategy: {fix['desc']}")
    
    a = fix.get('a', -1e10)
    delta = fix.get('delta', 1e-10)
    dt = fix.get('dt', 0.01)
    T = fix.get('T', 1.0)
    max_steps = fix.get('max_steps', 500)
    tol_abs = fix.get('tol_abs', 1e-8)
    tol_rel = fix.get('tol_rel', 1e-8)
    backtrack_factor = fix.get('backtrack_factor', 0.5)
    max_backtracks = fix.get('max_backtracks', 50)
    
    config = {
        'case_id': fix['name'],
        'model': 'C_I',
        'domain': {'L': 10.0, 'dim': 2, 'bc': 'periodic'},
        'grid': {'N': 32},
        'time': {
            'dt': dt,
            'T': T,
            'max_steps': max_steps,
            'tol_abs': tol_abs,
            'tol_rel': tol_rel,
            'backtrack': {'factor': backtrack_factor, 'max_backtracks': max_backtracks}
        },
        'params': {
            'potC': {'type': 'quartic', 'a': a, 'delta': delta, 's': 0},
            'potI': {'type': 'quartic', 'a': a, 'delta': delta, 's': 0},
            'beta': 0.5,
            'kC': 0.5,
            'kI': 0.5,
            'MC': 1.0,
            'MI': 1.0
        }
    }
    
    try:
        # Custom settings
        settings = StrictSettings()
        settings.max_backtracks = max_backtracks
        settings.backtrack_factor = backtrack_factor
        settings.tol_abs = tol_abs
        settings.tol_rel = tol_rel
        
        summary, _ = run_case(config, rng, settings)
        status = summary.get('status', 'UNKNOWN')
        fail_reasons = summary.get('fail_reasons', [])
        Omega0 = summary.get('Omega0', 0)
        OmegaT = summary.get('OmegaT', 0)
        V = Omega0 - OmegaT if not (np.isnan(Omega0) or np.isnan(OmegaT)) else float('nan')
        bt = summary.get('dt_backtracks_total', 0)
        
        if status == 'PASS':
            print(f"  *** SUCCESS! Status: PASS, V={V:.2e} ***")
        elif status == 'WARN':
            print(f"  Partial: WARN, V={V:.2e}, BT={bt}")
        else:
            print(f"  Still FAIL: {fail_reasons}")
            
    except Exception as e:
        print(f"  ERROR: {str(e)[:60]}")
    
    print()

print('='*80)
print('SUMMARY')
print('='*80)
print("If any FIX shows PASS with original (a=-1e10, delta=1e-10):")
print("  => It's purely numerical, can be fixed with better solver")
print()
print("If only scaled versions (FIX5-7) pass:")
print("  => Need parameter constraints in theory")
print('='*80)
