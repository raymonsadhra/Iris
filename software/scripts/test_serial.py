"""Phase 3 helper: send known Iris commands to Arduino over serial.

Use this to verify the Brain->Body bridge before enabling camera logic.
"""

from __future__ import annotations

import argparse
import time
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.constants import COMMANDS
from app.serial_bridge import SerialBridge, SerialConfig


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Iris serial command tester")
    parser.add_argument("--port", required=True, help="Serial port (e.g., /dev/tty.usbmodem1101)")
    parser.add_argument("--baud", type=int, default=115200)
    parser.add_argument("--delay", type=float, default=1.0, help="Delay between commands")
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    bridge = SerialBridge(
        SerialConfig(port=args.port, baud_rate=args.baud, timeout_sec=0.2),
        dry_run=args.dry_run,
    )

    if not bridge.connect():
        print(f"[ERROR] Could not connect to {args.port}")
        return

    ordered = [
        "TEST",
        "PERSON_LEFT",
        "PERSON_CENTER",
        "PERSON_RIGHT",
        "CHAIR_LEFT",
        "CHAIR_CENTER",
        "CHAIR_RIGHT",
        "OBSTACLE_LEFT",
        "OBSTACLE_CENTER",
        "OBSTACLE_RIGHT",
        "DANGER",
        "SILENT",
    ]

    for cmd in ordered:
        if cmd not in COMMANDS:
            print(f"[WARN] Unknown command in test list: {cmd}")
            continue
        ok = bridge.send_command(cmd)
        print(f"[SEND] {cmd} ({'ok' if ok else 'failed'})")
        time.sleep(args.delay)

    bridge.close()


if __name__ == "__main__":
    main()
