"""
UET Tensorizer — Physics-Derived Vector Embeddings
===================================================
Converts research files into UET vectors using the REAL UET engine.
Each file gets a physics-informed signature (Ω, κ, β, entropy, axiom bits).

Design from: docs/v/01.md (UET Vector Database Design Guide)

Rules (from 00.md failure lessons):
    ❌ DO NOT invent ad-hoc tensor formats
    ❌ DO NOT write math — delegate to uet_master_equation.py
    ✅ Derive vectors FROM UET equations
    ✅ Data structures must be Rust-compatible (JSON/serde)

Usage:
    from docs.knowledge_base.tensorizer import UetTensorizer

    tensorizer = UetTensorizer()
    vector = tensorizer.tensorize_file("docs/topics/0.1_Quantum_Mechanics/Research_QM.py")
    print(vector)  # UetVector(omega=1.234, kappa=0.1, beta=0.05, ...)

Rust Equivalent:
    #[derive(Serialize, Deserialize)]
    struct UetVector {
        omega: f64,
        kappa: f64,
        beta: f64,
        entropy: f64,
        axiom_signature: [bool; 12],
        topic_id: String,
        content_hash: [u8; 32],
    }
"""

import hashlib
import json
import math
import re
import sys
from dataclasses import dataclass, asdict, field
from pathlib import Path
from typing import Optional

import numpy as np

# Import UET engine — the ONLY source of physics calculations
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from docs.core.uet_parameters import get_params, UETParameters, _TOPIC_SCALE_MAP
from docs.scripts.core.runners.uet_lite_engine import UETLiteEngine


# =============================================================================
# UET VECTOR — Rust-compatible dataclass
# =============================================================================

# The 12 UET Axioms for axiom signature detection
UET_AXIOMS = [
    "energy conservation",  # A1
    "information irreversibility",  # A2
    "space memory",  # A3
    "semi-open system",  # A4
    "natural will",  # A5
    "learning nea",  # A6
    "pattern recurrence",  # A7
    "game dynamics",  # A8
    "dynamic equilibrium",  # A9
    "multi-layer coherence",  # A10
    "known physics reduction",  # A11
    "theory evolution",  # A12
]

# Keywords that indicate axiom references in text
_AXIOM_KEYWORDS = {
    0: ["energy", "conservation", "potential", "V(C)", "dissipation", "thermodynamic"],
    1: ["information", "irreversibility", "landauer", "entropy", "coupling", "β", "beta"],
    2: ["space", "memory", "gradient", "∇C", "κ", "kappa", "diffusion", "geometry"],
    3: ["semi-open", "exchange", "in-ex", "J_in", "J_out", "γ_J", "boundary"],
    4: ["natural will", "W_N", "persistence", "drive", "existence"],
    5: ["learning", "NEA", "adjustment", "adaptation", "constraint"],
    6: ["pattern", "recurrence", "fractal", "scale-invariant", "self-similar"],
    7: ["game", "competition", "nash", "strategy", "β_U"],
    8: ["equilibrium", "dynamic center", "Ω", "omega", "balance", "stable"],
    9: ["coherence", "multi-layer", "λ", "lambda_coherence", "hierarchy"],
    10: ["reduce", "known physics", "GR", "QM", "standard model", "classical limit"],
    11: ["evolution", "adapt", "update", "evolve", "meta", "self-modify"],
}


@dataclass
class UetVector:
    """
    UET physics-derived vector for a research file.

    This is a Rust-compatible struct:
    - All fields are primitive types or fixed-size arrays
    - Serializable to JSON (serde-compatible)
    - No Python-only tricks (no pickle, no dynamic typing)
    """

    omega: float  # Ω — Balance functional value
    kappa: float  # κ — Gradient penalty / diffusion
    beta: float  # β — Information coupling strength
    alpha: float  # α — Equilibrium stiffness
    gamma: float  # γ — Nonlinear stability
    entropy: float  # Shannon entropy H of content
    axiom_signature: list[bool]  # 12-bit: which axioms are referenced
    topic_id: str  # e.g. "0.1_Quantum_Mechanics"
    topic_number: str  # e.g. "0.1"
    file_path: str  # Relative path from docs/
    file_type: str  # "python" | "markdown" | "data" | "other"
    content_hash: str  # SHA-256 hex digest (32 bytes)
    char_count: int  # Content length
    axiom_count: int  # Number of True values in axiom_signature
    scale: str  # Physical scale used for params

    def to_dict(self) -> dict:
        """Convert to JSON-serializable dict."""
        return asdict(self)

    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), ensure_ascii=False)

    @classmethod
    def from_dict(cls, d: dict) -> "UetVector":
        """Reconstruct from dict."""
        return cls(**d)

    def to_flat_vector(self) -> list[float]:
        """
        Convert to a flat numeric vector for vector DB storage.

        Layout (20 dimensions):
            [0]     omega
            [1]     kappa
            [2]     beta
            [3]     alpha
            [4]     gamma
            [5]     entropy
            [6]     axiom_count (normalized to 0-1)
            [7:19]  axiom_signature (12 booleans as 0.0/1.0)
            [19]    char_count (log-scaled)
        """
        return [
            self.omega,
            self.kappa,
            self.beta,
            self.alpha,
            self.gamma,
            self.entropy,
            self.axiom_count / 12.0,
            *[1.0 if a else 0.0 for a in self.axiom_signature],
            math.log1p(self.char_count) / 15.0,  # Normalize ~33K chars → ~1.0
        ]


# =============================================================================
# TENSORIZER
# =============================================================================


class UetTensorizer:
    """
    Convert research files into UetVector using the real UET engine.

    DOES NOT invent math — delegates computation to:
    - UETLiteEngine.compute_omega() for Ω
    - get_params() for κ, β, α, γ
    - Shannon entropy for information density
    - Keyword matching for axiom signatures
    """

    def __init__(self, grid_size: int = 64):
        self.grid_size = grid_size

    def tensorize_file(self, filepath: str | Path) -> UetVector:
        """
        Tensorize a single file into a UetVector.

        Args:
            filepath: Path to any file in docs/topics/

        Returns:
            UetVector with physics-derived features
        """
        filepath = Path(filepath)

        # 1. Read content
        content = self._read_file(filepath)

        # 2. Extract topic info
        topic_id, topic_number = self._extract_topic(filepath)

        # 3. Get UET parameters for this topic's physical scale
        params = self._get_topic_params(topic_number)

        # 4. Compute Ω using real UET engine
        omega = self._compute_omega(content, params)

        # 5. Compute Shannon entropy
        entropy = self._compute_shannon_entropy(content)

        # 6. Detect axiom references
        axiom_sig = self._detect_axioms(content)

        # 7. Content hash (SHA-256)
        content_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()

        # 8. File type classification
        file_type = self._classify_file(filepath)

        return UetVector(
            omega=round(omega, 8),
            kappa=params.kappa,
            beta=params.beta,
            alpha=params.alpha,
            gamma=params.gamma,
            entropy=round(entropy, 8),
            axiom_signature=axiom_sig,
            topic_id=topic_id,
            topic_number=topic_number,
            file_path=str(filepath.as_posix()),
            file_type=file_type,
            content_hash=content_hash,
            char_count=len(content),
            axiom_count=sum(axiom_sig),
            scale=params.scale,
        )

    def tensorize_text(
        self,
        text: str,
        topic_number: str = "0.0",
        label: str = "inline",
    ) -> UetVector:
        """
        Tensorize raw text (for queries or inline content).

        Args:
            text: Raw text content
            topic_number: UET topic number for parameter selection
            label: Identifier label

        Returns:
            UetVector
        """
        params = self._get_topic_params(topic_number)
        omega = self._compute_omega(text, params)
        entropy = self._compute_shannon_entropy(text)
        axiom_sig = self._detect_axioms(text)
        content_hash = hashlib.sha256(text.encode("utf-8")).hexdigest()

        return UetVector(
            omega=round(omega, 8),
            kappa=params.kappa,
            beta=params.beta,
            alpha=params.alpha,
            gamma=params.gamma,
            entropy=round(entropy, 8),
            axiom_signature=axiom_sig,
            topic_id=f"inline:{label}",
            topic_number=topic_number,
            file_path="",
            file_type="text",
            content_hash=content_hash,
            char_count=len(text),
            axiom_count=sum(axiom_sig),
            scale=params.scale,
        )

    # =========================================================================
    # PRIVATE METHODS — all physics delegated to UET engine
    # =========================================================================

    def _read_file(self, filepath: Path) -> str:
        """Read file content, handling encoding gracefully."""
        try:
            return filepath.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            try:
                return filepath.read_text(encoding="latin-1")
            except Exception:
                return ""
        except Exception:
            return ""

    def _extract_topic(self, filepath: Path) -> tuple[str, str]:
        """
        Extract topic_id and topic_number from file path.

        Examples:
            "topics/0.1_Quantum_Mechanics/Research_QM.py" → ("0.1_Quantum_Mechanics", "0.1")
            "topics/General/some_file.py" → ("General", "general")
        """
        parts = filepath.parts
        # Find "topics" in path and get next component
        for i, part in enumerate(parts):
            if part == "topics" and i + 1 < len(parts):
                topic_dir = parts[i + 1]
                # Extract number: "0.1_Quantum_Mechanics" → "0.1"
                match = re.match(r"^(\d+\.\d+)", topic_dir)
                if match:
                    return topic_dir, match.group(1)
                else:
                    return topic_dir, "general"
        return "unknown", "general"

    def _get_topic_params(self, topic_number: str) -> UETParameters:
        """Get UET parameters for a topic number, with fallback."""
        try:
            return get_params(topic_number)
        except ValueError:
            # Fallback to general scale
            return get_params("general")

    def _compute_omega(self, content: str, params: UETParameters) -> float:
        """
        Compute Ω using real UET engine.

        Process:
        1. Convert text → Information field I(x) via deterministic hashing
           (Same approach as Developmental_Agent.py)
        2. Create initial C field (uniform)
        3. Compute Ω = ∫[ V(C) + (κ/2)|∇C|² + β·C·I ] dx

        This gives each document a physics-meaningful "balance score".
        """
        n = self.grid_size

        # Create Information field I from text content
        # (Deterministic: same text always produces same I field)
        I_field = self._text_to_information_field(content, n)

        # Initial C field = uniform (represents "blank slate")
        C_field = np.ones(n) * params.C0

        # Compute Ω using UET Lite Engine
        engine = UETLiteEngine(params)
        omega = engine.compute_omega(C_field, dx=0.1, I=I_field)

        return float(omega)

    def _text_to_information_field(self, text: str, n: int) -> np.ndarray:
        """
        Convert text to Information field I(x).

        Uses deterministic hashing (same approach as Developmental_Agent.py
        but adapted for 1D field).

        The information content of texts is encoded as activation patterns
        on a 1D field, where different words activate different spatial positions.
        """
        I_field = np.zeros(n)

        if not text:
            return I_field

        # Use SHA-256 of full content for reproducibility
        content_hash = hashlib.sha256(text.encode("utf-8")).digest()
        seed = int.from_bytes(content_hash[:4], "big") % (2**31)
        rng = np.random.RandomState(seed)

        # Each word activates a position with its "information energy"
        words = text.split()
        num_activations = min(len(words), n * 4)  # Cap at 4x grid

        for i in range(num_activations):
            pos = rng.randint(0, n)
            # Information amplitude varies by word "complexity"
            word = words[i % len(words)]
            amplitude = len(word) / 10.0  # Longer words = more info
            I_field[pos] += amplitude

        # Normalize to reasonable range
        if I_field.max() > 0:
            I_field = I_field / I_field.max()

        return I_field

    def _compute_shannon_entropy(self, text: str) -> float:
        """
        Compute Shannon entropy H = -Σ pᵢ log₂ pᵢ of text content.

        This measures information density:
        - Low H: repetitive content (low information)
        - High H: diverse content (high information)
        """
        if not text:
            return 0.0

        # Character-level frequency distribution
        freq: dict[str, int] = {}
        for char in text:
            freq[char] = freq.get(char, 0) + 1

        total = len(text)
        entropy = 0.0
        for count in freq.values():
            p = count / total
            if p > 0:
                entropy -= p * math.log2(p)

        return entropy

    def _detect_axioms(self, text: str) -> list[bool]:
        """
        Detect which of the 12 UET axioms are referenced in the text.

        Returns a 12-bit signature (list of booleans).
        Uses keyword matching — not ML, deterministic and fast.
        """
        text_lower = text.lower()
        signature = []

        for axiom_idx in range(12):
            keywords = _AXIOM_KEYWORDS.get(axiom_idx, [])
            found = any(kw.lower() in text_lower for kw in keywords)
            signature.append(found)

        return signature

    def _classify_file(self, filepath: Path) -> str:
        """Classify file type."""
        suffix = filepath.suffix.lower()
        if suffix == ".py":
            return "python"
        elif suffix in (".md", ".txt", ".rst"):
            return "markdown"
        elif suffix in (".csv", ".json", ".jsonl", ".log"):
            return "data"
        elif suffix in (".png", ".jpg", ".svg", ".pdf"):
            return "media"
        else:
            return "other"


# =============================================================================
# STANDALONE TEST
# =============================================================================

if __name__ == "__main__":
    """
    Quick self-test: tensorize a known file and print the UET vector.
    Run: python -m docs.knowledge_base.tensorizer
    """
    print("=" * 60)
    print("  UET Tensorizer — Self Test")
    print("=" * 60)

    tensorizer = UetTensorizer(grid_size=64)

    # Test 1: Tensorize inline text
    print("\n--- Test 1: Inline text ---")
    vec = tensorizer.tensorize_text(
        "The UET Master Equation describes energy conservation and "
        "information coupling through the β parameter. Space serves as "
        "a universal memory substrate with gradient κ.",
        topic_number="0.0",
        label="test_snippet",
    )
    print(f"  Ω = {vec.omega}")
    print(f"  κ = {vec.kappa}, β = {vec.beta}")
    print(f"  Shannon H = {vec.entropy:.4f}")
    print(f"  Axioms: {vec.axiom_signature}")
    print(f"  Axiom count: {vec.axiom_count}/12")
    print(f"  Flat vector (20d): {vec.to_flat_vector()[:7]}...")
    print(f"  JSON size: {len(vec.to_json())} bytes")

    # Test 2: Try to tensorize a real file if available
    print("\n--- Test 2: Real file ---")
    project_root = Path(__file__).resolve().parent.parent
    test_file = project_root / "core" / "uet_master_equation.py"

    if test_file.exists():
        vec2 = tensorizer.tensorize_file(test_file)
        print(f"  File: {vec2.file_path}")
        print(f"  Topic: {vec2.topic_id} (scale: {vec2.scale})")
        print(f"  Ω = {vec2.omega}")
        print(f"  κ = {vec2.kappa}, β = {vec2.beta}")
        print(f"  Shannon H = {vec2.entropy:.4f}")
        print(f"  Axioms: {vec2.axiom_signature}")
        print(f"  Axiom count: {vec2.axiom_count}/12")
        print(f"  Content hash: {vec2.content_hash[:16]}...")
        print(f"  Chars: {vec2.char_count}")
    else:
        print(f"  Skipped — {test_file} not found")

    # Test 3: Rust compatibility check
    print("\n--- Test 3: Rust compatibility ---")
    d = vec.to_dict()
    roundtrip = UetVector.from_dict(d)
    assert roundtrip.omega == vec.omega
    assert roundtrip.axiom_signature == vec.axiom_signature
    print("  ✅ Dict roundtrip: PASS")

    j = vec.to_json()
    roundtrip2 = UetVector.from_dict(json.loads(j))
    assert roundtrip2.omega == vec.omega
    print("  ✅ JSON roundtrip: PASS (serde-compatible)")

    flat = vec.to_flat_vector()
    assert len(flat) == 20, f"Expected 20d, got {len(flat)}d"
    assert all(isinstance(v, float) for v in flat)
    print(f"  ✅ Flat vector: {len(flat)}d (all floats)")

    print("\n✅ ALL TESTS PASSED")
