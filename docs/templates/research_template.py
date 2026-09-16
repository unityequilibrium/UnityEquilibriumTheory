#!/usr/bin/env python3
"""
Template for New Research Topic
================================

This template demonstrates the correct way to use UETMetricLogger with the
Triple-Green Output Standard.

Usage:
1. Copy this file to your topic's Code/03_Research/ directory
2. Replace placeholders with your actual code
3. Follow the comments for proper logging usage
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(project_root))

from docs.scripts.core.runners.uet_glass_box import UETPathManager, UETMetricLogger


def main():
    """Main research function."""
    # ========================================================================
    # STEP 1: Initialize Logging (CORRECT WAY)
    # ========================================================================

    # ✅ CORRECT: Use topic_id + category
    # This will create output in: Result/01_Showcase/
    showcase_logger = UETMetricLogger(
        "My_Research_Showcase",
        topic_id="0.0",  # Replace with your topic ID
        category="showcase"
    )

    # ✅ CORRECT: Use topic_id + category
    # This will create output in: Result/02_Figures/
    figures_logger = UETMetricLogger(
        "My_Research_Figures",
        topic_id="0.0",  # Replace with your topic ID
        category="figures"
    )

    # ✅ CORRECT: Use topic_id + category
    # This will create output in: Result/_Logs/TIMESTAMP_My_Research_Logs/
    log_logger = UETMetricLogger(
        "My_Research_Logs",
        topic_id="0.0",  # Replace with your topic ID
        category="log"
    )

    print(f"📂 Showcase Output: {showcase_logger.run_dir}")
    print(f"📂 Figures Output: {figures_logger.run_dir}")
    print(f"📂 Logs Output: {log_logger.run_dir}")

    # ========================================================================
    # STEP 2: Your Research Code Here
    # ========================================================================

    # Example: Save high-quality visualizations to showcase
    # (Use for social media, papers, presentations)
    # showcase_logger.save_figure(plt.gcf(), "My_Research_Social.png")

    # Example: Save technical plots to figures
    # (Use for validation, analysis)
    # figures_logger.save_figure(plt.gcf(), "parity_plot.png")

    # Example: Log simulation data
    # (Automatically saves to _Logs/TIMESTAMP_My_Research_Logs/)
    # log_logger.log_step(step=0, time=0.0, omega=1.0, kinetic=0.5, potential=0.5)

    # ========================================================================
    # STEP 3: Save Reports
    # ========================================================================

    # Save metadata
    showcase_logger.set_metadata({
        "topic_id": "0.0",
        "experiment_name": "My_Research",
        "parameters": {
            "param1": "value1",
            "param2": "value2"
        }
    })

    # Save final report
    showcase_logger.save_report()
    figures_logger.save_report()
    log_logger.save_report()

    print("\n✅ Research complete!")
    print(f"Showcase: {showcase_logger.run_dir}")
    print(f"Figures: {figures_logger.run_dir}")
    print(f"Logs: {log_logger.run_dir}")


if __name__ == "__main__":
    main()
