#!/usr/bin/env python3
"""
Reset Topic Logs - Core Reset System

Provides flexible and safe log reset functionality for UET research topics.
Supports selective deletion, dry-run mode, and backup options.
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

from pathlib import Path
import shutil
import argparse
from datetime import datetime
import json


class LogResetter:
    """Core log reset functionality with safety features."""

    def __init__(self, dry_run=False, verbose=False):
        self.dry_run = dry_run
        self.verbose = verbose
        self.deleted_items = []
        self.skipped_items = []

    def log(self, message):
        """Print log message if verbose mode is enabled."""
        if self.verbose:
            print(f"  {message}")

    def get_log_dir(self, topic_id):
        """Get the log directory path for a topic."""
        topics_root = _UET_REPO_ROOT / "docs" / "topics"

        # Try exact match first
        topic_path = topics_root / topic_id
        if topic_path.exists():
            log_dir = topic_path / "Result" / "_Logs"
            return log_dir

        # Try to find topic by prefix (e.g., "0.10" matches "0.10_Fluid_Dynamics_Chaos")
        for topic in topics_root.iterdir():
            if topic.is_dir() and topic.name.startswith(topic_id):
                log_dir = topic / "Result" / "_Logs"
                return log_dir

        # Not found
        return None

    def count_logs(self, log_dir):
        """Count log files in a directory."""
        if not log_dir.exists():
            return 0
        return sum(1 for _ in log_dir.rglob("*") if _.is_file())

    def get_timestamp_folders(self, log_dir):
        """Get all timestamp folders sorted by timestamp (oldest first)."""
        if not log_dir.exists():
            return []

        folders = []
        for item in log_dir.iterdir():
            if item.is_dir():
                # Check if folder name starts with a digit (timestamp prefix)
                if item.name[0].isdigit():
                    try:
                        # Extract timestamp from start of name
                        timestamp_str = item.name.split('_')[0]
                        timestamp = int(timestamp_str)
                        folders.append((timestamp, item))
                    except (ValueError, IndexError):
                        # Not a timestamp folder, skip
                        pass

        # Sort by timestamp (oldest first)
        folders.sort(key=lambda x: x[0])
        return [f[1] for f in folders]

    def get_special_folders(self, log_dir):
        """Get special folders like 01_Engine, 02_Proof, etc."""
        if not log_dir.exists():
            return []

        special = []
        for item in log_dir.iterdir():
            if item.is_dir() and item.name.startswith(("0", "1", "2", "3", "4")) and not item.name.isdigit():
                special.append(item)

        return special

    def delete_folder(self, folder_path):
        """Delete a folder (or simulate in dry-run mode)."""
        if self.dry_run:
            self.log(f"[DRY RUN] Would delete: {folder_path}")
            self.deleted_items.append(str(folder_path))
            return True

        try:
            shutil.rmtree(folder_path)
            self.log(f"Deleted: {folder_path}")
            self.deleted_items.append(str(folder_path))
            return True
        except Exception as e:
            self.log(f"Failed to delete {folder_path}: {e}")
            return False

    def reset_topic(self, topic_id, keep_recent=0, keep_pattern=None, force=False):
        """Reset logs for a single topic."""
        log_dir = self.get_log_dir(topic_id)

        if not log_dir.exists():
            print(f"Topic {topic_id}: No log folder found")
            return False

        log_count = self.count_logs(log_dir)
        print(f"\nTopic {topic_id}: {log_count} log files")

        if log_count == 0:
            print("  No logs to delete")
            return True

        # Get all folders
        timestamp_folders = self.get_timestamp_folders(log_dir)
        special_folders = self.get_special_folders(log_dir)

        print(f"  Found {len(timestamp_folders)} timestamp folders")
        print(f"  Found {len(special_folders)} special folders")

        # Determine which folders to delete
        folders_to_delete = []

        # Handle timestamp folders
        if keep_recent > 0 and len(timestamp_folders) > keep_recent:
            # Keep N most recent folders, delete the rest
            folders_to_delete.extend(timestamp_folders[:-keep_recent])
            self.log(f"Keeping {keep_recent} most recent timestamp folders")
        elif keep_recent == 0:
            # Delete all timestamp folders
            folders_to_delete.extend(timestamp_folders)
            self.log(f"Deleting all timestamp folders")

        # Handle pattern matching
        if keep_pattern:
            folders_to_delete = [f for f in folders_to_delete if keep_pattern not in f.name]

        # Delete folders
        if not self.dry_run and not force:
            response = input(f"Delete {len(folders_to_delete)} folders from {topic_id}? [y/N]: ")
            if response.lower() != 'y':
                print("Cancelled")
                return False

        deleted_count = 0
        for folder in folders_to_delete:
            if self.delete_folder(folder):
                deleted_count += 1

        print(f"  Deleted {deleted_count} folders")
        return True

    def reset_all_topics(self, keep_recent=0, keep_pattern=None, force=False):
        """Reset logs for all topics."""
        topics_root = _UET_REPO_ROOT / "docs" / "topics"

        print("=" * 80)
        print("RESET ALL TOPIC LOGS")
        print("=" * 80)

        if not self.dry_run and not force:
            response = input("This will reset logs for ALL topics. Continue? [y/N]: ")
            if response.lower() != 'y':
                print("Cancelled")
                return

        count = 0
        for topic in topics_root.iterdir():
            if not topic.is_dir() or not topic.name.startswith("0."):
                continue

            if self.reset_topic(topic.name, keep_recent, keep_pattern, force=True):
                count += 1

        print(f"\nProcessed {count} topics")

    def reset_by_category(self, category, keep_recent=0, force=False):
        """Reset logs for topics in a specific category."""
        # Import analysis module to get categories
        try:
            from analyze_log_distribution import categorize_topic

            topics_root = _UET_REPO_ROOT / "docs" / "topics"

            print("=" * 80)
            print(f"RESET TOPICS IN CATEGORY: {category}")
            print("=" * 80)

            count = 0
            for topic in topics_root.iterdir():
                if not topic.is_dir() or not topic.name.startswith("0."):
                    continue

                log_dir = topic / "Result" / "_Logs"
                log_count = sum(1 for _ in log_dir.rglob("*")) if log_dir.exists() else 0
                topic_category = categorize_topic(log_count)

                if topic_category == category:
                    if self.reset_topic(topic.name, keep_recent, force=force):
                        count += 1

            print(f"\nProcessed {count} topics in {category} category")

        except ImportError:
            print("Error: Could not import analyze_log_distribution module")
            return False

    def generate_report(self):
        """Generate a report of what was deleted."""
        report = {
            "timestamp": datetime.now().isoformat(),
            "dry_run": self.dry_run,
            "deleted_count": len(self.deleted_items),
            "deleted_items": self.deleted_items,
            "skipped_count": len(self.skipped_items),
            "skipped_items": self.skipped_items
        }

        report_path = _UET_REPO_ROOT / "docs" / "scripts" / "maintenance" / "log_reset_report.json"
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)

        print(f"\nReport saved to: {report_path}")
        return report


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Reset logs for UET research topics",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Reset logs for a single topic (dry run)
  python reset_topic_logs.py --topic 0.10 --dry-run

  # Reset logs for a single topic, keep 10 most recent
  python reset_topic_logs.py --topic 0.10 --keep-recent 10

  # Reset logs for all topics with excessive logs
  python reset_topic_logs.py --category EXCESSIVE --keep-recent 5

  # Reset all logs (dangerous!)
  python reset_topic_logs.py --all --force
        """
    )

    parser.add_argument("--topic", help="Topic ID (e.g., 0.10)")
    parser.add_argument("--all", action="store_true", help="Reset all topics")
    parser.add_argument("--category", choices=["EXCESSIVE", "HIGH", "MODERATE", "LOW", "MINIMAL", "NO_LOGS"],
                       help="Reset topics in a specific category")
    parser.add_argument("--keep-recent", type=int, default=0,
                       help="Keep N most recent timestamp folders")
    parser.add_argument("--keep-pattern", help="Keep folders matching this pattern")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without deletion")
    parser.add_argument("--force", action="store_true", help="Skip confirmation prompts")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")

    args = parser.parse_args()

    # Validate arguments
    if not any([args.topic, args.all, args.category]):
        parser.error("Must specify --topic, --all, or --category")

    # Create resetter
    resetter = LogResetter(dry_run=args.dry_run, verbose=args.verbose)

    # Execute reset
    if args.topic:
        resetter.reset_topic(args.topic, args.keep_recent, args.keep_pattern, args.force)
    elif args.all:
        resetter.reset_all_topics(args.keep_recent, args.keep_pattern, args.force)
    elif args.category:
        resetter.reset_by_category(args.category, args.keep_recent, args.force)

    # Generate report
    resetter.generate_report()


if __name__ == "__main__":
    main()
