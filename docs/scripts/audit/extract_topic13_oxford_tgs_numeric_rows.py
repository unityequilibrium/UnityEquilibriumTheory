"""Extract source-defined Oxford TGS Figure 1 rows from a MATLAB v7.3 file.

This is a provenance-preserving extraction only. It does not fit the trace,
infer thermal diffusivity, or emit a UET calibration coefficient.
"""

from __future__ import annotations

import csv
import io
import gzip
import hashlib
import json
from datetime import date
from pathlib import Path

import h5py
import numpy as np


ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research"
RAW_DIR = BASE / "raw/oxford_tgs_figure1"
MAT = RAW_DIR / "helsinki_unimp1_vacmod_map1.mat"
PROCESSING = RAW_DIR / "map_fitting_2d_supplementary_plots.m"
PACKAGE = BASE / "oxford_tgs_figure1_source_package.json"
CSV_GZ = BASE / "oxford_tgs_figure1_numeric_rows.csv.gz"
MANIFEST = BASE / "oxford_tgs_figure1_numeric_rows_manifest.json"

MATLAB_MAP_HORIZONTAL_INDEX = 1
MATLAB_MAP_VERTICAL_INDEX = 2
EXPECTED_SHAPE_HDF5 = (2002, 10, 4, 7)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8-sig") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def build_metadata_only_manifest(package: dict) -> dict:
    records = {record["archive_file"]: record for record in package["raw_files"]}
    mat_record = records["helsinki_unimp1_vacmod_map1.mat"]
    processing_record = records["map_fitting_2d_supplementary_plots.m"]
    output_present = CSV_GZ.is_file()
    return {
        "schema_version": "t13-oxford-tgs-numeric-rows-manifest-v1",
        "artifact": "oxford_tgs_figure1_numeric_rows_manifest",
        "generated_at": date.today().isoformat(),
        "status": "METADATA_ONLY_PUBLIC_BOUNDARY_EXTRACTION_PENDING",
        "input_mode": "METADATA_ONLY_PUBLIC_BOUNDARY",
        "raw_payload_available": False,
        "topic": "0.13_Thermodynamic_Bridge",
        "source": {
            "source_id": package["source"]["source_id"],
            "doi": package["source"]["doi"],
            "record_url": package["source"]["record_url"],
            "raw_mat_path": mat_record["local_path"],
            "raw_mat_sha256": mat_record["sha256"],
            "raw_mat_expected_sha256": mat_record["sha256"],
            "raw_mat_hash_match": False,
            "raw_mat_hash_is_expected_when_unavailable": True,
            "source_filename_variable": mat_record["archive_file"],
            "processing_script_path": processing_record["local_path"],
            "processing_script_sha256": processing_record["sha256"],
            "processing_script_hash_is_expected_when_unavailable": True,
        },
        "extraction": {
            "reader": "h5py (not run: raw MATLAB v7.3 payload unavailable)",
            "matlab_dimension_order": "xxx(horizontal, vertical, trace, sample)",
            "hdf5_storage_shape": list(EXPECTED_SHAPE_HDF5),
            "hdf5_to_matlab_transpose": [3, 2, 1, 0],
            "selected_horizontal_index_1based": MATLAB_MAP_HORIZONTAL_INDEX,
            "selected_vertical_index_1based": MATLAB_MAP_VERTICAL_INDEX,
            "selected_ph_source_value": None,
            "selected_pv_source_value": None,
            "trace_count": 0,
            "sample_count_per_trace": 0,
            "row_count": 0,
            "raw_variables": ["xx", "xx1", "yy", "yy1"],
            "derived_column": "y_delta_yy1_minus_yy_au = yy1_signal_au - yy_signal_au",
            "output_path": CSV_GZ.relative_to(ROOT).as_posix(),
            "output_sha256": None,
            "output_present_but_unverified": output_present,
        },
        "units": {
            "xx_time_s": "s (source processing axis label; not loaded in public checkout)",
            "xx1_time_s": "s (source processing axis label; not loaded in public checkout)",
            "yy_signal_au": "intensity (a.u.) (source processing axis label; not loaded in public checkout)",
            "yy1_signal_au": "intensity (a.u.) (source processing axis label; not loaded in public checkout)",
            "y_delta_yy1_minus_yy_au": "a.u.; source subtraction contract only",
            "ph_source_value": "source value; not loaded in public checkout",
            "pv_source_value": "source value; not loaded in public checkout",
        },
        "uncertainty_boundary": {
            "row_level_uncertainty_emitted": False,
            "source_fit_start_std_proxy_declared": "Bp_std_l",
            "fit_performed_by_extractor": False,
            "thermal_diffusivity_emitted": False,
            "material_identity_declared_for_selected_map": False,
            "temperature_declared_for_selected_map": False,
        },
        "holdout_policy": {
            "xie_2026_accessed": False,
            "xie_2026_source_data_consumed": False,
            "target_curve_used": False,
            "ding_target_curve_used": False,
            "alpha_fit_used": False,
            "numeric_alpha_Phi_K_emitted": False,
        },
        "data_role": "TRAINING/COMPARISON",
        "claim_boundary": (
            "Public metadata-only Oxford TGS boundary. No MATLAB rows were extracted in this checkout; "
            "the existing derived CSV, if present, is not consumed or promoted without the raw source payload."
        ),
    }

def main() -> int:
    package = load_json(PACKAGE)
    if not MAT.is_file() or not PROCESSING.is_file():
        manifest = build_metadata_only_manifest(package)
        MANIFEST.write_text(
            json.dumps(manifest, indent=2, ensure_ascii=True) + "\n",
            encoding="utf-8",
        )
        print(
            json.dumps(
                {
                    "status": manifest["status"],
                    "rows": 0,
                    "raw_payload_available": False,
                    "manifest": MANIFEST.relative_to(ROOT).as_posix(),
                },
                indent=2,
            )
        )
        return 0

    with h5py.File(MAT, "r") as source:
        arrays = {
            name: np.asarray(source[name][...], dtype=float)
            for name in ("xx", "xx1", "yy", "yy1")
        }
        if any(array.shape != EXPECTED_SHAPE_HDF5 for array in arrays.values()):
            raise SystemExit(
                "unexpected HDF5 source shape: "
                + repr({name: array.shape for name, array in arrays.items()})
            )
        ph = np.asarray(source["ph"][...], dtype=float).reshape(-1)
        pv = np.asarray(source["pv"][...], dtype=float).reshape(-1)
        filename = "".join(
            chr(int(value))
            for value in np.asarray(source["filename"][...]).reshape(-1)
        )

    # MATLAB stores the logical dimensions in reverse order in v7.3 HDF5.
    # The source script indexes xxx(m, k, trace, sample), so transpose back
    # before selecting its Figure 1 map point.
    matlab_arrays = {
        name: array.transpose(3, 2, 1, 0)
        for name, array in arrays.items()
    }
    m = MATLAB_MAP_HORIZONTAL_INDEX - 1
    k = MATLAB_MAP_VERTICAL_INDEX - 1
    trace_count = matlab_arrays["xx"].shape[2]
    sample_count = matlab_arrays["xx"].shape[3]
    if m >= len(ph) or k >= len(pv):
        raise SystemExit("selected source map index is outside ph/pv")

    CSV_GZ.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "horizontal_index_1based",
        "vertical_index_1based",
        "trace_index_1based",
        "sample_index_1based",
        "ph_source_value",
        "pv_source_value",
        "xx_time_s",
        "xx1_time_s",
        "yy_signal_au",
        "yy1_signal_au",
        "y_delta_yy1_minus_yy_au",
    ]
    row_count = 0
    with CSV_GZ.open("wb") as raw_handle:
        with gzip.GzipFile(fileobj=raw_handle, mode="wb", mtime=0) as compressed_handle:
            with io.TextIOWrapper(compressed_handle, encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=fieldnames)
                writer.writeheader()
                for trace in range(trace_count):
                    for sample in range(sample_count):
                        xx = float(matlab_arrays["xx"][m, k, trace, sample])
                        xx1 = float(matlab_arrays["xx1"][m, k, trace, sample])
                        yy = float(matlab_arrays["yy"][m, k, trace, sample])
                        yy1 = float(matlab_arrays["yy1"][m, k, trace, sample])
                        writer.writerow(
                            {
                                "horizontal_index_1based": MATLAB_MAP_HORIZONTAL_INDEX,
                                "vertical_index_1based": MATLAB_MAP_VERTICAL_INDEX,
                                "trace_index_1based": trace + 1,
                                "sample_index_1based": sample + 1,
                                "ph_source_value": repr(float(ph[m])),
                                "pv_source_value": repr(float(pv[k])),
                                "xx_time_s": repr(xx),
                                "xx1_time_s": repr(xx1),
                                "yy_signal_au": repr(yy),
                                "yy1_signal_au": repr(yy1),
                                "y_delta_yy1_minus_yy_au": repr(yy1 - yy),
                            }
                        )
                        row_count += 1

    raw_record = next(
        record
        for record in package["raw_files"]
        if record["archive_file"] == "helsinki_unimp1_vacmod_map1.mat"
    )
    manifest = {
        "schema_version": "t13-oxford-tgs-numeric-rows-manifest-v1",
        "artifact": "oxford_tgs_figure1_numeric_rows_manifest",
        "generated_at": date.today().isoformat(),
        "status": "NUMERIC_ROWS_SOURCE_LOCKED_COMPARATOR",
        "topic": "0.13_Thermodynamic_Bridge",
        "source": {
            "source_id": package["source"]["source_id"],
            "doi": package["source"]["doi"],
            "record_url": package["source"]["record_url"],
            "raw_mat_path": MAT.relative_to(ROOT).as_posix(),
            "raw_mat_sha256": sha256(MAT),
            "raw_mat_expected_sha256": raw_record["sha256"],
            "raw_mat_hash_match": sha256(MAT) == raw_record["sha256"],
            "source_filename_variable": filename,
            "processing_script_path": PROCESSING.relative_to(ROOT).as_posix(),
            "processing_script_sha256": sha256(PROCESSING),
        },
        "extraction": {
            "reader": "h5py",
            "matlab_dimension_order": "xxx(horizontal, vertical, trace, sample)",
            "hdf5_storage_shape": list(EXPECTED_SHAPE_HDF5),
            "hdf5_to_matlab_transpose": [3, 2, 1, 0],
            "selected_horizontal_index_1based": MATLAB_MAP_HORIZONTAL_INDEX,
            "selected_vertical_index_1based": MATLAB_MAP_VERTICAL_INDEX,
            "selected_ph_source_value": float(ph[m]),
            "selected_pv_source_value": float(pv[k]),
            "trace_count": trace_count,
            "sample_count_per_trace": sample_count,
            "row_count": row_count,
            "raw_variables": ["xx", "xx1", "yy", "yy1"],
            "derived_column": "y_delta_yy1_minus_yy_au = yy1_signal_au - yy_signal_au",
            "output_path": CSV_GZ.relative_to(ROOT).as_posix(),
            "output_sha256": sha256(CSV_GZ),
        },
        "units": {
            "xx_time_s": "s (source processing axis label)",
            "xx1_time_s": "s (source processing axis label)",
            "yy_signal_au": "intensity (a.u.) (source processing axis label)",
            "yy1_signal_au": "intensity (a.u.) (source processing axis label)",
            "y_delta_yy1_minus_yy_au": "a.u.; source subtraction only",
            "ph_source_value": "source value; unit not declared in Figure 1 package",
            "pv_source_value": "source value; unit not declared in Figure 1 package",
        },
        "uncertainty_boundary": {
            "row_level_uncertainty_emitted": False,
            "source_fit_start_std_proxy_declared": "Bp_std_l",
            "fit_performed_by_extractor": False,
            "thermal_diffusivity_emitted": False,
            "material_identity_declared_for_selected_map": False,
            "temperature_declared_for_selected_map": False,
        },
        "holdout_policy": {
            "xie_2026_accessed": False,
            "xie_2026_source_data_consumed": False,
            "target_curve_used": False,
            "ding_target_curve_used": False,
            "alpha_fit_used": False,
            "numeric_alpha_Phi_K_emitted": False,
        },
        "data_role": "TRAINING/COMPARISON",
        "claim_boundary": (
            "Source-locked Oxford TGS Figure 1 raw-row extraction and source-defined "
            "signal subtraction only. It is not a Ding PBTE C_src source, not a "
            "volumetric c_v source, not a Phi calibration, and not external validation."
        ),
    }
    MANIFEST.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "status": manifest["status"],
                "rows": row_count,
                "traces": trace_count,
                "samples_per_trace": sample_count,
                "csv_sha256": manifest["extraction"]["output_sha256"],
                "manifest": MANIFEST.relative_to(ROOT).as_posix(),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
