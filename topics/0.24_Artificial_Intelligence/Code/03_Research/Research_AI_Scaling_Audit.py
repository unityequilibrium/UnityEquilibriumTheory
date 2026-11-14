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
        if (parent / "docs").exists() and (parent / "docs" / "core").exists():
            if str(parent) not in sys.path:
                sys.path.insert(0, str(parent))
            return parent
    raise RuntimeError("Repository root with docs/core was not found.")


ROOT = bootstrap_repo()
TOPIC = ROOT / "docs" / "topics" / "0.24_Artificial_Intelligence"
DATA = TOPIC / "Data"
ARTIFACT = TOPIC / "Result" / "artifacts" / "0_24_artificial_intelligence_verification.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def fit_power_exponent(points: list[tuple[float, float]]) -> dict:
    """Fit loss ~= A * N^-alpha in log space."""
    xs = [math.log(p) for p, _ in points]
    ys = [math.log(loss) for _, loss in points]
    x_mean = sum(xs) / len(xs)
    y_mean = sum(ys) / len(ys)
    denom = sum((x - x_mean) ** 2 for x in xs)
    slope = sum((x - x_mean) * (y - y_mean) for x, y in zip(xs, ys)) / denom
    intercept = y_mean - slope * x_mean
    predictions = [math.exp(intercept + slope * x) for x in xs]
    rmse = math.sqrt(sum((pred - actual) ** 2 for pred, (_, actual) in zip(predictions, points)) / len(points))
    return {
        "alpha_fit": -slope,
        "intercept_log": intercept,
        "rmse_loss": rmse,
        "point_count": len(points),
    }


def read_gpt3_csv(path: Path) -> list[tuple[float, float]]:
    points: list[tuple[float, float]] = []
    with path.open("r", encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            points.append((float(row["Parameters"]), float(row["Test_Loss"])))
    return points


def model_sparsity_table(moe_data: dict) -> list[dict]:
    rows = []
    for name, spec in moe_data["models"].items():
        total = float(spec["Total_Params"])
        active = float(spec["Active_Params"])
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


def main() -> int:
    scaling_path = DATA / "03_Research" / "scaling_laws.json"
    moe_path = DATA / "03_Research" / "deepseek_moe_data.json"
    gpt3_path = DATA / "GPT3_Scaling_Laws.csv"

    scaling = load_json(scaling_path)
    moe_data = load_json(moe_path)
    csv_fit = fit_power_exponent(read_gpt3_csv(gpt3_path))

    alpha_n = float(scaling["constants"]["alpha_N"])
    alpha_c = float(scaling["constants"]["alpha_C"])
    kappa_macro = 0.1
    alpha_kappa_abs_delta = abs(alpha_n - kappa_macro)
    alpha_kappa_relative_delta = alpha_kappa_abs_delta / alpha_n
    csv_alpha_delta = abs(csv_fit["alpha_fit"] - alpha_n)

    sparsity_rows = model_sparsity_table(moe_data)
    dense_rows = [row for row in sparsity_rows if row["type"].lower().startswith("dense")]
    moe_rows = [row for row in sparsity_rows if "moe" in row["type"].lower()]
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
        "command": "python docs/topics/0.24_Artificial_Intelligence/Code/03_Research/Research_AI_Scaling_Audit.py",
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
                "path": str(scaling_path.relative_to(ROOT)).replace("\\", "/"),
                "source": scaling.get("source", "unspecified"),
                "sha256": sha256(scaling_path),
            },
            {
                "path": str(moe_path.relative_to(ROOT)).replace("\\", "/"),
                "source": moe_data.get("source", "unspecified"),
                "sha256": sha256(moe_path),
            },
            {
                "path": str(gpt3_path.relative_to(ROOT)).replace("\\", "/"),
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

    ARTIFACT.parent.mkdir(parents=True, exist_ok=True)
    ARTIFACT.write_text(json.dumps(artifact, indent=2, sort_keys=True), encoding="utf-8")

    print("UET AI scaling/sparsity audit")
    print(f"  status: {status}")
    print(f"  alpha_N: {alpha_n:.6f}")
    print(f"  csv alpha fit: {csv_fit['alpha_fit']:.6f}")
    print(f"  |alpha_N - kappa| / alpha_N: {alpha_kappa_relative_delta:.3f}")
    print(f"  min dense active fraction: {min_dense_fraction:.4f}")
    print(f"  min MoE active fraction: {min_moe_fraction:.4f}")
    print(f"  artifact: {ARTIFACT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
