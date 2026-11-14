import os
import sys
import matplotlib.pyplot as plt

# Link to Engine
script_dir = os.path.dirname(os.path.abspath(__file__))
result_dir = os.path.abspath(os.path.join(script_dir, "../../Result/02_Proof"))
engine_dir = os.path.abspath(os.path.join(script_dir, "../01_Engine"))
if engine_dir not in sys.path:
    sys.path.append(engine_dir)

if not os.path.exists(result_dir):
    os.makedirs(result_dir)

from Engine_Growth_Simulation import YggdrasilEngine


def run_proof():
    log_file = os.path.join(result_dir, "Res_Bio_Anchor.txt")
    with open(log_file, "w", encoding="utf-8") as f:

        def log_print(msg):
            print(msg)
            f.write(str(msg) + "\n")

        log_print("\n🌳 UET TOPIC 0.30: THE YGGDRASIL PROJECT")
        log_print("========================================")
        log_print("Objective: Compare 'Living Roots' vs 'Dead Concrete' for flood prevention.")

        # 1. Setup Models
        engine = YggdrasilEngine()
        years = 50
        tree_timeline = engine.grow_tree(years)

        # Concrete Wall Specs (Standard Engineering)
        concrete_strength_initial = 500000.0  # N (Shear resistance of a sheet pile)
        concrete_degradation_rate = 0.015  # 1.5% decay per year (Cracks, corrosion)

        # 2. Simulation Loop (50 Years)
        log_print(
            f"\n{'Year':<5} | {'Tree Height':<12} | {'Root Depth':<12} | {'Tree Strength (N)':<18} | {'Concrete Strength (N)':<20} | {'Winner'}"
        )
        log_print("-" * 100)

        results = []  # Store for plotting (if needed)
        crossing_point = None

        concrete_current = concrete_strength_initial

        for i, state in enumerate(tree_timeline):
            year = state["year"]

            # A. Concrete Degradation
            concrete_current *= 1.0 - concrete_degradation_rate

            # B. Tree Strength (Derived from Integrity Score)
            # We normalize Integrity Score to Newtons for comparison
            # Assumption: A mature Yggdrasil (Year 50) is stronger than a typical wall
            tree_strength_n = state["integrity_score"] * 50.0

            # C. Comparison
            winner = "🏛️ Concrete"
            if tree_strength_n > concrete_current:
                winner = "🌳 Yggdrasil"
                if crossing_point is None:
                    crossing_point = year

            log_print(
                f"{year:<5} | {state['height_m']:<12} | {state['root_depth_m']:<12} | {tree_strength_n:,.0f}{'':<12} | {concrete_current:,.0f}{'':<14} | {winner}"
            )

            results.append({"year": year, "tree": tree_strength_n, "concrete": concrete_current})

        # 3. Verdict
        log_print("-" * 100)
        log_print(f"\n🏆 Final Result at Year {years}:")
        log_print(f"   Concrete Strength: {concrete_current:,.0f} N (Degraded)")
        log_print(f"   Yggdrasil Strength: {tree_strength_n:,.0f} N (Anti-Fragile)")

        if crossing_point:
            log_print(f"\n✅ SUCCESS: Biology overtakes Engineering at Year {crossing_point}.")
            log_print("Verdict: The Tree is the superior long-term investment.")
        else:
            log_print("\n❌ FAILURE: Tree never caught up to Concrete.")

        # 4. Plotting
        plt.figure(figsize=(10, 6))
        years_list = [r["year"] for r in results]
        tree_list = [r["tree"] for r in results]
        conc_list = [r["concrete"] for r in results]

        plt.plot(
            years_list, tree_list, label="Yggdrasil (Living Roots)", color="green", linewidth=2
        )
        plt.plot(
            years_list, conc_list, label="Concrete Wall (Decaying)", color="red", linestyle="--"
        )
        plt.title("Structural Integrity: Living Roots vs. Concrete Wall")
        plt.xlabel("Years")
        plt.ylabel("Strength (Newtons)")
        plt.legend()
        plt.grid(True, alpha=0.3)

        plot_path = os.path.join(result_dir, "Res_Bio_Anchor.png")
        plt.savefig(plot_path)
        log_print(f"\n📊 Plot saved to: {plot_path}")


if __name__ == "__main__":
    run_proof()
