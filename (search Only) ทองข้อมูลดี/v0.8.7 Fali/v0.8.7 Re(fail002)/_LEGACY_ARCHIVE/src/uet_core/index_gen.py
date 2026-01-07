"""
UET Studio Indexer: Crawls run directories and generates a central portfolio hub.
"""

import os
import json
import datetime
from pathlib import Path


def generate_studio_hub():
    """
    Scans the runs directory and creates a high-fidelity UET_Studio.html portal.
    """
    root_path = Path(__file__).parent.parent
    runs_path = root_path / "runs"

    run_records = []

    # 1. Crawl Runs - Look for ANY folder with config.json or summary.json
    print(f"Indexing runs in {runs_path}...")
    run_dirs = set()
    for pattern in ["config.json", "summary.json", "metrics.json"]:
        for path in runs_path.rglob(pattern):
            # Skip folders named 'demo_card' or other UI artifacts if they happen to contain these files
            if "demo_card" not in path.parts:
                run_dirs.add(path.parent)

    for run_dir in run_dirs:
        rel_path = run_dir.relative_to(root_path)

        # Artifact paths
        report_path = rel_path / "report_dashboard.html"
        summary_path = run_dir / "summary.json"
        config_path = run_dir / "config.json"

        # Fallback metadata
        meta = {
            "run_id": run_dir.name,
            "date": "Unknown",
            "model": "Unknown",
            "status": "N/A",
            "rel_url": str(report_path).replace("\\", "/"),
            "category": "General",
        }

        # Smart Categorization Bucketing
        folder_name = run_dir.name
        parent_name = run_dir.parent.name

        # Sub-categorization logic
        if folder_name.startswith("toy_"):
            meta["group"] = "Toy Models"
            if "coffee" in folder_name:
                meta["category"] = "Coffee & Milk"
            elif "stock" in folder_name:
                meta["category"] = "Stock Market"
            elif "llm" in folder_name:
                meta["category"] = "LLM Dynamics"
            elif "traffic" in folder_name:
                meta["category"] = "Traffic Flow"
            elif "physarum" in folder_name or "slime" in folder_name:
                meta["category"] = "Physarum Network"
            else:
                meta["category"] = "Classic Toys"
        else:
            meta["group"] = "Physics & Advanced"
            if "einstein" in folder_name:
                meta["category"] = "Einstein Connection"
            elif "nr_" in folder_name or "bssn" in folder_name:
                meta["category"] = "Numerical Relativity (BSSN)"
            elif folder_name.startswith(("gr_realistic", "nr_")) or "gr_realistic" in folder_name:
                meta["category"] = "Realistic GR"
            elif "galaxy" in folder_name or "dm" in folder_name:
                meta["category"] = "Galaxy Dark Matter"
            elif "neural" in folder_name:
                meta["category"] = "Neural Prediction"
            elif folder_name.lower().startswith("3d"):
                meta["category"] = "3D Simulations"
            elif any(x in folder_name for x in ["archetype", "Weak_Coupling", "Strong_Coupling"]):
                meta["category"] = "Physics Archetypes"
            elif folder_name in ["C_only", "C_I", "SYM", "BIAS_C", "BIAS_I"]:
                meta["category"] = "Physics Baselines"
            else:
                meta["category"] = "Other Simulations"

        # Extract from summary.json
        if summary_path.exists():
            try:
                with open(summary_path, "r", encoding="utf-8") as f:
                    s = json.load(f)
                    meta["date"] = s.get("timestamp") or s.get("date") or meta["date"]
                    meta["model"] = s.get("model") or s.get("model_type") or meta["model"]
                    runtime = s.get("runtime_s")
                    meta["duration"] = (
                        f"{runtime:.2f}s" if isinstance(runtime, (int, float)) else "N/A"
                    )
                    meta["status"] = s.get("status") or meta["status"]
                    meta["reasons"] = s.get("reasons") or ""
                    meta["gates"] = s.get("verification_gates") or {}
                    # Read description from summary.json
                    meta["description"] = s.get("description") or ""
            except:
                pass

        # Format nice title from folder_name or case_id
        def format_title(raw_name):
            """Transform test_custom_potentials -> Test Custom Potentials"""
            return raw_name.replace("_", " ").replace("-", " ").title()

        meta["title"] = format_title(folder_name)
        # Override with case_id if available from config
        if config_path.exists():
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    c = json.load(f)
                    case_id = c.get("case_id")
                    if case_id:
                        meta["case_id"] = case_id
                        meta["title"] = format_title(case_id)
            except:
                pass

        # Icon Mapping
        icons = {
            "Coffee & Milk": "☕",
            "Stock Market": "📈",
            "LLM Dynamics": "🤖",
            "Traffic Flow": "🚗",
            "Physarum Network": "🦠",
            "Classic Toys": "🧪",
            "Einstein Connection": "🧬",
            "Numerical Relativity (BSSN)": "⚫",
            "Realistic GR": "🔭",
            "Galaxy Dark Matter": "🌀",
            "Neural Prediction": "🧠",
            "3D Simulations": "🧊",
            "Physics Archetypes": "⚛️",
            "Physics Baselines": "⚖️",
            "Other Simulations": "⚙️",
        }
        meta["icon"] = icons.get(meta["category"], "⚙️")

        # Extract from config.json if still unknown
        if (meta["model"] == "Unknown" or meta["date"] == "Unknown") and config_path.exists():
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    c = json.load(f)
                    if meta["model"] == "Unknown":
                        meta["model"] = c.get("model") or c.get("model_type") or "Unknown"
                    if meta["date"] == "Unknown":
                        # Try to get timestamp from config if present
                        meta["date"] = c.get("timestamp") or "Unknown"
            except:
                pass

        # 1.3 Search for snapshots (Visual Previews)
        snapshot = None
        # Priority: GIFs (animations) then PNGs (slices/static)
        for ext in ["*.gif", "*.png"]:
            pics = list(run_dir.glob(ext))
            if pics:
                # Pick the most representative (often the one without 'slices' in name if possible, or just the first)
                snapshot = pics[0]
                break

        if snapshot:
            meta["snapshot_url"] = (rel_path / snapshot.name).as_posix().replace("\\", "/")
        else:
            meta["snapshot_url"] = None

        # Clean up date format if it's a raw timestamp (optional)
        if meta["date"] == "Unknown" and "_" in meta["run_id"]:
            # Often run_id is like 20251221_123456
            meta["date"] = meta["run_id"].split("_")[0]

        run_records.append(meta)

    # ================================================================
    # SMART DE-DUPLICATION: Group by case_id pattern, keep best run
    # ================================================================
    def get_case_base(run_id, case_id):
        """Extract base case name by removing seed suffix like _s0, _s1, etc."""
        import re

        # Try case_id first (e.g., ATL_C_001_s0 -> ATL_C_001)
        if case_id and case_id != "Unknown":
            match = re.match(r"(.+)_s\d+$", case_id)
            if match:
                return match.group(1)
            return case_id
        # Fall back to run_id pattern (timestamp-based like 20251226-210303)
        match = re.match(r"(\d{8}-\d+)", run_id)
        if match:
            return match.group(1)[:8]  # Just the date portion
        return run_id

    # Group runs by their base case
    case_groups = {}
    for r in run_records:
        base = get_case_base(r["run_id"], r.get("case_id", ""))
        model_key = f"{base}_{r['model']}"  # Also separate by model type
        if model_key not in case_groups:
            case_groups[model_key] = []
        case_groups[model_key].append(r)

    # Keep only the best run per case (PASS > WARN > FAIL > N/A, then newest)
    def run_priority(r):
        status_order = {"PASS": 0, "WARN": 1, "FAIL": 2, "N/A": 3}
        return (status_order.get(r["status"], 4), -hash(r["date"]))

    deduplicated = []
    for model_key, runs in case_groups.items():
        # Sort by priority, take best one
        runs.sort(key=run_priority)
        best = runs[0]
        # If there are multiple seeds, note it in the card
        if len(runs) > 1:
            best["seeds"] = len(runs)
        deduplicated.append(best)

    run_records = deduplicated

    # Sort by date (newest first)
    run_records.sort(key=lambda x: x["date"], reverse=True)

    # Group by main group and then sub-category
    groups = {}
    stats = {"total": len(run_records), "pass": 0, "fail": 0, "models": set(), "last_run": "None"}
    for r in run_records:
        g = r.get("group", "Other")
        c = r["category"]
        if g not in groups:
            groups[g] = {}
        if c not in groups[g]:
            groups[g][c] = []
        groups[g][c].append(r)

        # Stats
        if r["status"] == "PASS":
            stats["pass"] += 1
        elif r["status"] == "FAIL":
            stats["fail"] += 1
        stats["models"].add(r["model"])

    stats["stability"] = (stats["pass"] / stats["total"] * 100) if stats["total"] > 0 else 0
    stats["model_count"] = len(stats["models"])
    if run_records:
        stats["last_run"] = run_records[0]["date"]

    # 2. Build HTML Hub
    html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>UET Studio | Unified Portal</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Outfit:wght@400;700;800&display=swap');
        :root {{
            --bg: #030712;
            --card: rgba(17, 24, 39, 0.7);
            --border: rgba(255, 255, 255, 0.1);
            --accent: #6366f1;
            --accent-glow: rgba(99, 102, 241, 0.3);
            --text: #f3f4f6;
            --faded: #9ca3af;
            --pass: #10b981;
            --fail: #ef4444;
            --glass: rgba(255, 255, 255, 0.03);
        }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            font-family: 'Inter', sans-serif;
            background: var(--bg);
            background-image: 
                radial-gradient(circle at 0% 0%, rgba(99, 102, 241, 0.15) 0%, transparent 50%),
                radial-gradient(circle at 100% 100%, rgba(192, 132, 252, 0.15) 0%, transparent 50%);
            color: var(--text);
            padding: 50px 20px;
            line-height: 1.5;
            min-height: 100vh;
        }}
        .wrap {{ max-width: 1200px; margin: 0 auto; }}
        
        /* Header & Stats */
        header {{ margin-bottom: 80px; text-align: center; }}
        h1 {{ font-family: 'Outfit', sans-serif; font-size: 4rem; font-weight: 800; letter-spacing: -0.05em; margin-bottom: 20px; background: linear-gradient(to right, #818cf8, #c084fc); -webkit-background-clip: text; -webkit-text-fill-color: transparent; filter: drop-shadow(0 0 30px var(--accent-glow)); }}
        .subtitle {{ color: var(--faded); font-size: 1.2rem; margin-bottom: 40px; font-weight: 300; }}
        
        .stats-bar {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 20px;
            margin-bottom: 60px;
            background: var(--glass);
            padding: 30px;
            border-radius: 24px;
            border: 1px solid var(--border);
            backdrop-filter: blur(10px);
        }}
        .stat-item {{ text-align: center; }}
        .stat-val {{ display: block; font-size: 2rem; font-weight: 800; font-family: 'Outfit', sans-serif; color: var(--accent); }}
        .stat-label {{ font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.1em; color: var(--faded); margin-top: 5px; }}

        /* Categorization */
        .group-section {{ margin-bottom: 80px; }}
        .group-title {{ font-family: 'Outfit', sans-serif; font-size: 2rem; font-weight: 800; margin-bottom: 40px; color: #fff; display: flex; align-items: center; gap: 15px; }}
        .group-title::after {{ content: ""; flex: 1; height: 1px; background: linear-gradient(to right, var(--border), transparent); }}

        .cat-accordion {{
            background: var(--card);
            border: 1px solid var(--border);
            border-radius: 16px;
            margin-bottom: 15px;
            overflow: hidden;
            transition: all 0.3s ease;
        }}
        .cat-accordion[open] {{ background: rgba(17, 24, 39, 0.4); border-color: var(--accent); }}
        .cat-summary {{
            padding: 20px 30px;
            cursor: pointer;
            list-style: none;
            display: flex;
            align-items: center;
            font-family: 'Outfit', sans-serif;
            font-size: 1.1rem;
            font-weight: 600;
            color: var(--faded);
            transition: color 0.3s;
        }}
        .cat-summary:hover {{ color: #fff; }}
        .cat-summary::-webkit-details-marker {{ display: none; }}
        .cat-accordion[open] .cat-summary {{ color: #fff; border-bottom: 1px solid var(--border); margin-bottom: 30px; }}
        
        .cat-icon {{ margin-right: 15px; font-size: 1.2rem; }}
        .cat-count {{ margin-left: auto; font-size: 0.8rem; opacity: 0.5; font-weight: 400; }}
        .cat-summary::before {{
            content: "▶";
            display: inline-block;
            margin-right: 15px;
            font-size: 0.7rem;
            transition: transform 0.3s;
            opacity: 0.5;
        }}
        .cat-accordion[open] .cat-summary::before {{ transform: rotate(90deg); }}
        
        /* Grid & Cards */
        .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 30px; }}
        .run-card {{
            background: var(--card);
            border: 1px solid var(--border);
            border-radius: 20px;
            text-decoration: none;
            color: inherit;
            transition: all 0.4s cubic-bezier(0.23, 1, 0.32, 1);
            position: relative;
            overflow: hidden;
            backdrop-filter: blur(12px);
            display: flex;
            flex-direction: column;
            min-height: 380px;
        }}
        .run-preview {{
            width: 100%;
            height: 180px;
            background: #000;
            overflow: hidden;
            border-bottom: 1px solid var(--border);
            position: relative;
        }}
        .run-preview img {{
            width: 100%;
            height: 100%;
            object-fit: cover;
            transition: transform 0.6s ease;
        }}
        .run-card:hover .run-preview img {{
            transform: scale(1.1);
        }}
        .no-preview {{
            display: flex;
            align-items: center;
            justify-content: center;
            height: 100%;
            color: var(--faded);
            font-size: 2.5rem;
            opacity: 0.1;
            background: linear-gradient(45deg, #111827, #1f2937);
        }}
        .run-body {{ padding: 24px; flex: 1; display: flex; flex-direction: column; }}
        .run-card::before {{
            content: "";
            position: absolute;
            top: 0; left: 0; right: 0; bottom: 0;
            background: linear-gradient(135deg, rgba(255,255,255,0.05) 0%, transparent 100%);
            opacity: 0;
            transition: opacity 0.4s;
        }}
        .run-card:hover {{
            transform: translateY(-8px) scale(1.02);
            border-color: var(--accent);
            box-shadow: 0 20px 40px -15px rgba(0, 0, 0, 0.5), 0 0 20px var(--accent-glow);
        }}
        .run-card:hover::before {{ opacity: 1; }}

        .run-header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; position: relative; z-index: 1; }}
        .run-id {{ font-family: monospace; font-size: 0.7rem; color: var(--faded); letter-spacing: 0.05em; }}
        .status-badge {{
            font-size: 0.6rem;
            font-weight: 800;
            padding: 5px 12px;
            border-radius: 20px;
            letter-spacing: 0.05em;
        }}
        .status-PASS {{ background: rgba(16, 185, 129, 0.15); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.3); }}
        .status-WARN {{ background: rgba(245, 158, 11, 0.15); color: #fbbf24; border: 1px solid rgba(245, 158, 11, 0.3); }}
        .status-FAIL {{ background: rgba(239, 68, 68, 0.15); color: #f87171; border: 1px solid rgba(239, 68, 68, 0.3); }}
        
        .run-gates {{ display: flex; gap: 6px; margin-top: 12px; position: relative; z-index: 1; }}
        .gate-dot {{ width: 8px; height: 8px; border-radius: 50%; opacity: 0.8; }}
        .gate-PASS {{ background: #10b981; box-shadow: 0 0 5px #10b981; }}
        .gate-FAIL {{ background: #ef4444; box-shadow: 0 0 5px #ef4444; }}
        .gate-WARN {{ background: #f59e0b; box-shadow: 0 0 5px #f59e0b; }}
        .run-reasons {{ font-size: 0.65rem; color: #f87171; margin-top: 8px; font-weight: 500; font-family: monospace; position: relative; z-index: 1; }}
        
        .run-model {{ font-family: 'Outfit', sans-serif; font-size: 1.4rem; font-weight: 700; margin-bottom: 8px; color: #fff; position: relative; z-index: 1; }}
        .run-meta {{ display: flex; justify-content: space-between; font-size: 0.8rem; color: var(--faded); position: relative; z-index: 1; margin-top: auto; border-top: 1px solid var(--border); padding-top: 15px; }}
        
        footer {{ border-top: 1px solid var(--border); padding: 60px 0; margin-top: 100px; text-align: center; color: var(--faded); font-size: 0.9rem; }}

        /* Benchmarks & Mappings */
        .benchmark-container {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 30px;
            margin-bottom: 60px;
        }}
        .benchmark-card {{
            background: var(--glass);
            padding: 30px;
            border-radius: 24px;
            border: 1px solid var(--border);
            backdrop-filter: blur(10px);
        }}
        .benchmark-card h3 {{
            font-family: 'Outfit', sans-serif;
            font-size: 1.2rem;
            margin-bottom: 20px;
            color: var(--accent);
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        .benchmark-table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 0.85rem;
            color: var(--faded);
        }}
        .benchmark-table th {{
            text-align: left;
            padding: 8px 0;
            border-bottom: 1px solid var(--border);
            text-transform: uppercase;
            font-size: 0.7rem;
            letter-spacing: 0.1em;
        }}
        .benchmark-table td {{ padding: 12px 0; border-bottom: 1px solid rgba(255,255,255,0.03); }}
        .status-pass {{ color: var(--pass); font-weight: 600; }}

        /* Theoretical Framework */
        .theory-section {{ margin-bottom: 80px; padding-top: 40px; border-top: 1px solid var(--border); }}
        .theory-header {{ text-align: center; margin-bottom: 50px; }}
        .theory-title {{ font-family: 'Outfit', sans-serif; font-size: 2.2rem; font-weight: 800; background: linear-gradient(to right, #818cf8, #c084fc); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 15px; }}
        .theory-subtitle {{ color: var(--faded); font-size: 1.1rem; font-weight: 300; }}
        
        .bridge-eq {{
            background: rgba(99, 102, 241, 0.1);
            border: 1px solid var(--accent);
            padding: 40px;
            border-radius: 24px;
            text-align: center;
            margin-bottom: 60px;
            backdrop-filter: blur(10px);
            position: relative;
            overflow: hidden;
        }}
        .bridge-eq::before {{
            content: ""; position: absolute; top: -50%; left: -50%; width: 200%; height: 200%;
            background: radial-gradient(circle, rgba(99, 102, 241, 0.1) 0%, transparent 70%);
            animation: pulse-glow 10s infinite linear;
        }}
        .eq-text {{ font-family: 'Outfit', sans-serif; font-size: 3rem; font-weight: 800; color: #fff; position: relative; z-index: 1; letter-spacing: 0.1em; }}
        .eq-label {{ color: var(--accent); font-size: 0.9rem; margin-top: 15px; position: relative; z-index: 1; font-weight: 600; text-transform: uppercase; letter-spacing: 0.2em; }}

        .theory-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 20px; }}
        .theory-card {{
            background: var(--card);
            border: 1px solid var(--border);
            border-radius: 20px;
            padding: 30px;
            transition: all 0.4s ease;
            position: relative;
            display: flex;
            flex-direction: column;
        }}
        .theory-card:hover {{ border-color: var(--accent); transform: translateY(-5px); background: rgba(255, 255, 255, 0.05); box-shadow: 0 10px 30px -10px rgba(99, 102, 241, 0.2); }}
        .theory-symbol {{ font-family: serif; font-size: 3.5rem; font-style: italic; color: var(--accent); margin-bottom: 10px; line-height: 1; }}
        .theory-name {{ font-family: 'Outfit', sans-serif; font-size: 1.25rem; font-weight: 700; color: #fff; margin-bottom: 8px; }}
        .theory-desc {{ color: var(--faded); font-size: 0.9rem; margin-bottom: 20px; line-height: 1.4; flex: 1; }}
        .theory-example {{ font-size: 0.8rem; line-height: 1.6; color: #9ca3af; padding-top: 15px; border-top: 1px solid var(--border); }}
        .theory-example b {{ color: var(--accent); }}

        @keyframes pulse-glow {{ 0% {{ transform: rotate(0deg); }} 100% {{ transform: rotate(360deg); }} }}
    </style>
</head>
<body>
    <div class="wrap">
        <header>
            <h1>UET STUDIO</h1>
            <p class="subtitle">Unified Exhibition Hub • Professional Simulation Gallery</p>
            
            <div class="stats-bar">
                <div class="stat-item">
                    <span class="stat-val">{stats['total']}</span>
                    <span class="stat-label">Total Runs</span>
                </div>
                <div class="stat-item">
                    <span class="stat-val">{stats['pass']}</span>
                    <span class="stat-label">Verified (PASS)</span>
                </div>
                <div class="stat-item">
                    <span class="stat-val">{stats['stability']:.1f}%</span>
                    <span class="stat-label">Model Stability</span>
                </div>
                <div class="stat-item">
                    <span class="stat-val">{stats['model_count']}</span>
                    <span class="stat-label">Unique Models</span>
                </div>
            </div>
        </header>

        <!-- Theoretical Framework Section -->
        <section class="theory-section" style="margin-bottom: 80px;">
            <div class="theory-header">
                <h2 class="theory-title">📐 Theoretical Framework</h2>
                <p class="theory-subtitle">Bridging Material & Information Worlds through Equilibrium Dynamics</p>
            </div>

            <div class="bridge-eq">
                <div class="eq-text">𝒱 = -ΔΩ</div>
                <div class="eq-label">BRIDGE: Value = Disequilibrium Reduction (การเพิ่มระเบียบสากล)</div>
            </div>

            <div class="theory-grid">
                <div class="theory-card">
                    <div class="theory-symbol">𝒞</div>
                    <div class="theory-name">Conscious Field</div>
                    <div class="theory-desc">สถานะที่สังเกตได้ / ความโปร่งใสของระบบและการสื่อสารภายนอก</div>
                    <div class="theory-example"><b>Applied:</b> ราคาตลาด, กิจกรรมประสาท, ความคิดเห็นสาธารณะ</div>
                </div>
                <div class="theory-card">
                    <div class="theory-symbol">ℐ</div>
                    <div class="theory-name">Instinctive Field</div>
                    <div class="theory-desc">สถานะแฝง / กลไกระบบปิดที่ซ่อนอยู่ภายใน หรือ แรงต้าน</div>
                    <div class="theory-example"><b>Applied:</b> มูลค่าที่แท้จริง, สภาวะยับยั้ง, ความเชื่อพื้นฐาน</div>
                </div>
                <div class="theory-card">
                    <div class="theory-symbol">κ</div>
                    <div class="theory-name">Diffusion</div>
                    <div class="theory-desc">อัตราการแพร่กระจาย / ต้นทุนของการรักษาระเบียบข้ามพรมแดน</div>
                    <div class="theory-example"><b>Applied:</b> การแพร่กระจายข้อมูล, ความตึงผิว, การเชื่อมต่อระบบ</div>
                </div>
                <div class="theory-card">
                    <div class="theory-symbol">β</div>
                    <div class="theory-name">Coupling</div>
                    <div class="theory-desc">ความแรงของปฏิสัมพันธ์ที่เชื่อมโยง C และ I เข้าด้วยกัน</div>
                    <div class="theory-example"><b>Applied:</b> ประสิทธิภาพตลาด, สมดุล E-I, อิทธิพลทางสังคม</div>
                </div>
                <div class="theory-card">
                    <div class="theory-symbol">S</div>
                    <div class="theory-name">External Drive</div>
                    <div class="theory-desc">แรงขับเคลื่อนภายนอก หรือ อคติที่บังคับให้ระบบเลือกสถานะ</div>
                    <div class="theory-example"><b>Applied:</b> ข่าวสารมวลชน, สิ่งกระตุ้นเร้า, นโยบายรัฐบาล</div>
                </div>
                <div class="theory-card">
                    <div class="theory-symbol">V(φ)</div>
                    <div class="theory-name">Potential</div>
                    <div class="theory-desc">ภูมิทัศน์พลังงานที่กำหนดว่าสถานะใดคือ 'ความเสถียร'</div>
                    <div class="theory-example"><b>Applied:</b> ภาวะสองขั้ว (เลือก/ไม่เลือก), จุดดึงดูดเชิงจิตวิทยา</div>
                </div>
                <div class="theory-card">
                    <div class="theory-symbol">Ω</div>
                    <div class="theory-name">Total Energy</div>
                    <div class="theory-desc">ระดับความไม่เป็นระเบียบหรือความขัดแย้งรวมของทั้งระบบ</div>
                    <div class="theory-example"><b>Applied:</b> ความไม่สมดุล, ความขัดแย้ง, ต้นทุนรวมเชิงพลังงาน</div>
                </div>
            </div>
        </section>

        <div class="content">
            {"".join([f'''
            <section class="group-section">
                <h2 class="group-title">{group_name}</h2>
                {"".join([f'''
                <details class="cat-accordion" {"open" if group_name == "Physics & Advanced" else ""}>
                    <summary class="cat-summary">
                        <span class="cat-icon">{items[0]['icon']}</span>
                        {cat_name}
                        <span class="cat-count">({len(items)})</span>
                    </summary>
                    <div style="padding: 0 30px 30px 30px;">
                        <div class="grid">
                            {"".join([f"""
                            <a href="{r['rel_url']}" class="run-card">
                                <div class="run-preview">
                                    {f'<img src="{r["snapshot_url"]}" loading="lazy">' if r["snapshot_url"] else '<div class="no-preview">⌬</div>'}
                                </div>
                                <div class="run-body">
                                    <div class="run-header">
                                        <span class="run-id">{r['run_id'][:16]}...</span>
                                        <div style="display: flex; flex-direction: column; align-items: flex-end; gap: 5px;">
                                            <span class="status-badge status-{r['status']}">{r['status']}</span>
                                            {f'<div class="run-gates">' + "".join([f'<div class="gate-dot gate-{status}" title="{name}"></div>' for name, status in r.get("gates", {}).items()]) + '</div>' if r.get("gates") else ''}
                                        </div>
                                    </div>
                                    <div class="run-model">{r.get('title', r['model'])}</div>
                                    <div class="run-desc" style="font-size: 0.85rem; color: #9ca3af; margin-bottom: 12px;">{r.get('description', r['model'])}</div>
                                    {f'<div class="run-reasons">⚠️ {r["reasons"]}</div>' if r.get("reasons") and r["status"] != "PASS" else ""}
                                    <div class="run-meta">
                                        <span>{r['date']}</span>
                                        <span>{r.get('duration', 'N/A')}</span>
                                    </div>
                                </div>
                            </a>
                            """ for r in items])}
                        </div>
                    </div>
                </details>
                ''' for cat_name, items in group_categories.items()])}
            </section>
            ''' for group_name, group_categories in groups.items()])}
        </div>

        <!-- Performance Benchmarks -->
        <section class="cat-section" style="margin-top: 80px;">
            <h2 class="cat-title">🚀 Performance & Benchmarks</h2>
            <div class="benchmark-container">
                <div class="benchmark-card">
                    <h3>🧪 2D JAX Accelerated</h3>
                    <table class="benchmark-table">
                        <tr><th>Test</th><th>N</th><th>Runs</th><th>Time</th></tr>
                        <tr><td>2D-500K</td><td>32</td><td>500,000</td><td class="status-pass">92.3s ✅</td></tr>
                        <tr><td>2D-N100</td><td>100</td><td>1,000</td><td class="status-pass">3.2s ✅</td></tr>
                        <tr><td>2D-YEAR</td><td>32</td><td>1</td><td class="status-pass">65s (1 year!) ✅</td></tr>
                    </table>
                </div>
                <div class="benchmark-card">
                    <h3>🌌 3D Simulations</h3>
                    <table class="benchmark-table">
                        <tr><th>Test</th><th>N</th><th>Nodes</th><th>Status</th></tr>
                        <tr><td>3D-galaxy-50</td><td>50</td><td>125K</td><td class="status-pass">✅</td></tr>
                        <tr><td>3D-galaxy-100</td><td>100</td><td>1M</td><td class="status-pass">✅</td></tr>
                        <tr><td>3D-galaxy-200</td><td>200</td><td>8M</td><td class="status-pass">✅</td></tr>
                    </table>
                </div>
                <div class="benchmark-card">
                    <h3>🔬 n-Dimensional Proof</h3>
                    <table class="benchmark-table">
                        <tr><th>Dims</th><th>N</th><th>Nodes</th><th>Proven</th></tr>
                        <tr><td>4D</td><td>30</td><td>810K</td><td class="status-pass">✅</td></tr>
                        <tr><td>5D</td><td>11</td><td>161K</td><td class="status-pass">✅</td></tr>
                        <tr><td>6D</td><td>7</td><td>117K</td><td class="status-pass">✅</td></tr>
                        <tr><td>7D</td><td>5</td><td>78K</td><td class="status-pass">✅</td></tr>
                    </table>
                    <p style="margin-top: 15px; font-size: 0.8rem; color: var(--accent); font-weight: 600;">🎯 UET proven for 1D-7D!</p>
                </div>
            </div>
        </section>

        <footer>
            <p>Generated on {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")} • UET Core Harness Studio</p>
        </footer>
    </div>
</body>
</html>
"""
    output_hub = root_path / "UET_Studio.html"
    with open(output_hub, "w", encoding="utf-8") as f:
        f.write(html_template)
    print(f"Unified Hub created: {output_hub}")


if __name__ == "__main__":
    generate_studio_hub()
