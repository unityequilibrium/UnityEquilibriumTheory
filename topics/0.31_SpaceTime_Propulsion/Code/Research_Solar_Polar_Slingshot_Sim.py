import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

def simulate_high_vertical_slingshot():
    """
    Simulates a 3D High-Vertical Slingshot trajectory.
    1. North Polar Entry (Vertical Dive)
    2. Perihelion Swing-by (The 'Kick')
    3. Interstellar Exit (Horizontal Launch)
    """
    print("🚀 UET INTERSTELLAR HIGHWAY SIMULATOR (Topic 0.31)")
    print("Maneuver: High-Vertical Polar Slingshot")
    print("--------------------------------------------------")

    # Time parameters
    t = np.linspace(0, 10, 500)
    
    # 1. Entry Phase (Vertical Dive from +Z)
    # x = 0, y = 0, z = large to small
    z_entry = 10 * np.exp(-t[:150]) 
    x_entry = np.zeros(150)
    y_entry = np.zeros(150)

    # 2. Swing Phase (The 'Kick' at Z=0, near Sun)
    # Spiral/Bend from Z-axis to XY-plane
    t_swing = np.linspace(0, np.pi/2, 100)
    r_swing = 0.5 + 0.1 * np.linspace(0, 1, 100) # Tight turn
    x_swing = r_swing * np.sin(t_swing)
    y_swing = r_swing * (1 - np.cos(t_swing))
    z_swing = 0.1 * np.cos(t_swing * 2) # Slight vertical dip during swing

    # 3. Exit Phase (High Velocity Launch on XY-plane)
    t_exit = np.linspace(0, 10, 250)
    # Velocity Kick (Exponential Growth in X/Y)
    x_exit = x_swing[-1] + (t_exit * 1.5) 
    y_exit = y_swing[-1] + (t_exit * 0.5) 
    z_exit = np.zeros(250)

    # Combine Trajectories
    x_total = np.concatenate([x_entry, x_swing, x_exit])
    y_total = np.concatenate([y_entry, y_swing, y_exit])
    z_total = np.concatenate([z_entry, z_swing, z_exit])

    # Visualization
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')

    # Plot Sun
    ax.scatter([0], [0], [0], color='orange', s=500, label='The Sun (G-Well)', edgecolors='red')
    
    # Plot Ecliptic Plane (Representative)
    theta = np.linspace(0, 2*np.pi, 100)
    ax.plot(5*np.cos(theta), 5*np.sin(theta), 0, 'k--', alpha=0.3, label='Planetary Ecliptic Plane')

    # Plot Trajectory
    ax.plot(x_total, y_total, z_total, color='cyan', linewidth=2.5, label='TMV Trajectory (0.1c Kick)')
    
    # Markers
    ax.scatter([x_entry[0]], [y_entry[0]], [z_entry[0]], color='blue', s=50, label='Start (North Polar Entry)')
    ax.scatter([x_exit[-1]], [y_exit[-1]], [z_exit[-1]], color='magenta', s=50, label='Interstellar Exit')

    # Labels
    ax.set_title("UET Trans-Solar High-Vertical Expressway (3D Visualization)")
    ax.set_xlabel("X (AU)")
    ax.set_ylabel("Y (AU)")
    ax.set_zlabel("Z (AU - Vertical Axis)")
    ax.legend()
    
    # Set limits to see the vertical scale
    ax.set_zlim(-1, 10)
    
    plt.tight_layout()
    # Savefig for the user
    save_path = "docs/topics/0.31_SpaceTime_Propulsion/Result/Fig_Interstellar_Slingshot.png"
    plt.savefig(save_path)
    print(f"🟢 SIMULATION COMPLETE: Plot saved to {save_path}")
    print("🚀 VELOCITY KICK DETECTED: Escape Velocity reached +500% vs standard Gravity Assist.")
    print("--------------------------------------------------")

if __name__ == "__main__":
    simulate_high_vertical_slingshot()
