"""Phase 4 helper: validate detection->command interpretation logic without camera.

Useful when iterating haptic language and priority rules quickly.
"""

from __future__ import annotations

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.interpreter import DetectionInterpreter, InterpreterConfig
from app.models import BoundingBox, Detection


def main() -> None:
    interpreter = DetectionInterpreter(
        InterpreterConfig(
            confidence_threshold=0.35,
            target_labels=("person", "chair", "bottle"),
            close_area_ratio=0.18,
            very_close_area_ratio=0.32,
            enable_closeness=True,
        )
    )

    frame_width = 960
    frame_height = 540

    samples = [
        Detection(
            label="chair",
            confidence=0.88,
            bbox=BoundingBox(x1=600, y1=180, x2=860, y2=520),
        ),
        Detection(
            label="person",
            confidence=0.71,
            bbox=BoundingBox(x1=40, y1=120, x2=360, y2=530),
        ),
        Detection(
            label="bottle",
            confidence=0.66,
            bbox=BoundingBox(x1=450, y1=250, x2=550, y2=500),
        ),
    ]

    decision = interpreter.interpret(samples, frame_width=frame_width, frame_height=frame_height)
    print("Decision:", decision.command)
    print("Reason:  ", decision.reason)
    print("Label:   ", decision.label)
    print("Pos:     ", decision.position)
    print("Conf:    ", decision.confidence)
    print("Area:    ", decision.area_ratio)


if __name__ == "__main__":
    main()
