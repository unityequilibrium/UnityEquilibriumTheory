"""
UET Glass Box System
====================
The complete Nervous System of UET.
"""

import numpy as np
import json
import time
import pandas as pd
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional, Any, Tuple
from pathlib import Path


# =============================================================================
# 0. PATH MANAGER
# =============================================================================


class UETPathManager:
    _ROOT = None

    @staticmethod
    def get_root() -> Path:
        if UETPathManager._ROOT:
            return UETPathManager._ROOT
        
        # 1. Check current working directory (Priority for Source Code)
        cwd = Path.cwd()
        if (cwd / "docs").exists():
            UETPathManager._ROOT = cwd / "docs"
            return UETPathManager._ROOT
            
        # 2. Check parent directories of CWD
        for parent in cwd.parents:
            if (parent / "docs").exists():
                UETPathManager._ROOT = parent / "docs"
                return UETPathManager._ROOT

        # 3. Fallback to __file__ resolution (for installed pkgs)
        current = Path(__file__).resolve()
        for _ in range(6):
            if (current / "core").exists() and current.name == "docs":
                UETPathManager._ROOT = current
                return UETPathManager._ROOT
            current = current.parent
            
        raise FileNotFoundError("Could not find 'docs' root directory.")

    TOPIC_MAP = {
        "0.1": "0.1_Galaxy_Rotation_Problem",
        "0.2": "0.2_Black_Hole_Physics",
        "0.3": "0.3_Cosmology_Hubble_Tension",
        "0.4": "0.4_Superconductivity_Superfluids",
        "0.5": "0.5_Nuclear_Binding_Hadrons",
        "0.6": "0.6_Electroweak_Physics",
        "0.7": "0.7_Neutrino_Physics",
        "0.8": "0.8_Muon_g2_Anomaly",
        "0.9": "0.9_Quantum_Nonlocality",
        "0.10": "0.10_Fluid_Dynamics_Chaos",
        "0.11": "0.11_Phase_Transitions",
        "0.12": "0.12_Vacuum_Energy_Casimir",
        "0.13": "0.13_Thermodynamic_Bridge",
        "0.14": "0.14_Complex_Systems",
        "0.15": "0.15_Cluster_Dynamics",
        "0.16": "0.16_Heavy_Nuclei",
        "0.17": "0.17_Mass_Generation",
        "0.18": "0.18_Mathnicry",
        "0.19": "0.19_Gravity_GR",
        "0.20": "0.20_Atomic_Physics",
        "0.21": "0.21_Yang_Mills_Mass_Gap",
        "0.22": "0.22_Biophysics_Origin_of_Life",
        "0.23": "0.23_Unity_Scale_Link",
        "0.24": "0.24_Artificial_Intelligence",
        "0.25": "0.25_Strategy_Power_Economics",
        "0.26": "0.26_Cosmic_Dynamic_Frame",
        "0.27": "0.27_Cold_Light_Hologram",
        "0.28": "0.28_Material_Synthesis",
        "0.29": "0.29_Ocean_Recovery",
        "0.30": "0.30_Mega_Flora_Biotech",
        "0.31": "0.31_SpaceTime_Propulsion",
        "0.34": "0.34_Information_Centric_Nanofabrication",
    }

    @staticmethod
    def get_canonical_topic(topic_id: str) -> str:
        if "_" in topic_id and topic_id in UETPathManager.TOPIC_MAP.values():
            return topic_id
        clean_id = topic_id.split("_")[0]
        return UETPathManager.TOPIC_MAP.get(clean_id, topic_id)

    @staticmethod
    def get_result_dir(
        topic_id: str,
        experiment_name: str,
        pillar: str = "01_Engine",
        stable: bool = True,
        use_archive: bool = False,
        category: str = "log",  # [NEW] Options: 'log', 'showcase', 'figures'
    ) -> Path:
        root = UETPathManager.get_root()
        topic_full = UETPathManager.get_canonical_topic(topic_id)
        topic_dir = root / "topics" / topic_full

        # Base Result Path
        result_base = topic_dir / "Result"

        if category == "showcase":
            # 01_Showcase: Flat directory for high-quality assets
            target_path = result_base / "01_Showcase"
        elif category == "figures":
            # 02_Figures: Flat directory for scientific plots
            target_path = result_base / "02_Figures"
        else:
            # Default "log": Timestamped run folders in _Logs
            # Note: We move logs to _Logs subfolder to reduce clutter
            timestamp = f"{int(time.time())}"
            run_id = f"{timestamp}_{experiment_name}"

            # If use_archive is explicitly requested (old logic), honor it, but mapped to _Archive
            if use_archive:
                target_path = topic_dir / "_Archive" / run_id
            else:
                # Standard Logs go to Result/_Logs/RunID
                target_path = result_base / "_Logs" / run_id

        target_path.mkdir(parents=True, exist_ok=True)
        return target_path

    @staticmethod
    def get_doc_dir(topic_id: str, pillar: str = "02_Proof") -> Path:
        root = UETPathManager.get_root()
        topic_full = UETPathManager.get_canonical_topic(topic_id)
        doc_path = root / "topics" / topic_full / "Doc"
        doc_path.mkdir(parents=True, exist_ok=True)
        return doc_path


@dataclass
class ValidationResult:
    is_valid: bool
    status: str
    reason: str
    metrics: Dict[str, float]


class UETValidator:
    C_MAX_FAIL = 50.0
    DT_COLLAPSE_FAIL = 1e-6
    DT_COLLAPSE_WARN = 1e-3
    DOMEGA_TOL_ABS = 1e-12
    DOMEGA_TOL_REL = 1e-8
    DOMEGA_WARN_REL = 1e-10

    @staticmethod
    def check_state(
        C: np.ndarray,
        I: Optional[np.ndarray] = None,
        step_info: Optional[Dict[str, float]] = None,
    ) -> ValidationResult:
        reasons, metrics, status = [], {}, "PASS"
        if not np.isfinite(C).all():
            return ValidationResult(False, "FAIL", "nan_inf_detected_in_C", {})
        max_c = np.max(np.abs(C))
        metrics["max_abs_C"] = float(max_c)
        if max_c > UETValidator.C_MAX_FAIL:
            return ValidationResult(False, "FAIL", f"field_blowup(max_C={max_c:.2f})", metrics)
        if step_info:
            dOmega = step_info.get("dOmega", float("-inf"))
            Omega = step_info.get("Omega", 1.0)
            metrics["dOmega"] = dOmega
            scale = max(1.0, abs(Omega))
            tol = UETValidator.DOMEGA_TOL_REL * scale + UETValidator.DOMEGA_TOL_ABS
            if dOmega > tol:
                return ValidationResult(
                    False, "FAIL", f"energy_violation(dOmega={dOmega:.2e})", metrics
                )
        return ValidationResult(True, status, "|".join(reasons), metrics)


@dataclass
class UETStepData:
    step: int
    time: float
    omega: float
    kinetic: float
    potential: float
    entropy: float
    gradient_norm: float
    max_density: float = 0.0
    min_density: float = 0.0
    is_stable: bool = True
    extra_metrics: Dict[str, float] = None

    def to_dict(self):
        base = asdict(self)
        if self.extra_metrics:
            base.update(self.extra_metrics)
        del base["extra_metrics"]
        return base


class UETMetricLogger:
    VALID_CATEGORIES = ["log", "showcase", "figures"]

    def __init__(
        self,
        simulation_name: str,
        output_dir: Optional[str] = None,
        flat_mode: bool = False,
        category: str = "log",  # [NEW]
        topic_id: str = "General",  # [NEW] Optional topic binding
    ):
        # Validate category parameter
        if category not in self.VALID_CATEGORIES:
            raise ValueError(
                f"Invalid category '{category}'. "
                f"Valid categories: {', '.join(self.VALID_CATEGORIES)}"
            )

        # Warn about legacy patterns
        if output_dir and not topic_id or topic_id == "General":
            print(
                f"⚠️ [UETMetricLogger] Using 'output_dir' directly is deprecated. "
                f"Use 'topic_id' and 'category' parameters instead."
            )
            print(f"   Example: UETMetricLogger('Simulation', topic_id='0.1', category='showcase')")

        if not output_dir and topic_id == "General":
            print(
                f"⚠️ [UETMetricLogger] No 'topic_id' provided. "
                f"Using legacy fallback. Please specify 'topic_id' for proper output organization."
            )

        self.simulation_name, self.flat_mode = simulation_name, flat_mode
        self.category = category
        root = UETPathManager.get_root()

        # Resolution Strategy:
        # 1. If output_dir is Explicit -> Use it.
        # 2. If topic_id provided -> Use UETPathManager logic (Best Practice).
        # 3. Fallback -> data_logs

        if output_dir:
            base_path = Path(output_dir)
            if not base_path.is_absolute():
                base_path = root / output_dir
            self.run_dir = base_path
            # Explicit output_dir given, defaulting run_id to dir name
            self.run_id = self.run_dir.name

        elif topic_id != "General":
            # Use the new standard
            self.run_dir = UETPathManager.get_result_dir(
                topic_id=topic_id, experiment_name=simulation_name, category=category
            )
            # Standard output dir, using directory name for run_id
            self.run_id = self.run_dir.name
        else:
            # Legacy Fallback
            base_path = root.parent / "data_logs"
            self.timestamp_str = f"{int(time.time())}"
            self.run_id = (
                simulation_name if self.flat_mode else f"{self.timestamp_str}_{simulation_name}"
            )
            self.run_dir = base_path if self.flat_mode else base_path / self.run_id

        self.run_dir.mkdir(parents=True, exist_ok=True)
        self._init_state()

    def _init_state(self):
        self.history, self.snapshot_interval = [], 100
        self.start_time, self.step_count = time.time(), 0
        self.metadata = {}
        self.csv_file = self.run_dir / "timeseries.csv"
        self._csv_handle, self._csv_writer = None, None
        print(f"🔍 UET Glass Box: Logging (Streaming) to '{self.run_dir}'")

    def log_step(
        self,
        step: int,
        time_val: float,
        omega: float,
        kinetic: float = 0.0,
        potential: float = 0.0,
        entropy: float = 0.0,
        gradient: float = 0.0,
        field_c: Optional[np.ndarray] = None,
        **kwargs,
    ):
        clean_kwargs = {
            k: v for k, v in kwargs.items() if not isinstance(v, (np.ndarray, list, dict))
        }
        max_c = float(np.max(field_c)) if field_c is not None else 0.0
        min_c = float(np.min(field_c)) if field_c is not None else 0.0
        stable = not (np.isnan(omega) or np.isinf(omega))
        data = UETStepData(
            step=step,
            time=time_val,
            omega=float(omega),
            kinetic=float(kinetic),
            potential=float(potential),
            entropy=float(entropy),
            gradient_norm=float(gradient),
            max_density=max_c,
            min_density=min_c,
            is_stable=stable,
            extra_metrics=clean_kwargs,
        )
        self._stream_to_csv(data)
        if self.step_count % self.snapshot_interval == 0:
            self.history.append(data)
            if len(self.history) > 500:
                self.history.pop(0)
        self.step_count += 1
        dOmega = (self.history[-1].omega - self.history[-2].omega) if len(self.history) > 1 else 0.0
        scale = max(1.0, abs(omega))
        # SOC MODELS require much higher tolerance for valid discrete jumps (Topic 0.14)
        is_discrete = "0.14" in str(self.run_dir)
        tol_multiplier = 1e12 if is_discrete else 1.0
        tol = (UETValidator.DOMEGA_TOL_REL * scale + UETValidator.DOMEGA_TOL_ABS) * tol_multiplier
        if dOmega > tol:
            print(f"⚠️ [UET Safety] Energy Violation: dOmega={dOmega:.2e}")
        if not stable:
            print(f"❌ CRITICAL FAILURE at step {step}: Instability!")
            self.close()

    def _stream_to_csv(self, data: UETStepData):
        import csv

        row = data.to_dict()
        if self._csv_handle is None:
            self._csv_handle = open(self.csv_file, "w", newline="")
            self._csv_writer = csv.DictWriter(self._csv_handle, fieldnames=row.keys())
            self._csv_writer.writeheader()
        self._csv_writer.writerow(row)
        if self.step_count % 100 == 0:
            self._csv_handle.flush()

    def close(self):
        if self._csv_handle:
            self._csv_handle.close()
            self._csv_handle = None

    def set_metadata(self, params: Dict[str, Any]):
        self.metadata = params
        with open(self.run_dir / "config.json", "w") as f:
            json.dump(params, f, indent=2)

    def save_report(self) -> str:
        self.close()
        summary_file, step_final = self.run_dir / "summary.json", (
            self.history[-1] if self.history else None
        )
        report = {
            "run_id": self.run_id,
            "simulation": self.simulation_name,
            "status": ("COMPLETED" if (step_final and step_final.is_stable) else "FAILED"),
            "timestamp": time.ctime(self.start_time),
            "duration_seconds": time.time() - self.start_time,
            "total_steps": self.step_count,
            "metadata": self.metadata,
            "final_state": step_final.to_dict() if step_final else None,
        }
        with open(summary_file, "w") as f:
            json.dump(report, f, indent=2)
        print(f"📄 Report Saved: {self.run_dir}")
        return str(self.run_dir)


class UETLedger:
    def __init__(self, log_dir: str = "data_logs"):
        self.log_dir = Path(log_dir)
        self.ledger_file = self.log_dir / "ledger.csv"

    def rebuild(self) -> pd.DataFrame:
        rows = []
        if not self.log_dir.exists():
            return pd.DataFrame()
        for summary_path in self.log_dir.rglob("summary.json"):
            try:
                with open(summary_path, "r") as f:
                    data = json.load(f)
                row = {
                    "run_id": data.get("run_id"),
                    "path": str(summary_path.parent),
                    "simulation": data.get("simulation"),
                    "status": data.get("status"),
                }
                rows.append(row)
            except Exception:
                pass
        if rows:
            df = pd.DataFrame(rows)
            df.to_csv(self.ledger_file, index=False)
            return df
        return pd.DataFrame()
