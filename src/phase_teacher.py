"""Minimal trajectory-to-phase logic for a public research demonstration.

The module operates only on numeric observations. It contains no participant
data, model weights, private configuration, or restricted-dataset content.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable, Sequence


class Phase(str, Enum):
    """Coarse movement phases in image coordinates."""

    STANDING = "standing"
    DESCENDING = "descending"
    BOTTOM = "bottom"
    ASCENDING = "ascending"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class Observation:
    """One trajectory observation.

    Attributes:
        time_s: Timestamp in seconds.
        y_px: Vertical image coordinate in pixels; larger means lower in frame.
        confidence: Tracking confidence in the closed interval [0, 1].
    """

    time_s: float
    y_px: float
    confidence: float = 1.0


@dataclass(frozen=True)
class QualityReport:
    """Explain whether a trajectory is suitable for phase inference."""

    accepted: bool
    valid_ratio: float
    rom_px: float
    reasons: tuple[str, ...]


def audit_trajectory(
    observations: Sequence[Observation],
    *,
    minimum_confidence: float = 0.5,
    minimum_valid_ratio: float = 0.8,
    minimum_rom_px: float = 20.0,
) -> QualityReport:
    """Apply transparent quality checks before phase inference."""

    if not observations:
        return QualityReport(False, 0.0, 0.0, ("empty_sequence",))

    valid = [x for x in observations if x.confidence >= minimum_confidence]
    valid_ratio = len(valid) / len(observations)
    rom_px = max((x.y_px for x in valid), default=0.0) - min(
        (x.y_px for x in valid), default=0.0
    )

    reasons: list[str] = []
    if valid_ratio < minimum_valid_ratio:
        reasons.append("insufficient_tracking_confidence")
    if rom_px < minimum_rom_px:
        reasons.append("insufficient_range_of_motion")

    return QualityReport(
        accepted=not reasons,
        valid_ratio=valid_ratio,
        rom_px=rom_px,
        reasons=tuple(reasons),
    )


def infer_phases(
    observations: Sequence[Observation],
    *,
    speed_threshold_px_s: float = 12.0,
    bottom_tolerance_px: float = 4.0,
    minimum_confidence: float = 0.5,
) -> list[Phase]:
    """Infer coarse phases from vertical motion in image coordinates.

    This is intentionally a small, interpretable baseline. A research model
    would learn a more robust phase representation from video and trajectory.
    """

    if not observations:
        return []

    maximum_y = max(x.y_px for x in observations)
    phases: list[Phase] = [Phase.STANDING]

    for previous, current in zip(observations, observations[1:]):
        if min(previous.confidence, current.confidence) < minimum_confidence:
            phases.append(Phase.UNKNOWN)
            continue

        dt = current.time_s - previous.time_s
        if dt <= 0:
            phases.append(Phase.UNKNOWN)
            continue

        vertical_speed = (current.y_px - previous.y_px) / dt
        near_bottom = abs(maximum_y - current.y_px) <= bottom_tolerance_px

        if near_bottom and abs(vertical_speed) <= speed_threshold_px_s:
            phases.append(Phase.BOTTOM)
        elif vertical_speed > speed_threshold_px_s:
            phases.append(Phase.DESCENDING)
        elif vertical_speed < -speed_threshold_px_s:
            phases.append(Phase.ASCENDING)
        else:
            phases.append(Phase.STANDING)

    return phases


def phase_values(phases: Iterable[Phase]) -> list[str]:
    """Return phase names for serialization or display."""

    return [phase.value for phase in phases]

