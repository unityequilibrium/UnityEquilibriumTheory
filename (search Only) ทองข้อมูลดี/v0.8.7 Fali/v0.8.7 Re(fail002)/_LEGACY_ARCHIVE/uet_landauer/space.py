"""
UET Landauer Space Module
=========================

Space as information recorder:
- Bekenstein bound: S_max = (2πkRE)/(ħc)
- Information preserved on boundary
- Record of all behavior

"Space บันทึกข้อมูลจากพฤติกรรมทุกอย่าง"

Author: Santa (Original Vision)
Date: 2025-12-30
"""

import numpy as np
from dataclasses import dataclass, field
from typing import List, Dict, Optional

from .core import K_B, LN_2, energy_per_bit


# Physical Constants
HBAR = 1.054571817e-34  # Reduced Planck constant (J·s)
C_LIGHT = 299792458  # Speed of light (m/s)


@dataclass
class InformationRecord:
    """A record of behavior stored in Space."""

    time: float  # When it happened
    bits: float  # Information content
    energy: float  # Energy involved
    source: str = ""  # Description


@dataclass
class SpaceRegion:
    """
    A region of Space that stores information.

    Implements holographic principle:
    - Information on boundary, not in volume
    - Bekenstein bound limits capacity
    """

    radius: float  # Region size (m)
    T: float = 300.0  # Temperature (K)
    records: List[InformationRecord] = field(default_factory=list)

    @property
    def total_energy(self) -> float:
        """Total energy in this region."""
        return sum(r.energy for r in self.records)

    @property
    def total_bits(self) -> float:
        """Total information stored."""
        return sum(r.bits for r in self.records)

    @property
    def bekenstein_bound(self) -> float:
        """
        Maximum information capacity (Bekenstein bound).

        S_max = (2π k R E) / (ħ c)

        Returns:
            Maximum entropy in J/K
        """
        if self.total_energy <= 0:
            return 0
        return (2 * np.pi * K_B * self.radius * self.total_energy) / (HBAR * C_LIGHT)

    @property
    def max_bits(self) -> float:
        """Maximum information in bits."""
        S_max = self.bekenstein_bound
        return S_max / (K_B * LN_2) if S_max > 0 else 0

    @property
    def capacity_used(self) -> float:
        """Fraction of capacity used (0 to 1)."""
        max_b = self.max_bits
        if max_b <= 0:
            return 0
        return min(1.0, self.total_bits / max_b)

    def can_record(self, bits: float) -> bool:
        """Check if there's capacity to record more."""
        return self.total_bits + bits <= self.max_bits

    def record_behavior(self, time: float, bits: float, source: str = "") -> bool:
        """
        Record a behavior in Space.

        "พฤติกรรม → เสื่อมพลังงาน → บันทึกเป็นข้อมูลลงใน Space"

        Args:
            time: When behavior occurred
            bits: Information content
            source: Description

        Returns:
            True if recorded successfully
        """
        energy = energy_per_bit(self.T) * bits

        record = InformationRecord(time=time, bits=bits, energy=energy, source=source)

        self.records.append(record)
        return True


class UniverseSpace:
    """
    The entire Space as information storage.

    Key properties:
    - Records all behavior
    - We see "past" not "present" (light cone)
    - Information is real, not imagination
    """

    def __init__(self, T: float = 300.0):
        """Initialize universe Space."""
        self.T = T
        self.regions: Dict[str, SpaceRegion] = {}
        self.global_time = 0.0

    def create_region(self, name: str, radius: float) -> SpaceRegion:
        """Create a region of Space."""
        region = SpaceRegion(radius=radius, T=self.T)
        self.regions[name] = region
        return region

    def record(self, region_name: str, bits: float, source: str = ""):
        """Record behavior in a region."""
        if region_name not in self.regions:
            raise ValueError(f"Region {region_name} not found")

        self.regions[region_name].record_behavior(time=self.global_time, bits=bits, source=source)

    def advance_time(self, dt: float):
        """Advance global time."""
        self.global_time += dt

    def total_information(self) -> float:
        """Total information in all Space."""
        return sum(r.total_bits for r in self.regions.values())

    def total_energy(self) -> float:
        """Total energy in all Space."""
        return sum(r.total_energy for r in self.regions.values())

    def light_cone_visible(self, observer_pos: float, event_pos: float, event_time: float) -> bool:
        """
        Check if event is visible to observer.

        "เราเห็นดาวเป็นอดีต ไม่ใช่ปัจจุบัน"

        Light cone: |Δx| ≤ c × Δt

        Args:
            observer_pos: Observer position
            event_pos: Event position
            event_time: When event occurred

        Returns:
            True if in past light cone (visible)
        """
        distance = abs(observer_pos - event_pos)
        time_since = self.global_time - event_time

        # Can only see if light had time to reach us
        max_distance = C_LIGHT * time_since
        return distance <= max_distance

    def summary(self) -> dict:
        """Get Space summary."""
        return {
            "time": self.global_time,
            "regions": len(self.regions),
            "total_bits": self.total_information(),
            "total_energy_J": self.total_energy(),
        }


# Quick verification
if __name__ == "__main__":
    print("=" * 60)
    print("Space Module - Verification")
    print("=" * 60)

    # Create universe
    universe = UniverseSpace(T=300)

    # Create a star (1 meter radius for demo)
    star = universe.create_region("Star", radius=1.0)

    print(f"\n1. Created Space with region 'Star' (radius=1m)")

    # Record some behaviors
    print("\n2. Recording behaviors...")
    for i in range(5):
        bits = 1e20 * (i + 1)
        universe.record("Star", bits, source=f"Event {i+1}")
        universe.advance_time(1.0)
        print(f"   Event {i+1}: {bits:.1e} bits recorded")

    print(f"\n3. Summary:")
    summary = universe.summary()
    print(f"   Total time: {summary['time']} s")
    print(f"   Total bits: {summary['total_bits']:.2e}")
    print(f"   Total energy: {summary['total_energy_J']:.2e} J")

    # Check light cone
    print(f"\n4. Light cone test:")
    # Event at t=0, distance = 1 light-second away
    visible = universe.light_cone_visible(
        observer_pos=0, event_pos=C_LIGHT * 1, event_time=0  # 1 light-second away
    )
    print(f"   Event 1 light-second away, 5s ago: {'Visible' if visible else 'Not visible'}")

    print("\n" + "=" * 60)
    print("Space Module - READY")
    print("=" * 60)
