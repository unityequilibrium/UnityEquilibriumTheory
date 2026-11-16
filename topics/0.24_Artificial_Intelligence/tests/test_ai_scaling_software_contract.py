"""Synthetic software regressions, not an AI/UET physical comparison."""

from __future__ import annotations

import importlib.util
import json
import math
from pathlib import Path

import pytest


TOPIC = Path(__file__).resolve().parents[1]
SOURCE = TOPIC / "Code/03_Research/Research_AI_Scaling_Audit.py"


@pytest.fixture(scope="module")
def audit():
    spec = importlib.util.spec_from_file_location("ai_scaling_software_fixture", SOURCE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    original = module.ARTIFACT.read_bytes()
    yield module
    assert module.ARTIFACT.read_bytes() == original, "Software fixtures must not replace saved evidence"


def models():
    def row(kind, total, active):
        return {"Type": kind, "Total_Params": total, "Active_Params": active,
                "Context_Window": None, "Training_Tokens": None, "Note": "synthetic fixture, not a source claim"}
    return {"source": "synthetic", "models": {"dense": row("Dense", 8, 8), "sparse": row("MoE", 8, 2)}}


def inputs(tmp_path, *, alpha=0.1, fitted_alpha=None, moe=None):
    data = tmp_path / "data"
    (data / "03_Research").mkdir(parents=True)
    scaling = {"source": "synthetic", "constants": {"alpha_N": alpha, "alpha_C": 0.05}}
    (data / "03_Research/scaling_laws.json").write_text(json.dumps(scaling), encoding="utf-8")
    (data / "03_Research/deepseek_moe_data.json").write_text(json.dumps(models() if moe is None else moe), encoding="utf-8")
    exponent = alpha if fitted_alpha is None else fitted_alpha
    rows = "Parameters,Test_Loss\n" + "".join(f"{n},{n ** (-exponent)}\n" for n in (1, 4, 16))
    (data / "GPT3_Scaling_Laws.csv").write_text(rows, encoding="utf-8", newline="\n")
    return data


def test_current_root_and_import_have_no_legacy_data_redirect(audit):
    assert audit.ROOT == TOPIC.parents[1]
    assert audit.TOPIC == TOPIC
    assert audit.DATA == TOPIC / "Data"
    assert audit.ARTIFACT == TOPIC / "Result/artifacts/0_24_artificial_intelligence_verification.json"


@pytest.mark.parametrize("alpha", [0.25, 0.5, 1.0])
def test_estimator_recovers_known_synthetic_power_law(audit, alpha):
    result = audit.fit_power_exponent([(n, 4 * n ** (-alpha)) for n in (1, 4, 16)])
    assert result["alpha_fit"] == pytest.approx(alpha, abs=1e-12)
    assert result["intercept_log"] == pytest.approx(math.log(4), abs=1e-12)
    assert result["rmse_loss"] < 1e-12
    assert result["point_count"] == 3


@pytest.mark.parametrize("points", [
    [], [(1, 1)], [(1, 1), (1, 2)], [(0, 1), (2, 1)], [(-1, 1), (2, 1)],
    [(1, 0), (2, 1)], [(1, -1), (2, 1)], [(True, 1), (2, 1)],
    [("1", 1), (2, 1)], [(float("nan"), 1), (2, 1)],
    [(1, float("inf")), (2, 1)], [(10 ** 1000, 1), (2, 1)],
])
def test_invalid_or_unidentifiable_fit_is_not_a_numeric_zero(audit, points):
    with pytest.raises(ValueError):
        audit.fit_power_exponent(points)


@pytest.mark.parametrize("content", ["", "Other,Test_Loss\n1,1\n", "Parameters,Test_Loss\n", "Parameters,Test_Loss\n0,1\n", "Parameters,Test_Loss\n1,nan\n"])
def test_csv_rejects_missing_columns_rows_and_nonfinite_values(audit, tmp_path, content):
    path = tmp_path / "input.csv"
    path.write_text(content, encoding="utf-8")
    with pytest.raises(ValueError):
        audit.read_gpt3_csv(path)


def test_windows_utf8_bom_input_is_read_without_changing_values(audit, tmp_path):
    path = tmp_path / "input.csv"
    path.write_text("Parameters,Test_Loss\n1,4\n4,2\n16,1\n", encoding="utf-8-sig")
    assert audit.read_gpt3_csv(path) == [(1, 4), (4, 2), (16, 1)]


def test_model_ratios_keep_unknown_ancillary_metadata_as_unknown(audit):
    rows = audit.model_sparsity_table(models())
    assert rows[0]["active_fraction"] == 1
    assert rows[1]["active_fraction"] == 0.25
    assert rows[1]["capacity_to_active_ratio"] == 4
    assert rows[1]["training_tokens"] is None


@pytest.mark.parametrize("field,value", [("Total_Params", 0), ("Total_Params", -1), ("Total_Params", float("nan")), ("Active_Params", 0), ("Active_Params", 9), ("Active_Params", True), ("Type", ""), ("Type", None)])
def test_invalid_model_table_is_rejected(audit, field, value):
    package = models()
    package["models"]["sparse"][field] = value
    with pytest.raises(ValueError):
        audit.model_sparsity_table(package)


@pytest.mark.parametrize("package", [None, {}, {"models": {}}, {"models": {"bad": None}}])
def test_missing_model_package_is_not_empty_success(audit, package):
    with pytest.raises(ValueError):
        audit.model_sparsity_table(package)


@pytest.mark.parametrize("scenario", ["pass", "csv_warn", "proxy_warn", "sparsity_warn"])
def test_main_retains_declared_thresholds_and_warning_meaning(audit, tmp_path, scenario):
    package = models()
    if scenario == "sparsity_warn":
        package["models"]["sparse"]["Active_Params"] = 8
    data = inputs(tmp_path, alpha=0.2 if scenario == "proxy_warn" else 0.1,
                  fitted_alpha=0.5 if scenario == "csv_warn" else None, moe=package)
    output = tmp_path / "isolated/result.json"
    assert audit.main(data_dir=data, artifact_path=output) == 0  # WARN is not a structural crash.
    result = json.loads(output.read_text())
    assert result["status"] == ("PASS" if scenario == "pass" else "WARN")
    assert result["threshold"] == {"csv_alpha_delta_max": 0.20,
        "moe_active_fraction_must_be_below_dense": True, "alpha_kappa_relative_delta_warn_max": 0.25}
    assert result["metrics"]["kappa_macro_proxy"] == 0.1  # Existing diagnostic proxy, not a derivation.
    assert all(row["sha256"] for row in result["inputs"])
    assert bool(result["blockers"]) == (scenario != "pass")
    assert result["limitations"]


@pytest.mark.parametrize("failure", ["missing_csv", "zero_alpha", "no_dense", "nonfinite_metadata"])
def test_invalid_main_inputs_never_overwrite_a_previous_result(audit, tmp_path, failure):
    data = inputs(tmp_path)
    if failure == "missing_csv":
        (data / "GPT3_Scaling_Laws.csv").unlink()
    elif failure == "zero_alpha":
        path = data / "03_Research/scaling_laws.json"
        value = json.loads(path.read_text())
        value["constants"]["alpha_N"] = 0
        path.write_text(json.dumps(value), encoding="utf-8")
    else:
        package = models()
        if failure == "no_dense":
            package["models"].pop("dense")
        else:
            package["models"]["dense"]["Context_Window"] = float("nan")
        (data / "03_Research/deepseek_moe_data.json").write_text(json.dumps(package), encoding="utf-8")
    output = tmp_path / "previous.json"
    previous = b'{"prior_result":"preserve"}\n'
    output.write_bytes(previous)
    with pytest.raises((ValueError, FileNotFoundError)):
        audit.main(data_dir=data, artifact_path=output)
    assert output.read_bytes() == previous
