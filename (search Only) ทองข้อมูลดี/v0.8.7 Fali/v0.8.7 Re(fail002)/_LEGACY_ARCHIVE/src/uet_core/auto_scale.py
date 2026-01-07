"""
Smart Auto-scaling utilities for UET solver.
Provides automatic dt calculation and parameter validation.
"""
import numpy as np
from typing import Dict, Any, Tuple, Optional
from dataclasses import dataclass


@dataclass
class AutoScaleResult:
    """Result of auto-scaling calculation."""
    dt_recommended: float
    dt_original: float
    was_adjusted: bool
    warnings: list
    stability_info: dict


def compute_safe_dt(params: dict, dx: float, dt_user: float) -> AutoScaleResult:
    """
    Compute safe timestep based on CFL-like conditions.
    
    Uses soft warnings (informational) rather than blocking.
    User can override with auto_dt: false if needed.
    
    Thresholds based on real-world domain analysis:
    - ratio < 1e6:  Normal, no adjustment
    - ratio 1e6-1e10: May need smaller dt (cosmology/galaxy)
    - ratio 1e10-1e15: Edge case, warning + adjust
    - ratio > 1e15: Very extreme, soft fail recommended
    """
    warnings = []
    stability_info = {}
    
    # Extract parameters
    if 'potC' in params:
        potC = params['potC']
        a = potC.get('a', -1)
        delta = potC.get('delta', 1)
    elif 'pot' in params:
        pot = params['pot']
        a = pot.get('a', -1)
        delta = pot.get('delta', 1)
    else:
        a = params.get('a', -1)
        delta = params.get('delta', 1)
    
    kappa = params.get('kC', params.get('kappa', 0.5))
    beta = params.get('beta', 0.5)
    
    # Ensure positive values for division
    a_abs = max(abs(a), 1e-15)
    delta_safe = max(delta, 1e-15)
    kappa_safe = max(kappa, 1e-15)
    beta_safe = max(abs(beta), 1e-15)
    
    # CFL-like conditions
    dt_potential = 0.5 / a_abs
    dt_diffusion = dx**2 / (4 * kappa_safe)
    dt_coupling = 0.5 / beta_safe
    
    # Ratio analysis with tiered thresholds
    ratio = a_abs / delta_safe
    dt_ratio = dt_potential  # default
    
    stability_info['ratio_a_delta'] = ratio
    stability_info['ratio_tier'] = 'normal'
    
    if ratio > 1e15:
        # Very extreme - soft fail recommended
        dt_ratio = 1e-15  # Minimum possible
        warnings.append(f"EXTREME_RATIO: |a|/δ = {ratio:.1e} (> 1e15) - may not be computable")
        stability_info['ratio_tier'] = 'extreme'
        stability_info['recommendation'] = 'Consider using normalized parameters'
    elif ratio > 1e10:
        # Edge case - adjust with warning
        dt_ratio = 0.01 / ratio
        warnings.append(f"HIGH_RATIO: |a|/δ = {ratio:.1e} (1e10-1e15) - auto-adjusting dt")
        stability_info['ratio_tier'] = 'high'
    elif ratio > 1e6:
        # May need adjustment (cosmology-level)
        dt_ratio = 0.1 / ratio
        warnings.append(f"ELEVATED_RATIO: |a|/δ = {ratio:.1e} (1e6-1e10) - minor adjustment")
        stability_info['ratio_tier'] = 'elevated'
    # else: normal, no adjustment needed
    
    # Minimum safe dt
    dt_safe = min(dt_potential, dt_diffusion, dt_coupling, dt_ratio)
    
    # Cap at reasonable values
    dt_safe = max(dt_safe, 1e-15)  # Don't go below 1e-15
    dt_safe = min(dt_safe, 0.1)    # Don't go above 0.1
    
    stability_info.update({
        'dt_potential': dt_potential,
        'dt_diffusion': dt_diffusion,
        'dt_coupling': dt_coupling,
        'dt_ratio_adjusted': dt_ratio if ratio > 1e6 else None,
        'limiting_factor': 'ratio' if ratio > 1e6 else 'potential'
    })
    
    # Determine if adjustment needed
    was_adjusted = False
    dt_recommended = dt_user
    
    # Only adjust if user's dt is significantly larger than safe dt
    # Use 10x margin for normal cases, stricter for extreme
    margin = 2.0 if ratio > 1e10 else 10.0
    
    if dt_user > dt_safe * margin:
        was_adjusted = True
        dt_recommended = dt_safe
        warnings.append(f"DT_ADJUSTED: {dt_user:.2e} -> {dt_safe:.2e}")
    
    return AutoScaleResult(
        dt_recommended=dt_recommended,
        dt_original=dt_user,
        was_adjusted=was_adjusted,
        warnings=warnings,
        stability_info=stability_info
    )


def validate_parameters(params: dict) -> Tuple[bool, list]:
    """
    Validate parameters for numerical stability.
    Returns (is_valid, warnings_list).
    """
    warnings = []
    is_valid = True
    
    # Extract parameters
    if 'potC' in params:
        potC = params['potC']
        a = potC.get('a', -1)
        delta = potC.get('delta', 1)
    elif 'pot' in params:
        pot = params['pot']
        a = pot.get('a', -1)
        delta = pot.get('delta', 1)
    else:
        a = params.get('a', -1)
        delta = params.get('delta', 1)
    
    kappa = params.get('kC', params.get('kappa', 0.5))
    beta = params.get('beta', 0.5)
    
    # Check delta
    if delta <= 0:
        warnings.append("INVALID: delta <= 0 (unbounded potential)")
        is_valid = False
    elif delta < 1e-10:
        warnings.append(f"WARNING: delta very small ({delta:.2e})")
    
    # Check kappa
    if kappa <= 0:
        warnings.append("INVALID: kappa <= 0 (anti-diffusion)")
        is_valid = False
    elif kappa < 1e-10:
        warnings.append(f"WARNING: kappa very small ({kappa:.2e})")
    
    # Check ratio
    if delta > 0:
        ratio = abs(a) / delta
        if ratio > 1e15:
            warnings.append(f"EXTREME: |a|/delta = {ratio:.2e} (may cause BLOWUP)")
        elif ratio > 1e10:
            warnings.append(f"WARNING: |a|/delta = {ratio:.2e} (may need small dt)")
    
    # Check beta
    if abs(beta) > 1e10:
        warnings.append(f"WARNING: beta very large ({beta:.2e})")
    
    return is_valid, warnings


def get_recommended_T(params: dict, dt: float, target_steps: int = 100) -> float:
    """
    Get recommended simulation time based on parameters and dt.
    """
    return dt * target_steps


def estimate_equilibrium_time(params: dict, L: float) -> float:
    """
    Estimate time needed to reach equilibrium.
    Based on diffusion timescale + potential relaxation.
    """
    kappa = params.get('kC', params.get('kappa', 0.5))
    if 'potC' in params:
        a = abs(params['potC'].get('a', 1))
    else:
        a = abs(params.get('a', 1))
    
    t_diffusion = L**2 / (4 * max(kappa, 1e-10))
    t_potential = 1.0 / max(a, 1e-10)
    
    return max(t_diffusion, t_potential) * 5  # 5x for safety


# Convenience function for quick check
def auto_scale_config(config: dict) -> Tuple[dict, list]:
    """
    Auto-scale a configuration for numerical stability.
    Returns (modified_config, warnings).
    """
    warnings = []
    config = config.copy()
    
    params = config.get('params', {})
    time_cfg = config.get('time', {})
    grid_cfg = config.get('grid', {})
    domain_cfg = config.get('domain', {})
    
    # Get grid spacing
    L = domain_cfg.get('L', 10.0)
    N = grid_cfg.get('N', 32)
    dx = L / N
    
    # Validate parameters
    is_valid, param_warnings = validate_parameters(params)
    warnings.extend(param_warnings)
    
    if not is_valid:
        warnings.append("CONFIG_INVALID: Parameters will cause instability")
        return config, warnings
    
    # Compute safe dt
    dt_user = time_cfg.get('dt', 0.01)
    auto_result = compute_safe_dt(params, dx, dt_user)
    
    warnings.extend(auto_result.warnings)
    
    if auto_result.was_adjusted:
        config['time'] = config.get('time', {}).copy()
        config['time']['dt'] = auto_result.dt_recommended
        config['time']['_dt_original'] = dt_user
        config['time']['_auto_adjusted'] = True
    
    return config, warnings


if __name__ == "__main__":
    # Test
    print("Testing auto-scaling...")
    
    # Test case: RATIO_EXTREME_2
    test_config = {
        'domain': {'L': 10.0},
        'grid': {'N': 32},
        'time': {'dt': 0.01, 'T': 1.0},
        'params': {
            'potC': {'a': -1e10, 'delta': 1e-10},
            'kC': 0.5,
            'beta': 0.5
        }
    }
    
    new_config, warnings = auto_scale_config(test_config)
    
    print(f"Original dt: {test_config['time']['dt']}")
    print(f"Recommended dt: {new_config['time'].get('dt')}")
    print(f"Warnings: {warnings}")
