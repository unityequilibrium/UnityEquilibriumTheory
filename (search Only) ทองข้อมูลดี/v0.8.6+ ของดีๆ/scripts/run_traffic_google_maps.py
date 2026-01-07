"""
Google Maps Style Traffic Visualization

Colors like Google Maps:
- 🟢 Green = Free flow (0-30% congestion)
- 🟡 Yellow = Moderate (30-60% congestion)  
- 🟠 Orange = Slow (60-80% congestion)
- 🔴 Red = Heavy/Jam (80-100% congestion)

Road layout: Grid city with main roads, intersections, on-ramps
"""
from __future__ import annotations
import argparse
import json
import numpy as np
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import animation
from matplotlib.colors import LinearSegmentedColormap, Normalize
from matplotlib.patches import Rectangle, Circle

# Google Maps traffic colors (exact hex values)
GOOGLE_COLORS = [
    (0.18, 0.80, 0.44),   # #2ECC71 - Green (free)
    (0.95, 0.77, 0.06),   # #F1C40F - Yellow (moderate)
    (0.90, 0.49, 0.13),   # #E67E22 - Orange (slow)
    (0.91, 0.30, 0.24),   # #E74C3C - Red (heavy)
    (0.56, 0.14, 0.14),   # #8E2323 - Dark red (jam)
]
GOOGLE_CMAP = LinearSegmentedColormap.from_list('google_traffic', GOOGLE_COLORS)


def create_road_network(N: int = 64) -> dict:
    """
    Create a realistic road network grid.
    
    Returns:
        road_mask: Binary mask (1 = road, 0 = building)
        road_type: 0 = none, 1 = local, 2 = main, 3 = highway
        intersections: List of (x, y) intersection points
    """
    road_mask = np.zeros((N, N))
    road_type = np.zeros((N, N))
    intersections = []
    
    # Main roads (horizontal and vertical)
    main_roads_h = [N//4, N//2, 3*N//4]
    main_roads_v = [N//4, N//2, 3*N//4]
    
    # Local roads (more frequent)
    local_spacing = N // 8
    
    # Draw main roads (wider, type 2)
    for y in main_roads_h:
        for dy in range(-2, 3):
            if 0 <= y + dy < N:
                road_mask[:, y + dy] = 1
                road_type[:, y + dy] = 2
    
    for x in main_roads_v:
        for dx in range(-2, 3):
            if 0 <= x + dx < N:
                road_mask[x + dx, :] = 1
                road_type[x + dx, :] = 2
    
    # Draw local roads (thinner, type 1)
    for i in range(0, N, local_spacing):
        if i not in main_roads_h:
            for dy in range(-1, 2):
                if 0 <= i + dy < N:
                    road_mask[:, i + dy] = np.maximum(road_mask[:, i + dy], 1)
                    road_type[:, i + dy] = np.where(road_type[:, i + dy] == 0, 1, road_type[:, i + dy])
        
        if i not in main_roads_v:
            for dx in range(-1, 2):
                if 0 <= i + dx < N:
                    road_mask[i + dx, :] = np.maximum(road_mask[i + dx, :], 1)
                    road_type[i + dx, :] = np.where(road_type[i + dx, :] == 0, 1, road_type[i + dx, :])
    
    # Find intersections
    for x in main_roads_v:
        for y in main_roads_h:
            intersections.append((x, y))
    
    return {
        "mask": road_mask,
        "type": road_type,
        "intersections": intersections,
    }


def run_google_traffic_sim(road_net: dict, scenario: str = "rush_hour", 
                           n_steps: int = 300, dt: float = 0.05) -> dict:
    """
    Run traffic simulation with realistic congestion patterns.
    """
    N = road_net["mask"].shape[0]
    road_mask = road_net["mask"]
    road_type = road_net["type"]
    intersections = road_net["intersections"]
    
    # Initialize with VERY LOW traffic (starts green!)
    traffic = np.random.rand(N, N) * 0.02 * road_mask  # Almost empty roads
    
    # Capacity based on road type (main roads have higher capacity)
    capacity = np.where(road_type == 2, 1.0, 0.6) * road_mask
    
    # Speed based on road type
    speed = np.where(road_type == 2, 1.5, 1.0) * road_mask
    
    # Accident scenario: block intersection but don't add traffic yet
    if scenario == "accident":
        cx, cy = N//2, N//2
        for dx in range(-5, 6):
            for dy in range(-5, 6):
                if 0 <= cx+dx < N and 0 <= cy+dy < N:
                    speed[cx+dx, cy+dy] *= 0.1  # Almost blocked
    
    # Simulation parameters
    kappa = 0.3  # Diffusion
    dx = 1.0 / N
    
    traffic_history = [traffic.copy()]
    avg_congestion = [float(np.mean(traffic[road_mask > 0] / np.maximum(capacity[road_mask > 0], 0.1)))]
    
    print(f"  Simulating {scenario}: {n_steps} steps...")
    
    for step in range(1, n_steps + 1):
        progress = step / n_steps  # 0 to 1
        
        # Calculate current congestion level
        congestion = traffic / np.maximum(capacity, 0.1)
        
        # Speed decreases with congestion (like real traffic)
        effective_speed = speed * (1 - 0.8 * np.clip(congestion, 0, 1))
        
        # Laplacian diffusion (traffic spreading)
        lap = (np.roll(traffic, 1, 0) + np.roll(traffic, -1, 0) +
               np.roll(traffic, 1, 1) + np.roll(traffic, -1, 1) - 4*traffic) / dx**2
        
        # Update
        d_traffic = kappa * effective_speed * lap * road_mask
        
        # Add inflow based on scenario and time
        if scenario == "rush_hour":
            if progress < 0.3:  # First 30%: light traffic (green)
                inflow = 0.005
            elif progress < 0.5:  # 30-50%: building (yellow to orange)
                inflow = 0.03
            elif progress < 0.7:  # 50-70%: peak (red!)
                inflow = 0.05
            else:  # 70-100%: clearing (back to green)
                inflow = 0.005
            
            traffic[0, :] += inflow * road_mask[0, :]
            traffic[:, 0] += inflow * road_mask[:, 0]
            
        elif scenario == "accident":
            # Steady flow that backs up at accident
            inflow = 0.015 if progress < 0.7 else 0.005
            traffic[0, :] += inflow * road_mask[0, :]
            traffic[:, 0] += inflow * road_mask[:, 0]
            
        elif scenario == "event":
            # Build up to event, then disperse
            if progress < 0.4:
                inflow = 0.02 * (progress / 0.4)  # Building
            elif progress < 0.6:
                inflow = 0.02  # Peak
            else:
                inflow = 0.005  # Dispersing
            
            # Traffic converges to center
            cx, cy = N//2, N//2
            for dx in range(-10, 11):
                for dy in range(-10, 11):
                    if 0 <= cx+dx < N and 0 <= cy+dy < N:
                        traffic[cx+dx, cy+dy] += inflow * 0.5 * road_mask[cx+dx, cy+dy]
            traffic[0, :] += inflow * road_mask[0, :]
            
        elif scenario == "normal":
            # Light steady traffic
            inflow = 0.008
            traffic[0, :] += inflow * road_mask[0, :]
            traffic[:, 0] += inflow * road_mask[:, 0]
        
        # Apply update
        traffic = traffic + dt * d_traffic
        
        # Strong dissipation at exits (traffic leaving)
        dissipation = 0.92 if progress > 0.6 else 0.96
        traffic[-1, :] *= dissipation
        traffic[:, -1] *= dissipation
        traffic[0, :] *= 0.98
        traffic[:, 0] *= 0.98
        
        # Clip and mask
        traffic = np.clip(traffic, 0, 1.2) * road_mask
        
        # Record history
        if step % (n_steps // 60) == 0:
            traffic_history.append(traffic.copy())
            avg_congestion.append(float(np.mean(traffic[road_mask > 0] / np.maximum(capacity[road_mask > 0], 0.1))))
    
    return {
        "traffic": traffic_history,
        "congestion": avg_congestion,
        "road_net": road_net,
        "scenario": scenario,
    }


def make_google_maps_animation(case_dir: Path, history: dict, fps: int = 12):
    """Create Google Maps style traffic animation."""
    traffic_hist = history["traffic"]
    congestion = history["congestion"]
    road_net = history["road_net"]
    scenario = history["scenario"]
    
    road_mask = road_net["mask"]
    road_type = road_net["type"]
    
    n_frames = len(traffic_hist)
    N = road_mask.shape[0]
    
    # Background colors
    building_color = np.array([0.95, 0.95, 0.93])  # Light gray buildings
    
    fig = plt.figure(figsize=(16, 8), facecolor='white')
    
    def update(frame):
        fig.clear()
        
        traffic = traffic_hist[frame]
        
        # Calculate congestion level (0-1)
        capacity = np.where(road_type == 2, 1.0, 0.6) * road_mask
        cong_level = np.clip(traffic / np.maximum(capacity, 0.1), 0, 1)
        
        # Left: Google Maps style view
        ax1 = fig.add_subplot(121)
        
        # Create the map image
        map_img = np.ones((N, N, 3)) * building_color
        
        # Color roads based on congestion
        for i in range(N):
            for j in range(N):
                if road_mask[i, j] > 0:
                    c = cong_level[i, j]
                    if c < 0.3:
                        color = GOOGLE_COLORS[0]  # Green
                    elif c < 0.5:
                        color = GOOGLE_COLORS[1]  # Yellow
                    elif c < 0.7:
                        color = GOOGLE_COLORS[2]  # Orange
                    elif c < 0.85:
                        color = GOOGLE_COLORS[3]  # Red
                    else:
                        color = GOOGLE_COLORS[4]  # Dark red
                    map_img[i, j] = color
        
        ax1.imshow(map_img, origin='lower', interpolation='nearest')
        
        # Add grid lines for streets
        for x in range(0, N, N//8):
            ax1.axvline(x, color='white', alpha=0.1, lw=0.5)
            ax1.axhline(x, color='white', alpha=0.1, lw=0.5)
        
        ax1.set_title(f'Traffic: {scenario.upper()}\nt = {frame * 5}s', 
                     fontsize=14, fontweight='bold')
        ax1.set_xlabel('West ← → East')
        ax1.set_ylabel('South ← → North')
        ax1.set_xticks([])
        ax1.set_yticks([])
        
        # Add legend
        legend_colors = ['#2ECC71', '#F1C40F', '#E67E22', '#E74C3C', '#8E2323']
        legend_labels = ['Free flow', 'Moderate', 'Slow', 'Heavy', 'Jam']
        for i, (color, label) in enumerate(zip(legend_colors, legend_labels)):
            ax1.add_patch(Rectangle((N*0.02, N*0.95 - i*N*0.05), N*0.08, N*0.04,
                                    facecolor=color, edgecolor='black', lw=0.5))
            ax1.text(N*0.12, N*0.97 - i*N*0.05, label, fontsize=9, va='center')
        
        # Right: Congestion timeline
        ax2 = fig.add_subplot(122)
        
        times = np.linspace(0, frame * 5, len(congestion[:frame+1]))
        
        # Color-coded congestion zones
        ax2.axhspan(0, 0.3, color='#2ECC71', alpha=0.2, label='Free')
        ax2.axhspan(0.3, 0.5, color='#F1C40F', alpha=0.2, label='Moderate')
        ax2.axhspan(0.5, 0.7, color='#E67E22', alpha=0.2, label='Slow')
        ax2.axhspan(0.7, 1.0, color='#E74C3C', alpha=0.2, label='Heavy')
        
        # Plot congestion line
        ax2.plot(times, congestion[:frame+1], 'k-', lw=2)
        ax2.scatter([times[-1]], [congestion[frame]], s=100, c='black', zorder=5)
        
        ax2.set_xlim(0, (n_frames-1) * 5)
        ax2.set_ylim(0, 1.0)
        ax2.set_xlabel('Time (seconds)', fontsize=11)
        ax2.set_ylabel('Average Congestion', fontsize=11)
        ax2.set_title('Congestion Level Over Time', fontsize=14, fontweight='bold')
        ax2.grid(True, alpha=0.3)
        
        # Current status indicator
        current_cong = congestion[frame]
        if current_cong < 0.3:
            status = "FREE FLOW"
            status_color = '#2ECC71'
        elif current_cong < 0.5:
            status = "MODERATE"
            status_color = '#F1C40F'
        elif current_cong < 0.7:
            status = "SLOW"
            status_color = '#E67E22'
        else:
            status = "HEAVY TRAFFIC"
            status_color = '#E74C3C'
        
        ax2.text(0.5, 0.92, status, transform=ax2.transAxes, 
                fontsize=16, fontweight='bold', ha='center',
                color=status_color,
                bbox=dict(boxstyle='round', facecolor='white', edgecolor=status_color, lw=2))
        
        fig.suptitle('Google Maps Style Traffic Simulation', 
                    fontsize=16, fontweight='bold', y=0.98)
        plt.tight_layout()
        
        return []
    
    ani = animation.FuncAnimation(fig, update, frames=n_frames, interval=1000//fps)
    
    output = case_dir / "google_maps_traffic.gif"
    print(f"  Saving Google Maps style animation...")
    ani.save(output, writer='pillow', fps=fps)
    plt.close(fig)
    
    # Also save as main.gif
    import shutil
    shutil.copy(output, case_dir / "main.gif")
    
    print(f"  Saved: {output}")
    return output


def main():
    parser = argparse.ArgumentParser(description="Google Maps style traffic simulation")
    parser.add_argument("--out", default="runs_gallery")
    parser.add_argument("--scenario", default="rush_hour", 
                       choices=["rush_hour", "accident", "event", "normal"])
    parser.add_argument("--N", type=int, default=64, help="Grid size")
    parser.add_argument("--steps", type=int, default=300, help="Simulation steps")
    parser.add_argument("--all", action="store_true", help="Run all scenarios")
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("Google Maps Style Traffic Simulation")
    print("=" * 60)
    
    scenarios = ["rush_hour", "accident", "event", "normal"] if args.all else [args.scenario]
    
    for scenario in scenarios:
        print(f"\nRunning: {scenario}")
        
        # Create folder
        folder_name = f"toy_traffic_google_{scenario}"
        case_dir = Path(args.out) / folder_name
        case_dir.mkdir(parents=True, exist_ok=True)
        
        # Create road network
        road_net = create_road_network(args.N)
        print(f"  Created {args.N}x{args.N} road grid")
        
        # Run simulation
        history = run_google_traffic_sim(road_net, scenario, n_steps=args.steps)
        
        # Save config
        config = {
            "case_id": folder_name,
            "model": "google_maps_traffic",
            "scenario": scenario,
            "description": f"Google Maps style traffic - {scenario}",
            "grid": {"N": args.N},
        }
        with open(case_dir / "config.json", "w") as f:
            json.dump(config, f, indent=2)
        
        # Save summary
        summary = {
            "case_id": folder_name,
            "status": "PASS",
            "scenario": scenario,
            "final_congestion": float(history["congestion"][-1]),
            "description": f"Google Maps style traffic visualization - {scenario}",
        }
        with open(case_dir / "summary.json", "w") as f:
            json.dump(summary, f, indent=2)
        
        # Create visualization
        make_google_maps_animation(case_dir, history)
        
        print(f"  Saved to: {case_dir}")
    
    print("\n" + "=" * 60)
    print("Done! Run: python scripts/generate_uet_gallery.py")
    print("=" * 60)


if __name__ == "__main__":
    main()
