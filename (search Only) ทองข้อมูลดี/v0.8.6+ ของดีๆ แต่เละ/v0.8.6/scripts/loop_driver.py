#!/usr/bin/env python
from __future__ import annotations
import argparse, json, subprocess, sys, shutil
from pathlib import Path
from typing import Dict, Any, List

def parse_list(s: str) -> List[str]:
    return [x.strip() for x in (s or "").split(";") if x.strip()]

def run(cmd: List[str], cwd: Path | None = None):
    print("\n$ " + " ".join(cmd))
    r = subprocess.run(cmd, cwd=str(cwd) if cwd else None)
    if r.returncode != 0:
        raise SystemExit(r.returncode)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True, help="loop_config.json")
    ap.add_argument("--max_iters", type=int, default=-1, help="override config.params.max_iters if >0")
    ap.add_argument("--dry", action="store_true", help="print planned commands only (no execution)")
    args = ap.parse_args()

    cfg = json.loads(Path(args.config).read_text(encoding="utf-8"))
    paths = cfg.get("paths", {})
    params = cfg.get("params", {})

    max_iters = int(params.get("max_iters", 3))
    if args.max_iters and args.max_iters > 0:
        max_iters = args.max_iters

    # Required paths
    stress_spec = Path(paths["stress_spec"])
    band_presets = Path(paths["band_dt_presets"])
    global_presets = Path(paths.get("dt_presets", "")) if paths.get("dt_presets","") else None
    baseline_manifest = Path(paths.get("baseline_manifest", "baseline/baseline_manifest.json"))
    work_dir = Path(paths.get("work_dir", "loop_runs"))
    work_dir.mkdir(parents=True, exist_ok=True)

    # Scripts dir (defaults to repo scripts/)
    scripts_dir = Path(paths.get("scripts_dir", "scripts"))

    # Gate
    min_pass_rate = float(params.get("min_pass_rate", 0.95))
    min_ci_lo = float(params.get("min_ci_lo", 0.90))

    # Adaptive parameters
    dt_scales = str(params.get("dt_scales_grid", "1.0;0.7;0.5;0.35;0.25"))
    adaptive_mode = str(params.get("adaptive_mode", "grid")).lower()  # grid|zoom
    zoom_rounds = int(params.get("zoom_rounds", 2))
    zoom_eps_ratio = float(params.get("zoom_eps_ratio", 1.15))
    zoom_min_scale = float(params.get("zoom_min_scale", 0.1))
    zoom_max_new_scales_per_group = int(params.get("zoom_max_new_scales_per_group", 1))
    zoom_use_smoothing = bool(params.get("zoom_use_smoothing", True))
    zoom_band_policy_json = str(params.get("zoom_band_policy_json", ""))
    top_groups = int(params.get("top_groups", 5))
    cases_per_group = int(params.get("cases_per_group", 5))
    jitters_per_case = int(params.get("jitters_per_case", 3))

    # Proposal behavior
    prefer_keep_if_pass = bool(params.get("prefer_keep_if_pass", True))
    apply_only_gate_pass = bool(params.get("apply_only_gate_pass", True))
    band_aware_updates = bool(params.get("band_aware_updates", True))
    monotonic_check = bool(params.get("monotonic_check", True))
    monotonic_min_n = int(params.get("monotonic_min_n", 50))
    monotonic_delta = float(params.get("monotonic_delta", 0.05))
    resample_on_block = bool(params.get("resample_on_block", True))
    resample_rounds = int(params.get("resample_rounds", 2))
    resample_extra_seeds = int(params.get("resample_extra_seeds", 10))
    resample_seed_start = int(params.get("resample_seed_start", 200000))
    resample_max_rows = int(params.get("resample_max_rows", 20000))
    determinism_probe = bool(params.get("determinism_probe", True))
    determinism_repeats = int(params.get("determinism_repeats", 5))
    determinism_max_base_rows = int(params.get("determinism_max_base_rows", 200))
    escalate_on_persistent_block = bool(params.get("escalate_on_persistent_block", True))
    escalate_extra_seeds_multiplier = int(params.get("escalate_extra_seeds_multiplier", 2))
    escalate_additional_resample_rounds = int(params.get("escalate_additional_resample_rounds", 1))
    metric_triage = bool(params.get("metric_triage", True))
    metric_triage_top_k = int(params.get("metric_triage_top_k", 5))
    metric_triage_thresholds_json = str(params.get("metric_triage_thresholds_json", ""))
    action_router = bool(params.get("action_router", True))
    action_router_enforce = bool(params.get("action_router_enforce", True))
    hold_apply_if_unstable = bool(params.get("hold_apply_if_unstable", True))
    targeted_action_executor = bool(params.get("targeted_action_executor", True))
    targeted_action_allow_when_hold = bool(params.get("targeted_action_allow_when_hold", False))
    targeted_action_min_multiplier = float(params.get("targeted_action_min_multiplier", 0.1))
    targeted_action_respect_lock = bool(params.get("targeted_action_respect_lock", True))
    targeted_action_allow_modify_locked = bool(params.get("targeted_action_allow_modify_locked", False))
    targeted_action_do_not_touch_json = str(params.get("targeted_action_do_not_touch_json", ""))
    evidence_budgeter = bool(params.get("evidence_budgeter", True))
    evidence_budget_max_n = int(params.get("evidence_budget_max_n", 500))
    evidence_budget_total_extra_seeds = int(params.get("evidence_budget_total_extra_seeds", 200))
    evidence_budget_max_rounds = int(params.get("evidence_budget_max_rounds", 3))
    evidence_budget_stop_on_unstable = bool(params.get("evidence_budget_stop_on_unstable", True))
    # R0-E24 targeted evidence executor
    evidence_executor = bool(params.get("evidence_executor", True))
    evidence_rounds = int(params.get("evidence_rounds", 1))
    evidence_extra_seeds = int(params.get("evidence_extra_seeds", 20))
    evidence_extra_seeds_multiplier = float(params.get("evidence_extra_seeds_multiplier", 2.0))
    evidence_seed_start = int(params.get("evidence_seed_start", 500000))
    evidence_max_rows = int(params.get("evidence_max_rows", 50000))

    # Optional: extra artifacts to hash into baseline manifest
    freeze_extra = parse_list(str(params.get("freeze_extra_files", "")))

    # Current presets pointer (gets updated each iter)
    cur_band_presets = band_presets
    cur_global_presets = global_presets

    for it in range(1, max_iters+1):
        tag = f"iter{it:02d}"
        run_dir = work_dir / tag
        if run_dir.exists():
            shutil.rmtree(run_dir)
        run_dir.mkdir(parents=True, exist_ok=True)

        stress_matrix = run_dir / "stress_matrix.csv"
        stress_out = run_dir / "stress_runs"

        # 1) Generate stress matrix
        cmd = [sys.executable, str(scripts_dir/"generate_stress_matrix.py"),
               "--spec", str(stress_spec),
               "--band_dt_presets", str(cur_band_presets),
               "--out", str(stress_matrix)]
        if cur_global_presets:
            cmd += ["--dt_presets", str(cur_global_presets)]
        if args.dry:
            print("\nPLAN:", " ".join(cmd))
        else:
            run(cmd)

        # 2) Run stress
        cmd = [sys.executable, str(scripts_dir/"run_dt_ladder.py"),
               "--matrix", str(stress_matrix),
               "--out", str(stress_out),
               "--overwrite"]
        if args.dry:
            print("\nPLAN:", " ".join(cmd))
        else:
            run(cmd)

        # 3) Summarize stress
        cmd = [sys.executable, str(scripts_dir/"summarize_stress_test.py"),
               "--ledger", str(stress_out/"dt_ladder_ledger.csv")]
        if args.dry:
            print("\nPLAN:", " ".join(cmd))
        else:
            run(cmd)

        summary_csv = stress_out/"stress_summary"/"stress_summary.csv"
        gate_report = stress_out/"stress_summary"/"stress_gate_report.json"

        # 4) Gate stress (catch FAIL)
        cmd = [sys.executable, str(scripts_dir/"gate_stress_results.py"),
               "--summary_csv", str(summary_csv),
               "--min_pass_rate", str(min_pass_rate),
               "--min_ci_lo", str(min_ci_lo)]
        if args.dry:
            print("\nPLAN:", " ".join(cmd))
            continue
        else:
            r = subprocess.run(cmd)
            if r.returncode == 0:
                # PASS -> freeze baseline and exit
                extra = freeze_extra[:]
                extra += [str(cur_band_presets)]
                if cur_global_presets:
                    extra += [str(cur_global_presets)]
                cmd2 = [sys.executable, str(scripts_dir/"freeze_baseline_manifest.py"),
                        "--out", str(baseline_manifest),
                        "--stress_spec", str(stress_spec),
                        "--stress_report", str(gate_report),
                        "--extra_files", ";".join([x for x in extra if x]),
                        "--overwrite"]
                run(cmd2)
                print("\n✅ LOOP PASS: stress gate satisfied. Baseline manifest updated.")
                return
            print("\n⚠️  Stress gate FAIL; entering adaptive cycle...")
        failing_groups_json = run_dir/"failing_groups.json"
        if band_aware_updates and gate_report.exists():
            cmdFG = [sys.executable, str(scripts_dir/"failing_groups_from_gate_report.py"),
                     "--gate_report", str(gate_report),
                     "--out", str(failing_groups_json)]
            try:
                run(cmdFG)
            except SystemExit:
                pass
        else:
            failing_groups_json = None

        # 5) Adaptive matrix focusing on failures
        adaptive_matrix = run_dir / "adaptive_stress_matrix.csv"
        adaptive_out = run_dir / "adaptive_runs"
        adaptive_matrices_used = [adaptive_matrix]
        cmd = [sys.executable, str(scripts_dir/"make_adaptive_stress_matrix.py"),
               "--stress_matrix_in", str(stress_matrix),
               "--stress_ledger", str(stress_out/"dt_ladder_ledger.csv"),
               "--out", str(adaptive_matrix),
               "--top_groups", str(top_groups),
               "--cases_per_group", str(cases_per_group),
               "--jitters_per_case", str(jitters_per_case),
               "--dt_scales", dt_scales]
        run(cmd)

        # 6) Run adaptive
        cmd = [sys.executable, str(scripts_dir/"run_dt_ladder.py"),
               "--matrix", str(adaptive_matrix),
               "--out", str(adaptive_out),
               "--overwrite"]
        run(cmd)

        # 7) Summarize adaptive with variant grouping
        cmd = [sys.executable, str(scripts_dir/"summarize_stress_test.py"),
               "--ledger", str(adaptive_out/"dt_ladder_ledger.csv"),
               "--group", "band_model_integrator_variant"]
        run(cmd)

        
        # 7.1) Optional zoom rounds: propose new scales per (band|model|integrator|code) and re-run targeted adaptive tests
        if adaptive_mode == "zoom":
            merged = run_dir / "adaptive_variant_summary_merged.csv"
            # start merged as the first adaptive summary
            cmdm = [sys.executable, str(scripts_dir/"merge_variant_summaries.py"),
                    "--summaries", str(adaptive_summary),
                    "--out", str(merged)]
            run(cmdm)
            cur_merged = merged

            for zr in range(1, zoom_rounds+1):
                plan_json = run_dir / f"zoom_scale_plan_round{zr:02d}.json"
                cmdz = [sys.executable, str(scripts_dir/"suggest_zoom_scales.py"),
                        "--variant_summary_csv", str(cur_merged),
                        "--out_plan", str(plan_json),
                        "--min_pass_rate", str(min_pass_rate),
                        "--min_ci_lo", str(min_ci_lo),
                        "--min_scale", str(zoom_min_scale),
                        "--max_scale", "1.0",
                        "--eps_ratio", str(zoom_eps_ratio),
                        "--max_new_scales_per_group", str(zoom_max_new_scales_per_group)]
                if zoom_use_smoothing:
                    cmdz += ["--use_smoothed"]
                if zoom_band_policy_json:
                    cmdz += ["--band_policy_json", str(zoom_band_policy_json)]
                run(cmdz)

                payload = json.loads(Path(plan_json).read_text(encoding="utf-8"))
                n_new = int(payload.get("meta", {}).get("n_new_scales_total", 0))
                if n_new <= 0:
                    break

                # run targeted adaptive round using dt_scales_plan (plan_json)
                az_dir = run_dir / f"adaptive_zoom_round{zr:02d}"
                az_matrix = run_dir / f"adaptive_zoom_matrix_round{zr:02d}.csv"
                adaptive_matrices_used.append(az_matrix)
                cmdA = [sys.executable, str(scripts_dir/"make_adaptive_stress_matrix.py"),
                        "--stress_matrix_in", str(stress_matrix),
                        "--stress_ledger", str(stress_out/"dt_ladder_ledger.csv"),
                        "--out", str(az_matrix),
                        "--top_groups", str(top_groups),
                        "--cases_per_group", str(cases_per_group),
                        "--jitters_per_case", str(jitters_per_case),
                        "--dt_scales", "1.0",  # fallback (unused when plan applies)
                        "--dt_scales_plan", str(plan_json)]
                run(cmdA)

                cmdB = [sys.executable, str(scripts_dir/"run_dt_ladder.py"),
                        "--matrix", str(az_matrix),
                        "--out", str(az_dir),
                        "--overwrite"]
                run(cmdB)

                cmdC = [sys.executable, str(scripts_dir/"summarize_stress_test.py"),
                        "--ledger", str(az_dir/"dt_ladder_ledger.csv"),
                        "--group", "band_model_integrator_variant"]
                run(cmdC)

                az_summary = az_dir/"stress_summary"/"stress_summary.csv"
                # merge with previous merged summary
                new_merged = run_dir / f"adaptive_variant_summary_merged_round{zr:02d}.csv"
                cmdm2 = [sys.executable, str(scripts_dir/"merge_variant_summaries.py"),
                         "--summaries", f"{cur_merged};{az_summary}",
                         "--out", str(new_merged)]
                run(cmdm2)
                cur_merged = new_merged

            adaptive_summary = cur_merged

        adaptive_summary = adaptive_out/"stress_summary"/"stress_summary.csv"

        # 7.2) Optional monotonic consistency check (blocklist unstable groups)
        monotonic_report = run_dir/"monotonic_report.json"
        if monotonic_check:
            cmdM = [sys.executable, str(scripts_dir/"monotonic_consistency_check.py"),
                    "--variant_summary_csv", str(adaptive_summary),
                    "--out", str(monotonic_report),
                    "--min_n", str(monotonic_min_n),
                    "--delta", str(monotonic_delta),
                    "--use_smoothed_if_present"]
            try:
                run(cmdM)
            except SystemExit:
                pass
        else:
            monotonic_report = None

        # 7.3) Optional auto-resample for blocklisted groups (increase evidence, reduce noise)
        if resample_on_block and monotonic_check and monotonic_report is not None:
            try:
                rep = json.loads(Path(monotonic_report).read_text(encoding="utf-8"))
            except Exception:
                rep = {}
            status = str(rep.get("status","OK"))
            for rr in range(1, resample_rounds+1):
                if status != "BLOCK":
                    break
                # generate resample matrix from adaptive matrices used
                resample_matrix = run_dir / f"resample_matrix_round{rr:02d}.csv"
                resample_out = run_dir / f"resample_runs_round{rr:02d}"
                mats = ";".join([str(p) for p in adaptive_matrices_used])
                ledgers = []
                # include ledgers we already ran to dedupe
                ledgers.append(str(adaptive_out/"dt_ladder_ledger.csv"))
                for zr in range(1, zoom_rounds+1):
                    az_dir = run_dir / f"adaptive_zoom_round{zr:02d}"
                    if (az_dir/"dt_ladder_ledger.csv").exists():
                        ledgers.append(str(az_dir/"dt_ladder_ledger.csv"))
                cmdR = [sys.executable, str(scripts_dir/"resample_blocked_groups.py"),
                        "--matrices", mats,
                        "--blocklist_json", str(monotonic_report),
                        "--out", str(resample_matrix),
                        "--extra_seeds", str(resample_extra_seeds),
                        "--seed_start", str(resample_seed_start + rr*10000),
                        "--max_rows", str(resample_max_rows),
                        "--dedupe_ledger", ";".join(ledgers)]
                try:
                    run(cmdR)
                except SystemExit:
                    break

                # run resample
                cmdB = [sys.executable, str(scripts_dir/"run_dt_ladder.py"),
                        "--matrix", str(resample_matrix),
                        "--out", str(resample_out),
                        "--overwrite"]
                run(cmdB)

                # summarize
                cmdC = [sys.executable, str(scripts_dir/"summarize_stress_test.py"),
                        "--ledger", str(resample_out/"dt_ladder_ledger.csv"),
                        "--group", "band_model_integrator_variant"]
                run(cmdC)

                rs_summary = resample_out/"stress_summary"/"stress_summary.csv"
                new_merged = run_dir / f"adaptive_variant_summary_merged_resample_round{rr:02d}.csv"
                cmdm2 = [sys.executable, str(scripts_dir/"merge_variant_summaries.py"),
                         "--summaries", f"{adaptive_summary};{rs_summary}",
                         "--out", str(new_merged)]
                run(cmdm2)
                adaptive_summary = new_merged

                # rerun monotonic check
                cmdM2 = [sys.executable, str(scripts_dir/"monotonic_consistency_check.py"),
                         "--variant_summary_csv", str(adaptive_summary),
                         "--out", str(monotonic_report),
                         "--min_n", str(monotonic_min_n),
                         "--delta", str(monotonic_delta),
                         "--use_smoothed_if_present"]
                try:
                    run(cmdM2)
                except SystemExit:
                    pass
                try:
                    rep = json.loads(Path(monotonic_report).read_text(encoding="utf-8"))
                except Exception:
                    rep = {}
                status = str(rep.get("status","OK"))

        # 7.4) Escalation if still BLOCK after resample: determinism probe + heavier resample
        if resample_on_block and monotonic_check and monotonic_report is not None:
            try:
                rep = json.loads(Path(monotonic_report).read_text(encoding="utf-8"))
            except Exception:
                rep = {}
            status = str(rep.get("status","OK"))
            if status == "BLOCK" and escalate_on_persistent_block:
                # (a) Determinism probe (repeat same seeds/configs)
                if determinism_probe:
                    probe_matrix = run_dir/"determinism_probe_matrix.csv"
                    probe_out = run_dir/"determinism_probe_runs"
                    mats = ";".join([str(p) for p in adaptive_matrices_used])
                    cmdP = [sys.executable, str(scripts_dir/"determinism_probe_matrix.py"),
                            "--matrices", mats,
                            "--groups_json", str(monotonic_report),
                            "--out", str(probe_matrix),
                            "--repeats", str(determinism_repeats),
                            "--max_base_rows", str(determinism_max_base_rows)]
                    try:
                        run(cmdP)
                        run([sys.executable, str(scripts_dir/"run_dt_ladder.py"),
                             "--matrix", str(probe_matrix),
                             "--out", str(probe_out),
                             "--overwrite"])
                        det_rep = run_dir/"determinism_report.json"
                        run([sys.executable, str(scripts_dir/"determinism_report.py"),
                             "--ledger", str(probe_out/"dt_ladder_ledger.csv"),
                             "--out", str(det_rep),
                             "--min_repeats", str(max(3, determinism_repeats//2))])
                    except SystemExit:
                        pass

                # (b) heavier resample (more seeds) for a few more rounds
                for rr2 in range(1, escalate_additional_resample_rounds+1):
                    try:
                        rep = json.loads(Path(monotonic_report).read_text(encoding="utf-8"))
                        status = str(rep.get("status","OK"))
                    except Exception:
                        status = "OK"
                    if status != "BLOCK":
                        break

                    resample_matrix = run_dir / f"resample_escalated_matrix_round{rr2:02d}.csv"
                    resample_out = run_dir / f"resample_escalated_runs_round{rr2:02d}"
                    mats = ";".join([str(p) for p in adaptive_matrices_used])
                    ledgers = []
                    ledgers.append(str(adaptive_out/"dt_ladder_ledger.csv"))
                    for zr in range(1, zoom_rounds+1):
                        az_dir = run_dir / f"adaptive_zoom_round{zr:02d}"
                        if (az_dir/"dt_ladder_ledger.csv").exists():
                            ledgers.append(str(az_dir/"dt_ladder_ledger.csv"))
                    cmdR = [sys.executable, str(scripts_dir/"resample_blocked_groups.py"),
                            "--matrices", mats,
                            "--blocklist_json", str(monotonic_report),
                            "--out", str(resample_matrix),
                            "--extra_seeds", str(resample_extra_seeds * max(1, escalate_extra_seeds_multiplier)),
                            "--seed_start", str(resample_seed_start + 90000 + rr2*10000),
                            "--max_rows", str(resample_max_rows),
                            "--dedupe_ledger", ";".join(ledgers)]
                    try:
                        run(cmdR)
                    except SystemExit:
                        break

                    run([sys.executable, str(scripts_dir/"run_dt_ladder.py"),
                         "--matrix", str(resample_matrix),
                         "--out", str(resample_out),
                         "--overwrite"])
                    run([sys.executable, str(scripts_dir/"summarize_stress_test.py"),
                         "--ledger", str(resample_out/"dt_ladder_ledger.csv"),
                         "--group", "band_model_integrator_variant"])

                    rs_summary = resample_out/"stress_summary"/"stress_summary.csv"
                    new_merged = run_dir / f"adaptive_variant_summary_merged_resample_escalated_round{rr2:02d}.csv"
                    run([sys.executable, str(scripts_dir/"merge_variant_summaries.py"),
                         "--summaries", f"{adaptive_summary};{rs_summary}",
                         "--out", str(new_merged)])
                    adaptive_summary = new_merged

                    run([sys.executable, str(scripts_dir/"monotonic_consistency_check.py"),
                         "--variant_summary_csv", str(adaptive_summary),
                         "--out", str(monotonic_report),
                         "--min_n", str(monotonic_min_n),
                         "--delta", str(monotonic_delta),
                         "--use_smoothed_if_present"])

        # 7.5) Metric triage (map blocklist ↔ fail_codes ↔ run-level metrics)
        if metric_triage:
            ledgers = []
            if (adaptive_out/"dt_ladder_ledger.csv").exists():
                ledgers.append(str(adaptive_out/"dt_ladder_ledger.csv"))
            for zr in range(1, zoom_rounds+1):
                az_dir = run_dir / f"adaptive_zoom_round{zr:02d}"
                if (az_dir/"dt_ladder_ledger.csv").exists():
                    ledgers.append(str(az_dir/"dt_ladder_ledger.csv"))
            for rr in range(1, resample_rounds+1):
                rs_dir = run_dir / f"resample_runs_round{rr:02d}"
                if (rs_dir/"dt_ladder_ledger.csv").exists():
                    ledgers.append(str(rs_dir/"dt_ladder_ledger.csv"))
            for rr2 in range(1, escalate_additional_resample_rounds+1):
                rs_dir = run_dir / f"resample_escalated_runs_round{rr2:02d}"
                if (rs_dir/"dt_ladder_ledger.csv").exists():
                    ledgers.append(str(rs_dir/"dt_ladder_ledger.csv"))
            dp = run_dir/"determinism_probe_runs"/"dt_ladder_ledger.csv"
            if dp.exists():
                ledgers.append(str(dp))

            tri_json = run_dir/"metric_triage_report.json"
            tri_md = run_dir/"metric_triage_report.md"
            cmdT = [sys.executable, str(scripts_dir/"metric_triage.py"),
                    "--variant_summary_csv", str(adaptive_summary),
                    "--out_json", str(tri_json),
                    "--out_md", str(tri_md),
                    "--top_k", str(metric_triage_top_k)]
            if monotonic_report is not None:
                cmdT += ["--monotonic_report_json", str(monotonic_report)]
            if ledgers:
                cmdT += ["--ledgers", ";".join(ledgers)]
            if metric_triage_thresholds_json:
                cmdT += ["--thresholds_json", str(metric_triage_thresholds_json)]
            try:
                run(cmdT)
            except SystemExit:
                pass


        # 7.6) Action router from triage (decide: hold apply? ask for evidence?)
        action_plan = run_dir/"action_plan.json"
        action_plan_md = run_dir/"action_plan.md"
        skip_apply = False
        tri_json = run_dir/"metric_triage_report.json"
        if action_router and tri_json.exists():
            det_rep = run_dir/"determinism_report.json"
            cmdAR = [sys.executable, str(scripts_dir/"action_router.py"),
                     "--triage_json", str(tri_json),
                     "--out_json", str(action_plan),
                     "--out_md", str(action_plan_md)]
            if monotonic_report is not None:
                cmdAR += ["--monotonic_report_json", str(monotonic_report)]
            if det_rep.exists():
                cmdAR += ["--determinism_report_json", str(det_rep)]
            if hold_apply_if_unstable:
                cmdAR += ["--hold_apply_if_unstable"]
            try:
                run(cmdAR)
                if action_router_enforce:
                    ar = json.loads(Path(action_plan).read_text(encoding="utf-8"))
                    if bool(ar.get("global", {}).get("hold_apply", False)):
                        skip_apply = True
            except SystemExit:
                pass
            except Exception:
                pass

        # 7.65) Evidence budgeter (auto evidence amount + stop rules)
        evidence_budget = run_dir/"evidence_budget.json"
        evidence_budget_md = run_dir/"evidence_budget.md"
        if evidence_budgeter and action_plan.exists():
            det_rep = run_dir/"determinism_report.json"
            cmdEB = [sys.executable, str(scripts_dir/"evidence_budgeter.py"),
                     "--action_plan_json", str(action_plan),
                     "--variant_summary_csv", str(adaptive_summary),
                     "--out_json", str(evidence_budget),
                     "--out_md", str(evidence_budget_md),
                     "--base_extra_seeds", str(evidence_extra_seeds),
                     "--max_rounds", str(evidence_budget_max_rounds),
                     "--max_n_for_evidence", str(evidence_budget_max_n),
                     "--max_total_extra_seeds", str(evidence_budget_total_extra_seeds)]
            if monotonic_report is not None:
                cmdEB += ["--monotonic_report_json", str(monotonic_report)]
            if (run_dir/"metric_triage_report.json").exists():
                cmdEB += ["--triage_json", str(run_dir/"metric_triage_report.json")]
            if det_rep.exists():
                cmdEB += ["--determinism_report_json", str(det_rep)]
            if evidence_budget_stop_on_unstable:
                cmdEB += ["--stop_on_unstable"]
            try:
                run(cmdEB)
            except SystemExit:
                pass

        # 7.7) Targeted evidence executor (if action_plan asks INCREASE_EVIDENCE)
        if evidence_executor and action_plan.exists():
            try:
                ar = json.loads(Path(action_plan).read_text(encoding="utf-8"))
            except Exception:
                ar = {}
            targets = []
            for g in (ar.get("groups", []) or []):
                acts = g.get("recommended_actions", []) or []
                if any(str(a.get("type","")).upper() == "INCREASE_EVIDENCE" for a in acts):
                    gg = str(g.get("group","")).strip()
                    if not gg:
                        gg = f"{g.get('band','')}|{g.get('model','')}|{g.get('integrator','')}"
                    targets.append(gg)
            # Deduplicate
            targets = sorted(list(dict.fromkeys([t for t in targets if t])))
            # If evidence_budget.json exists, use per-group schedules
            budget = {}
            tasks = []
            if (run_dir/"evidence_budget.json").exists():
                try:
                    budget = json.loads(Path(run_dir/"evidence_budget.json").read_text(encoding="utf-8"))
                except Exception:
                    budget = {}
            if budget and isinstance(budget.get("groups", None), list):
                for gp in budget.get("groups", []):
                    if str(gp.get("decision","RUN")).upper() != "RUN":
                        continue
                    gk = str(gp.get("group",""))
                    sched = gp.get("extra_seeds_schedule", []) or []
                    if gk and sched:
                        tasks.append((gk, sched))
            else:
                # fallback: all targets share geometric schedule
                sched = [int(round(evidence_extra_seeds * (evidence_extra_seeds_multiplier ** (er-1)))) for er in range(1, evidence_rounds+1)]
                for gk in targets:
                    tasks.append((gk, sched))

            if targets:
                evidence_targets = run_dir/"evidence_targets.json"
                evidence_targets.write_text(json.dumps({"blocklist_band_model_integrator": targets}, indent=2), encoding="utf-8")

                # Reuse matrices from the adaptive batch (seed expansion around same cases)
                mats = ";".join([str(p) for p in adaptive_matrices_used]) if "adaptive_matrices_used" in locals() else ""
                if mats:
                    for (gk_target, sched) in tasks:
                        # Build a single-group blocklist json for resample_blocked_groups
                        evidence_targets = run_dir/"evidence_targets.json"
                        evidence_targets.write_text(json.dumps({"blocklist_band_model_integrator": [gk_target]}, indent=2), encoding="utf-8")
                        for er, extra_seeds in enumerate(sched, start=1):
                            evid_out = run_dir / f"evidence_runs_round{er:02d}"
                            evid_out.mkdir(parents=True, exist_ok=True)
                            evid_matrix = evid_out / "evidence_matrix.csv"

                            # Build dedupe ledgers list (all ledgers so far)
                            ledgers = []
                            if (adaptive_out/"dt_ladder_ledger.csv").exists():
                                ledgers.append(str(adaptive_out/"dt_ladder_ledger.csv"))
                            for zr in range(1, zoom_rounds+1):
                                az_dir = run_dir / f"adaptive_zoom_round{zr:02d}"
                                if (az_dir/"dt_ladder_ledger.csv").exists():
                                    ledgers.append(str(az_dir/"dt_ladder_ledger.csv"))
                            for rr in range(1, resample_rounds+1):
                                rs_dir = run_dir / f"resample_runs_round{rr:02d}"
                                if (rs_dir/"dt_ladder_ledger.csv").exists():
                                    ledgers.append(str(rs_dir/"dt_ladder_ledger.csv"))
                            for rr2 in range(1, escalate_additional_resample_rounds+1):
                                rs_dir = run_dir / f"resample_escalated_runs_round{rr2:02d}"
                                if (rs_dir/"dt_ladder_ledger.csv").exists():
                                    ledgers.append(str(rs_dir/"dt_ladder_ledger.csv"))
                            # prior evidence rounds
                            for pr in range(1, er):
                                pe = run_dir / f"evidence_runs_round{pr:02d}"
                                if (pe/"dt_ladder_ledger.csv").exists():
                                    ledgers.append(str(pe/"dt_ladder_ledger.csv"))
                            dp = run_dir/"determinism_probe_runs"/"dt_ladder_ledger.csv"
                            if dp.exists():
                                ledgers.append(str(dp))
                            cmdR = [sys.executable, str(scripts_dir/"resample_blocked_groups.py"),
                                    "--matrices", mats,
                                    "--blocklist_json", str(evidence_targets),
                                    "--out", str(evid_matrix),
                                    "--extra_seeds", str(extra_seeds),
                                    "--seed_start", str(evidence_seed_start + er*10000),
                                    "--max_rows", str(evidence_max_rows),
                                    "--dedupe_ledger", ";".join(ledgers)]
                            try:
                                run(cmdR)
                            except SystemExit:
                                break

                            # Run dt ladder for evidence
                            cmdB = [sys.executable, str(scripts_dir/"run_dt_ladder.py"),
                                    "--matrix", str(evid_matrix),
                                    "--out", str(evid_out),
                                    "--overwrite"]
                            run(cmdB)

                            run([sys.executable, str(scripts_dir/"summarize_stress_test.py"),
                                 "--ledger", str(evid_out/"dt_ladder_ledger.csv"),
                                 "--group", "band_model_integrator_variant"])

                            ev_summary = evid_out/"stress_summary"/"stress_summary.csv"
                            new_merged = run_dir / f"adaptive_variant_summary_merged_evidence_round{er:02d}.csv"
                            run([sys.executable, str(scripts_dir/"merge_variant_summaries.py"),
                                 "--summaries", f"{adaptive_summary};{ev_summary}",
                                 "--out", str(new_merged)])
                            adaptive_summary = new_merged

                            if monotonic_check and monotonic_report is not None:
                                run([sys.executable, str(scripts_dir/"monotonic_consistency_check.py"),
                                     "--variant_summary_csv", str(adaptive_summary),
                                     "--out", str(monotonic_report),
                                     "--min_n", str(monotonic_min_n),
                                     "--delta", str(monotonic_delta),
                                     "--use_smoothed_if_present"])
                                try:
                                    rep = json.loads(Path(monotonic_report).read_text(encoding="utf-8"))
                                except Exception:
                                    rep = {}
                                if str(rep.get("status","OK")).upper() == "OK":
                                    break


        # 7.62) Targeted action executor (non-evidence): apply safe dt reductions from action_plan
        if targeted_action_executor:
            try:
                apath = Path(action_plan)
            except Exception:
                apath = None
            if apath is not None and apath.exists():
                outJ = run_dir/"targeted_actions_applied.json"
                outM = run_dir/"targeted_actions_applied.md"
                allow_apply = (not skip_apply) or targeted_action_allow_when_hold
                cmdTA = [sys.executable, str(scripts_dir/"targeted_action_executor.py"),
                         "--action_plan_json", str(apath),
                         "--band_dt_presets", str(band_dt_presets_path),
                         "--dt_presets", str(dt_presets_path),
                         "--out_json", str(outJ),
                         "--out_md", str(outM),
                         "--min_multiplier", str(targeted_action_min_multiplier)]
                if allow_apply:
                    cmdTA += ["--apply"]
                try:
                    run(cmdTA)
                except SystemExit:
                    pass


        # 8) Propose updates from variant summary
        proposals = run_dir/"preset_update_proposals.csv"
        cmd = [sys.executable, str(scripts_dir/"propose_preset_updates_from_variant_summary.py"),
               "--variant_summary_csv", str(adaptive_summary),
               "--band_presets_json", str(cur_band_presets),
               "--min_pass_rate", str(min_pass_rate),
               "--min_ci_lo", str(min_ci_lo),
               "--out", str(proposals)]
        if band_aware_updates and failing_groups_json is not None:
            cmd += ["--only_groups_json", str(failing_groups_json)]
        if prefer_keep_if_pass:
            cmd += ["--prefer_keep_if_pass"]
        run(cmd)

        # 9) Apply updates to band presets for next iteration
        updated_band = run_dir/"band_dt_presets_updated.json"
        cmd = [sys.executable, str(scripts_dir/"apply_preset_updates.py"),
               "--presets_in", str(cur_band_presets),
               "--updates_csv", str(proposals),
               "--presets_out", str(updated_band),
               "--mode", "band"]
        if apply_only_gate_pass:
            cmd += ["--apply_only_gate_pass"]
        if monotonic_check:
            cmd += ["--blocklist_json", str(monotonic_report)]
        if 'skip_apply' in locals() and skip_apply:
            print("\n⛔ Action router hold_apply=true → skipping auto-apply presets this iteration.")
        else:
            run(cmd)

        cur_band_presets = updated_band

        # 10) Freeze intermediate evidence (best-effort)
        extra = freeze_extra[:]
        extra += [str(cur_band_presets), str(proposals), str(adaptive_summary)]
        cmd2 = [sys.executable, str(scripts_dir/"freeze_baseline_manifest.py"),
                "--out", str(baseline_manifest),
                "--stress_spec", str(stress_spec),
                "--stress_report", str(gate_report) if gate_report.exists() else "",
                "--extra_files", ";".join([x for x in extra if x]),
                "--overwrite"]
        try:
            run(cmd2)
        except SystemExit:
            pass

    print("\n❌ LOOP END: reached max_iters without passing stress gate.")
    raise SystemExit(3)

if __name__ == "__main__":
    main()
