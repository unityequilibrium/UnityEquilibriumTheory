#!/usr/bin/env python
"""
UET Simulation Runner API

FastAPI service that runs UET simulations and returns results.
This service is called by the Node.js backend.

Usage:
    uvicorn runner.api:app --host 0.0.0.0 --port 8000
    # or
    python -m runner.api
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
import numpy as np
from pathlib import Path
import json
import uuid
import asyncio
from datetime import datetime

# Add parent to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from uet_core.solvers.jax_solver import UETSolver, UETParams
from runner.streamer import router as streamer_router

app = FastAPI(
    title="UET Simulation Runner",
    description="API for running UET simulations",
    version="1.0.0"
)

# CORS for Node.js backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3001", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include WebSocket router
app.include_router(streamer_router)

# In-memory job store (for demo; use Redis in production)
jobs: Dict[str, Dict[str, Any]] = {}


class SimulationRequest(BaseModel):
    """Request to run a simulation."""
    # Grid parameters
    N: int = 32
    dimensions: int = 2
    
    # Time parameters
    T: float = 2.0
    dt: float = 0.02
    
    # Physical parameters
    kappa: float = 0.3
    beta: float = 0.5
    s: float = 0.0
    
    # Run options
    seed: Optional[int] = None
    n_runs: int = 1
    
    # Metadata
    run_id: Optional[str] = None
    simulation_id: Optional[str] = None


class SimulationResult(BaseModel):
    """Result of a simulation run."""
    run_id: str
    status: str  # PENDING, RUNNING, COMPLETED, FAILED
    
    # Results (only if completed)
    omega_initial: Optional[float] = None
    omega_final: Optional[float] = None
    omega_change: Optional[float] = None
    total_steps: Optional[int] = None
    elapsed_secs: Optional[float] = None
    grade: Optional[str] = None
    
    # Paths
    gif_path: Optional[str] = None
    timeseries_path: Optional[str] = None
    
    # Error (only if failed)
    error: Optional[str] = None
    
    # Timestamps
    created_at: str
    completed_at: Optional[str] = None


def run_simulation_sync(request: SimulationRequest) -> Dict[str, Any]:
    """
    Run a single UET simulation synchronously.
    
    Returns dict with omega values, timing, grade, and time series data.
    """
    import time
    from uet_core.solvers.jax_solver import run_single_with_history
    
    start_time = time.time()
    
    # =========================================================================
    # CFL Stability Condition: dt <= dx² / (2 * kappa)
    # For diffusion-type PDEs, this prevents numerical explosion
    # =========================================================================
    dx = 1.0 / request.N
    dx_sq = dx * dx
    safety_factor = 1.5  # Extra margin for coupled field dynamics
    dt_cfl = dx_sq / (2.0 * max(request.kappa, 0.1) * safety_factor)
    
    # Use the more stable of: user's dt or CFL-computed dt
    dt_stable = min(request.dt, dt_cfl)
    
    # CRITICAL: Ensure dt is never 0 or too small to prevent divide by zero
    dt_min = 0.0001
    if dt_stable < dt_min:
        dt_stable = dt_min
    
    # Log what we're doing (for debugging)
    print(f"[CFL] N={request.N}, kappa={request.kappa}, dx²={dx_sq:.6f}")
    print(f"[CFL] dt_user={request.dt}, dt_cfl={dt_cfl:.6f} -> dt_stable={dt_stable:.6f}")
    
    # Calculate sample interval based on total steps
    n_steps = int(request.T / dt_stable)
    sample_interval = max(1, n_steps // 50)  # ~50 data points max
    
    # Run simulation with history
    history = run_single_with_history(
        seed=request.seed or 42,
        N=request.N,
        T=request.T,
        dt=dt_stable,  # Use CFL-stable dt!
        kappa=request.kappa,
        beta=request.beta,
        s=request.s,
        sample_interval=sample_interval,
    )
    
    elapsed = time.time() - start_time
    
    # =========================================================================
    # Parameter Validation - check if parameters are in stable range
    # Mild issues = cap at WARN, Severe issues = force FAIL
    # =========================================================================
    params_valid = True
    params_severe = False  # Severely unstable = force FAIL
    param_warnings = []
    
    # Mild instability (cap at WARN)
    if request.beta > 0.3:
        params_valid = False
        param_warnings.append(f"β={request.beta} > 0.3")
    if abs(request.s) > 0.5:
        params_valid = False
        param_warnings.append(f"|s|={abs(request.s)} > 0.5")
    if request.kappa > 0.8:
        params_valid = False
        param_warnings.append(f"κ={request.kappa} > 0.8")
    # NOTE: T is simulation time, NOT a physics parameter - don't penalize it
    
    # SEVERE instability (force FAIL) - only physics parameters
    if request.kappa < 0.1 or request.kappa > 2.0:
        params_severe = True
        param_warnings.append(f"κ={request.kappa} SEVERE")
    if request.beta > 1.0 or request.beta < 0:
        params_severe = True
        param_warnings.append(f"β={request.beta} SEVERE")
    if abs(request.s) > 2.0:
        params_severe = True
        param_warnings.append(f"|s|={abs(request.s)} SEVERE")
    # T removed from SEVERE - it's just simulation duration, not physics instability
    
    # =========================================================================
    # Calculate grade based on CONVERGENCE + parameter validation
    # =========================================================================
    omega_initial = history['omega_initial']
    omega_final = history['omega_final']
    omega_history = history['omega_history']

    if omega_initial != 0:
        omega_change = abs(omega_final - omega_initial) / abs(omega_initial)
    else:
        omega_change = 0.0
    
    # Check convergence: compare last 20% of omega values
    n_samples = len(omega_history)
    if n_samples >= 5:
        # Look at the last 20% of the simulation
        tail_start = max(1, int(n_samples * 0.8))
        tail = omega_history[tail_start:]
        
        # Calculate relative variation in the tail
        tail_mean = sum(tail) / len(tail)
        if tail_mean > 0:
            tail_variation = max(abs(v - tail_mean) / tail_mean for v in tail)
        else:
            tail_variation = 0.0
        
        # Check if omega is still exploding (derivative at end)
        if n_samples >= 2:
            last_derivative = abs(omega_history[-1] - omega_history[-2])
            relative_derivative = last_derivative / max(abs(omega_final), 1.0)
        else:
            relative_derivative = 0.0
        
        # GRADE based on convergence:
        # If params are valid, be lenient - just check it didn't explode
        if params_valid:
            # Params are good - just make sure it didn't explode
            if tail_variation < 0.50 and relative_derivative < 0.20:
                grade = "PASS"
            else:
                grade = "FAIL"  # Exploded despite good params
        else:
            # Params are questionable - be stricter about convergence
            if tail_variation < 0.10 and relative_derivative < 0.05:
                grade = "PASS"
            elif tail_variation < 0.30 or relative_derivative < 0.10:
                grade = "WARN"
            else:
                grade = "FAIL"
    else:
        # Not enough samples - if params valid, assume PASS
        if params_valid:
            grade = "PASS"
        elif omega_change < 0.10:
            grade = "WARN"
        else:
            grade = "FAIL"
    
    # CRITICAL: If parameters are SEVERELY invalid, force FAIL
    if params_severe:
        grade = "FAIL"
        print(f"[GRADE] Forced FAIL due to SEVERE params: {param_warnings}")
    # If parameters are mildly invalid, cap grade at WARN (never PASS)
    elif not params_valid and grade == "PASS":
        grade = "WARN"
        print(f"[GRADE] Downgraded PASS->WARN due to unstable params: {param_warnings}")

    
    return {
        "omega_initial": float(omega_initial),
        "omega_final": float(omega_final),
        "omega_change": float(omega_change),
        "total_steps": n_steps,
        "elapsed_secs": float(elapsed),
        "grade": grade,
        "n_runs": 1,
        "params": {
            "N": request.N,
            "T": request.T,
            "dt": request.dt,
            "kappa": request.kappa,
            "beta": request.beta,
            "s": request.s,
        },
        # Time series data
        "history": {
            "times": history['times'],
            "omega": history['omega_history'],
            "energy": history['energy_history'],
            "C_mean": history['C_mean'],
            "I_mean": history['I_mean'],
        },
        # Final field state for 2D visualization
        "field_C": history['C_final'],
        "field_I": history['I_final'],
    }


async def run_simulation_async(run_id: str, request: SimulationRequest):
    """Run simulation in background and update job store."""
    jobs[run_id]["status"] = "RUNNING"
    
    try:
        # Run in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, run_simulation_sync, request)
        
        # Update job
        jobs[run_id].update({
            "status": "COMPLETED",
            "omega_initial": result["omega_initial"],
            "omega_final": result["omega_final"],
            "omega_change": result["omega_change"],
            "total_steps": result["total_steps"],
            "elapsed_secs": result["elapsed_secs"],
            "grade": result["grade"],
            "completed_at": datetime.utcnow().isoformat(),
        })
        
    except Exception as e:
        jobs[run_id].update({
            "status": "FAILED",
            "error": str(e),
            "completed_at": datetime.utcnow().isoformat(),
        })


# ============================================================================
# API Endpoints
# ============================================================================

@app.get("/")
async def root():
    """Health check."""
    return {"status": "ok", "service": "uet-runner", "version": "1.0.0"}


@app.get("/health")
async def health():
    """Health check for Docker/K8s."""
    return {"status": "healthy"}


@app.post("/run", response_model=SimulationResult)
async def run_simulation(request: SimulationRequest, background_tasks: BackgroundTasks):
    """
    Queue a simulation to run in background.
    
    Returns immediately with run_id. Poll /run/{run_id} for results.
    """
    run_id = request.run_id or str(uuid.uuid4())
    
    # Initialize job
    jobs[run_id] = {
        "run_id": run_id,
        "status": "PENDING",
        "created_at": datetime.utcnow().isoformat(),
        "request": request.dict(),
    }
    
    # Queue background task
    background_tasks.add_task(run_simulation_async, run_id, request)
    
    return SimulationResult(
        run_id=run_id,
        status="PENDING",
        created_at=jobs[run_id]["created_at"],
    )


@app.post("/run/sync")
async def run_simulation_synchronous(request: SimulationRequest):
    """
    Run simulation synchronously (blocking).
    
    Use this for quick runs. For long runs, use /run (async).
    """
    try:
        result = run_simulation_sync(request)
        return {
            "status": "COMPLETED",
            "run_id": request.run_id or str(uuid.uuid4()),
            **result,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/run/{run_id}", response_model=SimulationResult)
async def get_run_status(run_id: str):
    """Get status of a queued run."""
    if run_id not in jobs:
        raise HTTPException(status_code=404, detail="Run not found")
    
    job = jobs[run_id]
    return SimulationResult(
        run_id=run_id,
        status=job["status"],
        omega_initial=job.get("omega_initial"),
        omega_final=job.get("omega_final"),
        omega_change=job.get("omega_change"),
        total_steps=job.get("total_steps"),
        elapsed_secs=job.get("elapsed_secs"),
        grade=job.get("grade"),
        error=job.get("error"),
        created_at=job["created_at"],
        completed_at=job.get("completed_at"),
    )


@app.get("/runs")
async def list_runs(limit: int = 50):
    """List recent runs."""
    sorted_jobs = sorted(
        jobs.values(),
        key=lambda x: x["created_at"],
        reverse=True
    )[:limit]
    
    return {"runs": sorted_jobs, "total": len(jobs)}


@app.delete("/run/{run_id}")
async def delete_run(run_id: str):
    """Delete a run from memory."""
    if run_id in jobs:
        del jobs[run_id]
        return {"deleted": True}
    raise HTTPException(status_code=404, detail="Run not found")


# ============================================================================
# Presets / Templates
# ============================================================================

PRESETS = {
    "bias_c": {"beta": 0.5, "s": 0.5, "description": "Positive tilt → C dominance"},
    "bias_i": {"beta": 0.5, "s": -0.5, "description": "Negative tilt → I dominance"},
    "symmetric": {"beta": 0.5, "s": 0.0, "description": "Zero tilt → random outcome"},
    "strong_coupling": {"beta": 0.9, "s": 0.3, "description": "High coupling"},
    "weak_coupling": {"beta": 0.1, "s": 0.3, "description": "Low coupling"},
    "galaxy": {"N": 64, "beta": 0.4, "kappa": 0.3, "T": 5.0, "description": "Galaxy rotation"},
    "coffee": {"N": 32, "beta": 0.5, "kappa": 0.2, "T": 2.0, "description": "Coffee & milk mixing"},
}


@app.get("/presets")
async def get_presets():
    """Get available simulation presets."""
    return {"presets": PRESETS}


@app.post("/run/preset/{preset_name}")
async def run_preset(preset_name: str, background_tasks: BackgroundTasks):
    """Run a preset simulation."""
    if preset_name not in PRESETS:
        raise HTTPException(status_code=404, detail=f"Preset '{preset_name}' not found")
    
    preset = PRESETS[preset_name]
    request = SimulationRequest(**{k: v for k, v in preset.items() if k != "description"})
    
    return await run_simulation(request, background_tasks)


# ============================================================================
# Main
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
