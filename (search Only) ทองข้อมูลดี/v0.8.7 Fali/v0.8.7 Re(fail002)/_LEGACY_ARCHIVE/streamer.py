"""
UET Real-Time Streamer (WebSocket)

Handles high-frequency state streaming for the "LAD Engine".
Uses MsgPack for efficient binary serialization of simulation frames.
"""

import asyncio
import msgpack
import time
import numpy as np
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict
from uet_core.solvers.jax_solver import UETSolver, UETParams
from uet_core.potentials import from_dict

router = APIRouter()

# Store active connections
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

manager = ConnectionManager()

@router.websocket("/ws/simulate")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    
    # Initialize default solver
    solver = UETSolver(N=64, kappa=0.3, beta=0.5, s=0.0)
    
    # Current state - Initialize with "Galaxy" structure for visual impact
    N = 64
    x, y = np.meshgrid(np.linspace(-10, 10, N), np.linspace(-10, 10, N))
    r = np.sqrt(x**2 + y**2)
    
    # Spiral arms / Central mass
    C = 3.0 * np.exp(-r**2 / 5.0)  + 0.5 * np.sin(3*np.arctan2(y, x) + r) * np.exp(-r**2/20.0)
    I = C * 0.8 # Follow C initially
    
    # Add some noise
    C += np.random.randn(N, N) * 0.05
    I += np.random.randn(N, N) * 0.05
    
    t = 0.0
    
    # Simulation loop state
    is_running = False
    
    try:
        while True:
            # Check for incoming messages (non-blocking if possible, but here we await)
            # To make it real-time interactive, we usually race between "receive" and "compute"
            # or just process messages when they arrive.
            
            # Simple approach: Receive parameters -> Update Solver -> Run Step -> Send Result
            # But we want a continuous stream.
            
            try:
                # Use asyncio.wait_for to peek for messages without blocking the loop forever
                # If no message, continue simulation
                if is_running:
                    try:
                        data = await asyncio.wait_for(websocket.receive_text(), timeout=0.001)
                        # Process command
                        import json
                        cmd = json.loads(data)
                        
                        if cmd["type"] == "update_params":
                            # Live parameter update
                            p = cmd["params"]
                            # Re-init solver if N changes, otherwise just update scalars
                            # JAX solver params are in solver.params which is a dataclass
                            # We might need to create a new solver or update the params object
                             # Best to just re-create solver for safety if cheap
                            
                            # Construct potentials if provided
                            pot_C = from_dict(p.get("pot_C", {"type": "quartic"})) if "pot_C" in p else None
                            pot_I = from_dict(p.get("pot_I", {"type": "quartic"})) if "pot_I" in p else None
                            
                            solver = UETSolver(
                                N=p.get("N", 64),
                                kappa=float(p.get("kappa", 0.3)),
                                beta=float(p.get("beta", 0.5)),
                                s=float(p.get("s", 0.0)),
                                dt=float(p.get("dt", 0.02)),
                                pot_C=pot_C,
                                pot_I=pot_I
                            )
                            # Resize fields if N changed (not handled here for simplicity, restart simulation)
                        
                        elif cmd["type"] == "interaction":
                            # "God Mode" touch - add perturbation
                            # Params: x, y (grid coords), radius, intensity
                            ix = int(cmd.get("x", 32))
                            iy = int(cmd.get("y", 32))
                            radius = float(cmd.get("radius", 5.0))
                            val = float(cmd.get("value", 1.0))
                            
                            # Apply Gaussian splat to C field
                            # We need to construct a meshgrid centered at ix, iy
                            # C is a numpy array (N, N)
                            N = solver.params.N
                            
                            # Simple loop for now (or numpy optimized)
                            y_grid, x_grid = np.ogrid[:N, :N]
                            dist_sq = (x_grid - ix)**2 + (y_grid - iy)**2
                            perturbation = val * np.exp(-dist_sq / (2 * radius**2))
                            
                            C += perturbation
                        
                        elif cmd["type"] == "pause":
                            is_running = False
                            
                        elif cmd["type"] == "start":
                            is_running = True
                            
                    except asyncio.TimeoutError:
                        pass # No input, carry on
                else:
                    # If paused, we MUST wait for a message
                    data = await websocket.receive_text()
                    import json
                    cmd = json.loads(data)
                    if cmd["type"] == "start":
                        is_running = True
                    elif cmd["type"] == "update_params":
                        # Allow updates while paused
                        pass

                if is_running:
                    # Run physics step
                    C, I = solver.step(C, I)
                    t += solver.params.dt
                    
                    # Convert to numpy for transmission (if JAX array)
                    if hasattr(C, "block_until_ready"):
                         # Ensure sync if needed, though usually not needed for pure streaming unless measuring perf
                         pass
                         
                    C_np = np.array(C, dtype=np.float32)
                    I_np = np.array(I, dtype=np.float32)
                    
                    # Pack data
                    # Structure: [t, C_bytes, I_bytes]
                    packed = msgpack.packb({
                        "t": t,
                        "C": C_np.tobytes(),
                        "I": I_np.tobytes(),
                        "shape": C_np.shape
                    })
                    
                    await websocket.send_bytes(packed)
                    
                    # Cap FPS
                    await asyncio.sleep(0.016) # ~60 FPS cap

            except Exception as e:
                # Send error
                print(f"Simulation Error: {e}")
                break
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)
