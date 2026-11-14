"""
Module: Data Loader (Ingestion Layer)
Topic: 0.24 Artificial Intelligence
Folder: 05_Developmental_AI

Responsible for fetching high-quality data (Hugging Face, Kaggle)
to feed the developmental agent.
"""

import sys
import random

try:
    from datasets import load_dataset

    HAS_HF_DATASETS = True
except ImportError:
    HAS_HF_DATASETS = False


class DataLoader:
    def __init__(self):
        self.sources = ["Synthetic_Basic"]
        if HAS_HF_DATASETS:
            self.sources.append("HuggingFace")

    def fetch_learning_material(self, stage, topic="general"):
        """
        Returns a list of text snippets or data points suitable for the age using the best available source.
        """
        print(f"[Data_Loader] Fetching material for {stage.name} (Topic: {topic})...")

        if stage.name == "Infant":
            return self._generate_infant_data()
        elif stage.name == "Child":
            return self._fetch_child_data(topic)
        elif stage.name == "Adolescent":
            return self._fetch_adolescent_data()
        else:
            return ["Complex Real-world Data Stream..."]

    def _generate_infant_data(self):
        """Infants learn signals vs noise."""
        data = []
        for _ in range(5):
            noise = "".join(random.choices("xo#%!", k=10))
            signal = "MAMA"
            data.append(f"{noise}{signal}{noise}")
        return data

    def _fetch_child_data(self, topic):
        """Children need structured, simple datasets."""
        if HAS_HF_DATASETS:
            try:
                # Example: Load a tiny slice of a simple Wikipedia dataset or similar
                # For now, we simulate the return to avoid massive downloads during dev
                # dataset = load_dataset("wikipedia", "20220301.simple", split="train[:100]")
                return [
                    f"Simulated HF entry for {topic}: The sky is blue.",
                    f"Simulated HF entry for {topic}: Cats have fur.",
                ]
            except Exception as e:
                print(f"[Warning] HF Load Failed: {e}")

        # Fallback
        return ["A is for Apple", "B is for Ball", "1 + 1 = 2", "The sun rises in the east."]

    def _fetch_adolescent_data(self):
        return [
            "Logic Prob: If P implies Q, and P is true, what is Q?",
            "Ethics: Trolley Problem scenario setup...",
            "Coding: print('Hello World')",
        ]
