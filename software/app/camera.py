"""Camera and YOLO integration for Iris (The Eye + first part of the Brain).

What this file does:
- Opens the webcam feed.
- Runs YOLO object detection on each frame.
- Returns simplified detections for the interpretation layer.

Why this matters for Iris:
- The webcam is Iris's "eye". This module is where the system first perceives
  the environment before translating vision into haptic meaning.

Hardware relation:
- Logitech webcam is connected to the laptop, not the Arduino.
- All vision work is done here on the laptop CPU/GPU.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import cv2

from .models import BoundingBox, Detection

try:
    from ultralytics import YOLO
except ImportError as exc:  # pragma: no cover - import-time guard
    YOLO = None
    _YOLO_IMPORT_ERROR = exc
else:
    _YOLO_IMPORT_ERROR = None


@dataclass(slots=True)
class CameraConfig:
    camera_index: int
    frame_width: int
    frame_height: int
    model_path: str


class VisionCamera:
    """Owns webcam and YOLO model lifecycle."""

    def __init__(self, config: CameraConfig) -> None:
        if YOLO is None:
            raise RuntimeError(
                "ultralytics is not installed. Install requirements before running Iris."
            ) from _YOLO_IMPORT_ERROR

        self.config = config
        # Lightweight default model keeps hackathon demo responsive in real time.
        self.model = YOLO(config.model_path)
        self.cap = cv2.VideoCapture(config.camera_index)

        if not self.cap.isOpened():
            raise RuntimeError(
                f"Could not open camera index {config.camera_index}. Check webcam connection."
            )

        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, float(config.frame_width))
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, float(config.frame_height))

    def read_frame(self):
        ok, frame = self.cap.read()
        if not ok or frame is None:
            raise RuntimeError("Failed to read frame from webcam.")
        return frame

    def detect(self, frame) -> list[Detection]:
        """Runs one detection pass and returns simplified, model-agnostic objects."""
        result = self.model(frame, verbose=False)[0]

        detections: list[Detection] = []
        names = result.names

        boxes = result.boxes
        if boxes is None:
            return detections

        for box in boxes:
            xyxy = box.xyxy[0].tolist()
            cls_id = int(box.cls[0])
            confidence = float(box.conf[0])

            label_name = names.get(cls_id, str(cls_id)) if isinstance(names, dict) else str(cls_id)
            detections.append(
                Detection(
                    label=label_name.lower(),
                    confidence=confidence,
                    bbox=BoundingBox(x1=xyxy[0], y1=xyxy[1], x2=xyxy[2], y2=xyxy[3]),
                )
            )

        return detections

    def read_and_detect(self) -> tuple[object, list[Detection]]:
        frame = self.read_frame()
        return frame, self.detect(frame)

    def close(self) -> None:
        if self.cap is not None:
            self.cap.release()



def detections_to_debug_strings(detections: Iterable[Detection], frame_width: int) -> list[str]:
    """Small helper for console-friendly detection logging."""
    lines: list[str] = []
    for det in detections:
        x_norm = det.normalized_center_x(frame_width)
        lines.append(
            f"{det.label:>12} conf={det.confidence:.2f} x={x_norm:.2f} "
            f"bbox=({det.bbox.x1:.0f},{det.bbox.y1:.0f},{det.bbox.x2:.0f},{det.bbox.y2:.0f})"
        )
    return lines
