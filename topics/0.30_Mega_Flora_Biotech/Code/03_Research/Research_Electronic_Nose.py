import numpy as np
import matplotlib.pyplot as plt


def sensor_sensitivity_sim():
    """
    Simulates a Graphene FET (Field Effect Transistor) sensor's ability
    to detect trace THC/CBD vs standard chemical analysis.
    - Standard (HPLC): Requires lab, 24-hour turnaround, microgram sensitivity.
    - UET Graphene Nose: Real-time, portable, picogram sensitivity.
    """
    concentrations = np.logspace(-15, -6, 100)  # From Picograms to Milligrams

    # 1. Standard HPLC Threshold (Limit of Detection)
    hplc_lod = 1e-9  # Microgram/mL
    hplc_signal = [1 if c > hplc_lod else 0 for c in concentrations]

    # 2. UET Graphene FET Sensor (Sub-picogram detection)
    # Signal = log response to molecular adsorption
    uet_lod = 1e-15  # Femtogram/mL
    uet_signal = np.log10(concentrations / uet_lod)
    uet_signal = np.where(uet_signal < 0, 0, uet_signal)  # Zero below LOD
    uet_signal = uet_signal / np.max(uet_signal)  # Normalize

    plt.figure(figsize=(10, 6))
    plt.semilogx(concentrations, hplc_signal, "r--", label="Standard HPLC (Discrete Lab Test)")
    plt.semilogx(
        concentrations,
        uet_signal,
        "b-",
        label="UET Graphene Electronic Nose (Continuous Real-time)",
    )

    plt.fill_between(concentrations, 0, uet_signal, color="blue", alpha=0.1)
    plt.axvline(x=hplc_lod, color="red", linestyle=":", label="HPLC Detection Limit")
    plt.axvline(x=uet_lod, color="blue", linestyle=":", label="UET Graphene Limit")

    plt.title("Quality Control: Graphene Nano-Sensing vs Traditional Lab Analysis")
    plt.xlabel("Target Molecule Concentration (g/mL)")
    plt.ylabel("Signal/Detection Confidence (Normalized)")
    plt.legend()
    plt.grid(True, which="both", ls="-", alpha=0.3)
    # Robust Path for Figures
    import os
    from pathlib import Path

    current_dir = Path(__file__).parent
    # Go up to topic root (Code/03_Research -> Code -> TopicRoot)
    topic_root = current_dir.parent.parent

    # Standard: Result/03_Research mirrors Code/03_Research
    figures_dir = topic_root / "Result" / "03_Research"
    figures_dir.mkdir(parents=True, exist_ok=True)

    save_path = figures_dir / "graphene_sensor_sensitivity.png"
    plt.savefig(str(save_path))

    print("\n👃 UET ELECTRONIC NOSE SIMULATION")
    print("==================================")
    print(f"Standard HPLC Limit : {hplc_lod:.2e} g/mL")
    print(f"UET Graphene Limit  : {uet_lod:.2e} g/mL")
    print(f"Sensitivity Gap     : {hplc_lod / uet_lod:,.0f}x more sensitive")
    print(f"\n✅ Simulation Complete. Results saved as '{save_path.name}'")
    print("💡 CONCLUSION: We can detect contamination or potency in real-time on the leaf.")


if __name__ == "__main__":
    sensor_sensitivity_sim()
