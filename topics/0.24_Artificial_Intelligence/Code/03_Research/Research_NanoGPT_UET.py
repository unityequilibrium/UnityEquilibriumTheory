"""
Research_NanoGPT_UET.py
=======================
Topic 0.24: Artificial Intelligence
Goal: Build a "UET-NanoGPT" Language Model trained on 'UET_Merged_2025-11-27_Theory.md'.

Architecture: Holographic Associative Memory (HAM)
- Instead of Neural Weights (Black Box), we use "Resonance Links".
- Words are Nodes. Sentences are Paths.
- Training = Strengthening $\beta$ (Conductivity) between nodes.
- Generation = Signal propagating through the path of least resistance (Lowest Entropy).

This demonstrates "White Box" Intelligence: We can see exactly *why* it chose a word.
"""

import sys
import random
import re
from pathlib import Path
from collections import defaultdict
import math

# --- PROLOGUE: UET ENGINE SETUP ---
current_path = Path(__file__).resolve()
# Need to go up 6 levels to get to Lab_uet_harness_v0.9.0
# Script -> 03_Research -> Code -> 0.24_AI -> topics -> docs -> Root
root_dir = current_path.parents[5]
data_dir = root_dir / "(search Only) ทองข้อมูลดี"
target_file = data_dir / "UET_Merged_2025-11-27_Theory.md"


class UETLanguageManifold:
    def __init__(self, order=3):
        self.order = order  # N-Gram Order (Memory Horizon)
        self.field = defaultdict(lambda: defaultdict(float))  # The "Connectome"
        self.vocab = set()
        self.total_energy = 0.0

    def tokenize(self, text):
        # Basic UET Tokenizer: Preserve Thai/English structure, remove noise
        # 1. Normalize Whitespace
        text = re.sub(r"\s+", " ", text)
        # 2. Keep words and punctuation as separate tokens
        # Hacky regex for mixed Thai/English
        tokens = text.split(" ")
        return [t for t in tokens if t.strip()]

    def train(self, text):
        print(f"⚡ Ingesting Knowledge (Length: {len(text):,} chars)...")
        # 1. Clean Text
        text = re.sub(r"[\r\n]+", "\n", text)

        # 2. Build N-Gram Lattice (For "Creative" generation)
        tokens = self.tokenize(text)
        self.vocab.update(tokens)
        print(f"⚡ Building Semantic Lattice (Order {self.order})...")
        for i in range(len(tokens) - self.order):
            context = tuple(tokens[i : i + self.order])
            target = tokens[i + self.order]
            self.field[context][target] += 1.0
            self.total_energy += 1.0  # Keep total_energy for N-gram part

        # 3. Build Resonance Index (For "Accurate" Retrieval)
        # Split into Paragraphs (Chunks of wisdom)
        raw_paragraphs = text.split("\n")
        self.knowledge_chunks = []
        for p in raw_paragraphs:
            p = p.strip()
            if len(p) > 30:  # Ignore short noise
                # Store (Clean Text, Set of Tokens for fast search)
                p_tokens = set(self.tokenize(p.lower()))
                self.knowledge_chunks.append(
                    {"text": p, "tokens": p_tokens, "vector": len(p_tokens)}  # Simple magnitude
                )
        print(f"⚡ Indexed {len(self.knowledge_chunks):,} knowledge chunks.")

    def query(self, prompt, max_tokens=100):
        # Hybrid Intelligence: Retrieval + Generation

        # 1. PERCEPTION: Analyze Prompt
        prompt_tokens = set(self.tokenize(prompt.lower()))

        # 2. RESONANCE: Find most relevant chunk (Jaccard/Overlap High Score)
        best_chunk = None
        best_score = 0.0

        for chunk in self.knowledge_chunks:
            # Score = Intersection / Union (Jaccard) or just Intersection count
            overlap = len(prompt_tokens & chunk["tokens"])
            if overlap > 0:
                # Bonus for shorter chunks (Density)
                score = overlap / (math.log(len(chunk["tokens"]) + 1) + 1)
                if score > best_score:
                    best_score = score
                    best_chunk = chunk

        # 3. RESPONSE FORMULATION
        response = ""

        if best_chunk and best_score > 0.1:  # Threshold for relevance
            # Found a specific answer in the user's data
            response += f"📚 **Reference:** \"{best_chunk['text']}\"\n\n"
            response += "🤖 **UET Insight:** "

            # Use the chunk ends to seed the generator for a "Follow up" thought
            seed = best_chunk["text"][-50:]
            generated = self.generate(seed, max_tokens=30, temperature=0.6)

            # Clean up the generated part (remove the seed echo)
            clean_gen = generated.replace(map_seed_to_tokens(seed), "")
            response += clean_gen

        else:
            # No direct answer found, fallback to Dreaming
            response += "🤖 **(Dreaming):** "
            response += self.generate(prompt, max_tokens=60, temperature=0.8)

        return response

    def generate(self, prompt, max_tokens=100, temperature=1.0):
        # This remains as the "Creative Engine" backend
        prompt_tokens = self.tokenize(prompt)
        # Safety: If prompt is new, pick random start
        if not prompt_tokens and self.field:
            context = random.choice(list(self.field.keys()))
            output = list(context)
        elif prompt_tokens:
            output = list(prompt_tokens)
        else:  # No prompt, no field, nothing to do
            return ""

        for _ in range(max_tokens):
            if len(output) < self.order:
                context = random.choice(list(self.field.keys())) if self.field else ()
            else:
                context = tuple(output[-self.order :])

            possible_nexts = self.field.get(context)
            if not possible_nexts:
                break  # Stop if dead end

            # Weighted Choice
            words = list(possible_nexts.keys())
            counts = list(possible_nexts.values())

            # Apply Temperature (Chaos)
            if temperature != 1.0:
                # P' = P^(1/T) / Norm
                # Convert counts to probabilities for temperature scaling
                total_flux = sum(counts)
                if total_flux == 0:  # Avoid division by zero
                    break
                probs = [c / total_flux for c in counts]
                probs = [p ** (1.0 / temperature) for p in probs]
                norm = sum(probs)
                if norm == 0:  # Avoid division by zero
                    break
                probs = [p / norm for p in probs]
                weights_for_choice = probs
            else:
                weights_for_choice = counts

            try:
                next_word = random.choices(words, weights=weights_for_choice, k=1)[0]
                output.append(next_word)
            except Exception:  # Catch potential errors from random.choices with bad weights
                break

        # Determine where to cut: Return ONLY the new part if possible,
        # but for now returning full string is safer for coherence.
        full_text = " ".join(output)

        # Heuristic to clean up "Pulse" output
        return full_text


# Helper for safety
def map_seed_to_tokens(text):
    # This is a placeholder. A proper implementation would tokenize the seed
    # and then join it back to match the format of the generated output.
    # For now, a simple string replacement is used in query, so this just returns text.
    return text


def run_chatbot_siege():
    print("=" * 60)
    print("🧠 UET-NanoGPT: The Unified Theory Chatbot")
    print("=" * 60)

    # 1. Load Data (Recursive Crawl)
    print(f"📂 Scanning Knowledge Base at: {data_dir.name}")

    all_text = ""
    file_count = 0

    if data_dir.exists():
        # Recursive glob for all .md files
        for file_path in data_dir.rglob("*.md"):
            try:
                content = file_path.read_text(encoding="utf-8", errors="ignore")
                all_text += content + "\n"
                file_count += 1
                # print(f"   + Ingested: {file_path.name}")
            except Exception as e:
                print(f"   ❌ Skipped {file_path.name}: {e}")
    else:
        print(f"❌ Error: Data directory not found at {data_dir}. Using Mock Data.")
        all_text = "The universe is an information processing system. UET unifies the standard model. Consciousness is an emergent property."

    if not all_text:
        all_text = "The universe is an information processing system. UET unifies the standard model. Consciousness is an emergent property."

    print(f"📚 Loaded {file_count} documents ({len(all_text):,} characters).")

    # 2. Initialize Brain
    # Upgrade to Order 3 for higher complexity given more data
    brain = UETLanguageManifold(order=3)

    # 3. Train (Physics)
    start_time = sys.time() if hasattr(sys, "time") else __import__("time").time()
    brain.train(all_text)
    train_time = (__import__("time").time()) - start_time
    print(f"✨ Training Complete in {train_time:.4f}s")
    print(f"   Vocabulary Size: {len(brain.vocab):,} unique tokens")
    print(f"   Manifold Connections: {len(brain.field):,} pathways")

    # Save brain state? (Not implemented for nano version, we retrain fast)

    # 4. Conversation Loop
    prompts = [
        "UET is",
        "The standard model",
        "Equation",
        "Consciousness is",
        "Future of humanity",  # New prompt relevant to new data
        "Economic system",
    ]

    log_path = Path("UET_Chatbot_Log.txt")
    with open(log_path, "w", encoding="utf-8") as f:
        f.write("UET-NanoGPT Conversation Log (Full Knowledge)\n")
        f.write("=============================================\n\n")

        for p in prompts:
            print(f"\n👤 User: {p}")
            response = brain.generate(p, max_tokens=50, temperature=0.8)
            print(f"🤖 UET: {response}")

            f.write(f"User: {p}\n")
            f.write(f"UET: {response}\n")
            f.write("-" * 20 + "\n")

    print(f"\n💾 Conversation saved to {log_path.resolve()}")


if __name__ == "__main__":
    run_chatbot_siege()
