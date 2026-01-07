"""
Export utilities for creating self-contained static reports.
"""

import json
import os
from pathlib import Path

def export_static_dashboard(run_dir: str):
    """
    Creates a single-file static HTML dashboard in the run directory.
    Embeds config, metrics, summary, gates, and timeseries directly into the HTML.
    Inline CSS and JS for a truly portable file without server requirements.
    """
    run_path = Path(run_dir)
    root_path = Path(__file__).parent.parent
    
    # 1. Read Data Artifacts
    data = {}
    
    def read_json_safe(filename):
        try:
            with open(run_path / filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return None

    data['config'] = read_json_safe('config.json')
    data['metrics'] = read_json_safe('metrics.json')
    data['summary'] = read_json_safe('summary.json')
    data['gates'] = read_json_safe('gate_report.json')
    
    try:
        with open(run_path / 'timeseries.csv', 'r', encoding='utf-8') as f:
            data['timeseries'] = f.read()
    except Exception:
        data['timeseries'] = None
        
    # 1.5 Find Visual Snapshots (GIFs, PNGs)
    data['visuals'] = []
    for ext in ['*.gif', '*.png', '*.jpg']:
        for img_path in run_path.glob(ext):
            data['visuals'].append({
                "name": img_path.name,
                "url": img_path.name
            })
        
    # 2. Read UI Template Files
    try:
        with open(root_path / 'ui' / 'index.html', 'r', encoding='utf-8') as f:
            html_template = f.read()
        with open(root_path / 'ui' / 'css' / 'style.css', 'r', encoding='utf-8') as f:
            css_content = f.read()
        with open(root_path / 'ui' / 'js' / 'app.js', 'r', encoding='utf-8') as f:
            js_content = f.read()
    except Exception as e:
        print(f"[Export] Failed to read UI template files: {e}")
        return

    # 3. Embed Content
    # Remove existing link/script tags to replace with inline
    html_template = html_template.replace('<link rel="stylesheet" href="css/style.css">', f'<style>{css_content}</style>')
    html_template = html_template.replace('<script src="js/app.js"></script>', '')
    
    # Inject Data Variable
    injected_script = f"""
    <script>
        window.UET_STATIC_DATA = {json.dumps(data)};
    </script>
    <script>
        {js_content}
    </script>
    """
    
    # Insert before closing body
    final_html = html_template.replace('</body>', f'{injected_script}</body>')
    
    # 4. Write Output
    output_path = run_path / 'report_dashboard.html'
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(final_html)
        print(f"[Export] Generated static dashboard: {output_path}")
    except Exception as e:
        print(f"[Export] Failed to write dashboard file: {e}")
