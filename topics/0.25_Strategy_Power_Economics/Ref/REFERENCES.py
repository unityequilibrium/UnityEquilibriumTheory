"""
Topic 0.25 References: Strategy, Power, and Economics
=====================================================
Standardized Citation Registry for UET Economic Engine.
Follows Project Reference Standard.
"""

from dataclasses import dataclass


@dataclass
class Ref:
    id: str
    title: str
    url: str
    note: str


# --- DATA SOURCES ---
REF_WORLD_BANK_2024 = Ref(
    id="WORLD_BANK_2024",
    title="World Development Indicators 2024",
    url="https://databank.worldbank.org/source/world-development-indicators",
    note="Baseline for Global Population, GDP PPP, and Gini Coefficients.",
)

REF_WID_2024 = Ref(
    id="WID_2024",
    title="World Inequality Database 2024",
    url="https://wid.world/",
    note="Source for Wealth Distribution Entropy (Top 1% vs Bottom 50%).",
)

REF_KAPLAN_2020 = Ref(
    id="KAPLAN_2020",
    title="Scaling Laws for Neural Language Models",
    url="https://arxiv.org/abs/2001.08361",
    note="Mathematical basis for Power Law Decay in resource networks.",
)

# --- UET THEORETICAL BASIS ---
REF_UET_MASTER = Ref(
    id="UET_MASTER_EQ",
    title="The Unity Equilibrium Master Equation",
    url="docs/core/UET_MASTER_EQUATION.md",
    note="Defines Omega (Entropy) as the driver of Economic Friction.",
)

REGISTRY = [REF_WORLD_BANK_2024, REF_WID_2024, REF_KAPLAN_2020, REF_UET_MASTER]
