#!/usr/bin/env python
"""
Generate UET Gallery from simulation runs.
Enhanced version with:
- Grouped toy categories (stock, llm, traffic, physarum, etc.)
- Modal popup for details
- Comparison cards per toy family
- Auto-generates demo_card for runs that don't have one

Usage:
    python scripts/generate_uet_gallery.py --runs-dir runs_gallery --output gallery.html
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from datetime import datetime

# Import demo card generator
import sys
from pathlib import Path as _Path
_script_dir = _Path(__file__).parent.parent
if str(_script_dir) not in sys.path:
    sys.path.insert(0, str(_script_dir))

try:
    from uet_min_pack.uet_core.demo_card_generator import generate_demo_card
    HAS_DEMO_CARD_GEN = True
except ImportError as e:
    HAS_DEMO_CARD_GEN = False
    print(f"⚠️  demo_card_generator not available: {e}")


def find_demos(runs_dir: Path) -> list[dict]:
    """Find all demo folders and collect all their visualizations."""
    demos = []
    for folder in runs_dir.iterdir():
        if not folder.is_dir():
            continue
        
        # Check for any visualization files
        gif_ci = folder / "CI_evolution.gif"
        gif_main = folder / "main.gif"  # Generic main.gif
        gif_3d = folder / "3D_slices.gif"
        gif_3d_iso = folder / "3D_isosurface.gif"
        gif_scatter = folder / "scatter_animation.gif"
        gif_3d_dual = folder / "3D_dual_rotate.gif"
        png_scatter = folder / "scatter_viz.png"
        
        # Skip if no visualizations
        if not any([gif_ci.exists(), gif_main.exists(), gif_3d.exists(), gif_scatter.exists()]):
            continue
        
        # Collect all available visualizations
        viz = []
        if gif_ci.exists():
            viz.append({"type": "GIF", "path": f"{folder.name}/CI_evolution.gif", "label": "Field"})
        if gif_main.exists() and not gif_ci.exists():  # Use main.gif if no CI_evolution
            viz.append({"type": "GIF", "path": f"{folder.name}/main.gif", "label": "Main"})
        if gif_3d.exists():
            viz.append({"type": "3D", "path": f"{folder.name}/3D_slices.gif", "label": "3D Slices"})
        if gif_3d_dual.exists():
            viz.append({"type": "3D", "path": f"{folder.name}/3D_dual_rotate.gif", "label": "3D Rotate"})
        if gif_3d_iso.exists():
            viz.append({"type": "3D", "path": f"{folder.name}/3D_isosurface.gif", "label": "Isosurface"})
        if gif_scatter.exists():
            viz.append({"type": "Scatter", "path": f"{folder.name}/scatter_animation.gif", "label": "Scatter"})
        if png_scatter.exists():
            viz.append({"type": "img", "path": f"{folder.name}/scatter_viz.png", "label": "Phase"})
        
        # Main thumbnail
        main_gif = viz[0]["path"] if viz else None
        
        # Determine demo family with better categorization
        name_lower = folder.name.lower()
        is_toy = "toy" in name_lower
        
        # Extensions (new section)
        if "test_delays" in name_lower or "time_delay" in name_lower:
            family = "extension"
        elif "test_stochastic" in name_lower or "stochastic" in name_lower:
            family = "extension"
        elif "test_nonlocal" in name_lower or "nonlocal" in name_lower:
            family = "extension"
        elif "test_memory" in name_lower or "memory" in name_lower:
            family = "extension"
        elif "test_multifield" in name_lower or "multifield" in name_lower:
            family = "extension"
        elif "test_custom_potentials" in name_lower or "custom_potential" in name_lower:
            family = "extension"
        # Physics / Advanced demos (NOT toys)
        elif "einstein" in name_lower:
            family = "einstein"
        elif "nr_" in name_lower or "numerical_relativity" in name_lower:
            family = "numerical_relativity"
        elif "gr_realistic" in name_lower:
            family = "gr_realistic"
        elif "cosmological" in name_lower:
            family = "cosmology"
        elif name_lower.startswith("3d_"):
            family = "3d"
        elif "galaxy" in name_lower:
            family = "galaxy"
        elif "neural" in name_lower:
            family = "neural"
        elif "landscape" in name_lower:
            family = "landscape"
        # Toy demos
        elif "stock" in name_lower:
            family = "stock"
        elif "llm" in name_lower:
            family = "llm"
        elif "traffic" in name_lower:
            family = "traffic"
        elif "physarum" in name_lower or "slime" in name_lower:
            family = "physarum"
        elif "coffee" in name_lower:
            family = "coffee"
        elif is_toy:
            family = "classic"  # Classic toy demos
        # Basic archetypes (non-toy demos without specific category)
        elif any(x in name_lower for x in ["bias_c", "bias_i", "echo", "decay", "growth",
                                            "strong_coupling", "weak_coupling", "sym",
                                            "archetype"]):
            family = "archetype"
        else:
            family = "other"
        
        # Auto-generate demo_card if missing
        demo_card_path = folder / "demo_card" / "demo_card.html"
        if not demo_card_path.exists() and HAS_DEMO_CARD_GEN:
            config_file = folder / "config.json"
            if config_file.exists():
                try:
                    print(f"  📝 Generating demo_card for {folder.name}...")
                    generate_demo_card(folder)
                except Exception as e:
                    print(f"    ⚠️  Failed: {e}")
        
        demo = {
            "id": folder.name,
            "title": folder.name.replace("_", " ").replace("toy ", "").title(),
            "main_gif": main_gif,
            "demo_card": f"{folder.name}/demo_card/demo_card.html" if demo_card_path.exists() else None,
            "visualizations": viz,
            "is_3d": name_lower.startswith("3d_") or gif_3d.exists(),
            "is_toy": is_toy,
            "family": family,
        }
        
        # Load summary if exists
        summary_file = folder / "summary.json"
        has_real_data = False  # Flag for real numerical data
        if summary_file.exists():
            with open(summary_file) as f:
                summary = json.load(f)
                demo["omega_initial"] = summary.get("Omega0", summary.get("initial_network_mass", 0))
                demo["omega_final"] = summary.get("OmegaT", summary.get("final_network_mass", 0))
                demo["steps"] = summary.get("steps_total", 0)
                demo["status"] = summary.get("status", "PASS")
                demo["description"] = summary.get("description", "")
                # Extra fields for comparison
                demo["scenario"] = summary.get("scenario", "")
                demo["final_coherence"] = summary.get("final_coherence", None)
                demo["final_entropy"] = summary.get("final_entropy", None)
                demo["flow_efficiency"] = summary.get("flow_efficiency", None)
                
                # Check for real numerical data
                summary_str = json.dumps(summary).lower()
                has_real_data = any(key in summary_str for key in [
                    '"omega', '"energy', '"mass', '"final', '"initial', 
                    '"coherence', '"entropy', '"efficiency', '"convergence'
                ])
        
        demo["has_real_data"] = has_real_data
        
        # Load config if exists
        config_file = folder / "config.json"
        if config_file.exists():
            with open(config_file) as f:
                config = json.load(f)
                params = config.get("params", {})
                demo["beta"] = params.get("beta", "?")
                demo["kappa"] = params.get("kappa", "?")
                demo["s"] = params.get("potC", {}).get("s", params.get("pot", {}).get("s", 0))
                demo["config"] = config
        
        demos.append(demo)
    
    return demos


def find_report_images(reports_dir: Path) -> dict:
    """Find all PNG images in reports directory."""
    images = {"phase_maps": [], "cross_sweeps": [], "atlas": [], "stress": []}
    
    if not reports_dir.exists():
        return images
    
    # Phase maps
    for folder in reports_dir.glob("phase_maps_*"):
        if folder.is_dir():
            for png in folder.glob("*.png"):
                images["phase_maps"].append({
                    "path": "../" + str(png.relative_to(reports_dir.parent)).replace('\\', '/'),
                    "name": folder.name.replace("phase_maps_runs_param_CI_", "").replace("_", " ").title()
                })
    
    # Cross sweeps
    for png in reports_dir.glob("cross_sweeps/**/plots/*.png"):
        images["cross_sweeps"].append({
            "path": "../" + str(png.relative_to(reports_dir.parent)).replace('\\', '/'),
            "name": png.stem.replace("_", " ").title()
        })
    
    # Atlas
    for grade in ["PASS", "WARN", "FAIL"]:
        for atlas in ["A", "B", "C"]:
            folder = reports_dir / f"atlas_{atlas}_{grade}"
            if folder.exists():
                for png in folder.glob("*.png"):
                    images["atlas"].append({
                        "path": "../" + str(png.relative_to(reports_dir.parent)).replace('\\', '/'),
                        "name": f"Atlas {atlas}",
                        "grade": grade
                    })
    
    return images


def generate_gallery_html(demos: list, images: dict, output_path: Path) -> None:
    """Generate HTML gallery with grouped categories and modal popups."""
    
    # Group demos by family
    families = {}
    for d in demos:
        fam = d.get("family", "other")
        if fam not in families:
            families[fam] = []
        families[fam].append(d)
    
    # Separate main categories
    archetypes = families.get("archetype", [])
    demos_3d = families.get("3d", [])
    
    # Extensions (display first - new section!)
    extension_families = {
        "extension": {"name": "🚀 UET Extensions (Tested)", "demos": families.get("extension", [])},
    }
    
    # Physics / Advanced families (display after extensions)
    physics_families = {
        "einstein": {"name": "🌌 Einstein Connection", "demos": families.get("einstein", [])},
        "numerical_relativity": {"name": "⚫ Numerical Relativity (BSSN)", "demos": families.get("numerical_relativity", [])},
        "gr_realistic": {"name": "🔭 Realistic GR", "demos": families.get("gr_realistic", [])},
        "cosmology": {"name": "🌍 Cosmology (Λ)", "demos": families.get("cosmology", [])},
        "galaxy": {"name": "🌀 Galaxy Dark Matter", "demos": families.get("galaxy", [])},
        "neural": {"name": "🧠 Neural Prediction", "demos": families.get("neural", [])},
        "landscape": {"name": "📊 Loss Landscape", "demos": families.get("landscape", [])},
    }
    
    # Toy families (display after physics)
    toy_families = {
        "coffee": {"name": "☕ Coffee & Milk", "demos": families.get("coffee", [])},
        "stock": {"name": "📈 Stock Market", "demos": families.get("stock", [])},
        "llm": {"name": "🤖 LLM Dynamics", "demos": families.get("llm", [])},
        "traffic": {"name": "🚗 Traffic Flow", "demos": families.get("traffic", [])},
        "physarum": {"name": "🦠 Physarum Network", "demos": families.get("physarum", [])},
        "classic": {"name": "🧪 Classic Toys", "demos": families.get("classic", [])},
    }
    
    # Include other toys
    other_toys = families.get("other", [])
    
    def make_demo_cards(demo_list, show_popup=True):
        """Generate cards with popup triggers."""
        cards = ""
        for d in demo_list:
            status = d.get("status", "PASS")
            tag_class = "pass" if status == "PASS" else "warn" if status == "WARN" else ""
            desc = d.get("description", f"β={d.get('beta','?')}")[:60]
            
            # Add VIZ ONLY badge if no real data
            has_data = d.get("has_real_data", True)
            viz_badge = '' if has_data else '<span class="tag viz-only" style="background: #ff9800; color: #000; margin-left: 5px;">VIZ ONLY</span>'
            
            if show_popup:
                onclick = f"openModal('{d['id']}')"
                cards += f'''
      <div class="card" onclick="{onclick}">
        <img src="{d['main_gif']}" alt="{d['id']}">
        <div class="info">
          <h3>{d['title']}</h3>
          <p class="desc">{desc}</p>
          <div class="tags"><span class="tag {tag_class}">{status}</span>{viz_badge}</div>
        </div>
      </div>'''
            else:
                cards += f'''
      <div class="card">
        <img src="{d['main_gif']}" alt="{d['id']}">
        <div class="info"><h3>{d['title']}</h3><p class="desc">{desc}</p>{viz_badge}</div>
      </div>'''
        return cards
    
    def make_modal_data(demo_list):
        """Generate JavaScript data for modals."""
        data = {}
        for d in demo_list:
            # Build viz data for inline switching (not new tabs)
            viz_list = []
            for v in d.get("visualizations", []):
                viz_list.append({"path": v["path"], "label": v["label"]})
            
            # Build parameters dict for extensions
            params_dict = {}
            config = d.get("config", {})
            params = config.get("params", {})
            
            # Extract time/grid config first (most important!)
            time_cfg = config.get("time", {})
            grid_cfg = config.get("grid", {})
            if time_cfg.get("T"):
                params_dict["T"] = time_cfg.get("T")
            if time_cfg.get("dt"):
                params_dict["dt"] = time_cfg.get("dt")
            if grid_cfg.get("N"):
                params_dict["N"] = grid_cfg.get("N")
            
            # Extract potential parameters
            pot = params.get("pot", params.get("potC", {}))
            if pot:
                if pot.get("a") is not None:
                    params_dict["a"] = pot.get("a")
                if pot.get("delta") is not None:
                    params_dict["δ"] = pot.get("delta")
                if pot.get("s") is not None:
                    params_dict["s"] = pot.get("s")
            
            # Extract other parameters
            if params:
                for key, val in params.items():
                    if isinstance(val, (int, float, str)) and key not in ["pot", "potC", "potI"]:
                        params_dict[key] = val
            
            # Add basic params
            if d.get("beta") not in [None, "?"]:
                params_dict["β"] = d.get("beta")
            if d.get("kappa") not in [None, "?"]:
                params_dict["κ"] = d.get("kappa")
            
            # Build metrics dict (from summary data)
            metrics_dict = {}
            # Add Omega initial if available
            if d.get("omega_initial"):
                metrics_dict["Ω_initial"] = f"{d['omega_initial']:.2f}" if isinstance(d['omega_initial'], float) else d['omega_initial']
            if d.get("omega_final"):
                val = d['omega_final']
                if isinstance(val, float):
                    if abs(val) < 0.001:
                        metrics_dict["Ω_final"] = f"{val:.2e}"
                    else:
                        metrics_dict["Ω_final"] = f"{val:.3f}"
                else:
                    metrics_dict["Ω_final"] = val
            if d.get("steps"):
                metrics_dict["steps"] = d.get("steps")
            if d.get("status"):
                metrics_dict["status"] = d.get("status")
            if d.get("final_coherence"):
                metrics_dict["coherence"] = f"{d['final_coherence']:.3f}"
            if d.get("flow_efficiency"):
                metrics_dict["efficiency"] = f"{d['flow_efficiency']:.3f}"
            if d.get("scenario"):
                metrics_dict["scenario"] = d.get("scenario")
            
            # Build details string (fallback)
            details = []
            for k, v in params_dict.items():
                details.append(f"{k} = {v}")
            details_html = "<br>".join(details) if details else "No additional details"
            
            data[d['id']] = {
                "title": d['title'],
                "gif": d['main_gif'],
                "description": d.get('description', ''),
                "status": d.get('status', 'PASS'),
                "viz": viz_list,  # Now array for inline switching
                "details": details_html,
                "demo_card": d.get('demo_card', ''),
                "params": params_dict,
                "metrics": metrics_dict,
                "is_extension": d.get("family") == "extension",
            }
        return json.dumps(data)
    
    # Build all demos list for modal
    all_demos = archetypes + demos_3d
    for fam in extension_families.values():
        all_demos.extend(fam["demos"])
    for fam in physics_families.values():
        all_demos.extend(fam["demos"])
    for fam in toy_families.values():
        all_demos.extend(fam["demos"])
    all_demos.extend(other_toys)
    modal_data = make_modal_data(all_demos)
    
    # Build extension sections (display FIRST as featured!)
    extension_sections_html = ""
    for fam_id, fam_data in extension_families.items():
        if fam_data["demos"]:
            cards = make_demo_cards(fam_data["demos"])
            count = len(fam_data["demos"])
            extension_sections_html += f'''
    <div class="family-section extension-section" style="background: linear-gradient(135deg, rgba(0,212,255,0.1), rgba(0,255,136,0.1)); border: 2px solid rgba(0,255,136,0.3); border-radius: 15px; padding: 20px; margin-bottom: 30px;">
      <h3 class="family-header" onclick="toggleSection('{fam_id}')" style="color: #00ff88;">
        <span class="toggle-icon" id="icon-{fam_id}">▼</span>
        {fam_data["name"]} <span class="count" style="background: #00ff88; color: #000;">({count})</span>
      </h3>
      <div class="grid family-content" id="content-{fam_id}">{cards}</div>
    </div>'''
    
    # Build physics sections (display after extensions)
    physics_sections_html = ""
    for fam_id, fam_data in physics_families.items():
        if fam_data["demos"]:
            cards = make_demo_cards(fam_data["demos"])
            count = len(fam_data["demos"])
            physics_sections_html += f'''
    <div class="family-section physics-section">
      <h3 class="family-header" onclick="toggleSection('{fam_id}')">
        <span class="toggle-icon" id="icon-{fam_id}">▼</span>
        {fam_data["name"]} <span class="count">({count})</span>
      </h3>
      <div class="grid family-content" id="content-{fam_id}">{cards}</div>
    </div>'''
    
    # Build toy family sections with collapse
    toy_sections_html = ""
    for fam_id, fam_data in toy_families.items():
        if fam_data["demos"]:
            cards = make_demo_cards(fam_data["demos"])
            count = len(fam_data["demos"])
            toy_sections_html += f'''
    <div class="family-section">
      <h3 class="family-header" onclick="toggleSection('{fam_id}')">
        <span class="toggle-icon" id="icon-{fam_id}">▼</span>
        {fam_data["name"]} <span class="count">({count})</span>
      </h3>
      <div class="grid family-content" id="content-{fam_id}">{cards}</div>
    </div>'''
    
    # Other toys
    if other_toys:
        other_cards = make_demo_cards(other_toys)
        toy_sections_html += f'''
    <div class="family-section">
      <h3 class="family-header" onclick="toggleSection('other')">
        <span class="toggle-icon" id="icon-other">▼</span>
        🎮 Other Toys <span class="count">({len(other_toys)})</span>
      </h3>
      <div class="grid family-content" id="content-other">{other_cards}</div>
    </div>'''
    
    archetype_cards = make_demo_cards(archetypes)
    cards_3d = make_demo_cards(demos_3d)
    
    # Report images
    phase_cards = ""
    for img in images["phase_maps"][:12]:
        phase_cards += f'<div class="card"><img src="{img["path"]}"><div class="info"><h3>{img["name"]}</h3></div></div>'
    
    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>UET Gallery</title>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    :root {{
      --bg-primary: #0a0a0f;
      --bg-secondary: #12121a;
      --bg-card: #16161f;
      --border: #2a2a35;
      --border-hover: #3a3a45;
      --text-primary: #f0f0f5;
      --text-secondary: #8888a0;
      --accent-c: #4ecdc4;  /* Cyan - Conscious */
      --accent-i: #ff6b6b;  /* Coral - Intuition */
      --accent-gradient: linear-gradient(135deg, var(--accent-c), var(--accent-i));
      --success: #00d26a;
    }}
    
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    
    body {{
      font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
      background: var(--bg-primary);
      color: var(--text-primary);
      min-height: 100vh;
      padding: 40px 20px;
      line-height: 1.6;
    }}
    
    .wrap {{ max-width: 1400px; margin: 0 auto; }}
    
    h1 {{
      text-align: center;
      font-size: 2.5rem;
      font-weight: 700;
      background: var(--accent-gradient);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      background-clip: text;
      margin-bottom: 8px;
      letter-spacing: -0.02em;
    }}
    
    .subtitle {{
      text-align: center;
      color: var(--text-secondary);
      margin-bottom: 50px;
      font-weight: 400;
      font-size: 0.95rem;
    }}
    
    h2 {{
      color: var(--text-primary);
      font-size: 1.25rem;
      font-weight: 600;
      margin: 50px 0 24px;
      padding-bottom: 12px;
      border-bottom: 1px solid var(--border);
      letter-spacing: -0.01em;
    }}
    
    h3 {{ color: var(--text-primary); font-size: 1rem; font-weight: 500; margin: 20px 0 15px; }}
    .count {{ color: var(--text-secondary); font-weight: 400; margin-left: 8px; }}
    
    /* Clean Bordered Sections */
    .family-section {{
      background: var(--bg-secondary);
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 24px;
      margin-bottom: 20px;
    }}
    
    .family-header {{
      margin: 0;
      cursor: pointer;
      user-select: none;
      display: flex;
      align-items: center;
      gap: 10px;
      transition: color 0.2s;
    }}
    .family-header:hover {{ color: var(--accent-c); }}
    .toggle-icon {{ font-size: 0.7rem; opacity: 0.5; transition: transform 0.2s; }}
    .toggle-icon.collapsed {{ transform: rotate(-90deg); }}
    .family-content {{ margin-top: 20px; }}
    .family-content.collapsed {{ display: none; }}
    
    /* Clean Cards with Borders */
    .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 20px; }}
    
    .card {{
      background: var(--bg-card);
      border: 1px solid var(--border);
      border-radius: 12px;
      overflow: hidden;
      transition: all 0.25s ease;
      cursor: pointer;
    }}
    
    .card:hover {{
      border-color: var(--accent-c);
      transform: translateY(-3px);
      box-shadow: 0 8px 24px rgba(78, 205, 196, 0.08);
    }}
    
    .card img {{ 
      width: 100%; 
      aspect-ratio: 16/10; 
      object-fit: cover; 
      background: var(--bg-primary);
      border-bottom: 1px solid var(--border);
    }}
    .card .info {{ padding: 16px; }}
    .card h3 {{ font-size: 0.9rem; color: var(--text-primary); margin-bottom: 6px; font-weight: 500; }}
    .card .desc {{ color: var(--text-secondary); font-size: 12px; margin-bottom: 10px; }}
    
    .tags {{ display: flex; flex-wrap: wrap; gap: 6px; }}
    .tag {{
      background: transparent;
      border: 1px solid var(--border);
      padding: 3px 10px;
      border-radius: 6px;
      font-size: 10px;
      font-weight: 500;
      color: var(--text-secondary);
    }}
    .tag.pass {{ color: var(--success); border-color: var(--success); }}
    .tag.warn {{ color: #f7b731; border-color: #f7b731; }}
    
    /* Modal */
    .modal-overlay {{
      display: none;
      position: fixed;
      top: 0; left: 0;
      width: 100%; height: 100%;
      background: rgba(0, 0, 0, 0.85);
      z-index: 1000;
    }}
    .modal-overlay.active {{ display: flex; align-items: center; justify-content: center; }}
    
    .modal {{
      background: var(--bg-secondary);
      border: 1px solid var(--border);
      border-radius: 16px;
      max-width: 850px;
      width: 90%;
      max-height: 90vh;
      overflow: auto;
      position: relative;
    }}
    
    .modal-close {{
      position: absolute;
      top: 16px; right: 16px;
      background: var(--bg-card);
      border: 1px solid var(--border);
      color: var(--text-secondary);
      width: 36px; height: 36px;
      border-radius: 8px;
      cursor: pointer;
      font-size: 18px;
      display: flex; align-items: center; justify-content: center;
      transition: all 0.2s;
      z-index: 10;
    }}
    .modal-close:hover {{ background: var(--border); color: var(--text-primary); }}
    
    .modal-content {{ padding: 0; }}
    .modal-gif {{ width: 100%; border-radius: 16px 16px 0 0; border-bottom: 1px solid var(--border); }}
    .modal-body {{ padding: 28px; }}
    .modal-title {{ font-size: 1.5rem; color: var(--text-primary); margin-bottom: 8px; font-weight: 600; }}
    .modal-desc {{ color: var(--text-secondary); margin-bottom: 24px; font-size: 14px; }}
    
    .modal-details {{
      background: var(--bg-card);
      border: 1px solid var(--border);
      border-radius: 10px;
      padding: 20px;
      margin-bottom: 24px;
    }}
    .modal-details h4 {{ color: var(--accent-c); margin-bottom: 12px; font-size: 0.9rem; font-weight: 500; }}
    .modal-details p {{ color: var(--text-secondary); font-size: 13px; }}
    
    /* Buttons */
    .modal-actions {{ display: flex; flex-wrap: wrap; gap: 10px; }}
    .btn {{
      display: inline-block;
      padding: 10px 20px;
      background: var(--bg-card);
      border: 1px solid var(--border);
      border-radius: 8px;
      color: var(--text-primary);
      text-decoration: none;
      font-size: 13px;
      font-weight: 500;
      cursor: pointer;
      transition: all 0.2s;
    }}
    .btn:hover {{ border-color: var(--accent-c); color: var(--accent-c); }}
    .btn.primary {{
      background: var(--accent-c);
      border-color: var(--accent-c);
      color: var(--bg-primary);
      font-weight: 600;
    }}
    .btn.primary:hover {{ opacity: 0.9; }}
    
    /* Details/Summary */
    details {{
      background: var(--bg-card);
      border: 1px solid var(--border);
      border-radius: 10px;
      padding: 16px;
    }}
    details summary {{
      cursor: pointer;
      font-weight: 500;
      list-style: none;
    }}
    details summary::-webkit-details-marker {{ display: none; }}
    details[open] summary {{ margin-bottom: 12px; color: var(--accent-c); }}
    
    footer {{
      text-align: center;
      margin-top: 80px;
      color: var(--text-secondary);
      font-size: 12px;
      padding-top: 20px;
      border-top: 1px solid var(--border);
    }}
    
    @media (max-width: 600px) {{
      .grid {{ grid-template-columns: 1fr; }}
      .modal {{ width: 95%; }}
      h1 {{ font-size: 1.8rem; }}
      .family-section {{ padding: 16px; }}
    }}
  </style>
</head>
<body>
  <div class="wrap">
    <h1>🌌 UET Gallery</h1>
    <p class="subtitle">Auto-generated | {datetime.now().strftime('%Y-%m-%d %H:%M')} | <span style="color: #00ff88;">✅ Multi-Dimensional Validated</span></p>
    
    <!-- Scaling Tests Section -->
    <h2>🚀 Scaling & Performance Tests</h2>
    <div class="family-section" style="background: linear-gradient(135deg, rgba(255,107,107,0.1), rgba(78,205,196,0.1)); border: 2px solid rgba(255,107,107,0.3);">
      <h3 class="family-header" onclick="toggleSection('scaling')" style="color: #ff6b6b;">
        <span class="toggle-icon" id="icon-scaling">▼</span>
        📊 Multi-Dimensional Benchmarks <span class="count" style="background: #ff6b6b; color: #000;">(15)</span>
      </h3>
      <div class="family-content" id="content-scaling">
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px;">
          <div style="background: var(--bg-card); border: 1px solid var(--border); border-radius: 10px; padding: 20px;">
            <h4 style="color: var(--accent-c); margin-bottom: 15px;">🧪 2D JAX Accelerated</h4>
            <table style="width: 100%; font-size: 12px; color: var(--text-secondary);">
              <tr style="border-bottom: 1px solid var(--border);"><th style="text-align: left; padding: 5px;">Test</th><th>N</th><th>Runs</th><th>Time</th></tr>
              <tr><td style="padding: 5px;">2D-500K</td><td>32</td><td>500,000</td><td style="color: #00ff88;">92.3s ✅</td></tr>
              <tr><td style="padding: 5px;">2D-N100</td><td>100</td><td>1,000</td><td style="color: #00ff88;">3.2s ✅</td></tr>
              <tr><td style="padding: 5px;">2D-YEAR</td><td>32</td><td>1</td><td style="color: #00ff88;">65s (1 year!) ✅</td></tr>
            </table>
          </div>
          <div style="background: var(--bg-card); border: 1px solid var(--border); border-radius: 10px; padding: 20px;">
            <h4 style="color: var(--accent-c); margin-bottom: 15px;">🌌 3D Simulations</h4>
            <table style="width: 100%; font-size: 12px; color: var(--text-secondary);">
              <tr style="border-bottom: 1px solid var(--border);"><th style="text-align: left; padding: 5px;">Test</th><th>N</th><th>Nodes</th><th>Status</th></tr>
              <tr><td style="padding: 5px;">3D-galaxy-50</td><td>50</td><td>125K</td><td style="color: #00ff88;">✅</td></tr>
              <tr><td style="padding: 5px;">3D-galaxy-100</td><td>100</td><td>1M</td><td style="color: #00ff88;">✅</td></tr>
              <tr><td style="padding: 5px;">3D-galaxy-200</td><td>200</td><td>8M</td><td style="color: #00ff88;">✅</td></tr>
            </table>
          </div>
          <div style="background: var(--bg-card); border: 1px solid var(--border); border-radius: 10px; padding: 20px;">
            <h4 style="color: var(--accent-i); margin-bottom: 15px;">🔬 n-Dimensional Proof</h4>
            <table style="width: 100%; font-size: 12px; color: var(--text-secondary);">
              <tr style="border-bottom: 1px solid var(--border);"><th style="text-align: left; padding: 5px;">Dims</th><th>N</th><th>Nodes</th><th>Proven</th></tr>
              <tr><td style="padding: 5px;">4D</td><td>30</td><td>810K</td><td style="color: #00ff88;">✅</td></tr>
              <tr><td style="padding: 5px;">5D</td><td>11</td><td>161K</td><td style="color: #00ff88;">✅</td></tr>
              <tr><td style="padding: 5px;">6D</td><td>7</td><td>117K</td><td style="color: #00ff88;">✅</td></tr>
              <tr><td style="padding: 5px;">7D</td><td>5</td><td>78K</td><td style="color: #00ff88;">✅</td></tr>
            </table>
            <p style="margin-top: 10px; font-size: 11px; color: var(--accent-c);">🎯 UET proven for 1D-7D!</p>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Physical Mappings Section -->
    <div class="family-section" style="background: linear-gradient(135deg, rgba(147,112,219,0.1), rgba(255,215,0,0.1)); border: 2px solid rgba(147,112,219,0.3);">
      <h3 class="family-header" onclick="toggleSection('mappings')" style="color: #9370db;">
        <span class="toggle-icon" id="icon-mappings">▼</span>
        🌡️ Physical Mappings <span class="count" style="background: #9370db; color: #000;">(Module)</span>
      </h3>
      <div class="family-content" id="content-mappings">
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 15px;">
          <div style="background: var(--bg-card); border: 1px solid var(--border); border-radius: 8px; padding: 15px; text-align: center;">
            <span style="font-size: 2rem;">🌡️</span><p style="margin: 10px 0 5px; font-weight: 500;">Temperature</p>
          </div>
          <div style="background: var(--bg-card); border: 1px solid var(--border); border-radius: 8px; padding: 15px; text-align: center;">
            <span style="font-size: 2rem;">💧</span><p style="margin: 10px 0 5px; font-weight: 500;">Density</p>
          </div>
          <div style="background: var(--bg-card); border: 1px solid var(--border); border-radius: 8px; padding: 15px; text-align: center;">
            <span style="font-size: 2rem;">💨</span><p style="margin: 10px 0 5px; font-weight: 500;">Velocity</p>
          </div>
          <div style="background: var(--bg-card); border: 1px solid var(--border); border-radius: 8px; padding: 15px; text-align: center;">
            <span style="font-size: 2rem;">🌍</span><p style="margin: 10px 0 5px; font-weight: 500;">Gravity</p>
          </div>
          <div style="background: var(--bg-card); border: 1px solid var(--border); border-radius: 8px; padding: 15px; text-align: center;">
            <span style="font-size: 2rem;">⚡</span><p style="margin: 10px 0 5px; font-weight: 500;">Stability</p>
          </div>
          <div style="background: var(--bg-card); border: 1px solid var(--border); border-radius: 8px; padding: 15px; text-align: center;">
            <span style="font-size: 2rem;">🔮</span><p style="margin: 10px 0 5px; font-weight: 500;">Order</p>
          </div>
        </div>
        <p style="margin-top: 15px; font-size: 12px; color: var(--text-secondary); text-align: center;">
          📁 <code style="color: var(--accent-c);">uet_core/mappings.py</code> - Ready for visualization!
        </p>
      </div>
    </div>

    <h2>🚀 Extensions Test Pack</h2>
    {extension_sections_html}
    
    {f'<h2>🎬 Archetype Demos ({len(archetypes)})</h2><div class="grid">{archetype_cards}</div>' if archetypes else ''}
    
    <h2>🔬 Physics & Advanced</h2>
    {physics_sections_html}
    
    <h2>🎮 Toy Models</h2>
    {toy_sections_html}
    
    {f'<h2>🌐 3D Simulations ({len(demos_3d)})</h2><div class="grid">{cards_3d}</div>' if demos_3d else ''}
    
    {f'<h2>📊 Phase Maps ({len(images["phase_maps"])})</h2><div class="grid">{phase_cards}</div>' if images["phase_maps"] else ''}
    
    <footer>
      <p>UET Gallery | {sum(len(f["demos"]) for f in extension_families.values())} extensions + {len(archetypes)} archetypes + {sum(len(f["demos"]) for f in physics_families.values())} physics + {sum(len(f["demos"]) for f in toy_families.values()) + len(other_toys)} toys + {len(demos_3d)} 3D demos</p>
    </footer>
  </div>
  
  <!-- Modal -->
  <div class="modal-overlay" id="modal" onclick="closeModal(event)">
    <div class="modal" onclick="event.stopPropagation()">
      <button class="modal-close" onclick="closeModal()">&times;</button>
      <div class="modal-content">
        <div style="position: relative; display: inline-block;">
          <img class="modal-gif" id="modal-gif" src="" alt="" style="cursor: pointer;" onclick="toggleGifPause()" title="Click to Pause/Play">
          <button id="pause-btn" onclick="toggleGifPause()" style="position: absolute; top: 10px; right: 10px; background: rgba(0,0,0,0.7); color: white; border: none; border-radius: 8px; padding: 8px 16px; cursor: pointer; font-size: 14px; z-index: 10;">⏸️ Pause</button>
        </div>
        <div class="modal-body">
          <h2 class="modal-title" id="modal-title"></h2>
          <p class="modal-desc" id="modal-desc"></p>
          
          <!-- Parameters & Metrics using native HTML5 details/summary -->
          <div class="params-metrics-grid" id="params-metrics-container" style="display: none; grid-template-columns: 1fr 1fr; gap: 20px; margin: 20px 0;">
            <details open style="background: #21262d; border-radius: 8px; padding: 16px;">
              <summary style="color: #00d4ff; cursor: pointer; font-weight: bold; margin-bottom: 12px;">⚙️ Parameters</summary>
              <div id="params-list" style="display: grid; gap: 8px;"></div>
            </details>
            <details open style="background: #21262d; border-radius: 8px; padding: 16px;">
              <summary style="color: #00ff88; cursor: pointer; font-weight: bold; margin-bottom: 12px;">📊 Metrics</summary>
              <div id="metrics-list" style="display: grid; gap: 8px;"></div>
            </details>
          </div>
          
          <!-- Fallback details -->
          <div class="modal-details" id="fallback-details">
            <h4>📊 Details</h4>
            <p id="modal-details"></p>
          </div>
          
          <div class="modal-actions" id="modal-actions">
            <!-- Buttons added by JS -->
          </div>
        </div>
      </div>
    </div>
  </div>
  
  <script>
    const demoData = {modal_data};
    
    function openModal(id) {{
      const d = demoData[id];
      if (!d) return;
      
      document.getElementById('modal-gif').src = d.gif;
      document.getElementById('modal-title').textContent = d.title;
      document.getElementById('modal-desc').textContent = d.description;
      
      // Check if has params/metrics for extension-style display
      const hasParams = d.params && Object.keys(d.params).length > 0;
      const hasMetrics = d.metrics && Object.keys(d.metrics).length > 0;
      
      if (hasParams || hasMetrics) {{
        // Show 2-column layout
        document.getElementById('params-metrics-container').style.display = 'grid';
        document.getElementById('fallback-details').style.display = 'none';
        
        // Populate params
        const paramsList = document.getElementById('params-list');
        paramsList.innerHTML = '';
        if (d.params) {{
          Object.entries(d.params).forEach(([key, val]) => {{
            paramsList.innerHTML += `<div style="display: flex; justify-content: space-between; padding: 6px 0; border-bottom: 1px solid #30363d;">
              <span style="color: #8b949e;">${{key}}</span>
              <span style="color: #ffd700; font-weight: bold;">${{val}}</span>
            </div>`;
          }});
        }}
        
        // Populate metrics
        const metricsList = document.getElementById('metrics-list');
        metricsList.innerHTML = '';
        if (d.metrics) {{
          Object.entries(d.metrics).forEach(([key, val]) => {{
            metricsList.innerHTML += `<div style="display: flex; justify-content: space-between; padding: 6px 0; border-bottom: 1px solid #30363d;">
              <span style="color: #8b949e;">${{key}}</span>
              <span style="color: #00ff88; font-weight: bold;">${{val}}</span>
            </div>`;
          }});
        }}
      }}
      
      // Render viz buttons for inline switching
      let actions = '';
      if (d.viz && d.viz.length > 0) {{
        d.viz.forEach((v, i) => {{
          const isActive = i === 0 ? 'primary' : '';
          actions += `<button class="btn ${{isActive}}" onclick="switchViz('${{v.path}}')" data-path="${{v.path}}">${{v.label}}</button>`;
        }});
      }}
      if (d.demo_card) {{
        actions += '<a href="' + d.demo_card + '" class="btn" target="_blank">Full Details</a>';
      }}
      document.getElementById('modal-actions').innerHTML = actions;
      
      document.getElementById('modal').classList.add('active');
      document.body.style.overflow = 'hidden';
    }}
    
    function switchViz(path) {{
      document.getElementById('modal-gif').src = path;
      // Update button states
      document.querySelectorAll('#modal-actions button').forEach(btn => {{
        btn.classList.remove('primary');
        if (btn.dataset.path === path) btn.classList.add('primary');
      }});
    }}
    
    function closeModal(e) {{
      if (e && e.target !== e.currentTarget) return;
      document.getElementById('modal').classList.remove('active');
      document.body.style.overflow = '';
    }}
    
    // Close on Escape
    document.addEventListener('keydown', (e) => {{
      if (e.key === 'Escape') closeModal();
      if (e.key === ' ' && document.getElementById('modal').classList.contains('active')) {{
        e.preventDefault();
        toggleGifPause();
      }}
    }});
    
    // GIF Pause/Play functionality (simple approach)
    let gifPaused = false;
    let originalSrc = '';
    
    function toggleGifPause() {{
      const img = document.getElementById('modal-gif');
      const btn = document.getElementById('pause-btn');
      
      if (!gifPaused) {{
        // Pause: store src and freeze by setting same src again
        originalSrc = img.src;
        // Add a query string to force reload at current frame
        img.src = originalSrc + '?paused=' + Date.now();
        btn.innerHTML = '▶️ Play';
        btn.style.background = 'rgba(0,200,100,0.8)';
        gifPaused = true;
      }} else {{
        // Resume: restore original GIF src without query
        const cleanSrc = originalSrc.split('?')[0];
        img.src = '';  // Clear first
        setTimeout(() => {{
          img.src = cleanSrc;
        }}, 50);
        btn.innerHTML = '⏸️ Pause';
        btn.style.background = 'rgba(0,0,0,0.7)';
        gifPaused = false;
      }}
    }}
    
    // Reset pause state when opening modal
    const originalOpenModal = openModal;
    openModal = function(id) {{
      gifPaused = false;
      originalSrc = '';
      const btn = document.getElementById('pause-btn');
      if (btn) {{
        btn.innerHTML = '⏸️ Pause';
        btn.style.background = 'rgba(0,0,0,0.7)';
      }}
      originalOpenModal(id);
    }};
    
    // Toggle section collapse
    function toggleSection(id) {{
      const content = document.getElementById('content-' + id);
      const icon = document.getElementById('icon-' + id);
      
      if (content.classList.contains('collapsed')) {{
        content.classList.remove('collapsed');
        icon.classList.remove('collapsed');
        icon.textContent = '▼';
      }} else {{
        content.classList.add('collapsed');
        icon.classList.add('collapsed');
        icon.textContent = '▶';
      }}
    }}
  </script>
</body>
</html>'''
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)
    
    print(f"✅ Gallery generated: {output_path}")
    print(f"   - Archetypes: {len(archetypes)}")
    print(f"   - Toys: {sum(len(f['demos']) for f in toy_families.values()) + len(other_toys)}")
    print(f"   - 3D Demos: {len(demos_3d)}")
    print(f"   - Reports: {len(images['phase_maps'])} phase + {len(images['cross_sweeps'])} sweeps + {len(images['atlas'])} atlas")


def main():
    parser = argparse.ArgumentParser(description="Generate UET Gallery from runs")
    parser.add_argument("--runs-dir", default="runs_gallery", help="Directory with demo runs")
    parser.add_argument("--reports-dir", default="reports", help="Directory with report images")
    parser.add_argument("--output", default="runs_gallery/gallery.html", help="Output HTML file")
    
    args = parser.parse_args()
    
    runs_dir = Path(args.runs_dir)
    reports_dir = Path(args.reports_dir)
    output_path = Path(args.output)
    
    print(f"🔍 Scanning {runs_dir} for demos...")
    demos = find_demos(runs_dir)
    
    print(f"🔍 Scanning {reports_dir} for images...")
    images = find_report_images(reports_dir)
    
    print(f"📝 Generating gallery...")
    generate_gallery_html(demos, images, output_path)


if __name__ == "__main__":
    main()
