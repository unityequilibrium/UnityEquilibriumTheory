# Central METRICS registry for UET Harness
# Each entry defines a metric name, its unit (simulation native or SI) and a human‑readable label.
# The `record` helper writes a JSON file ``metrics.json`` inside a run directory,
# guaranteeing that every metric is stored with its unit and label consistently.

import json
from pathlib import Path
from typing import Any, Dict

# ---------------------------------------------------------------------------
# METRICS dictionary – extend as new metrics are introduced in the code base.
# ---------------------------------------------------------------------------
METRICS: Dict[str, Dict[str, str]] = {
    "Omega0": {"unit": "sim", "label": "Ω₀"},
    "OmegaT": {"unit": "sim", "label": "Ω_T"},
    "dt": {"unit": "s", "label": "Δt"},
    "dx": {"unit": "m", "label": "Δx"},
    "energy": {"unit": "sim", "label": "E"},
    "com": {"unit": "sim", "label": "COM"},
    "max_dt": {"unit": "s", "label": "max Δt"},
    # Add additional metrics here as needed
}

def _load_metrics_file(run_dir: Path) -> Dict[str, Any]:
    """Load (or create) the metrics.json file for a given run directory."""
    metrics_path = run_dir / "metrics.json"
    if metrics_path.is_file():
        try:
            return json.loads(metrics_path.read_text())
        except json.JSONDecodeError:
            # Corrupted file – start fresh
            return {}
    return {}

def record(metric_name: str, value: Any, run_dir: str) -> None:
    """Record a metric value for the current run.

    Parameters
    ----------
    metric_name: str
        The key defined in the METRICS dictionary.
    value: Any
        The numeric (or JSON‑serialisable) value to store.
    run_dir: str
        Absolute path to the run folder where ``metrics.json`` lives.
    """
    if metric_name not in METRICS:
        raise KeyError(f"Metric '{metric_name}' is not defined in METRICS registry")

    run_path = Path(run_dir)
    if not run_path.is_dir():
        raise FileNotFoundError(f"Run directory '{run_dir}' does not exist")

    data = _load_metrics_file(run_path)
    entry = {
        "value": value,
        "unit": METRICS[metric_name]["unit"],
        "label": METRICS[metric_name]["label"]
    }
    data[metric_name] = entry
    (run_path / "metrics.json").write_text(json.dumps(data, indent=2))

# ---------------------------------------------------------------------------
# Convenience wrapper used by other modules (solver, auto_scale, validation)
# ---------------------------------------------------------------------------
def record_metric(name: str, value: Any, run_dir: str) -> None:
    """Alias kept for backward compatibility – forwards to :func:`record`."""
    record(name, value, run_dir)
