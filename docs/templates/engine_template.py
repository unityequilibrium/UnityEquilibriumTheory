#!/usr/bin/env python3
"""
Template for New Engine Class
==============================

This template demonstrates the correct way to use UETMetricLogger in an Engine class
with the Triple-Green Output Standard.

Usage:
1. Copy this file to your topic's Code/01_Engine/ directory
2. Replace placeholders with your actual code
3. Follow the comments for proper logging usage
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(project_root))

from docs.scripts.core.runners.uet_glass_box import UETMetricLogger


class MyEngine:
    """
    Template Engine Class

    This class demonstrates proper logging usage with UETMetricLogger.
    """

    def __init__(self, topic_id: str):
        """
        Initialize the engine.

        Args:
            topic_id: Topic ID (e.g., "0.0", "0.1", etc.)
        """
        self.topic_id = topic_id

        # ====================================================================
        # Initialize Loggers (CORRECT WAY)
        # ====================================================================

        # ✅ CORRECT: Use topic_id + category for logs
        # This will create output in: Result/_Logs/TIMESTAMP_MyEngine_Logs/
        self.logger = UETMetricLogger(
            "MyEngine_Logs",
            topic_id=self.topic_id,
            category="log"
        )

        # ✅ CORRECT: Use topic_id + category for showcase
        # This will create output in: Result/01_Showcase/
        self.showcase_logger = UETMetricLogger(
            "MyEngine_Showcase",
            topic_id=self.topic_id,
            category="showcase"
        )

        # ✅ CORRECT: Use topic_id + category for figures
        # This will create output in: Result/02_Figures/
        self.figures_logger = UETMetricLogger(
            "MyEngine_Figures",
            topic_id=self.topic_id,
            category="figures"
        )

        print(f"📂 Logs: {self.logger.run_dir}")
        print(f"📂 Showcase: {self.showcase_logger.run_dir}")
        print(f"📂 Figures: {self.figures_logger.run_dir}")

        # Initialize engine state
        self.step = 0
        self.time = 0.0

    def run_simulation(self, num_steps: int = 100):
        """
        Run the simulation.

        Args:
            num_steps: Number of simulation steps
        """
        print(f"\n🚀 Starting simulation ({num_steps} steps)...")

        for step in range(num_steps):
            # Your simulation code here
            self.time += 0.1
            omega = 1.0  # Example value
            kinetic = 0.5  # Example value
            potential = 0.5  # Example value

            # ✅ Log simulation data (automatically saves to _Logs/)
            self.logger.log_step(
                step=step,
                time=self.time,
                omega=omega,
                kinetic=kinetic,
                potential=potential
            )

            # Save figures every 20 steps
            if step % 20 == 0:
                # Example: Save to figures directory
                # self.figures_logger.save_figure(plt.gcf(), f"step_{step}.png")
                pass

            # Save showcase every 50 steps
            if step % 50 == 0:
                # Example: Save to showcase directory
                # self.showcase_logger.save_figure(plt.gcf(), f"showcase_step_{step}.png")
                pass

        print(f"✅ Simulation complete!")

    def save_reports(self):
        """Save final reports."""
        print("\n💾 Saving reports...")

        # Save metadata
        self.logger.set_metadata({
            "topic_id": self.topic_id,
            "engine_name": "MyEngine",
            "total_steps": self.step,
            "final_time": self.time
        })

        # Save reports
        self.logger.save_report()
        self.showcase_logger.save_report()
        self.figures_logger.save_report()

        print(f"✅ Reports saved!")
        print(f"   Logs: {self.logger.run_dir}")
        print(f"   Showcase: {self.showcase_logger.run_dir}")
        print(f"   Figures: {self.figures_logger.run_dir}")


def main():
    """Main entry point."""
    # Create engine
    engine = MyEngine(topic_id="0.0")  # Replace with your topic ID

    # Run simulation
    engine.run_simulation(num_steps=100)

    # Save reports
    engine.save_reports()


if __name__ == "__main__":
    main()
