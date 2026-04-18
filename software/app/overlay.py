"""OpenCV visualization helpers for Iris debug/demo mode.

The overlay is for developers and judges, not the end-user's haptic channel.
It shows what the "brain" saw and what command it decided to send.
"""

from __future__ import annotations

import cv2

from .models import Detection, SemanticDecision


CLASS_COLORS = {
    "person": (90, 200, 90),
    "chair": (230, 190, 80),
}


def _color_for_label(label: str) -> tuple[int, int, int]:
    return CLASS_COLORS.get(label, (120, 180, 255))


def draw_overlay(
    frame,
    detections: list[Detection],
    decision: SemanticDecision,
    scan_mode_enabled: bool,
    last_sent: str | None,
) -> object:
    out = frame.copy()

    for det in detections:
        x1, y1 = int(det.bbox.x1), int(det.bbox.y1)
        x2, y2 = int(det.bbox.x2), int(det.bbox.y2)
        color = _color_for_label(det.label)

        cv2.rectangle(out, (x1, y1), (x2, y2), color, 2)
        text = f"{det.label} {det.confidence:.2f}"
        cv2.putText(out, text, (x1, max(18, y1 - 8)), cv2.FONT_HERSHEY_SIMPLEX, 0.55, color, 2)

    status_lines = [
        f"Decision: {decision.command}",
        f"Reason: {decision.reason}",
        f"Scan mode: {'ON' if scan_mode_enabled else 'OFF'}",
        f"Last sent: {last_sent or '-'}",
        "Controls: [q]=quit [s]=scan toggle [t]=TEST [x]=SILENT",
    ]

    y = 24
    for line in status_lines:
        cv2.putText(out, line, (12, y), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 2)
        cv2.putText(out, line, (12, y), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (30, 30, 30), 1)
        y += 22

    return out
