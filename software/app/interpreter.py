"""Detection interpretation for Iris (semantic meaning layer).

This is the core UX file in Iris. It converts many raw detections into one clear,
usable haptic message. The user should feel concise meaning, not detector noise.

Pipeline in this module:
1) Filter weak/irrelevant detections.
2) Determine horizontal position (left/center/right).
3) Estimate rough closeness from box size.
4) Score candidates by priority + confidence + closeness.
5) Emit one semantic command for Arduino.
"""

from __future__ import annotations

from dataclasses import dataclass

from . import constants as C
from .models import Detection, SemanticDecision


@dataclass(slots=True)
class InterpreterConfig:
    confidence_threshold: float
    target_labels: tuple[str, ...]
    close_area_ratio: float
    very_close_area_ratio: float
    enable_closeness: bool


@dataclass(slots=True)
class Candidate:
    detection: Detection
    object_kind: str
    position: str
    area_ratio: float
    score: float


class DetectionInterpreter:
    """Maps YOLO detections into Iris haptic command strings."""

    def __init__(self, config: InterpreterConfig) -> None:
        self.config = config
        self.allowed_labels = {label.lower() for label in config.target_labels}

    def interpret(
        self,
        detections: list[Detection],
        frame_width: int,
        frame_height: int,
    ) -> SemanticDecision:
        candidates = self._build_candidates(detections, frame_width, frame_height)

        if not candidates:
            return SemanticDecision(
                command=C.SILENT_COMMAND,
                reason="No meaningful detection above threshold",
            )

        best = max(candidates, key=lambda c: c.score)

        # Optional urgency behavior: very large near-field person/obstacle => DANGER.
        if (
            self.config.enable_closeness
            and best.area_ratio >= self.config.very_close_area_ratio
            and best.object_kind in {C.PERSON, C.OBSTACLE}
        ):
            return SemanticDecision(
                command=C.DANGER_COMMAND,
                reason=(
                    f"{best.object_kind.lower()} appears very close "
                    f"(area_ratio={best.area_ratio:.2f})"
                ),
                label=best.detection.label,
                position=best.position,
                confidence=best.detection.confidence,
                area_ratio=best.area_ratio,
            )

        return SemanticDecision(
            command=C.compose_directional_command(best.object_kind, best.position),
            reason=(
                f"Selected {best.detection.label} as highest-priority candidate "
                f"(score={best.score:.2f})"
            ),
            label=best.detection.label,
            position=best.position,
            confidence=best.detection.confidence,
            area_ratio=best.area_ratio,
        )

    def _build_candidates(
        self,
        detections: list[Detection],
        frame_width: int,
        frame_height: int,
    ) -> list[Candidate]:
        candidates: list[Candidate] = []

        for det in detections:
            if det.confidence < self.config.confidence_threshold:
                continue

            if self.allowed_labels and det.label not in self.allowed_labels:
                continue

            object_kind = self._map_label_to_object_kind(det.label)
            if object_kind is None:
                continue

            pos = self._position_from_bbox(det, frame_width)
            area_ratio = det.area_ratio(frame_width, frame_height)
            score = self._score_candidate(object_kind, det.confidence, area_ratio)

            candidates.append(
                Candidate(
                    detection=det,
                    object_kind=object_kind,
                    position=pos,
                    area_ratio=area_ratio,
                    score=score,
                )
            )

        return candidates

    @staticmethod
    def _position_from_bbox(det: Detection, frame_width: int) -> str:
        x_norm = det.normalized_center_x(frame_width)
        if x_norm < C.POSITION_LEFT_MAX:
            return C.LEFT
        if x_norm < C.POSITION_CENTER_MAX:
            return C.CENTER
        return C.RIGHT

    @staticmethod
    def _map_label_to_object_kind(label: str) -> str | None:
        if label == "person":
            return C.PERSON
        if label == "chair":
            return C.CHAIR
        if label in C.OBSTACLE_FALLBACK_LABELS:
            return C.OBSTACLE
        return None

    def _score_candidate(self, object_kind: str, confidence: float, area_ratio: float) -> float:
        # Priority is the dominant term, then confidence, then optional closeness bonus.
        priority_score = C.OBJECT_PRIORITY[object_kind]
        confidence_score = confidence * 20.0

        closeness_bonus = 0.0
        if self.config.enable_closeness:
            if area_ratio >= self.config.very_close_area_ratio:
                closeness_bonus = 12.0
            elif area_ratio >= self.config.close_area_ratio:
                closeness_bonus = 5.0

        return priority_score + confidence_score + closeness_bonus
