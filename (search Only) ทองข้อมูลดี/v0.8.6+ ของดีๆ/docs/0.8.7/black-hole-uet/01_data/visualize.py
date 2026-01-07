"""
CCBH Analysis Pipeline - Visualization
========================================
Create publication-quality plots
"""

import numpy as np
import matplotlib.pyplot as plt


def setup_plot_style():
    """Set up nice plot aesthetics."""
    plt.style.use("default")
    plt.rcParams.update(
        {
            "font.size": 12,
            "axes.labelsize": 14,
            "axes.titlesize": 16,
            "xtick.labelsize": 11,
            "ytick.labelsize": 11,
            "legend.fontsize": 11,
            "figure.figsize": (10, 8),
            "figure.dpi": 100,
            "savefig.dpi": 150,
            "axes.grid": True,
            "grid.alpha": 0.3,
        }
    )


def plot_raw_data(z, logMBH, output_path="raw_data.png"):
    """Plot raw M_BH vs redshift."""
    setup_plot_style()

    fig, ax = plt.subplots(figsize=(10, 7))

    # Scatter plot with alpha for density
    ax.scatter(z, logMBH, alpha=0.1, s=2, c="blue", label=f"N = {len(z):,}")

    ax.set_xlabel("Redshift z")
    ax.set_ylabel(r"$\log_{10}(M_{BH} / M_\odot)$")
    ax.set_title("Quasar Black Hole Masses vs Redshift")
    ax.legend(loc="upper right")

    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()
    print(f"Saved: {output_path}")


def plot_ccbh_fit(bins, fit_result, output_path="ccbh_fit.png"):
    """
    Plot the CCBH fit result.

    Parameters
    ----------
    bins : list of dict
        Binned data from quality_cuts.bin_by_redshift
    fit_result : dict
        Result from ccbh_analysis.fit_ccbh_model
    output_path : str
        Output filename
    """
    setup_plot_style()

    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    # Extract bin data
    z_med = np.array([b["z_median"] for b in bins])
    logMBH_med = np.array([b["logMBH_median"] for b in bins])
    logMBH_std = np.array([b["logMBH_std"] for b in bins])
    n_obj = np.array([b["n_objects"] for b in bins])

    # Scale factor
    a = 1.0 / (1.0 + z_med)
    log_a = np.log10(a)

    # Left panel: M_BH vs z
    ax1 = axes[0]
    ax1.errorbar(
        z_med,
        logMBH_med,
        yerr=logMBH_std,
        fmt="o",
        markersize=8,
        capsize=4,
        color="blue",
        label="Data (binned)",
    )

    # Plot fit
    z_fit = np.linspace(z_med.min(), z_med.max(), 100)
    a_fit = 1.0 / (1.0 + z_fit)
    log_a_fit = np.log10(a_fit)
    logMBH_fit = fit_result["logM0"] + fit_result["k_fit"] * log_a_fit

    ax1.plot(
        z_fit,
        logMBH_fit,
        "r-",
        linewidth=2,
        label=f"Fit: k = {fit_result['k_fit']:.2f} ± {fit_result['k_err']:.2f}",
    )

    # Farrah prediction
    logMBH_farrah = fit_result["logM0"] + 3.0 * log_a_fit
    ax1.plot(z_fit, logMBH_farrah, "g--", linewidth=2, alpha=0.7, label="Farrah (2023): k = 3.0")

    ax1.set_xlabel("Redshift z")
    ax1.set_ylabel(r"$\log_{10}(M_{BH} / M_\odot)$")
    ax1.set_title("CCBH Scaling: $M_{BH}$ vs Redshift")
    ax1.legend(loc="best")
    ax1.invert_xaxis()  # High z on left

    # Right panel: log(M) vs log(a)
    ax2 = axes[1]
    ax2.errorbar(
        log_a,
        logMBH_med,
        yerr=logMBH_std,
        fmt="o",
        markersize=8,
        capsize=4,
        color="blue",
        label="Data",
    )

    ax2.plot(log_a_fit, logMBH_fit, "r-", linewidth=2, label=f'k = {fit_result["k_fit"]:.2f}')
    ax2.plot(log_a_fit, logMBH_farrah, "g--", linewidth=2, alpha=0.7, label="k = 3.0")

    ax2.set_xlabel(r"$\log_{10}(a)$ = $\log_{10}(1/(1+z))$")
    ax2.set_ylabel(r"$\log_{10}(M_{BH} / M_\odot)$")
    ax2.set_title(r"Linear Fit: $\log M = \log M_0 + k \log a$")
    ax2.legend(loc="best")

    # Add text box with results
    textstr = f"k = {fit_result['k_fit']:.3f} ± {fit_result['k_err']:.3f}\n"
    textstr += f"$\\chi^2$/dof = {fit_result['chi2']:.1f}/{fit_result['ndof']}"
    props = dict(boxstyle="round", facecolor="wheat", alpha=0.8)
    ax2.text(
        0.05,
        0.95,
        textstr,
        transform=ax2.transAxes,
        fontsize=12,
        verticalalignment="top",
        bbox=props,
    )

    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()
    print(f"Saved: {output_path}")


def plot_bootstrap_distribution(bootstrap_result, output_path="bootstrap_k.png"):
    """Plot bootstrap k distribution."""
    setup_plot_style()

    fig, ax = plt.subplots(figsize=(10, 6))

    k_samples = bootstrap_result["k_samples"]

    # Histogram
    ax.hist(
        k_samples,
        bins=50,
        density=True,
        alpha=0.7,
        color="blue",
        label=f"Bootstrap (N={len(k_samples)})",
    )

    # Mark median and CIs
    ax.axvline(
        bootstrap_result["k_median"],
        color="red",
        linestyle="-",
        linewidth=2,
        label=f"Median = {bootstrap_result['k_median']:.3f}",
    )
    ax.axvline(bootstrap_result["k_16"], color="red", linestyle="--", linewidth=1.5)
    ax.axvline(bootstrap_result["k_84"], color="red", linestyle="--", linewidth=1.5)

    # Mark Farrah prediction
    ax.axvline(3.0, color="green", linestyle="-", linewidth=2, label="Farrah (2023): k = 3.0")

    ax.set_xlabel("k (coupling parameter)")
    ax.set_ylabel("Probability Density")
    ax.set_title("Bootstrap Distribution of CCBH Coupling Parameter k")
    ax.legend(loc="best")

    # Add text
    textstr = f"k = {bootstrap_result['k_median']:.3f}\n"
    textstr += f"68% CI: [{bootstrap_result['k_16']:.3f}, {bootstrap_result['k_84']:.3f}]\n"
    textstr += f"95% CI: [{bootstrap_result['k_2.5']:.3f}, {bootstrap_result['k_97.5']:.3f}]"
    props = dict(boxstyle="round", facecolor="wheat", alpha=0.8)
    ax.text(
        0.95,
        0.95,
        textstr,
        transform=ax.transAxes,
        fontsize=11,
        verticalalignment="top",
        horizontalalignment="right",
        bbox=props,
    )

    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()
    print(f"Saved: {output_path}")


def plot_comparison_summary(comparison, output_path="comparison_summary.png"):
    """Plot comparison with Farrah (2023)."""
    setup_plot_style()

    fig, ax = plt.subplots(figsize=(8, 6))

    # Plot both measurements
    x = [0, 1]
    y = [comparison["k_fit"], comparison["k_farrah"]]
    yerr = [comparison["k_err"], comparison["k_farrah_err"]]
    labels = ["This Work", "Farrah (2023)"]
    colors = ["blue", "green"]

    for i in range(2):
        ax.errorbar(
            x[i],
            y[i],
            yerr=yerr[i],
            fmt="o",
            markersize=15,
            capsize=8,
            capthick=2,
            color=colors[i],
            label=labels[i],
        )

    # Horizontal line at k=3
    ax.axhline(3.0, color="gray", linestyle="--", alpha=0.5, label="k = 3 (cosmological)")

    ax.set_xlim(-0.5, 1.5)
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylabel("k (coupling parameter)")
    ax.set_title(f'CCBH Coupling Parameter Comparison ({comparison["sigma"]:.1f}σ difference)')
    ax.legend(loc="best")

    # Decision box
    decision_colors = {
        "GO": "green",
        "INVESTIGATE": "orange",
        "INTERESTING": "yellow",
        "INVESTIGATE MORE": "red",
    }
    box_color = decision_colors.get(comparison["decision"], "gray")
    textstr = f"Decision: {comparison['decision']}"
    props = dict(boxstyle="round", facecolor=box_color, alpha=0.5)
    ax.text(
        0.5,
        0.05,
        textstr,
        transform=ax.transAxes,
        fontsize=14,
        horizontalalignment="center",
        bbox=props,
    )

    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()
    print(f"Saved: {output_path}")


if __name__ == "__main__":
    print("Visualization Module")
    print("\nThis creates publication-quality plots!")
    print("\nUsage: run via run_all.py")
