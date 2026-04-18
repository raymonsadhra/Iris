"""Phase 2 helper: webcam + YOLO bring-up test.

This script confirms the Eye + vision stack works before serial integration.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

import cv2

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.camera import CameraConfig, VisionCamera, detections_to_debug_strings


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Iris camera + YOLO test")
    parser.add_argument("--camera-index", type=int, default=0)
    parser.add_argument("--model", type=str, default="yolov8n.pt")
    parser.add_argument("--confidence", type=float, default=0.35)
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    cam = VisionCamera(
        CameraConfig(
            camera_index=args.camera_index,
            frame_width=960,
            frame_height=540,
            model_path=args.model,
        )
    )

    print("[INFO] Camera test started. Press q to quit.")

    try:
        while True:
            frame, detections = cam.read_and_detect()
            h, w = frame.shape[:2]

            filtered = [d for d in detections if d.confidence >= args.confidence]
            for line in detections_to_debug_strings(filtered, frame_width=w):
                print("[DETECT]", line)

            for det in filtered:
                x1, y1 = int(det.bbox.x1), int(det.bbox.y1)
                x2, y2 = int(det.bbox.x2), int(det.bbox.y2)
                cv2.rectangle(frame, (x1, y1), (x2, y2), (80, 220, 120), 2)
                cv2.putText(
                    frame,
                    f"{det.label} {det.confidence:.2f}",
                    (x1, max(20, y1 - 10)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.55,
                    (80, 220, 120),
                    2,
                )

            cv2.imshow("Iris Camera Test", frame)
            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):
                break
    finally:
        cam.close()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
