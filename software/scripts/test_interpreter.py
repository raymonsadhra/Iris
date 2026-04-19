"""Phase 4 helper: validate detection->command interpretation logic without camera.

Useful when iterating haptic language and priority rules quickly.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.interpreter import DetectionInterpreter, InterpreterConfig
from app.models import BoundingBox, Detection


@dataclass(frozen=True)
class Scenario:
    name: str
    detections: list[Detection]
    expected_command: str


def main() -> None:
    interpreter = DetectionInterpreter(
        InterpreterConfig(
            confidence_threshold=0.45,
            target_labels=("person", "chair", "bottle"),
            close_area_ratio=0.22,
            very_close_area_ratio=0.40,
            enable_closeness=True,
        )
    )

    frame_width = 960
    frame_height = 540

    scenarios = [
        Scenario(
            name="person priority beats chair",
            expected_command="PERSON_LEFT",
            detections=[
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
            ],
        ),
        Scenario(
            name="very close person triggers danger",
            expected_command="DANGER",
            detections=[
                Detection(
                    label="person",
                    confidence=0.92,
                    bbox=BoundingBox(x1=80, y1=40, x2=760, y2=520),
                )
            ],
        ),
        Scenario(
            name="obstacle fallback works",
            expected_command="OBSTACLE_RIGHT",
            detections=[
                Detection(
                    label="bottle",
                    confidence=0.73,
                    bbox=BoundingBox(x1=720, y1=170, x2=860, y2=480),
                )
            ],
        ),
        Scenario(
            name="low confidence detections are ignored",
            expected_command="SILENT",
            detections=[
                Detection(
                    label="person",
                    confidence=0.31,
                    bbox=BoundingBox(x1=150, y1=90, x2=380, y2=430),
                )
            ],
        ),
        Scenario(
            name="unsupported labels are ignored",
            expected_command="SILENT",
            detections=[
                Detection(
                    label="dog",
                    confidence=0.99,
                    bbox=BoundingBox(x1=120, y1=110, x2=510, y2=430),
                )
            ],
        ),
    ]

    failures = 0

    for scenario in scenarios:
        decision = interpreter.interpret(
            scenario.detections,
            frame_width=frame_width,
            frame_height=frame_height,
        )
        ok = decision.command == scenario.expected_command
        status = "PASS" if ok else "FAIL"
        print(f"[{status}] {scenario.name}")
        print(f"  expected: {scenario.expected_command}")
        print(f"  actual:   {decision.command}")
        print(f"  reason:   {decision.reason}")
        if decision.label is not None:
            print(f"  label:    {decision.label}")
        if decision.position is not None:
            print(f"  position: {decision.position}")
        if decision.confidence is not None:
            print(f"  conf:     {decision.confidence:.2f}")
        if decision.area_ratio is not None:
            print(f"  area:     {decision.area_ratio:.3f}")
        print()

        if not ok:
            failures += 1

    if failures:
        raise SystemExit(f"{failures} interpreter scenario(s) failed")


if __name__ == "__main__":
    main()
