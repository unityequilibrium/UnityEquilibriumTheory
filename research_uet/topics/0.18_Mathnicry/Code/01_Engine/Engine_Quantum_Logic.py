"""
Engine_Quantum_Logic.py - UET Topic 0.18
========================================
Optimized High-Performance Engine for Quantum Unity Simulation.
Supports 17+ qubits (~131,072 states) without building massive matrices.

Architecture:
- State = NumPy array of size 2^N.
- Gate Application = Tensor reshaping + tensordot (Standard High-Perf Method).
"""

import numpy as np
import sys
from pathlib import Path

# --- ROBUST PATH FINDER ---
current_path = Path(__file__).resolve()
root_path = None
for parent in [current_path] + list(current_path.parents):
    if (parent / "research_uet" / "core").exists():
        root_path = parent
        break

if root_path and str(root_path) not in sys.path:
    sys.path.insert(0, str(root_path))


try:
    from research_uet.core.uet_base_solver import UETBaseSolver
    from research_uet.core.uet_parameters import UETParameters, get_params
except ImportError:
    # Fallback: Direct injection of core
    core_path = root_path / "research_uet" / "core"
    if str(core_path) not in sys.path:
        sys.path.append(str(core_path))
    from uet_base_solver import UETBaseSolver
    from uet_parameters import UETParameters, get_params


class QuantumUnityEngine(UETBaseSolver):
    """
    V4.0 Quantum Logic Engine (Production Grade).
    Simulates Unitary Evolution of the Unity Information Field (Psi).

    Features:
    - Tensor-based State Vector (Supports N < 20).
    - Von Neumann Entropy Calculation (Quantifying Entanglement).
    - UET Measurement Axiom (Probabilistic Collapse).
    """

    def __init__(
        self,
        num_qubits=2,
        params: UETParameters = None,
        name="UET_Quantum_Logic",
        **kwargs,
    ):
        if params is None:
            # Quantum Logic operates at the fundamental information limit (Planck)
            params = get_params("planck")

        super().__init__(
            nx=2**num_qubits,  # Flat state size
            ny=1,
            dt=1.0,
            params=params,
            name=name,
            topic="0.18_Quantum_Computing",
            pillar="01_Engine",
            stable_path=True,
        )

        self.num_qubits = num_qubits

        # Global State Vector (Dimensions: 2^N)
        # Normalized Complex Field
        self.state = np.zeros(2**num_qubits, dtype=complex)
        self.state[0] = 1.0 + 0j  # |00...0>

        self.resolution = self.nx
        self.history = []

    def _apply_gate(self, gate_matrix, target):
        """
        Optimized Gate Application:
        Reshapes the state into a tensor and uses tensordot.
        Avoids building full 2^N x 2^N matrices.
        """
        # 1. Reshape state to a N-dimensional tensor (2, 2, ..., 2)
        shape = [2] * self.num_qubits
        state_tensor = self.state.reshape(shape)

        # 2. Apply gate on the target dimension
        # tensordot(gate, tensor, axes=([1], [target]))
        # contract axis 1 of gate matrix with axis 'target' of state tensor
        new_state = np.tensordot(gate_matrix, state_tensor, axes=([1], [target]))

        # 3. Move the new gate axis (index 0) back to the 'target' position
        # Create a permutation used to restore order
        axes = list(
            range(1, self.num_qubits)
        )  # Indices after dot (excluding the new axis at 0)
        axes.insert(target, 0)  # Insert the new axis 0 at the target position

        self.state = np.transpose(new_state, axes).flatten()

    def apply_hadamard(self, target):
        h_matrix = (1 / np.sqrt(2)) * np.array([[1, 1], [1, -1]], dtype=complex)
        self._apply_gate(h_matrix, target)
        self.history.append(f"H({target})")

    def apply_pauli_x(self, target):
        x_matrix = np.array([[0, 1], [1, 0]], dtype=complex)
        self._apply_gate(x_matrix, target)
        self.history.append(f"X({target})")

    def apply_cnot(self, control, target):
        """
        CNOT implementation for large tensors.
        We reshape and flip based on the control axis.
        """
        shape = [2] * self.num_qubits
        state_tensor = self.state.reshape(shape)

        # Slicing: Flip target only where control is 1
        idx_control_1 = [slice(None)] * self.num_qubits
        idx_control_1[control] = 1

        # The target axis index in the slice changes because one dimension is removed
        relative_target = target if target < control else target - 1

        # Reverse target at these indices
        state_tensor[tuple(idx_control_1)] = np.flip(
            state_tensor[tuple(idx_control_1)], axis=relative_target
        )

        self.state = state_tensor.flatten()
        self.history.append(f"CNOT({control}, {target})")

    def measure_collapse(self) -> str:
        """
        Performs a Projective Measurement (Collapse).
        Updates the state vector to the collapsed basis state.
        Returns the binary string of the result.
        """
        probs = np.abs(self.state) ** 2
        # Normalize to avoid float errors
        probs /= np.sum(probs)

        res_idx = np.random.choice(range(len(probs)), p=probs)

        # Collapse State
        self.state = np.zeros_like(self.state)
        self.state[res_idx] = 1.0 + 0j

        bits = format(res_idx, f"0{self.num_qubits}b")
        return bits

    def calculate_entropy(self, subsystem_size: int = 1) -> float:
        """
        Calculates Von Neumann Entropy of the subsystem (Entanglement Metric).
        S = -Tr(rho * ln(rho))

        For pure state, S=0.
        For entangled state, S > 0 for the reduced density matrix.
        """
        # 1. Reshape to Tensor
        # System A: First 'subsystem_size' qubits
        # System B: The rest

        if subsystem_size >= self.num_qubits:
            return 0.0  # Pure state entropy is 0

        dim_A = 2**subsystem_size
        dim_B = 2 ** (self.num_qubits - subsystem_size)

        # Reshape to Matrix [dim_A, dim_B] (Schmidt Decomposition Prep)
        psi_matrix = self.state.reshape((dim_A, dim_B))

        # Reduced Density Matrix rho_A = psi * psi_dagger (Partial Trace over B)
        # SVD is faster: singular values lambda_i of psi_matrix match sqrt(eigenvalues of rho_A)
        # Entropy S = - Sum( lambda_i^2 * log(lambda_i^2) )

        try:
            # Singular Value Decomposition
            # We don't need U or Vh, only s (singular values)
            s = np.linalg.svd(psi_matrix, compute_uv=False)

            # Squared singular values are expectations
            eigenvalues = s**2

            # Filter non-zeros to avoid log(0)
            eigenvalues = eigenvalues[eigenvalues > 1e-12]

            # Von Neumann Entropy
            entropy = -np.sum(eigenvalues * np.log2(eigenvalues))

            return float(entropy)

        except np.linalg.LinAlgError:
            return 0.0

    def summary(self):
        print(f"--- Unity Quantum State (Res: {self.resolution}) ---")
        probs = np.abs(self.state) ** 2
        found_indices = np.where(probs > 0.0001)[0]
        for i in found_indices:
            print(f" |{format(i, f'0{self.num_qubits}b')}>: {probs[i]:.4f}")
        print(f" History: {' -> '.join(self.history)}")

    def save_summary(self, category="01_Engine"):
        """Saves a JSON summary to the Result directory."""
        import json
        from pathlib import Path

        output = {
            "NumQubits": self.num_qubits,
            "Resolution": self.resolution,
            "History": self.history,
            "Probabilities": {
                format(i, f"0{self.num_qubits}b"): float(abs(self.state[i]) ** 2)
                for i in np.where(np.abs(self.state) ** 2 > 0.0001)[0]
            },
        }
        output_path = (
            Path(__file__).resolve().parent.parent.parent
            / "Result"
            / category
            / f"{category}_Engine_Summary.json"
        )
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w") as f:
            json.dump(output, f, indent=4)
        print(f"📁 Summary saved to: {output_path.name}")


# Backward Compatibility
UETQuantumSolver = QuantumUnityEngine
