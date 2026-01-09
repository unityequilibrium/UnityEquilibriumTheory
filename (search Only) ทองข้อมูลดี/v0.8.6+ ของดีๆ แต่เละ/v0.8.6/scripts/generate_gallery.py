#!/usr/bin/env python
"""
Generate 5 Archetype Demos for UET Gallery.

Archetypes:
1. BIAS_C - Positive tilt (s > 0), system biases toward C
2. BIAS_I - Negative tilt (s < 0), system biases toward I
3. SYM - Zero tilt (s = 0), symmetric/random outcome
4. Strong Coupling - High beta, tight field coupling
5. Weak Coupling - Low beta, more independent fields
"""
from __future__ import annotations
import subprocess
import sys
from pathlib import Path
import json
from datetime import datetime


# Define 5 archetype demo configurations
ARCHETYPES = [
    {
        "name": "archetype_bias_c",
        "title": "BIAS_C: Positive Tilt",
        "description": "System with positive tilt (s=0.5) biases toward C field dominance",
        "params": {
            "model": "C_I",
            "beta": 0.5,
            "s": 0.5,
            "a": -1.0,
            "delta": 1.0,
            "kappa": 0.5,
        }
    },
    {
        "name": "archetype_bias_i",
        "title": "BIAS_I: Negative Tilt",
        "description": "System with negative tilt (s=-0.5) biases toward I field dominance",
        "params": {
            "model": "C_I",
            "beta": 0.5,
            "s": -0.5,
            "a": -1.0,
            "delta": 1.0,
            "kappa": 0.5,
        }
    },
    {
        "name": "archetype_symmetric",
        "title": "SYM: Zero Tilt",
        "description": "Symmetric system (s=0) with random/balanced outcome",
        "params": {
            "model": "C_I",
            "beta": 0.5,
            "s": 0.0,
            "a": -1.0,
            "delta": 1.0,
            "kappa": 0.5,
        }
    },
    {
        "name": "archetype_strong_coupling",
        "title": "Strong Coupling",
        "description": "High coupling (β=0.9) causes tight field interaction",
        "params": {
            "model": "C_I",
            "beta": 0.9,
            "s": 0.3,
            "a": -1.0,
            "delta": 1.0,
            "kappa": 0.5,
        }
    },
    {
        "name": "archetype_weak_coupling",
        "title": "Weak Coupling",
        "description": "Low coupling (β=0.1) allows more independent field evolution",
        "params": {
            "model": "C_I",
            "beta": 0.1,
            "s": 0.3,
            "a": -1.0,
            "delta": 1.0,
            "kappa": 0.5,
        }
    },
]


def run_demo(archetype: dict, out_dir: str = "runs_gallery", N: int = 48, T: float = 10.0) -> Path:
    """Run a single demo."""
    name = archetype["name"]
    params = archetype["params"]
    
    cmd = [
        sys.executable, "scripts/run_with_snapshots.py",
        "--case-id", name,
        "--model", params["model"],
        "--beta", str(params["beta"]),
        "--s", str(params["s"]),
        "--a", str(params["a"]),
        "--delta", str(params["delta"]),
        "--kappa", str(params["kappa"]),
        "--N", str(N),
        "--T", str(T),
        "--out", out_dir,
    ]
    
    print(f"\n{'='*60}")
    print(f"Running: {archetype['title']}")
    print(f"  {archetype['description']}")
    print(f"{'='*60}")
    
    result = subprocess.run(cmd, cwd=Path(__file__).parent.parent)
    
    return Path(out_dir) / name


def generate_gallery_html(out_dir: str = "runs_gallery") -> Path:
    """Generate gallery HTML page linking all demo cards."""
    out_path = Path(out_dir)
    
    # Build gallery items
    items_html = ""
    for arch in ARCHETYPES:
        name = arch["name"]
        demo_card = out_path / name / "demo_card" / "demo_card.html"
        omega_plot = out_path / name / "demo_card" / "omega_evolution.png"
        
        # Check if exists
        exists = demo_card.exists()
        status = "✅" if exists else "❌"
        link = f"{name}/demo_card/demo_card.html" if exists else "#"
        
        items_html += f"""
        <div class="gallery-item" onclick="window.location='{link}'">
            <div class="item-header">
                <span class="status">{status}</span>
                <h3>{arch['title']}</h3>
            </div>
            <p class="description">{arch['description']}</p>
            <div class="params">
                <span>β={arch['params']['beta']}</span>
                <span>s={arch['params']['s']}</span>
            </div>
            {"<img src='" + name + "/demo_card/omega_evolution.png' alt='Omega'>" if omega_plot.exists() else ""}
        </div>
        """
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>UET Demo Gallery</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #0f0f23 0%, #1a1a3e 100%);
            color: #e0e0e0;
            min-height: 100vh;
            padding: 30px;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}
        h1 {{
            font-size: 2.5rem;
            text-align: center;
            margin-bottom: 10px;
            background: linear-gradient(90deg, #00d4ff, #7b2cbf, #ff6b6b);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        .subtitle {{
            text-align: center;
            color: #888;
            margin-bottom: 40px;
        }}
        .gallery {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 25px;
        }}
        .gallery-item {{
            background: rgba(255,255,255,0.05);
            border-radius: 16px;
            padding: 25px;
            cursor: pointer;
            transition: all 0.3s ease;
            border: 1px solid rgba(255,255,255,0.1);
        }}
        .gallery-item:hover {{
            transform: translateY(-5px);
            box-shadow: 0 20px 40px rgba(0,212,255,0.2);
            border-color: rgba(0,212,255,0.5);
        }}
        .item-header {{
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 15px;
        }}
        .status {{
            font-size: 1.2rem;
        }}
        h3 {{
            color: #00d4ff;
            font-size: 1.3rem;
        }}
        .description {{
            color: #aaa;
            margin-bottom: 15px;
            line-height: 1.5;
        }}
        .params {{
            display: flex;
            gap: 15px;
            margin-bottom: 15px;
        }}
        .params span {{
            background: rgba(123,44,191,0.3);
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 0.9rem;
            color: #c9a0ff;
        }}
        .gallery-item img {{
            width: 100%;
            border-radius: 8px;
            margin-top: 10px;
        }}
        .footer {{
            text-align: center;
            color: #666;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid rgba(255,255,255,0.1);
        }}
        .legend {{
            display: flex;
            justify-content: center;
            gap: 30px;
            margin-bottom: 30px;
            flex-wrap: wrap;
        }}
        .legend-item {{
            display: flex;
            align-items: center;
            gap: 8px;
            color: #888;
        }}
        .legend-color {{
            width: 20px;
            height: 20px;
            border-radius: 4px;
        }}
        .bias-c {{ background: linear-gradient(90deg, #ff6b6b, #ee5a24); }}
        .bias-i {{ background: linear-gradient(90deg, #4834d4, #686de0); }}
        .sym {{ background: linear-gradient(90deg, #6ab04c, #badc58); }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🌌 UET Demo Gallery</h1>
        <p class="subtitle">5 Archetype Demonstrations of Coupled Field Phase Transitions</p>
        
        <div class="legend">
            <div class="legend-item">
                <div class="legend-color bias-c"></div>
                <span>BIAS_C (s &gt; 0)</span>
            </div>
            <div class="legend-item">
                <div class="legend-color bias-i"></div>
                <span>BIAS_I (s &lt; 0)</span>
            </div>
            <div class="legend-item">
                <div class="legend-color sym"></div>
                <span>SYM (s = 0)</span>
            </div>
        </div>
        
        <div class="gallery">
            {items_html}
        </div>
        
        <div class="footer">
            UET Demo Gallery | Generated {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        </div>
    </div>
</body>
</html>
"""
    
    gallery_path = out_path / "gallery.html"
    with open(gallery_path, "w", encoding="utf-8") as f:
        f.write(html)
    
    print(f"\n✅ Gallery saved to: {gallery_path}")
    return gallery_path


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate UET Demo Gallery")
    parser.add_argument("--out", default="runs_gallery", help="Output directory")
    parser.add_argument("--N", type=int, default=48, help="Grid size")
    parser.add_argument("--T", type=float, default=10.0, help="Simulation time")
    parser.add_argument("--gallery-only", action="store_true", help="Only generate gallery HTML")
    
    args = parser.parse_args()
    
    if not args.gallery_only:
        # Run all demos
        for arch in ARCHETYPES:
            run_demo(arch, args.out, args.N, args.T)
    
    # Generate gallery
    generate_gallery_html(args.out)
    
    print("\n" + "="*60)
    print("🎉 Gallery generation complete!")
    print(f"   Open: {args.out}/gallery.html")
    print("="*60)


if __name__ == "__main__":
    main()
