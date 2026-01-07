import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import networkx as nx
import os
from scipy.optimize import curve_fit

# --- CONFIG ---
DATA_DIR = (
    r"c:\Users\santa\Desktop\lad\Lab_uet_harness_v0.8.7\research_v3\03_universal_physics\data"
)
RESULTS_DIR = r"c:\Users\santa\Desktop\lad\Lab_uet_harness_v0.8.7\research_v3\03_universal_physics\results_complex"
os.makedirs(RESULTS_DIR, exist_ok=True)


def power_law(x, a, gamma):
    return a * x ** (-gamma)


def analyze_networks():
    print("--- ANALYZING NETWORK TOPOLOGY (Scale-Free Check) ---")
    networks = {
        "Network_Karate.txt": "Karate Club",
        "Network_Enron.txt": "Enron Email",
        "Network_Social_FB.txt": "Facebook",
        "Network_Citation.txt": "Citation Graph",
    }

    summary = []

    for filename, label in networks.items():
        path = os.path.join(DATA_DIR, filename)
        if not os.path.exists(path):
            print(f"SKIP: {filename} not found.")
            continue

        print(f"Processing {label}...")
        try:
            if filename == "Network_Karate.txt":
                try:
                    G = nx.read_edgelist(path, nodetype=int)
                except:
                    G = nx.read_weighted_edgelist(path)
            else:
                G = nx.read_edgelist(path, nodetype=int)

            degrees = [d for n, d in G.degree()]
            degree_counts = pd.Series(degrees).value_counts().sort_index()
            x = degree_counts.index.values
            y = degree_counts.values

            mask = x > 2
            if sum(mask) > 5:
                x_fit = x[mask]
                y_fit = y[mask]
                try:
                    popt, _ = curve_fit(power_law, x_fit, y_fit, p0=[max(y), 2.0])
                    gamma = popt[1]
                except:
                    coeffs = np.polyfit(np.log(x_fit), np.log(y_fit), 1)
                    gamma = -coeffs[0]
            else:
                gamma = 0

            print(f"   Scale-Free Exponent (gamma): {gamma:.4f}")

            plt.figure()
            plt.loglog(x, y, "b.", label="Data")
            if gamma > 0:
                plt.loglog(x, power_law(x, *popt), "r-", label=f"Fit $\gamma$={gamma:.2f}")
            plt.title(f"{label} Degree Distribution")
            plt.xlabel("Degree (k)")
            plt.ylabel("Count P(k)")
            plt.legend()
            plt.savefig(os.path.join(RESULTS_DIR, f"{filename}_dist.png"))
            plt.close()

            summary.append(
                {
                    "System": label,
                    "Type": "Network",
                    "Metric": "Scale-Free Gamma",
                    "Value": gamma,
                    "Result": "Fluid Topology" if gamma > 1.5 else "Random/Rigid",
                }
            )

        except Exception as e:
            print(f"   FAIL: {e}")

    return summary


def analyze_biology():
    print("\n--- ANALYZING BIOLOGY (HRV 1/f Noise) ---")
    # Updated filename based on manual copy
    path = os.path.join(DATA_DIR, "Biology_HRV.csv")
    if not os.path.exists(path):
        print("   SKIP: Biology_HRV.csv not found")
        return []

    try:
        df = pd.read_csv(path, comment="#")
        # Check if wide format (RR_Interval_1...)
        rr_cols = [c for c in df.columns if "RR" in c]
        if rr_cols:
            rr_data = df[rr_cols].values.flatten()
        else:
            # Assume simple list if no RR cols
            rr_data = df.iloc[:, 0].values

        rr_data = rr_data[~np.isnan(rr_data)]

        # PSD
        psd, freqs = plt.psd(rr_data, NFFT=256, Fs=1.0)
        plt.close()

        # Fit 1/f region
        mask = (freqs > 0.01) & (freqs < 0.2)
        if sum(mask) > 5:
            x_fit = freqs[mask]
            y_fit = psd[mask]

            coeffs = np.polyfit(np.log10(x_fit), np.log10(y_fit), 1)
            beta = -coeffs[0]

            print(f"   HRV Spectral Slope (beta): {beta:.4f}")

            plt.figure()
            plt.loglog(freqs, psd, "g-", alpha=0.5, label="PSD")
            plt.loglog(
                x_fit, 10 ** (coeffs[1] - beta * np.log10(x_fit)), "r-", label=f"1/f^{beta:.2f}"
            )
            plt.title(f"Biology: HRV 1/f Scaling")
            plt.xlabel("Frequency")
            plt.ylabel("Power")
            plt.legend()
            plt.savefig(os.path.join(RESULTS_DIR, "HRV_Scaling.png"))
            plt.close()

            res = "Pink Noise (Healthy)" if 0.5 < beta < 1.5 else "White/Brown Noise"

            return [
                {
                    "System": "Human Heart",
                    "Type": "Biology",
                    "Metric": "1/f Beta",
                    "Value": beta,
                    "Result": res,
                }
            ]
        else:
            print("   WARN: Not enough frequency data.")
            return []

    except Exception as e:
        print(f"   BIO FAIL: {e}")
        return []


def run_analysis():
    s1 = analyze_networks()
    s2 = analyze_biology()

    total = s1 + s2
    df = pd.DataFrame(total)

    print("\n--- COMPLEX SYSTEMS RESULTS ---")
    print(df)
    df.to_csv(os.path.join(RESULTS_DIR, "complex_summary.csv"), index=False)


if __name__ == "__main__":
    run_analysis()
