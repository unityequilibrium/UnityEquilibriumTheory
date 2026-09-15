"""
uet_data_orchestrator.py - UET Core (v0.9.0)
===========================================
Standardized Data Orchestrator for Total Connectivity.
Prevents "Shadow Data" by providing a unified interface for all topics.
"""

import json
import pandas as pd
from pathlib import Path
from typing import Dict, Any, Optional


class UETDataOrchestrator:
    """
    Central orchestrator for all UET-related data.
    Implements singleton-like behavior for caching.
    """

    _instance = None
    _cache = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(UETDataOrchestrator, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        self.root = self._find_project_root()

    def _find_project_root(self) -> Path:
        current = Path(__file__).resolve()
        for parent in [current] + list(current.parents):
            # Check for the TRUE root marker: docs/core/uet_parameters.py
            if (parent / "docs" / "core" / "uet_parameters.py").exists():
                return parent
        # Fallback to checking for uet_harness name if parents aren't helping
        for parent in [current] + list(current.parents):
            if parent.name == "uet_harness":
                return parent
        return Path.cwd()

    def get_data(self, topic: str, filename: str) -> Dict[str, Any]:
        """Fetches data from a specific topic's Data folder."""
        cache_key = f"{topic}/{filename}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        data_path = self.root / "docs" / "topics"
        # Find the full topic directory (e.g., '0.25_Strategy_Power_Economics')
        topic_dir = None
        for d in data_path.iterdir():
            if not d.is_dir():
                continue
            # Strict filtering: "0.1" must match "0.1_Galaxy..." not "0.10_Fluid..."
            # Check if name is exactly "0.1" (rare) or starts with "0.1_"
            name = d.name.lower()
            key = topic.lower()
            if name == key or name.startswith(key + "_"):
                topic_dir = d
                break

        if not topic_dir:
            print(f"⚠️ Orchestrator Warning: Topic {topic} not found.")
            return {}

        file_path = topic_dir / "Data" / filename
        if not file_path.exists():
            print(f"⚠️ Orchestrator Warning: File {filename} not found in {topic_dir}.")
            return {}

        data = {}
        try:
            if file_path.suffix == ".json":
                with open(file_path, "r") as f:
                    data = json.load(f)
            elif file_path.suffix == ".csv":
                data = pd.read_csv(file_path).to_dict(orient="list")
        except Exception as e:
            print(f"⚠️ Orchestrator Error loading {file_path}: {e}")

        self._cache[cache_key] = data
        return data

    def get_economy_baseline(self) -> Dict[str, Any]:
        """Helper for standard Topic 0.25 economic snapshots."""
        return self.get_data("0.25", "Global_Economy_2024.json")

    def get_market_baseline(self) -> Dict[str, Any]:
        """Helper for Topic 0.14 market experiment baselines."""
        return self.get_data("0.14", "CI_s_validation.json")


# Singleton instance
orchestrator = UETDataOrchestrator()
