"""
Data Loader: AI Architectures (Real World Production)
=====================================================
Topic: 0.24 Artificial Intelligence
Source: Technical Reports (DeepSeek, Meta, OpenAI)
Target: Honest comparison of Dense vs MoE architectures.

Generates 'deepseek_moe_data.json' with full specs for UET Analysis.
"""

import sys
import json
from pathlib import Path


def fetch_ai_specs():
    print("📥 Compiling Production AI Architecture Data...")

    # DATA: Extracted from Official Technical Reports (2023-2025)
    models = {
        "Llama-3-70B": {
            "Type": "Dense",
            "Total_Params": 70e9,
            "Active_Params": 70e9,
            "Context_Window": 8192,
            "Training_Tokens": 15e12,
            "Note": "Standard Dense Baseline",
        },
        "Llama-3-405B": {
            "Type": "Dense",
            "Total_Params": 405e9,
            "Active_Params": 405e9,
            "Context_Window": 128000,
            "Training_Tokens": 15e12,
            "Note": "Massive Dense Model",
        },
        "DeepSeek-V3": {
            "Type": "MoE",
            "Total_Params": 671e9,
            "Active_Params": 37e9,  # Only 37B active per token!
            "Context_Window": 128000,
            "Training_Tokens": 14.8e12,
            "Note": "UET Sparse Equilibrium Champion",
        },
        "Mixtral-8x7B": {
            "Type": "MoE",
            "Total_Params": 46.7e9,
            "Active_Params": 12.9e9,
            "Context_Window": 32000,
            "Training_Tokens": 6e12,
            "Note": "First Open Weights MoE",
        },
        "GPT-4-Turbo": {
            "Type": "MoE (Estimated)",
            "Total_Params": 1.76e12,  # 1.7 Trillion (Leak)
            "Active_Params": 55e9,  # Estimated active
            "Context_Window": 128000,
            "Training_Tokens": 13e12,
            "Note": "Proprietary MoE",
        },
    }

    data = {
        "source": "UET Production Audit 2026",
        "description": "Comparative Specs for Density-Efficiency Analysis",
        "models": models,
    }

    # Save to Data/03_Research/ to match Engine path
    output_dir = Path(__file__).parent / "03_Research"
    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / "deepseek_moe_data.json"

    with open(output_path, "w") as f:
        json.dump(data, f, indent=4)

    print(f"✅ Production Data Saved: {output_path}")
    print(f"   Models Tracked: {len(models)}")


if __name__ == "__main__":
    fetch_ai_specs()
