"""Deterministic finite 2-D HP protein-folding model benchmark.

This verifier is intentionally narrower than AlphaFold or molecular dynamics. It
uses the historical topic-local HP sequence on a square lattice to make the old
exploratory script auditable:

* exhaustive enumeration supplies an exact optimum within the finite model;
* unbiased random and centroid-biased searches are compared against that oracle;
* fixed seeds and a JSON input contract make the run repeatable;
* all energies remain dimensionless HP model units, not physical free energy.

The artifact is claim_class=C and data_class=synthetic for an internal algorithmic
benchmark only. It does not establish real protein folding, AlphaFold replication,
biological efficacy, or external validation.
"""

from __future__ import annotations

import hashlib
import json
import random
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Sequence


TOPIC_DIR = Path(__file__).resolve().parents[2]
ROOT_DIR = TOPIC_DIR.parents[2]
INPUT_PATH = TOPIC_DIR / "data" / "03_Research" / "protein_folding_hp_benchmark.json"
ARTIFACT_PATH = TOPIC_DIR / "Result" / "artifacts" / "0_22_protein_folding_hp_benchmark.json"

TOPIC_ID = "0.22_Biophysics_Origin_of_Life"
SCRIPT_RELATIVE_PATH = (
    "docs/topics/0.22_Biophysics_Origin_of_Life/"
    "Code/03_Research/Research_Protein_Folding_HP_Benchmark.py"
)
INPUT_RELATIVE_PATH = (
    "docs/topics/0.22_Biophysics_Origin_of_Life/"
    "data/03_Research/protein_folding_hp_benchmark.json"
)

Coord = tuple[int, int]
Coords = tuple[Coord, ...]


def _plain(value: Any) -> Any:
    """Convert tuples and nested values into stable JSON-compatible values."""

    if isinstance(value, tuple):
        return [_plain(item) for item in value]
    if isinstance(value, list):
        return [_plain(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _plain(item) for key, item in value.items()}
    return value


def _stable_json(value: Any) -> str:
    return json.dumps(_plain(value), ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_config(path: Path = INPUT_PATH) -> dict[str, Any]:
    config = json.loads(path.read_text(encoding="utf-8"))
    sequence = config.get("sequence")
    if not isinstance(sequence, str) or len(sequence) < 2 or set(sequence) - {"H", "P"}:
        raise ValueError("sequence must contain at least two H/P residues")

    search = config.get("search", {})
    seeds = search.get("seeds")
    attempts = search.get("attempts_per_seed")
    bias_probability = search.get("centroid_bias_probability")
    methods = search.get("methods")
    if not isinstance(seeds, list) or not seeds or not all(isinstance(seed, int) for seed in seeds):
        raise ValueError("search.seeds must be a non-empty list of integers")
    if not isinstance(attempts, int) or attempts <= 0:
        raise ValueError("search.attempts_per_seed must be a positive integer")
    if not isinstance(bias_probability, (int, float)) or not 0 <= bias_probability <= 1:
        raise ValueError("search.centroid_bias_probability must be between zero and one")
    if methods != ["unbiased_random", "centroid_biased"]:
        raise ValueError("search.methods must declare the two registered comparison methods")
    if config.get("lattice") != "2d_square_integer_lattice":
        raise ValueError("only the registered 2-D square lattice is supported")
    return config


def valid_next_moves(coords: Sequence[Coord]) -> list[Coord]:
    x, y = coords[-1]
    candidates = [(x - 1, y), (x, y - 1), (x, y + 1), (x + 1, y)]
    occupied = set(coords)
    return sorted(candidate for candidate in candidates if candidate not in occupied)


def hp_energy(coords: Sequence[Coord], sequence: str) -> int:
    """Return HP contact energy in model units.

    A contact contributes -1 only for H-H pairs that are spatial neighbors but
    are not covalently adjacent in the chain. Each pair is considered once, so
    no double-count correction is required in this implementation.
    """

    if len(coords) != len(sequence):
        raise ValueError("coordinate and sequence lengths must match")
    if len(set(coords)) != len(coords):
        raise ValueError("self-intersecting coordinates are not valid HP folds")

    energy = 0
    for i in range(len(sequence)):
        if sequence[i] != "H":
            continue
        for j in range(i + 2, len(sequence)):
            if sequence[j] != "H":
                continue
            dx = abs(coords[i][0] - coords[j][0])
            dy = abs(coords[i][1] - coords[j][1])
            if dx + dy == 1:
                energy -= 1
    return energy


def enumerate_self_avoiding_walks(sequence_length: int, first_step: Coord = (1, 0)) -> Iterable[Coords]:
    """Enumerate the finite canonical search space for the 2-D HP chain."""

    if sequence_length < 1:
        raise ValueError("sequence_length must be positive")
    if sequence_length == 1:
        yield ((0, 0),)
        return

    start: list[Coord] = [(0, 0), first_step]
    visited = set(start)

    def extend() -> Iterable[Coords]:
        if len(start) == sequence_length:
            yield tuple(start)
            return
        for move in valid_next_moves(start):
            start.append(move)
            visited.add(move)
            yield from extend()
            visited.remove(move)
            start.pop()

    yield from extend()


def exact_reference(sequence: str) -> dict[str, Any]:
    count = 0
    optimum_energy: int | None = None
    optimum_folds = 0
    optimum_coordinates: Coords | None = None
    histogram: Counter[int] = Counter()

    for coords in enumerate_self_avoiding_walks(len(sequence)):
        count += 1
        energy = hp_energy(coords, sequence)
        histogram[energy] += 1
        if optimum_energy is None or energy < optimum_energy:
            optimum_energy = energy
            optimum_folds = 1
            optimum_coordinates = coords
        elif energy == optimum_energy:
            optimum_folds += 1
            if optimum_coordinates is None or coords < optimum_coordinates:
                optimum_coordinates = coords

    if count == 0 or optimum_energy is None or optimum_coordinates is None:
        raise RuntimeError("exhaustive enumeration produced no valid fold")

    return {
        "symmetry_breaking": "residue 0=[0,0], residue 1=[1,0]",
        "configuration_count": count,
        "optimum_energy": optimum_energy,
        "optimum_fold_count": optimum_folds,
        "one_optimal_coordinates": _plain(optimum_coordinates),
        "energy_histogram": {str(key): histogram[key] for key in sorted(histogram)},
    }


def _choose_move(
    coords: list[Coord],
    sequence: str,
    index: int,
    rng: random.Random,
    method: str,
    bias_probability: float,
) -> Coord:
    options = valid_next_moves(coords)
    if not options:
        raise RuntimeError("no valid next move")
    if method == "unbiased_random" or sequence[index] != "H":
        return rng.choice(options)

    h_coords = [coords[j] for j in range(len(coords)) if sequence[j] == "H"]
    if not h_coords:
        return rng.choice(options)

    cx = sum(point[0] for point in h_coords) / len(h_coords)
    cy = sum(point[1] for point in h_coords) / len(h_coords)
    ranked = sorted(options, key=lambda point: ((point[0] - cx) ** 2 + (point[1] - cy) ** 2, point))
    if rng.random() < bias_probability:
        return ranked[0]
    return rng.choice(options)


def _summarize_search(
    energies: list[int],
    valid_count: int,
    invalid_count: int,
    best_energy: int | None,
    best_coords: Coords | None,
    optimum_energy: int,
    seed: int | None = None,
) -> dict[str, Any]:
    if not energies or best_energy is None or best_coords is None:
        raise RuntimeError("stochastic search produced no valid fold")
    result: dict[str, Any] = {
        "valid_fold_count": valid_count,
        "invalid_fold_count": invalid_count,
        "best_energy": best_energy,
        "optimum_gap": best_energy - optimum_energy,
        "optimum_hit_count": sum(1 for energy in energies if energy == optimum_energy),
        "optimum_hit_rate": round(sum(1 for energy in energies if energy == optimum_energy) / len(energies), 6),
        "mean_energy": round(sum(energies) / len(energies), 6),
        "energy_histogram": {str(key): count for key, count in sorted(Counter(energies).items())},
        "best_coordinates": _plain(best_coords),
    }
    if seed is not None:
        result["seed"] = seed
    return result


def run_stochastic_method(
    sequence: str,
    seeds: Sequence[int],
    attempts_per_seed: int,
    method: str,
    optimum_energy: int,
    bias_probability: float,
) -> dict[str, Any]:
    per_seed: list[dict[str, Any]] = []
    all_energies: list[int] = []
    total_valid = 0
    total_invalid = 0
    best_energy: int | None = None
    best_coords: Coords | None = None

    for seed in seeds:
        rng = random.Random(seed)
        energies: list[int] = []
        valid_count = 0
        invalid_count = 0
        seed_best_energy: int | None = None
        seed_best_coords: Coords | None = None

        for _ in range(attempts_per_seed):
            coords: list[Coord] = [(0, 0), (1, 0)]
            try:
                while len(coords) < len(sequence):
                    index = len(coords)
                    coords.append(_choose_move(coords, sequence, index, rng, method, bias_probability))
            except RuntimeError:
                invalid_count += 1
                continue

            fold = tuple(coords)
            energy = hp_energy(fold, sequence)
            energies.append(energy)
            valid_count += 1
            if (
                seed_best_energy is None
                or energy < seed_best_energy
                or (energy == seed_best_energy and (seed_best_coords is None or fold < seed_best_coords))
            ):
                seed_best_energy = energy
                seed_best_coords = fold

        per_seed.append(
            _summarize_search(
                energies,
                valid_count,
                invalid_count,
                seed_best_energy,
                seed_best_coords,
                optimum_energy,
                seed=seed,
            )
        )
        all_energies.extend(energies)
        total_valid += valid_count
        total_invalid += invalid_count
        if (
            seed_best_energy is not None
            and seed_best_coords is not None
            and (
                best_energy is None
                or seed_best_energy < best_energy
                or (seed_best_energy == best_energy and (best_coords is None or seed_best_coords < best_coords))
            )
        ):
            best_energy = seed_best_energy
            best_coords = seed_best_coords

    aggregate = _summarize_search(
        all_energies,
        total_valid,
        total_invalid,
        best_energy,
        best_coords,
        optimum_energy,
    )
    return {
        "method": method,
        "attempts_per_seed": attempts_per_seed,
        "seeds": list(seeds),
        "aggregate": aggregate,
        "per_seed": per_seed,
    }


def _deterministic_signature(value: Any) -> str:
    return _sha256_bytes(_stable_json(value).encode("utf-8"))


def build_artifact(config_path: Path = INPUT_PATH) -> dict[str, Any]:
    config = load_config(config_path)
    sequence = config["sequence"]
    search = config["search"]
    input_hash = sha256_file(config_path)
    exact = exact_reference(sequence)

    first_run = {
        method: run_stochastic_method(
            sequence,
            search["seeds"],
            search["attempts_per_seed"],
            method,
            exact["optimum_energy"],
            search["centroid_bias_probability"],
        )
        for method in search["methods"]
    }
    replay_run = {
        method: run_stochastic_method(
            sequence,
            search["seeds"],
            search["attempts_per_seed"],
            method,
            exact["optimum_energy"],
            search["centroid_bias_probability"],
        )
        for method in search["methods"]
    }
    replay_match = _deterministic_signature(first_run) == _deterministic_signature(replay_run)
    model_rule_checks = {
        "non_bonded_contact_counts": hp_energy(((0, 0), (1, 0), (1, 1), (0, 1)), "HHHH") == -1,
        "covalent_contact_excluded": hp_energy(((0, 0), (1, 0), (2, 0), (3, 0)), "HHHH") == 0,
    }
    gaps = [
        first_run[method]["aggregate"]["optimum_gap"]
        for method in search["methods"]
    ]
    acceptance = {
        "exact_enumeration_completed": exact["configuration_count"] > 0,
        "exact_optimum_gap_is_zero": True,
        "stochastic_optimum_gaps_non_negative": all(gap >= 0 for gap in gaps),
        "model_rule_checks_pass": all(model_rule_checks.values()),
        "deterministic_replay_match": replay_match,
    }
    acceptance["status"] = "PASS" if all(acceptance.values()) else "FAIL"

    artifact: dict[str, Any] = {
        "schema_version": "1.0",
        "artifact": "0_22_protein_folding_hp_benchmark",
        "topic": TOPIC_ID,
        "lane": "protein_folding",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "verification_status": acceptance["status"],
        "claim_class": "C",
        "data_class": "synthetic",
        "benchmark_role": "internal_finite_model_algorithmic_benchmark",
        "run_contract": {
            "script": SCRIPT_RELATIVE_PATH,
            "input": INPUT_RELATIVE_PATH,
            "input_sha256": input_hash,
            "formula_id": "T22-010",
            "formula_status": "model_definition_in_dimensionless_hp_units",
            "parameter_policy": "All sequence, lattice, seed, attempt, and bias parameters are locked by the input JSON.",
        },
        "formula": {
            "relation": "E_HP = -sum(1) over H-H pairs with Manhattan distance 1 and index gap > 1",
            "derivation_class": "model_definition_with_exact_finite_oracle",
            "constant_origin": "benchmark_anchor",
            "proof_status": "checked_local_benchmark",
            "standard_physics_correspondence": "open; no atomistic free-energy mapping is claimed",
            "variables": {
                "sequence_i": "H or P residue label",
                "r_i": "integer 2-D lattice coordinate",
                "E_HP": "dimensionless HP model energy",
            },
            "unit_closure": "Closed only within the finite lattice model; the -1 contact term is a benchmark anchor, not SI energy or protein free energy.",
            "observable_mapping": "minimum model energy, optimum gap, optimum hit rate, and energy histogram",
        },
        "input": {
            "path": INPUT_RELATIVE_PATH,
            "sha256": input_hash,
            "sequence": sequence,
            "sequence_length": len(sequence),
            "lattice": config["lattice"],
            "coordinate_unit": config["coordinate_unit"],
            "energy_unit": config["energy_unit"],
            "preprocessing": config["preprocessing"],
        },
        "config": config["search"],
        "exact_reference": exact,
        "comparisons": first_run,
        "thresholds": {
            "exact_enumeration_configuration_count": "> 0",
            "exact_optimum_gap": "0 for the exhaustive oracle by definition",
            "stochastic_optimum_gap": ">= 0 relative to the exhaustive oracle",
            "deterministic_replay": "same locked input and seeds must produce identical comparison payloads",
        },
        "acceptance": acceptance,
        "deterministic_replay_signature": _deterministic_signature(first_run),
        "interpretation": [
            "PASS means the finite 2-D HP mechanics and deterministic comparison contract executed correctly.",
            "The stochastic methods are compared against an exact optimum within the declared model, not against a real protein structure.",
            "This artifact does not establish real protein folding, protein free energy, AlphaFold replication, PDB/CASP performance, experimental validation, or external replication.",
        ],
        "claim_boundary": "Class-C internal synthetic algorithmic benchmark only; the topic remains Draft/Tier B/WARN.",
    }
    digest_payload = {key: value for key, value in artifact.items() if key != "generated_at_utc"}
    artifact["deterministic_payload_sha256"] = _deterministic_signature(digest_payload)
    return artifact


def write_artifact(
    artifact_path: Path = ARTIFACT_PATH,
    config_path: Path = INPUT_PATH,
) -> dict[str, Any]:
    artifact = build_artifact(config_path)
    artifact_path.parent.mkdir(parents=True, exist_ok=True)
    artifact_path.write_text(
        json.dumps(artifact, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return artifact


def main() -> int:
    artifact = write_artifact()
    summary = {
        "artifact": artifact["artifact"],
        "verification_status": artifact["verification_status"],
        "claim_class": artifact["claim_class"],
        "data_class": artifact["data_class"],
        "optimum_energy": artifact["exact_reference"]["optimum_energy"],
        "configuration_count": artifact["exact_reference"]["configuration_count"],
        "method_gaps": {
            method: details["aggregate"]["optimum_gap"]
            for method, details in artifact["comparisons"].items()
        },
        "deterministic_payload_sha256": artifact["deterministic_payload_sha256"],
    }
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
    return 0 if artifact["verification_status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
