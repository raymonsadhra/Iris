"""Core typed models used across Iris software modules.

This file provides shared data structures for detections and semantic decisions.
Keeping these as dataclasses makes the camera, interpreter, and bridge modules
cleanly composable during hackathon iteration.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class BoundingBox:
    """Pixel-space rectangle from the detector output."""

    x1: float
    y1: float
    x2: float
    y2: float

    @property
    def width(self) -> float:
        return max(0.0, self.x2 - self.x1)

    @property
    def height(self) -> float:
        return max(0.0, self.y2 - self.y1)

    @property
    def area(self) -> float:
        return self.width * self.height

    @property
    def center_x(self) -> float:
        return self.x1 + self.width / 2.0

    @property
    def center_y(self) -> float:
        return self.y1 + self.height / 2.0


@dataclass(frozen=True)
class Detection:
    """Simplified detector output for Iris interpretation."""

    label: str
    confidence: float
    bbox: BoundingBox

    def normalized_center_x(self, frame_width: int) -> float:
        if frame_width <= 0:
            return 0.5
        return self.bbox.center_x / float(frame_width)

    def area_ratio(self, frame_width: int, frame_height: int) -> float:
        frame_area = float(max(1, frame_width * frame_height))
        return self.bbox.area / frame_area


@dataclass(frozen=True)
class SemanticDecision:
    """Single command that Iris will communicate through touch."""

    command: str
    reason: str
    label: str | None = None
    position: str | None = None
    confidence: float | None = None
    area_ratio: float | None = None
