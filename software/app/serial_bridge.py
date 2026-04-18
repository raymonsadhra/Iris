"""Serial communication bridge between Iris brain (Python) and body (Arduino).

What this file does:
- Handles pyserial connection lifecycle.
- Sends semantic command strings safely with newline framing.
- Reads optional incoming lines (e.g., button events from firmware).

Why it exists in Iris:
- This is the critical bridge that turns AI interpretation into physical feedback.
"""

from __future__ import annotations

import time
from dataclasses import dataclass

try:
    import serial
    from serial import SerialException
except ImportError as exc:  # pragma: no cover - import-time guard
    serial = None
    SerialException = Exception
    _SERIAL_IMPORT_ERROR = exc
else:
    _SERIAL_IMPORT_ERROR = None


@dataclass(slots=True)
class SerialConfig:
    port: str
    baud_rate: int
    timeout_sec: float


class SerialBridge:
    def __init__(self, config: SerialConfig, dry_run: bool = False) -> None:
        self.config = config
        self.dry_run = dry_run
        self.conn = None

    def connect(self) -> bool:
        if self.dry_run:
            return True

        if serial is None:
            raise RuntimeError(
                "pyserial is not installed. Install requirements before using serial bridge."
            ) from _SERIAL_IMPORT_ERROR

        if self.conn and self.conn.is_open:
            return True

        try:
            self.conn = serial.Serial(
                port=self.config.port,
                baudrate=self.config.baud_rate,
                timeout=self.config.timeout_sec,
            )
            # Give Arduino time to auto-reset and print ready line.
            time.sleep(1.5)
            return True
        except (SerialException, OSError):
            self.conn = None
            return False

    @property
    def is_connected(self) -> bool:
        return self.dry_run or (self.conn is not None and self.conn.is_open)

    def send_command(self, command: str) -> bool:
        if self.dry_run:
            print(f"[DRY-RUN SERIAL] {command}")
            return True

        if not self.is_connected and not self.connect():
            return False

        assert self.conn is not None

        try:
            payload = (command.strip() + "\n").encode("utf-8")
            self.conn.write(payload)
            self.conn.flush()
            return True
        except (SerialException, OSError):
            self.close()
            return False

    def read_line(self) -> str | None:
        """Reads one text line if available. Useful for optional button events."""
        if self.dry_run or not self.is_connected:
            return None

        assert self.conn is not None

        try:
            raw = self.conn.readline()
            if not raw:
                return None
            return raw.decode("utf-8", errors="replace").strip()
        except (SerialException, OSError, UnicodeDecodeError):
            return None

    def close(self) -> None:
        if self.conn is not None:
            try:
                self.conn.close()
            except Exception:
                pass
            self.conn = None
