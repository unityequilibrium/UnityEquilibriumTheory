#!/usr/bin/env python3
"""
Log Reset Manager - Interactive Master Interface

Provides an interactive menu system for managing log resets across all topics.
Supports batch operations, selective resets, and schedule-based cleanup.
"""

# BEGIN UET REPO ROOT BOOTSTRAP
import sys as _uet_sys
from pathlib import Path as _UETPath

_UET_REPO_ROOT = None
_UET_HERE = _UETPath(__file__).resolve()
for _UET_CANDIDATE in (_UET_HERE.parent, *_UET_HERE.parents):
    if (_UET_CANDIDATE / "docs" / "core" / "core_paths.py").is_file():
        _UET_REPO_ROOT = _UET_CANDIDATE
        break
if _UET_REPO_ROOT is None:
    raise RuntimeError("cannot locate repository root from the tooling script")
if str(_UET_REPO_ROOT) not in _uet_sys.path:
    _uet_sys.path.insert(0, str(_UET_REPO_ROOT))
# END UET REPO ROOT BOOTSTRAP

import sys
from pathlib import Path
from datetime import datetime

# Import core reset system
from reset_topic_logs import LogResetter


class LogResetManager:
    """Interactive manager for log reset operations."""

    def __init__(self):
        self.resetter = None

    def print_header(self, title):
        """Print a formatted header."""
        print()
        print("=" * 80)
        print(title)
        print("=" * 80)
        print()

    def print_menu(self):
        """Print the main menu."""
        self.print_header("LOG RESET MANAGER")
        print("1. Analyze log distribution")
        print("2. Diagnose log system health")
        print("3. Reset logs for a specific topic")
        print("4. Reset logs by category")
        print("5. Reset all logs (DANGEROUS)")
        print("6. Quick cleanup (excessive logs only)")
        print("7. Exit")
        print()

    def analyze_distribution(self):
        """Run log distribution analysis."""
        self.print_header("LOG DISTRIBUTION ANALYSIS")

        try:
            from analyze_log_distribution import main as analyze_main
            analyze_main()
        except ImportError:
            print("Error: Could not import analyze_log_distribution module")
            print("Make sure analyze_log_distribution.py is in the same directory.")

        input("\nPress Enter to continue...")

    def diagnose_health(self):
        """Run log system health diagnostic."""
        self.print_header("LOG SYSTEM HEALTH DIAGNOSTIC")

        try:
            from diagnose_log_systems import main as diagnose_main
            diagnose_main()
        except ImportError:
            print("Error: Could not import diagnose_log_systems module")
            print("Make sure diagnose_log_systems.py is in the same directory.")

        input("\nPress Enter to continue...")

    def reset_specific_topic(self):
        """Reset logs for a specific topic."""
        self.print_header("RESET LOGS FOR SPECIFIC TOPIC")

        # List all topics
        topics_root = _UET_REPO_ROOT / "docs" / "topics"
        topics = sorted([t.name for t in topics_root.iterdir() if t.is_dir() and t.name.startswith("0.")])

        print("Available topics:")
        for i, topic in enumerate(topics, 1):
            print(f"  {i:2d}. {topic}")

        # Get topic selection
        try:
            topic_num = int(input("\nEnter topic number: ")) - 1
            if topic_num < 0 or topic_num >= len(topics):
                print("Invalid selection")
                return

            topic = topics[topic_num]
        except ValueError:
            print("Invalid input")
            return

        # Get options
        print("\nOptions:")
        print("  1. Delete all logs")
        print("  2. Keep 10 most recent")
        print("  3. Keep 20 most recent")
        print("  4. Keep 50 most recent")
        print("  5. Custom number")

        try:
            option = int(input("\nSelect option: "))
            if option == 1:
                keep_recent = 0
            elif option == 2:
                keep_recent = 10
            elif option == 3:
                keep_recent = 20
            elif option == 4:
                keep_recent = 50
            elif option == 5:
                keep_recent = int(input("Keep how many most recent? "))
            else:
                print("Invalid selection")
                return
        except ValueError:
            print("Invalid input")
            return

        # Dry run first
        print("\n--- DRY RUN ---")
        self.resetter = LogResetter(dry_run=True, verbose=True)
        self.resetter.reset_topic(topic, keep_recent=keep_recent, force=True)

        # Confirm
        response = input("\nProceed with actual deletion? [y/N]: ")
        if response.lower() != 'y':
            print("Cancelled")
            return

        # Actual reset
        print("\n--- ACTUAL RESET ---")
        self.resetter = LogResetter(dry_run=False, verbose=True)
        self.resetter.reset_topic(topic, keep_recent=keep_recent, force=False)

        # Generate report
        self.resetter.generate_report()

        input("\nPress Enter to continue...")

    def reset_by_category(self):
        """Reset logs by category."""
        self.print_header("RESET LOGS BY CATEGORY")

        print("Categories:")
        print("  1. EXCESSIVE (1000+ logs)")
        print("  2. HIGH (500-999 logs)")
        print("  3. MODERATE (100-499 logs)")
        print("  4. LOW (10-99 logs)")
        print("  5. MINIMAL (1-9 logs)")
        print("  6. NO_LOGS (0 logs)")

        try:
            option = int(input("\nSelect category: "))
            categories = ["", "EXCESSIVE", "HIGH", "MODERATE", "LOW", "MINIMAL", "NO_LOGS"]
            category = categories[option]
        except (ValueError, IndexError):
            print("Invalid selection")
            return

        # Get keep recent option
        keep_recent = int(input("Keep how many most recent? [0 for all]: ") or "0")

        # Dry run first
        print("\n--- DRY RUN ---")
        self.resetter = LogResetter(dry_run=True, verbose=True)
        self.resetter.reset_by_category(category, keep_recent=keep_recent, force=True)

        # Confirm
        response = input("\nProceed with actual deletion? [y/N]: ")
        if response.lower() != 'y':
            print("Cancelled")
            return

        # Actual reset
        print("\n--- ACTUAL RESET ---")
        self.resetter = LogResetter(dry_run=False, verbose=True)
        self.resetter.reset_by_category(category, keep_recent=keep_recent, force=False)

        # Generate report
        self.resetter.generate_report()

        input("\nPress Enter to continue...")

    def reset_all_logs(self):
        """Reset all logs (dangerous operation)."""
        self.print_header("RESET ALL LOGS (DANGEROUS)")

        print("WARNING: This will reset logs for ALL topics!")
        print("This operation cannot be undone.")
        print()

        response = input("Are you sure? [yes/NO]: ")
        if response.lower() not in ['yes', 'y']:
            print("Cancelled")
            return

        # Get keep recent option
        keep_recent = int(input("Keep how many most recent per topic? [0 for all]: ") or "0")

        # Dry run first
        print("\n--- DRY RUN ---")
        self.resetter = LogResetter(dry_run=True, verbose=True)
        self.resetter.reset_all_topics(keep_recent=keep_recent, force=True)

        # Confirm
        response = input("\nProceed with actual deletion? [yes/NO]: ")
        if response.lower() != 'yes':
            print("Cancelled")
            return

        # Actual reset
        print("\n--- ACTUAL RESET ---")
        self.resetter = LogResetter(dry_run=False, verbose=True)
        self.resetter.reset_all_topics(keep_recent=keep_recent, force=False)

        # Generate report
        self.resetter.generate_report()

        input("\nPress Enter to continue...")

    def quick_cleanup(self):
        """Quick cleanup for excessive logs only."""
        self.print_header("QUICK CLEANUP (EXCESSIVE LOGS ONLY)")

        print("This will reset logs for topics with 1000+ log files.")
        print("Keeping 10 most recent timestamp folders per topic.")
        print()

        response = input("Proceed? [y/N]: ")
        if response.lower() != 'y':
            print("Cancelled")
            return

        # Dry run first
        print("\n--- DRY RUN ---")
        self.resetter = LogResetter(dry_run=True, verbose=True)
        self.resetter.reset_by_category("EXCESSIVE", keep_recent=10, force=True)

        # Confirm
        response = input("\nProceed with actual deletion? [y/N]: ")
        if response.lower() != 'y':
            print("Cancelled")
            return

        # Actual reset
        print("\n--- ACTUAL RESET ---")
        self.resetter = LogResetter(dry_run=False, verbose=True)
        self.resetter.reset_by_category("EXCESSIVE", keep_recent=10, force=False)

        # Generate report
        self.resetter.generate_report()

        input("\nPress Enter to continue...")

    def run(self):
        """Run the interactive manager."""
        while True:
            self.print_menu()

            try:
                choice = input("Enter choice: ")

                if choice == "1":
                    self.analyze_distribution()
                elif choice == "2":
                    self.diagnose_health()
                elif choice == "3":
                    self.reset_specific_topic()
                elif choice == "4":
                    self.reset_by_category()
                elif choice == "5":
                    self.reset_all_logs()
                elif choice == "6":
                    self.quick_cleanup()
                elif choice == "7":
                    print("Exiting...")
                    break
                else:
                    print("Invalid choice")
            except KeyboardInterrupt:
                print("\nInterrupted")
                break
            except Exception as e:
                print(f"Error: {e}")
                input("Press Enter to continue...")


def main():
    """Main entry point."""
    print()
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 78 + "║")
    print("║" + " " * 20 + "LOG RESET MANAGER" + " " * 47 + "║")
    print("║" + " " * 78 + "║")
    print("╚" + "=" * 78 + "╝")
    print()
    print("Interactive tool for managing log resets across UET research topics.")
    print()

    manager = LogResetManager()
    manager.run()


if __name__ == "__main__":
    main()
