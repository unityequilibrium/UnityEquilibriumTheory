"""Topic 0.24 verification: AI scaling and sparsity audit.

This verifier is intentionally narrow. It checks the topic-local scaling-law and
MoE metadata package, records hashes, computes transparent benchmark diagnostics,
and refuses to treat the result as a proof of AI alignment or ethics.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
import platform
import sys
from datetime import UTC, datetime
from pathlib import Path


def bootstrap_repo() -> Path:
    current = Path(__file__).resolve()
    for parent in [current] + list(current.parents):
        if (parent / "core").is_dir() and (parent / "topics").is_dir() and (parent / "docs" / "STANDARD.md").is_file():
            if str(parent) not in sys.path:
                sys.path.insert(0, str(parent))
            return parent
    raise RuntimeError("Repository root with core/, topics/ and docs/STANDARD.md was not found.")


ROOT = bootstrap_repo()
TOPIC = ROOT / "topics" / "0.24_Artificial_Intelligence"
DATA = TOPIC / "Data"
ARTIFACT = TOPIC / "Result" / "artifacts" / "0_24_artificial_intelligence_verification.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8-sig") as handle:
        return json.load(handle)


def fit_power_exponent(points: list[tuple[float, float]]) -> dict:
    """Fit loss ~= A * N^-alpha in log space."""
    if len(points) < 2:
        raise ValueError("At least two positive finite scaling points are required.")
    points = [(_positive_number(p, "Parameters"), _positive_number(loss, "Test_Loss"))
              for p, loss in points]
    xs = [math.log(p) for p, _ in points]
    ys = [math.log(loss) for _, loss in points]
    x_mean = sum(xs) / len(xs)
    y_mean = sum(ys) / len(ys)
    denom = sum((x - x_mean) ** 2 for x in xs)
    if denom <= 0 or not math.isfinite(denom):
        raise ValueError("Scaling points must contain distinct parameter counts.")
    slope = sum((x - x_mean) * (y - y_mean) for x, y in zip(xs, ys)) / denom
    intercept = y_mean - slope * x_mean
    predictions = [math.exp(intercept + slope * x) for x in xs]
    rmse = math.sqrt(sum((pred - actual) ** 2 for pred, (_, actual) in zip(predictions, points)) / len(points))
    if not all(math.isfinite(value) for value in (slope, intercept, rmse)):
        raise ValueError("Nonfinite scaling-fit result.")
    return {
        "alpha_fit": -slope,
        "intercept_log": intercept,
        "rmse_loss": rmse,
        "point_count": len(points),
    }


def _positive_number(value: object, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{name} must be a positive finite number.")
    try:
        value = float(value)
    except OverflowError as exc:
        raise ValueError(f"{name} must be a positive finite number.") from exc
    if not math.isfinite(value) or value <= 0:
        raise ValueError(f"{name} must be a positive finite number.")
    return value


def read_gpt3_csv(path: Path) -> list[tuple[float, float]]:
    points: list[tuple[float, float]] = []
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames or not {"Parameters", "Test_Loss"}.issubset(reader.fieldnames):
            raise ValueError("Scaling CSV requires Parameters and Test_Loss columns.")
        for row in reader:
            points.append((_positive_number(float(row["Parameters"]), "Parameters"),
                           _positive_number(float(row["Test_Loss"]), "Test_Loss")))
    if not points:
        raise ValueError("Scaling CSV contains no observations.")
    return points


def model_sparsity_table(moe_data: dict) -> list[dict]:
    rows = []
    if not isinstance(moe_data, dict):
        raise ValueError("The model package must be an object.")
    models = moe_data.get("models")
    if not isinstance(models, dict) or not models:
        raise ValueError("A nonempty models table is required.")
    for name, spec in models.items():
        if not isinstance(spec, dict):
            raise ValueError(f"{name}: model specification must be an object.")
        total = _positive_number(spec["Total_Params"], f"{name}.Total_Params")
        active = _positive_number(spec["Active_Params"], f"{name}.Active_Params")
        if active > total:
            raise ValueError(f"{name}: Active_Params exceeds Total_Params.")
        if not isinstance(spec["Type"], str) or not spec["Type"].strip():
            raise ValueError(f"{name}: nonempty model Type is required.")
        rows.append(
            {
                "model": name,
                "type": spec["Type"],
                "total_params": total,
                "active_params": active,
                "active_fraction": active / total,
                "capacity_to_active_ratio": total / active,
                "context_window": spec["Context_Window"],
                "training_tokens": spec["Training_Tokens"],
                "source_note": spec["Note"],
            }
        )
    return rows


def main(*, data_dir: Path | None = None, artifact_path: Path | None = None) -> int:
    # Explicit test/output isolation; defaults still identify the topic's inputs.
    data_dir = DATA if data_dir is None else data_dir
    artifact_path = ARTIFACT if artifact_path is None else artifact_path
    scaling_path = data_dir / "03_Research" / "scaling_laws.json"
    moe_path = data_dir / "03_Research" / "deepseek_moe_data.json"
    gpt3_path = data_dir / "GPT3_Scaling_Laws.csv"

    scaling = load_json(scaling_path)
    moe_data = load_json(moe_path)
    csv_fit = fit_power_exponent(read_gpt3_csv(gpt3_path))

    alpha_n = _positive_number(scaling["constants"]["alpha_N"], "alpha_N")
    alpha_c = _positive_number(scaling["constants"]["alpha_C"], "alpha_C")
    kappa_macro = 0.1
    alpha_kappa_abs_delta = abs(alpha_n - kappa_macro)
    alpha_kappa_relative_delta = alpha_kappa_abs_delta / alpha_n
    csv_alpha_delta = abs(csv_fit["alpha_fit"] - alpha_n)

    sparsity_rows = model_sparsity_table(moe_data)
    dense_rows = [row for row in sparsity_rows if row["type"].lower().startswith("dense")]
    moe_rows = [row for row in sparsity_rows if "moe" in row["type"].lower()]
    if not dense_rows or not moe_rows:
        raise ValueError("Both dense and MoE model rows are required for the declared comparison.")
    min_dense_fraction = min(row["active_fraction"] for row in dense_rows)
    min_moe_fraction = min(row["active_fraction"] for row in moe_rows)

    thresholds = {
        "csv_alpha_delta_max": 0.20,
        "moe_active_fraction_must_be_below_dense": True,
        "alpha_kappa_relative_delta_warn_max": 0.25,
    }

    csv_alpha_ok = csv_alpha_delta <= thresholds["csv_alpha_delta_max"]
    moe_sparsity_ok = min_moe_fraction < min_dense_fraction
    alpha_kappa_ok = alpha_kappa_relative_delta <= thresholds["alpha_kappa_relative_delta_warn_max"]

    status = "PASS" if (csv_alpha_ok and moe_sparsity_ok and alpha_kappa_ok) else "WARN"
    blockers = []
    if not alpha_kappa_ok:
        blockers.append(
            "Kaplan alpha_N is not numerically close enough to the current kappa_macro=0.1 proxy to support a UET constant-identification claim."
        )
    if not csv_alpha_ok:
        blockers.append("Topic-local GPT3 CSV fit does not reproduce the stored alpha_N within the provisional threshold.")
    if not moe_sparsity_ok:
        blockers.append("MoE active-parameter fraction is not below the dense-model active fraction in the topic-local table.")

    artifact = {
        "schema_version": "1.1",
        "topic": "0.24_Artificial_Intelligence",
        "status": status,
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "command": "python topics/0.24_Artificial_Intelligence/Code/03_Research/Research_AI_Scaling_Audit.py",
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
        },
        "claim_class": "C - internal scaling and sparsity benchmark",
        "formula_ids": [
            "AI24-SCALING-POWER-LAW",
            "AI24-UET-KAPPA-ALPHA-CHECK",
            "AI24-MOE-SPARSITY",
            "AI24-CSV-ALPHA-FIT",
        ],
        "inputs": [
            {
                "path": _input_locator(scaling_path),
                "source": scaling.get("source", "unspecified"),
                "sha256": sha256(scaling_path),
            },
            {
                "path": _input_locator(moe_path),
                "source": moe_data.get("source", "unspecified"),
                "sha256": sha256(moe_path),
            },
            {
                "path": _input_locator(gpt3_path),
                "source": "topic-local GPT-3 scaling-law working table",
                "sha256": sha256(gpt3_path),
            },
        ],
        "threshold": thresholds,
        "metrics": {
            "alpha_N_reference": alpha_n,
            "alpha_C_reference": alpha_c,
            "kappa_macro_proxy": kappa_macro,
            "alpha_kappa_abs_delta": alpha_kappa_abs_delta,
            "alpha_kappa_relative_delta": alpha_kappa_relative_delta,
            "csv_alpha_fit": csv_fit["alpha_fit"],
            "csv_alpha_delta": csv_alpha_delta,
            "csv_fit_rmse_loss": csv_fit["rmse_loss"],
            "min_dense_active_fraction": min_dense_fraction,
            "min_moe_active_fraction": min_moe_fraction,
        },
        "model_sparsity": sparsity_rows,
        "checks": {
            "csv_alpha_ok": csv_alpha_ok,
            "moe_sparsity_ok": moe_sparsity_ok,
            "alpha_kappa_ok": alpha_kappa_ok,
        },
        "blockers": blockers,
        "limitations": [
            "This artifact audits topic-local scaling and architecture metadata only.",
            "It does not prove AI alignment, ethics as a physical law, consciousness, or universal intelligence dynamics.",
            "Several model metadata fields remain working-copy or estimated values and require upstream source normalization.",
        ],
    }

    content = json.dumps(artifact, indent=2, sort_keys=True, allow_nan=False)
    artifact_path.parent.mkdir(parents=True, exist_ok=True)
    artifact_path.write_text(content + "\n", encoding="utf-8", newline="\n")

    print("UET AI scaling/sparsity audit")
    print(f"  status: {status}")
    print(f"  alpha_N: {alpha_n:.6f}")
    print(f"  csv alpha fit: {csv_fit['alpha_fit']:.6f}")
    print(f"  |alpha_N - kappa| / alpha_N: {alpha_kappa_relative_delta:.3f}")
    print(f"  min dense active fraction: {min_dense_fraction:.4f}")
    print(f"  min MoE active fraction: {min_moe_fraction:.4f}")
    print(f"  artifact: {artifact_path}")
    return 0


def _input_locator(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return str(path)  # Explicit synthetic/test inputs are not repository data.


if __name__ == "__main__":
    raise SystemExit(main())
