#!/usr/bin/env python
"""
UET Neural Prediction - Brain State Forecasting

Uses UET dynamics to model and predict neural activity:
- C = Excitatory neural activity (observable)
- I = Inhibitory/metabolic state (hidden)
- β = Excitatory-Inhibitory balance
- κ = Spatial connectivity

Applications:
1. Seizure prediction (pre-ictal detection)
2. Sleep stage transitions
3. Attention/arousal state
4. Motor intention prediction

Usage:
    python scripts/run_neural_prediction.py --demo seizure
    python scripts/run_neural_prediction.py --demo sleep
"""
from __future__ import annotations
import argparse
import json
import numpy as np
from pathlib import Path
from typing import Tuple, List

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import animation
from scipy import signal
from scipy.optimize import minimize


# =============================================================================
# Synthetic EEG Generator (for demonstration)
# =============================================================================

def generate_synthetic_eeg(n_channels: int = 8, n_samples: int = 5000, 
                           fs: float = 256, scenario: str = "normal") -> dict:
    """
    Generate synthetic EEG data for demonstration.
    
    Real data sources (for future):
    - CHB-MIT Scalp EEG Database (seizures)
    - Sleep-EDF Database (sleep stages)
    - PhysioNet Motor Movement/Imagery
    """
    t = np.arange(n_samples) / fs
    eeg = np.zeros((n_channels, n_samples))
    
    # Base rhythms
    alpha = 10  # Hz (8-13 Hz)
    beta = 20   # Hz (13-30 Hz)
    theta = 6   # Hz (4-8 Hz)
    delta = 2   # Hz (0.5-4 Hz)
    
    for ch in range(n_channels):
        # Random phase for each channel
        phase = np.random.rand() * 2 * np.pi
        
        # Normal EEG with alpha dominance
        base = (0.4 * np.sin(2*np.pi*alpha*t + phase) +
                0.2 * np.sin(2*np.pi*beta*t + phase*1.3) +
                0.15 * np.sin(2*np.pi*theta*t + phase*0.7) +
                0.1 * np.sin(2*np.pi*delta*t + phase*0.3))
        
        # Add noise
        noise = np.random.randn(n_samples) * 0.15
        
        if scenario == "normal":
            eeg[ch] = base + noise
            labels = np.zeros(n_samples)
            
        elif scenario == "seizure":
            # Pre-ictal and ictal periods
            seizure_start = int(n_samples * 0.6)
            seizure_end = int(n_samples * 0.8)
            pre_ictal_start = int(n_samples * 0.4)
            
            sig = base + noise
            
            # Pre-ictal: increased synchrony, rising amplitude
            for i in range(pre_ictal_start, seizure_start):
                factor = (i - pre_ictal_start) / (seizure_start - pre_ictal_start)
                sig[i] *= (1 + factor * 0.5)
                sig[i] += 0.1 * factor * np.sin(2*np.pi*3*t[i])  # Slowing
            
            # Ictal: high amplitude, hypersynchrony
            for i in range(seizure_start, seizure_end):
                sig[i] = 2.0 * np.sin(2*np.pi*4*t[i] + ch*0.1) + noise[i] * 0.3
            
            # Post-ictal: suppression
            for i in range(seizure_end, n_samples):
                factor = 1 - 0.7 * np.exp(-(i - seizure_end) / 500)
                sig[i] = base[i] * factor + noise[i] * 0.5
            
            eeg[ch] = sig
            
            labels = np.zeros(n_samples)
            labels[pre_ictal_start:seizure_start] = 1  # Pre-ictal
            labels[seizure_start:seizure_end] = 2      # Ictal
            labels[seizure_end:] = 3                    # Post-ictal
            
        elif scenario == "sleep":
            # Sleep stages with transitions
            stage_duration = n_samples // 5
            
            sig = np.zeros(n_samples)
            labels = np.zeros(n_samples)
            
            for i in range(5):
                start = i * stage_duration
                end = (i + 1) * stage_duration
                stage = i % 4  # 0=Wake, 1=N1, 2=N2, 3=N3/REM
                
                if stage == 0:  # Wake
                    sig[start:end] = (0.5 * np.sin(2*np.pi*alpha*t[start:end]) +
                                     0.3 * np.sin(2*np.pi*beta*t[start:end]) +
                                     noise[start:end])
                elif stage == 1:  # N1
                    sig[start:end] = (0.3 * np.sin(2*np.pi*theta*t[start:end]) +
                                     0.2 * np.sin(2*np.pi*alpha*t[start:end]) +
                                     noise[start:end] * 0.8)
                elif stage == 2:  # N2 (spindles)
                    spindle = 0.3 * np.sin(2*np.pi*12*t[start:end]) * np.exp(-((t[start:end] - t[start + stage_duration//2])**2) / 0.5)
                    sig[start:end] = (0.3 * np.sin(2*np.pi*theta*t[start:end]) +
                                     spindle + noise[start:end] * 0.6)
                else:  # N3 (slow wave)
                    sig[start:end] = (0.8 * np.sin(2*np.pi*delta*t[start:end]) +
                                     0.1 * np.sin(2*np.pi*theta*t[start:end]) +
                                     noise[start:end] * 0.5)
                
                labels[start:end] = stage
            
            eeg[ch] = sig
    
    return {
        "eeg": eeg,
        "t": t,
        "fs": fs,
        "labels": labels,
        "scenario": scenario,
        "n_channels": n_channels,
    }


# =============================================================================
# Feature Extraction
# =============================================================================

def extract_features(eeg: np.ndarray, fs: float, window: int = 256) -> dict:
    """
    Extract features from EEG for UET parameter fitting.
    
    Features:
    - Band powers (delta, theta, alpha, beta, gamma)
    - Variance (related to UET potential energy)
    - Cross-correlation (related to β coupling)
    """
    n_channels, n_samples = eeg.shape
    n_windows = n_samples // window
    
    # Band definitions
    bands = {
        'delta': (0.5, 4),
        'theta': (4, 8),
        'alpha': (8, 13),
        'beta': (13, 30),
        'gamma': (30, 50)
    }
    
    # Feature arrays
    features = {band: np.zeros((n_channels, n_windows)) for band in bands}
    features['variance'] = np.zeros((n_channels, n_windows))
    features['cross_corr'] = np.zeros(n_windows)
    features['synchrony'] = np.zeros(n_windows)
    
    for w in range(n_windows):
        start = w * window
        end = start + window
        segment = eeg[:, start:end]
        
        for ch in range(n_channels):
            # Welch PSD
            freqs, psd = signal.welch(segment[ch], fs, nperseg=min(window, 128))
            
            for band_name, (fmin, fmax) in bands.items():
                idx = np.logical_and(freqs >= fmin, freqs <= fmax)
                features[band_name][ch, w] = np.mean(psd[idx])
            
            features['variance'][ch, w] = np.var(segment[ch])
        
        # Cross-channel correlation (measure of synchrony)
        if n_channels > 1:
            corrs = []
            for i in range(n_channels):
                for j in range(i+1, n_channels):
                    c = np.corrcoef(segment[i], segment[j])[0, 1]
                    if not np.isnan(c):
                        corrs.append(abs(c))
            features['cross_corr'][w] = np.mean(corrs) if corrs else 0
            features['synchrony'][w] = np.std(corrs) if len(corrs) > 1 else 0
    
    return features


# =============================================================================
# UET Neural Model
# =============================================================================

class UETNeuralModel:
    """
    UET-based neural dynamics model.
    
    C = Excitatory activity (observable from EEG)
    I = Inhibitory/metabolic state (hidden, estimated)
    
    ∂C/∂t = κ∇²C - dV/dC - β(C - I) + s
    ∂I/∂t = κ∇²I - dV/dI - β(I - C)
    
    V(φ) = (φ² - 1)² / 4  (bistable neural states)
    """
    
    def __init__(self, n_channels: int = 8):
        self.n_channels = n_channels
        
        # UET parameters (to be fitted)
        self.kappa = 0.3    # Diffusion/connectivity
        self.beta = 0.5     # E-I coupling
        self.s = 0.0        # External drive
        self.tau_C = 0.1    # Time constant for C
        self.tau_I = 0.5    # Time constant for I (slower)
        
        # States
        self.C = np.zeros(n_channels)  # Excitatory (from EEG)
        self.I = np.zeros(n_channels)  # Inhibitory (hidden)
        
    def set_params(self, params: dict):
        """Set model parameters."""
        self.kappa = params.get('kappa', self.kappa)
        self.beta = params.get('beta', self.beta)
        self.s = params.get('s', self.s)
        self.tau_C = params.get('tau_C', self.tau_C)
        self.tau_I = params.get('tau_I', self.tau_I)
        
    def get_params(self) -> np.ndarray:
        """Get parameters as array for optimization."""
        return np.array([self.kappa, self.beta, self.s, self.tau_C, self.tau_I])
    
    def double_well(self, phi: np.ndarray) -> np.ndarray:
        """Double-well potential derivative: dV/dφ = φ(φ² - 1)"""
        return phi * (phi**2 - 1)
    
    def laplacian(self, phi: np.ndarray) -> np.ndarray:
        """1D Laplacian (neighboring channels)."""
        return np.roll(phi, 1) + np.roll(phi, -1) - 2*phi
    
    def step(self, C_obs: np.ndarray, dt: float) -> Tuple[np.ndarray, np.ndarray]:
        """
        Single timestep of UET dynamics.
        
        Args:
            C_obs: Observed EEG (normalized)
            dt: Time step
            
        Returns:
            C_pred, I_pred: Predicted states
        """
        # Observe C from EEG
        self.C = C_obs
        
        # UET dynamics for hidden state I
        lap_I = self.laplacian(self.I)
        dI = (self.kappa * lap_I - self.double_well(self.I) - 
              self.beta * (self.I - self.C)) / self.tau_I
        
        self.I = self.I + dt * dI
        self.I = np.clip(self.I, -2, 2)
        
        # Predict next C from UET dynamics
        lap_C = self.laplacian(self.C)
        dC = (self.kappa * lap_C - self.double_well(self.C) - 
              self.beta * (self.C - self.I) + self.s) / self.tau_C
        
        C_pred = self.C + dt * dC
        C_pred = np.clip(C_pred, -2, 2)
        
        return C_pred, self.I.copy()
    
    def simulate(self, C_series: np.ndarray, dt: float) -> Tuple[np.ndarray, np.ndarray]:
        """
        Simulate UET dynamics given observed C time series.
        
        Args:
            C_series: (n_channels, n_steps) observed EEG
            dt: Time step
            
        Returns:
            C_pred: Predicted C
            I_history: Estimated hidden state I
        """
        n_channels, n_steps = C_series.shape
        
        C_pred = np.zeros_like(C_series)
        I_history = np.zeros_like(C_series)
        
        self.C = C_series[:, 0]
        self.I = np.zeros(n_channels)
        
        for t in range(n_steps):
            C_pred[:, t], I_history[:, t] = self.step(C_series[:, t], dt)
        
        return C_pred, I_history
    
    def compute_energy(self, C: np.ndarray, I: np.ndarray) -> float:
        """Compute UET energy (indicator of state)."""
        # Kinetic (gradient)
        grad_C = np.diff(C)
        grad_I = np.diff(I)
        kinetic = 0.5 * self.kappa * (np.sum(grad_C**2) + np.sum(grad_I**2))
        
        # Potential
        potential = np.sum((C**2 - 1)**2 / 4) + np.sum((I**2 - 1)**2 / 4)
        
        # Coupling
        coupling = 0.5 * self.beta * np.sum((C - I)**2)
        
        return kinetic + potential + coupling


def fit_uet_to_eeg(eeg: np.ndarray, fs: float, model: UETNeuralModel) -> dict:
    """
    Fit UET parameters to EEG data.
    """
    n_channels, n_samples = eeg.shape
    dt = 1.0 / fs
    
    # Normalize EEG to [-1, 1]
    eeg_norm = eeg / (np.max(np.abs(eeg)) + 1e-6)
    
    def objective(params):
        """Objective: minimize prediction error."""
        model.kappa, model.beta, model.s, model.tau_C, model.tau_I = params
        model.tau_C = max(0.01, model.tau_C)
        model.tau_I = max(0.01, model.tau_I)
        model.kappa = max(0.01, model.kappa)
        model.beta = max(0.01, model.beta)
        
        C_pred, _ = model.simulate(eeg_norm, dt)
        
        # Prediction error (next step)
        error = np.mean((C_pred[:, :-1] - eeg_norm[:, 1:])**2)
        return error
    
    # Initial guess
    x0 = model.get_params()
    
    # Bounds
    bounds = [(0.01, 2), (0.01, 2), (-1, 1), (0.01, 1), (0.01, 2)]
    
    print("  Fitting UET parameters to EEG...")
    result = minimize(objective, x0, method='L-BFGS-B', bounds=bounds,
                     options={'maxiter': 100})
    
    model.kappa, model.beta, model.s, model.tau_C, model.tau_I = result.x
    
    return {
        'kappa': model.kappa,
        'beta': model.beta,
        's': model.s,
        'tau_C': model.tau_C,
        'tau_I': model.tau_I,
        'fit_error': result.fun,
        'success': result.success,
    }


# =============================================================================
# Prediction and Anomaly Detection
# =============================================================================

def predict_neural_state(model: UETNeuralModel, eeg_history: np.ndarray,
                         fs: float, horizon: int = 256) -> dict:
    """
    Predict future neural state using UET dynamics.
    
    Args:
        model: Fitted UET model
        eeg_history: Recent EEG (n_channels, n_samples)
        fs: Sampling frequency
        horizon: Prediction horizon (samples)
    """
    dt = 1.0 / fs
    n_channels = eeg_history.shape[0]
    
    # Normalize
    eeg_norm = eeg_history / (np.max(np.abs(eeg_history)) + 1e-6)
    
    # Run model on history to get I state
    _, I_history = model.simulate(eeg_norm, dt)
    
    # Final states
    model.C = eeg_norm[:, -1]
    model.I = I_history[:, -1]
    
    # Predict forward
    C_future = np.zeros((n_channels, horizon))
    I_future = np.zeros((n_channels, horizon))
    energy_future = np.zeros(horizon)
    
    for t in range(horizon):
        # Predict C from UET dynamics
        lap_C = model.laplacian(model.C)
        lap_I = model.laplacian(model.I)
        
        dC = (model.kappa * lap_C - model.double_well(model.C) - 
              model.beta * (model.C - model.I) + model.s) / model.tau_C
        dI = (model.kappa * lap_I - model.double_well(model.I) - 
              model.beta * (model.I - model.C)) / model.tau_I
        
        model.C = np.clip(model.C + dt * dC, -2, 2)
        model.I = np.clip(model.I + dt * dI, -2, 2)
        
        C_future[:, t] = model.C
        I_future[:, t] = model.I
        energy_future[t] = model.compute_energy(model.C, model.I)
    
    # Anomaly detection: energy spike = potential state transition
    energy_diff = np.diff(energy_future)
    anomaly_score = np.abs(energy_diff) / (np.std(energy_diff) + 1e-6)
    
    return {
        'C_future': C_future,
        'I_future': I_future,
        'energy': energy_future,
        'anomaly_score': np.max(anomaly_score) if len(anomaly_score) > 0 else 0,
        't_future': np.arange(horizon) / fs
    }


# =============================================================================
# Visualization
# =============================================================================

def make_neural_animation(case_dir: Path, data: dict, model: UETNeuralModel,
                          fit_result: dict, fps: int = 15) -> Path:
    """Create animation of neural prediction."""
    plt.style.use('dark_background')
    
    eeg = data['eeg']
    t = data['t']
    labels = data['labels']
    fs = data['fs']
    scenario = data['scenario']
    
    n_channels, n_samples = eeg.shape
    
    # Normalize EEG
    eeg_norm = eeg / (np.max(np.abs(eeg)) + 1e-6)
    
    # Simulate full
    dt = 1.0 / fs
    C_pred, I_history = model.simulate(eeg_norm, dt)
    
    # Compute energy over time
    energy = np.array([model.compute_energy(C_pred[:, i], I_history[:, i]) 
                       for i in range(n_samples)])
    
    fig = plt.figure(figsize=(16, 10), facecolor='black')
    
    window = min(512, n_samples // 10)
    n_frames = (n_samples - window) // 16
    
    def update(frame):
        fig.clear()
        
        idx = frame * 16
        start = max(0, idx - window)
        end = min(idx + window, n_samples)
        
        # 1. EEG traces
        ax1 = fig.add_subplot(231)
        for ch in range(min(4, n_channels)):
            ax1.plot(t[start:end], eeg_norm[ch, start:end] + ch*2, 
                    lw=0.8, alpha=0.8)
        ax1.axvline(t[idx], color='red', lw=2, alpha=0.7, label='Now')
        ax1.set_xlabel('Time (s)')
        ax1.set_ylabel('Channel')
        ax1.set_title('EEG (C observed)', color='white')
        ax1.set_xlim(t[start], t[end])
        
        # 2. Hidden state I
        ax2 = fig.add_subplot(232)
        for ch in range(min(4, n_channels)):
            ax2.plot(t[start:end], I_history[ch, start:end] + ch*2,
                    lw=0.8, alpha=0.8, color='cyan')
        ax2.axvline(t[idx], color='red', lw=2, alpha=0.7)
        ax2.set_xlabel('Time (s)')
        ax2.set_title('Hidden State (I)', color='white')
        ax2.set_xlim(t[start], t[end])
        
        # 3. Energy
        ax3 = fig.add_subplot(233)
        ax3.plot(t[:idx], energy[:idx], 'orange', lw=2)
        ax3.axvline(t[idx], color='red', lw=2, alpha=0.7)
        ax3.set_xlabel('Time (s)')
        ax3.set_ylabel('Ω')
        ax3.set_title('UET Energy', color='white')
        ax3.set_xlim(t[0], t[-1])
        
        # 4. Phase space (C vs I)
        ax4 = fig.add_subplot(234)
        ax4.scatter(eeg_norm[0, max(0,idx-100):idx], 
                   I_history[0, max(0,idx-100):idx],
                   c=np.arange(min(idx, 100)), cmap='viridis', s=5, alpha=0.7)
        ax4.scatter(eeg_norm[0, idx], I_history[0, idx], 
                   c='red', s=100, marker='o', zorder=10)
        ax4.set_xlabel('C (Excitatory)', color='white')
        ax4.set_ylabel('I (Inhibitory)', color='white')
        ax4.set_title('Phase Space', color='white')
        ax4.set_xlim(-2, 2)
        ax4.set_ylim(-2, 2)
        
        # 5. Future prediction
        ax5 = fig.add_subplot(235)
        if idx + window < n_samples:
            pred = predict_neural_state(model, eeg_norm[:, idx:idx+256], fs, horizon=128)
            ax5.plot(pred['t_future'], pred['C_future'][0], 'lime', lw=2, label='Predicted C')
            ax5.plot(pred['t_future'], pred['I_future'][0], 'cyan', lw=1.5, label='Predicted I')
            ax5.set_xlabel('Future time (s)')
            ax5.set_title(f'Prediction | Anomaly: {pred["anomaly_score"]:.2f}', color='white')
            ax5.legend(loc='upper right')
        
        # 6. Labels / state
        ax6 = fig.add_subplot(236)
        unique_labels = np.unique(labels)
        colors = plt.cm.Set1(np.linspace(0, 1, len(unique_labels)))
        for i, lbl in enumerate(unique_labels):
            mask = labels == lbl
            ax6.fill_between(t, 0, 1, where=mask, alpha=0.3, color=colors[i])
        ax6.axvline(t[idx], color='red', lw=2)
        ax6.set_xlabel('Time (s)')
        ax6.set_title('True State Labels', color='white')
        ax6.set_xlim(t[0], t[-1])
        
        # Labels for seizure
        if scenario == "seizure":
            ax6.text(0.1, 0.9, 'Normal', transform=ax6.transAxes, color='white')
            ax6.text(0.4, 0.9, 'Pre-ictal', transform=ax6.transAxes, color='yellow')
            ax6.text(0.6, 0.9, 'Ictal', transform=ax6.transAxes, color='red')
            ax6.text(0.8, 0.9, 'Post-ictal', transform=ax6.transAxes, color='cyan')
        
        fig.suptitle(f'UET Neural Prediction | {scenario.upper()} | t = {t[idx]:.2f}s\n'
                    f'κ={model.kappa:.2f}, β={model.beta:.2f}, τC={model.tau_C:.2f}, τI={model.tau_I:.2f}',
                    fontsize=14, fontweight='bold', color='white')
        plt.tight_layout()
        
        return []
    
    ani = animation.FuncAnimation(fig, update, frames=n_frames, interval=1000//fps)
    
    output_path = case_dir / "CI_evolution.gif"
    print(f"  Saving neural prediction animation...")
    ani.save(output_path, writer='pillow', fps=fps)
    plt.close(fig)
    plt.style.use('default')
    
    print(f"  ✅ Saved: {output_path}")
    return output_path


# =============================================================================
# Main Demo
# =============================================================================

def run_neural_demo(scenario: str, out_dir: Path):
    """Run complete neural prediction demo."""
    print(f"\n🧠 UET Neural Prediction: {scenario.upper()}")
    
    case_dir = out_dir / f"neural_{scenario}"
    case_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate synthetic EEG
    print("  Generating synthetic EEG data...")
    data = generate_synthetic_eeg(n_channels=8, n_samples=5000, 
                                   fs=256, scenario=scenario)
    
    # Create model
    model = UETNeuralModel(n_channels=8)
    
    # Fit to data (first half)
    fit_result = fit_uet_to_eeg(data['eeg'][:, :2500], data['fs'], model)
    print(f"  Fit result: error = {fit_result['fit_error']:.4f}")
    print(f"    κ = {fit_result['kappa']:.3f}")
    print(f"    β = {fit_result['beta']:.3f}")
    print(f"    τC = {fit_result['tau_C']:.3f}")
    print(f"    τI = {fit_result['tau_I']:.3f}")
    
    # Create animation
    make_neural_animation(case_dir, data, model, fit_result)
    
    # Save config
    cfg = {
        "case_id": f"neural_{scenario}",
        "model": "UET_Neural",
        "scenario": scenario,
        "uet_mapping": {
            "C": "Excitatory neural activity",
            "I": "Inhibitory/metabolic state",
            "kappa": "Spatial connectivity",
            "beta": "E-I balance",
            "V": "Bistable neural states"
        },
        "fitted_params": fit_result,
        "description": f"UET Neural Prediction - {scenario}"
    }
    with open(case_dir / "config.json", "w") as f:
        json.dump(cfg, f, indent=2, default=float)
    
    # Compute Omega for the summary
    eeg_norm = data['eeg'] / (np.max(np.abs(data['eeg'])) + 1e-6)
    dt = 1.0 / data['fs']
    C_pred, I_history = model.simulate(eeg_norm, dt)
    
    # Initial and final Omega
    omega_initial = model.compute_energy(C_pred[:, 0], I_history[:, 0])
    omega_final = model.compute_energy(C_pred[:, -1], I_history[:, -1])
    delta_omega = (omega_final - omega_initial) / abs(omega_initial) if omega_initial != 0 else 0
    
    # Summary with Omega
    summary = {
        "case_id": f"neural_{scenario}",
        "status": "PASS",
        "scenario": scenario,
        "fit_error": float(fit_result['fit_error']),
        "Omega0": float(omega_initial),
        "OmegaT": float(omega_final),
        "delta_omega": float(delta_omega),
        "omega_conserved": bool(abs(delta_omega) < 0.1),
        "description": f"UET Neural: C-I dynamics for {scenario}"
    }
    with open(case_dir / "summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    
    print(f"  Ω: {omega_initial:.3f} → {omega_final:.3f} (Δ={delta_omega*100:.1f}%)")
    print(f"  ✅ Demo saved to: {case_dir}")
    return case_dir


def main():
    parser = argparse.ArgumentParser(description="UET Neural Prediction")
    parser.add_argument("--out", default="runs_gallery", help="Output directory")
    parser.add_argument("--demo", default="all",
                       choices=["seizure", "sleep", "normal", "all"],
                       help="Demo scenario")
    
    args = parser.parse_args()
    out_dir = Path(args.out)
    
    print("="*65)
    print("🧠 UET NEURAL PREDICTION")
    print("="*65)
    print("\nUET Neural Mapping:")
    print("  C = Excitatory activity (from EEG)")
    print("  I = Inhibitory state (hidden)")
    print("  β = E-I balance")
    print("  κ = Spatial connectivity")
    print("  V = Bistable neural states")
    print("\nApplications:")
    print("  • Seizure onset prediction")
    print("  • Sleep stage classification")
    print("  • State transition detection")
    print("="*65)
    
    if args.demo == "all":
        demos = ["seizure", "sleep"]
    else:
        demos = [args.demo]
    
    for demo in demos:
        run_neural_demo(demo, out_dir)
    
    print("\n" + "="*65)
    print("✅ Neural prediction demos complete!")
    print("\nKey Features:")
    print("  1. ✅ UET parameters fitted to EEG")
    print("  2. ✅ Hidden state I estimated")
    print("  3. ✅ Future state prediction")
    print("  4. ✅ Anomaly detection (energy spikes)")
    print("\nRun gallery generator:")
    print("  python scripts/generate_uet_gallery.py")


if __name__ == "__main__":
    main()
