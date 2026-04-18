"""Main Iris orchestration loop.

End-to-end behavior:
1) Camera sees the world (Eye).
2) YOLO detects objects (Brain perception).
3) Interpreter chooses one semantic meaning (Brain decision).
4) Serial bridge sends a command to Arduino (Brain -> Body link).
5) Arduino drives vibro/buzzer (Body output).
6) User feels the environment through touch.

This file is optimized for hackathon demo reliability and debuggability.
"""

from __future__ import annotations

import argparse
import time

import cv2

from .camera import CameraConfig, VisionCamera, detections_to_debug_strings
from .config import Settings, get_settings
from .constants import SILENT_COMMAND, TEST_COMMAND
from .interpreter import DetectionInterpreter, InterpreterConfig
from .overlay import draw_overlay
from .serial_bridge import SerialBridge, SerialConfig


class IrisApp:
    def __init__(self, settings: Settings, dry_run_serial: bool = False, no_serial: bool = False) -> None:
        self.settings = settings

        self.camera = VisionCamera(
            CameraConfig(
                camera_index=settings.camera_index,
                frame_width=settings.frame_width,
                frame_height=settings.frame_height,
                model_path=settings.yolo_model_path,
            )
        )

        self.interpreter = DetectionInterpreter(
            InterpreterConfig(
                confidence_threshold=settings.confidence_threshold,
                target_labels=settings.target_labels,
                close_area_ratio=settings.close_area_ratio,
                very_close_area_ratio=settings.very_close_area_ratio,
                enable_closeness=settings.enable_closeness,
            )
        )

        self.bridge = SerialBridge(
            SerialConfig(
                port=settings.serial_port,
                baud_rate=settings.baud_rate,
                timeout_sec=settings.serial_timeout_sec,
            ),
            dry_run=(dry_run_serial or no_serial),
        )

        self.scan_mode_enabled = settings.start_in_scan_mode
        self.no_serial = no_serial
        self.last_sent_command: str | None = None
        self.last_sent_at = 0.0

    def run(self) -> None:
        if not self.no_serial:
            connected = self.bridge.connect()
            if not connected:
                print(
                    f"[WARN] Could not connect to serial port {self.settings.serial_port}. "
                    "Continuing without hardware output."
                )

        print("[INFO] Iris started. Press q to quit.")

        while True:
            frame, detections = self.camera.read_and_detect()
            h, w = frame.shape[:2]

            decision = self.interpreter.interpret(detections, frame_width=w, frame_height=h)

            if self.settings.debug and detections:
                for line in detections_to_debug_strings(detections, frame_width=w):
                    print("[DETECT]", line)
                print("[DECISION]", decision.command, "|", decision.reason)

            if self.scan_mode_enabled:
                self._maybe_send(decision.command)

            incoming = self.bridge.read_line()
            if incoming:
                self._handle_incoming_line(incoming)

            if self.settings.enable_overlay:
                view = draw_overlay(
                    frame=frame,
                    detections=detections,
                    decision=decision,
                    scan_mode_enabled=self.scan_mode_enabled,
                    last_sent=self.last_sent_command,
                )
                cv2.imshow("Iris Debug View", view)

            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):
                break
            if key == ord("s"):
                self.scan_mode_enabled = not self.scan_mode_enabled
                print(f"[INFO] Scan mode set to {self.scan_mode_enabled}")
                if not self.scan_mode_enabled:
                    self._force_send(SILENT_COMMAND)
            if key == ord("t"):
                self._force_send(TEST_COMMAND)
            if key == ord("x"):
                self._force_send(SILENT_COMMAND)

        self.shutdown()

    def _maybe_send(self, command: str) -> None:
        now = time.monotonic()
        if command == self.last_sent_command and (now - self.last_sent_at) < self.settings.command_cooldown_sec:
            return

        ok = self.bridge.send_command(command)
        if ok:
            self.last_sent_command = command
            self.last_sent_at = now
            print(f"[SERIAL] -> {command}")

    def _force_send(self, command: str) -> None:
        ok = self.bridge.send_command(command)
        if ok:
            self.last_sent_command = command
            self.last_sent_at = time.monotonic()
            print(f"[SERIAL] -> {command}")

    def _handle_incoming_line(self, line: str) -> None:
        # Optional button workflow: firmware can emit BUTTON_PRESSED.
        if line == "BUTTON_PRESSED":
            self.scan_mode_enabled = not self.scan_mode_enabled
            print(f"[INFO] Hardware button toggled scan mode to {self.scan_mode_enabled}")
        elif self.settings.debug:
            print(f"[ARDUINO] {line}")

    def shutdown(self) -> None:
        self._force_send(SILENT_COMMAND)
        self.camera.close()
        self.bridge.close()
        cv2.destroyAllWindows()
        print("[INFO] Iris shutdown complete.")



def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Iris semantic haptic navigation demo")
    parser.add_argument("--serial-port", type=str, default=None, help="Override serial port")
    parser.add_argument("--baud", type=int, default=None, help="Override baud rate")
    parser.add_argument("--camera-index", type=int, default=None, help="Override webcam index")
    parser.add_argument("--confidence", type=float, default=None, help="Override confidence threshold")
    parser.add_argument("--cooldown", type=float, default=None, help="Override command cooldown seconds")
    parser.add_argument("--model", type=str, default=None, help="YOLO model path")
    parser.add_argument("--dry-run-serial", action="store_true", help="Print commands instead of writing serial")
    parser.add_argument("--no-serial", action="store_true", help="Disable serial output entirely")
    parser.add_argument("--no-overlay", action="store_true", help="Disable debug overlay window")
    parser.add_argument("--quiet", action="store_true", help="Reduce debug console output")
    return parser.parse_args()



def apply_overrides(settings: Settings, args: argparse.Namespace) -> Settings:
    if args.serial_port is not None:
        settings.serial_port = args.serial_port
    if args.baud is not None:
        settings.baud_rate = args.baud
    if args.camera_index is not None:
        settings.camera_index = args.camera_index
    if args.confidence is not None:
        settings.confidence_threshold = args.confidence
    if args.cooldown is not None:
        settings.command_cooldown_sec = args.cooldown
    if args.model is not None:
        settings.yolo_model_path = args.model
    if args.no_overlay:
        settings.enable_overlay = False
    if args.quiet:
        settings.debug = False
    return settings



def main() -> None:
    args = parse_args()
    settings = apply_overrides(get_settings(), args)

    app = IrisApp(settings, dry_run_serial=args.dry_run_serial, no_serial=args.no_serial)
    try:
        app.run()
    except KeyboardInterrupt:
        app.shutdown()


if __name__ == "__main__":
    main()
