"""Audit pinned notebook text and ideal averaging identities, without execution."""
from __future__ import annotations

import ast
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path

import numpy as np

TOPIC = Path(__file__).resolve().parents[2]
ROOT = TOPIC.parents[2]
SOURCE = TOPIC / "Data/03_Research/raw/ued_treat_pickle_7f7036b.ipynb"
SOURCE_SHA256 = "1492289fde53f4cadeacb7e4132344c899a660c31fad23a305f4024b1c2c7b52"
OUTPUT = TOPIC / "Result/artifacts/ued_processing_boundary.json"


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def rotation_count(source):
    """Accept only the inspected straight-line literal loop, never evaluate code."""
    tree = ast.parse(source)
    loops = []
    for node in tree.body:
        if not isinstance(node, ast.For):
            continue
        appends = [n for n in ast.walk(node) if isinstance(n, ast.Call)
                   and isinstance(n.func, ast.Attribute)
                   and isinstance(n.func.value, ast.Name)
                   and n.func.value.id == "rotation_matrix" and n.func.attr == "append"]
        if appends:
            loops.append((node, appends))
    if len(loops) != 1:
        raise ValueError("expected one rotation constructor")
    loop, appends = loops[0]
    call = loop.iter
    if not (isinstance(call, ast.Call) and isinstance(call.func, ast.Name)
            and call.func.id == "range" and len(call.args) == 1 and not call.keywords
            and isinstance(call.args[0], ast.Constant)
            and type(call.args[0].value) is int and call.args[0].value > 0
            and len(loop.body) == 1 and isinstance(loop.body[0], ast.Expr)
            and loop.body[0].value is appends[0] and len(appends) == 1 and not loop.orelse):
        raise ValueError("unreviewed rotation loop")
    return call.args[0].value


def harmonic_gain(count, harmonic):
    if type(count) is not int or count not in (5, 6) or type(harmonic) is not int:
        raise ValueError("five/six rotations and an integer harmonic required")
    return complex(np.exp(1j * harmonic * np.arange(count) * np.pi / 3).mean())


def paired_ratio(on, off, threshold=100.0):
    """Ideal already-rotated samples: reproduce paired support, not image warping."""
    on, off = np.asarray(on, dtype=float), np.asarray(off, dtype=float)
    if on.shape != off.shape or on.ndim < 1 or not len(on):
        raise ValueError("matching nonempty rotation stacks required")
    if not np.isfinite(threshold) or threshold <= 0 or np.isinf(on).any() or np.isinf(off).any():
        raise ValueError("positive finite threshold and no infinities required")
    support = np.isfinite(on) & np.isfinite(off) & (on >= threshold) & (off >= threshold)
    on_sum = np.where(support, on, 0).sum(axis=0)
    off_sum = np.where(support, off, 0).sum(axis=0)
    if np.any(off_sum == 0):
        raise ValueError("no common support; no filling permitted")
    weights = np.where(support, off, 0) / off_sum
    local_ratios = np.divide(on, off, out=np.zeros_like(on), where=support)
    ratio = on_sum / off_sum
    return ratio, np.sum(weights * local_ratios, axis=0), weights, support


def inspect_notebook(path):
    if digest(path) != SOURCE_SHA256:
        raise ValueError("pinned notebook drift: review rather than silently accepting a new source")
    notebook = json.loads(path.read_text(encoding="utf-8"))
    cells = {i: "".join(c.get("source", [])) for i, c in enumerate(notebook["cells"])}
    constructor_cells = [i for i, s in cells.items() if "rotation_matrix.append" in s]
    if constructor_cells != [19]:
        raise ValueError("unreviewed additional rotation construction")
    count = rotation_count(cells[19])
    checks = {
        "rotation_count_five": count == 5,
        "comment_six_fold": "6 fold symmetry" in cells[19],
        "angle_step_60_degrees": "alpha + i*60" in cells[19],
        "bilinear_interpolation": cells[19].count("flags=cv2.INTER_LINEAR") == 2,
        "paired_nan_mask": "np.isnan(img_ON_rotated) | np.isnan(img_OFF_rotated)" in cells[20],
        "threshold_100_both_channels": all(f"{v}[{v}<100]" in cells[20]
                                             for v in ("img_ON_rotated", "img_OFF_rotated")),
        "rotation_axis_mean": all(f"np.nanmean({v}, axis=0)" in cells[20]
                                   for v in ("img_ON_rotated", "img_OFF_rotated")),
        "save_uses_averages": all(f"img_as_float(img{v}_rot_avg), sigma=s" in cells[24]
                                  and f"df['img{v}'] = list(img{v}_fliped)" in cells[24]
                                  for v in ("ON", "OFF")),
        "declared_gaussian_sigma_zero": "s=0\n" in cells[24],
        "save_call_present": "df.to_pickle(" in cells[24],
    }
    if not all(checks.values()):
        raise ValueError(f"unreviewed source path: {checks}")
    return checks, [dict(zero_based_cell=i, source_sha256=sha256(cells[i].encode()).hexdigest())
                    for i in (19, 20, 24)]


def main():
    # Explicit inputs only: no globbing, source execution, unpickling or holdout reads.
    controls = [ROOT / "docs/core/07_artifacts/topic13" / name for name in (
        "t13_topic13_closure_matrix.json", "t13_full_core_ready_acceptance_audit.json")]
    before = {str(p.relative_to(ROOT)).replace("\\", "/"): digest(p) for p in controls}
    checks, cells = inspect_notebook(SOURCE)
    gains = [dict(harmonic=m, five_magnitude=abs(harmonic_gain(5, m)),
                  six_magnitude=abs(harmonic_gain(6, m))) for m in range(7)]
    # Manufactured witnesses distinguish exact averaging algebra from measured data.
    on, off = np.array([200., 600.]), np.array([200., 300.])
    ratio, weighted, _, _ = paired_ratio(on, off)
    crossing = []
    for value in (99.999, 100.001):
        r, _, _, support = paired_ratio([value, 600.], off)
        crossing.append(dict(first_on=value, retained_count=int(support.sum()), ratio=float(r)))
    after = {str(p.relative_to(ROOT)).replace("\\", "/"): digest(p) for p in controls}
    if before != after:
        raise ValueError("closure controls changed during audit")
    files = [SOURCE, Path(__file__), Path(__file__).with_name("test_ued_processing_boundary.py")]
    result = dict(
        schema_version="t13-ued-processing-boundary-v1",
        generated_at=datetime.now(timezone.utc).isoformat(),
        major_result_id="T13_UED_PREPROCESSING_OPERATOR_BOUNDARY", topic="0.13",
        owner_topic="0.13_Thermodynamic_Bridge", closure_level="PARTIAL",
        what_is_closed=["Pinned notebook uses five rotations before paired masking and saved averages",
                        "Ideal unmasked five/six harmonic response and paired-ratio identity checked"],
        equation_or_mapping={
            "ideal_harmonic_gain": "H_m(N)=sum_i exp(i*m*i*pi/3)/N; N=5 or 6",
            "processed_ratio": "sum_i M_i ON_i / sum_i M_i OFF_i = sum_i w_i (ON_i/OFF_i)",
            "weights": "w_i=M_i OFF_i/sum_j M_j OFF_j",
            "frozen_support_forward_contract": "I_processed=W I_raw; covariance=W Sigma_raw W^T",
            "boundary": "W depends on geometry and masks; signal-dependent masks preclude a global fixed linear operator"},
        units={"angle": "degrees in notebook; radians in ideal harmonic diagnostic",
               "threshold": "100 in source image-intensity units, not SI energy",
               "gain_and_ratio": "dimensionless"},
        derivation_class="STATIC_SOURCE_AUDIT_AND_FINITE_SUM_IDENTITIES_NOT_UET_PHYSICS",
        observable="processed paired diffraction intensity", data_role="SOURCE_METHOD_DIAGNOSTIC",
        source={"commit": "7f7036bfda28f9330f19b40e57f4edf464b67d64",
                "repository": "https://github.com/remiclaude/UED_processing",
                "notebook_executed": False, "pickle_loaded": False,
                "source_redistribution": "not included; license not established",
                "archive_execution_lineage": "UNVERIFIED", "cell_locators": cells},
        source_checks=checks, ideal_unmasked_gains=gains,
        manufactured_witnesses={"ratio_of_averages": float(ratio), "weighted_ratio": float(weighted),
                                "unweighted_mean_ratio": float(np.mean(on/off)),
                                "threshold_crossing": crossing,
                                "role": "synthetic algebra tests, not experimental findings"},
        verification_status="SOURCE_PATH_VERIFIED_PUBLISHED_ARRAY_LINEAGE_OPEN",
        controlling_blocker="published_array_processing_lineage_and_detector_operator",
        open_blockers=["exact raw-cut pooling and processing revision for published arrays",
                       "rotation/interpolation masks and detector covariance for forward response",
                       "registration and finite-patch response uncertainty",
                       "independent physical Phi normalization and transport matching"],
        next_action="Replay declared raw-cut processing with source-locked parameters and compare saved arrays; no best-fit rotation selection",
        dependency_unlocked=[], full_core_unlock=False, global_claim_promotion=False,
        claim_boundary="Does not establish that the archive used this revision or explain measured residuals. No correction, fitted alpha, TTG validation or change to separate He-4 acceptance.",
        closure_controls_unchanged=before,
        holdout_access="This runner reads only the explicitly hashed notebook, two status controls and its own code/tests; not a repository-wide audit.",
        evidence_artifacts=[dict(path=p.relative_to(ROOT).as_posix(), sha256=digest(p)) for p in files])
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(result, indent=2, allow_nan=False)+"\n", encoding="utf-8", newline="\n")
    print(json.dumps(dict(status=result["verification_status"], gains=gains,
                         manufactured=result["manufactured_witnesses"], artifact=str(OUTPUT))))


if __name__ == "__main__":
    main()
