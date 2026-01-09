"""
Save traffic simulation as individual frames + HTML player
Allows play/pause and step-through analysis
"""
from __future__ import annotations
import argparse
import json
import numpy as np
from pathlib import Path
import shutil

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

# Google Maps traffic colors
GOOGLE_COLORS = [
    (0.18, 0.80, 0.44),   # Green (free)
    (0.95, 0.77, 0.06),   # Yellow (moderate)
    (0.90, 0.49, 0.13),   # Orange (slow)
    (0.91, 0.30, 0.24),   # Red (heavy)
    (0.56, 0.14, 0.14),   # Dark red (jam)
]


def create_road_network(N: int = 64) -> dict:
    """Create grid road network."""
    road_mask = np.zeros((N, N))
    road_type = np.zeros((N, N))
    
    main_roads = [N//4, N//2, 3*N//4]
    local_spacing = N // 8
    
    for y in main_roads:
        for dy in range(-2, 3):
            if 0 <= y + dy < N:
                road_mask[:, y + dy] = 1
                road_type[:, y + dy] = 2
    
    for x in main_roads:
        for dx in range(-2, 3):
            if 0 <= x + dx < N:
                road_mask[x + dx, :] = 1
                road_type[x + dx, :] = 2
    
    for i in range(0, N, local_spacing):
        for dy in range(-1, 2):
            if 0 <= i + dy < N:
                road_mask[:, i + dy] = np.maximum(road_mask[:, i + dy], 1)
        for dx in range(-1, 2):
            if 0 <= i + dx < N:
                road_mask[i + dx, :] = np.maximum(road_mask[i + dx, :], 1)
    
    return {"mask": road_mask, "type": road_type}


def run_simulation(road_net: dict, scenario: str = "rush_hour", n_steps: int = 200) -> list:
    """Run simulation and return list of traffic arrays."""
    N = road_net["mask"].shape[0]
    road_mask = road_net["mask"]
    road_type = road_net["type"]
    
    traffic = np.random.rand(N, N) * 0.05 * road_mask
    capacity = np.where(road_type == 2, 1.0, 0.6) * road_mask
    
    frames = [{"traffic": traffic.copy(), "time": 0}]
    
    kappa = 0.3
    dx = 1.0 / N
    dt = 0.05
    
    for step in range(1, n_steps + 1):
        progress = step / n_steps
        
        congestion = traffic / np.maximum(capacity, 0.1)
        effective_speed = 1.0 - 0.8 * np.clip(congestion, 0, 1)
        
        lap = (np.roll(traffic, 1, 0) + np.roll(traffic, -1, 0) +
               np.roll(traffic, 1, 1) + np.roll(traffic, -1, 1) - 4*traffic) / dx**2
        
        d_traffic = kappa * effective_speed * lap * road_mask
        traffic = traffic + dt * d_traffic
        
        # Inflow based on time
        if progress < 0.3:
            inflow = 0.01
        elif progress < 0.6:
            inflow = 0.04
        else:
            inflow = 0.008
        
        traffic[0, :] += inflow * road_mask[0, :]
        traffic[:, 0] += inflow * road_mask[:, 0]
        
        # Outflow
        outflow = 0.93 if progress > 0.6 else 0.97
        traffic[-1, :] *= outflow
        traffic[:, -1] *= outflow
        
        traffic = np.clip(traffic, 0, 1.2) * road_mask
        
        if step % (n_steps // 50) == 0:
            frames.append({"traffic": traffic.copy(), "time": step * dt})
    
    return frames


def save_frames_with_player(output_dir: Path, frames: list, road_net: dict, title: str):
    """Save individual frames as PNG and create HTML player."""
    N = road_net["mask"].shape[0]
    road_mask = road_net["mask"]
    road_type = road_net["type"]
    capacity = np.where(road_type == 2, 1.0, 0.6) * road_mask
    
    frames_dir = output_dir / "frames"
    frames_dir.mkdir(exist_ok=True)
    
    building_color = np.array([0.95, 0.95, 0.93])
    
    congestion_data = []
    
    print(f"  Saving {len(frames)} frames...")
    
    for i, frame in enumerate(frames):
        traffic = frame["traffic"]
        cong_level = np.clip(traffic / np.maximum(capacity, 0.1), 0, 1)
        avg_congestion = float(np.mean(traffic[road_mask > 0] / np.maximum(capacity[road_mask > 0], 0.1)))
        congestion_data.append({"frame": i, "time": frame["time"], "congestion": avg_congestion})
        
        # Create map image
        map_img = np.ones((N, N, 3)) * building_color
        for x in range(N):
            for y in range(N):
                if road_mask[x, y] > 0:
                    c = cong_level[x, y]
                    if c < 0.3:
                        color = GOOGLE_COLORS[0]
                    elif c < 0.5:
                        color = GOOGLE_COLORS[1]
                    elif c < 0.7:
                        color = GOOGLE_COLORS[2]
                    elif c < 0.85:
                        color = GOOGLE_COLORS[3]
                    else:
                        color = GOOGLE_COLORS[4]
                    map_img[x, y] = color
        
        # Save frame
        fig, ax = plt.subplots(1, 1, figsize=(8, 8))
        ax.imshow(map_img, origin='lower', interpolation='nearest')
        ax.set_title(f'{title} | Frame {i}/{len(frames)-1} | t={frame["time"]:.1f}s', fontsize=12)
        ax.set_xticks([])
        ax.set_yticks([])
        
        # Status
        if avg_congestion < 0.3:
            status = "FREE FLOW"
            color = '#2ECC71'
        elif avg_congestion < 0.5:
            status = "MODERATE"
            color = '#F1C40F'
        elif avg_congestion < 0.7:
            status = "SLOW"
            color = '#E67E22'
        else:
            status = "HEAVY"
            color = '#E74C3C'
        
        ax.text(0.02, 0.98, f'{status}\n{avg_congestion:.2f}', 
               transform=ax.transAxes, fontsize=10, va='top',
               bbox=dict(boxstyle='round', facecolor=color, alpha=0.8))
        
        plt.tight_layout()
        plt.savefig(frames_dir / f"frame_{i:04d}.png", dpi=100, bbox_inches='tight')
        plt.close(fig)
    
    # Save congestion data as JSON
    with open(output_dir / "congestion_data.json", "w") as f:
        json.dump(congestion_data, f, indent=2)
    
    # Create HTML player
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{title} - Frame Player</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 20px;
            color: white;
        }}
        h1 {{
            margin-bottom: 20px;
            font-size: 1.5em;
        }}
        .player-container {{
            background: rgba(255,255,255,0.1);
            border-radius: 16px;
            padding: 20px;
            backdrop-filter: blur(10px);
        }}
        #frame-display {{
            max-width: 600px;
            border-radius: 8px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        }}
        .controls {{
            display: flex;
            gap: 10px;
            justify-content: center;
            margin-top: 20px;
            flex-wrap: wrap;
        }}
        button {{
            padding: 12px 24px;
            font-size: 16px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            background: #4ecdc4;
            color: #1a1a2e;
            font-weight: bold;
            transition: all 0.2s;
        }}
        button:hover {{
            background: #45b7aa;
            transform: scale(1.05);
        }}
        button:active {{
            transform: scale(0.95);
        }}
        .slider-container {{
            width: 100%;
            margin-top: 20px;
        }}
        #frame-slider {{
            width: 100%;
            height: 8px;
            border-radius: 4px;
            cursor: pointer;
        }}
        .info {{
            margin-top: 15px;
            text-align: center;
            font-size: 1.1em;
        }}
        #frame-info {{
            background: rgba(255,255,255,0.1);
            padding: 10px 20px;
            border-radius: 8px;
            display: inline-block;
        }}
        .legend {{
            display: flex;
            gap: 15px;
            justify-content: center;
            margin-top: 15px;
            flex-wrap: wrap;
        }}
        .legend-item {{
            display: flex;
            align-items: center;
            gap: 5px;
            font-size: 0.9em;
        }}
        .legend-color {{
            width: 20px;
            height: 20px;
            border-radius: 4px;
        }}
        .speed-control {{
            display: flex;
            align-items: center;
            gap: 10px;
            margin-top: 15px;
            justify-content: center;
        }}
        #speed-slider {{
            width: 150px;
        }}
    </style>
</head>
<body>
    <h1>🚗 {title}</h1>
    
    <div class="player-container">
        <img id="frame-display" src="frames/frame_0000.png" alt="Traffic Frame">
        
        <div class="controls">
            <button onclick="firstFrame()">⏮️ First</button>
            <button onclick="prevFrame()">◀️ Prev</button>
            <button id="play-btn" onclick="togglePlay()">▶️ Play</button>
            <button onclick="nextFrame()">Next ▶️</button>
            <button onclick="lastFrame()">Last ⏭️</button>
        </div>
        
        <div class="slider-container">
            <input type="range" id="frame-slider" min="0" max="{len(frames)-1}" value="0" 
                   oninput="goToFrame(this.value)">
        </div>
        
        <div class="speed-control">
            <span>Speed:</span>
            <input type="range" id="speed-slider" min="1" max="20" value="5">
            <span id="speed-label">5 fps</span>
        </div>
        
        <div class="info">
            <div id="frame-info">Frame 0 / {len(frames)-1} | t = 0.0s</div>
        </div>
        
        <div class="legend">
            <div class="legend-item"><div class="legend-color" style="background:#2ECC71"></div> Free</div>
            <div class="legend-item"><div class="legend-color" style="background:#F1C40F"></div> Moderate</div>
            <div class="legend-item"><div class="legend-color" style="background:#E67E22"></div> Slow</div>
            <div class="legend-item"><div class="legend-color" style="background:#E74C3C"></div> Heavy</div>
            <div class="legend-item"><div class="legend-color" style="background:#8E2323"></div> Jam</div>
        </div>
    </div>
    
    <script>
        const totalFrames = {len(frames)};
        let currentFrame = 0;
        let isPlaying = false;
        let playInterval = null;
        
        const frameData = {json.dumps(congestion_data)};
        
        function updateDisplay() {{
            const frameStr = String(currentFrame).padStart(4, '0');
            document.getElementById('frame-display').src = `frames/frame_${{frameStr}}.png`;
            document.getElementById('frame-slider').value = currentFrame;
            
            const data = frameData[currentFrame];
            document.getElementById('frame-info').textContent = 
                `Frame ${{currentFrame}} / ${{totalFrames-1}} | t = ${{data.time.toFixed(1)}}s | Congestion: ${{data.congestion.toFixed(3)}}`;
        }}
        
        function goToFrame(n) {{
            currentFrame = parseInt(n);
            updateDisplay();
        }}
        
        function nextFrame() {{
            if (currentFrame < totalFrames - 1) {{
                currentFrame++;
                updateDisplay();
            }}
        }}
        
        function prevFrame() {{
            if (currentFrame > 0) {{
                currentFrame--;
                updateDisplay();
            }}
        }}
        
        function firstFrame() {{
            currentFrame = 0;
            updateDisplay();
        }}
        
        function lastFrame() {{
            currentFrame = totalFrames - 1;
            updateDisplay();
        }}
        
        function togglePlay() {{
            isPlaying = !isPlaying;
            document.getElementById('play-btn').textContent = isPlaying ? '⏸️ Pause' : '▶️ Play';
            
            if (isPlaying) {{
                const fps = parseInt(document.getElementById('speed-slider').value);
                playInterval = setInterval(() => {{
                    if (currentFrame < totalFrames - 1) {{
                        currentFrame++;
                        updateDisplay();
                    }} else {{
                        currentFrame = 0;
                        updateDisplay();
                    }}
                }}, 1000 / fps);
            }} else {{
                clearInterval(playInterval);
            }}
        }}
        
        document.getElementById('speed-slider').addEventListener('input', (e) => {{
            document.getElementById('speed-label').textContent = e.target.value + ' fps';
            if (isPlaying) {{
                clearInterval(playInterval);
                const fps = parseInt(e.target.value);
                playInterval = setInterval(() => {{
                    if (currentFrame < totalFrames - 1) {{
                        currentFrame++;
                    }} else {{
                        currentFrame = 0;
                    }}
                    updateDisplay();
                }}, 1000 / fps);
            }}
        }});
        
        // Keyboard controls
        document.addEventListener('keydown', (e) => {{
            if (e.key === 'ArrowRight') nextFrame();
            else if (e.key === 'ArrowLeft') prevFrame();
            else if (e.key === ' ') {{ e.preventDefault(); togglePlay(); }}
            else if (e.key === 'Home') firstFrame();
            else if (e.key === 'End') lastFrame();
        }});
    </script>
</body>
</html>
"""
    
    with open(output_dir / "player.html", "w", encoding="utf-8") as f:
        f.write(html)
    
    print(f"  Saved player: {output_dir / 'player.html'}")
    return output_dir / "player.html"


def main():
    parser = argparse.ArgumentParser(description="Traffic frame player generator")
    parser.add_argument("--out", default="runs_gallery/toy_traffic_player")
    parser.add_argument("--N", type=int, default=64)
    parser.add_argument("--steps", type=int, default=200)
    parser.add_argument("--title", default="Traffic Simulation")
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("Traffic Frame Player Generator")
    print("=" * 60)
    
    output_dir = Path(args.out)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Create road network
    road_net = create_road_network(args.N)
    
    # Run simulation
    print("  Running simulation...")
    frames = run_simulation(road_net, n_steps=args.steps)
    
    # Save frames and player
    save_frames_with_player(output_dir, frames, road_net, args.title)
    
    # Save config for gallery
    config = {
        "case_id": "toy_traffic_player",
        "model": "interactive_player",
        "description": "Interactive traffic frame player with play/pause controls",
    }
    with open(output_dir / "config.json", "w") as f:
        json.dump(config, f, indent=2)
    
    summary = {
        "case_id": "toy_traffic_player",
        "status": "PASS",
        "description": "Interactive frame-by-frame traffic player",
    }
    with open(output_dir / "summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    
    print("\n" + "=" * 60)
    print(f"Done! Open: {output_dir / 'player.html'}")
    print("Controls: Space=Play/Pause, Arrow Keys=Step")
    print("=" * 60)


if __name__ == "__main__":
    main()
