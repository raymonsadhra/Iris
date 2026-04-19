"""Runtime configuration for Iris.

This file defines practical defaults for a hackathon demo and supports
environment-variable overrides for quick retuning without code edits.
"""

from __future__ import annotations

import os
from dataclasses import dataclass

from .constants import CLOSE_AREA_RATIO, PRIMARY_TARGET_LABELS, VERY_CLOSE_AREA_RATIO


@dataclass(slots=True)
class Settings:
    # Eye (camera)
    camera_index: int = 0
    frame_width: int = 960
    frame_height: int = 540

    # Brain (vision)
    yolo_model_path: str = "yolov8n.pt"
    confidence_threshold: float = 0.45
    target_labels: tuple[str, ...] = tuple(sorted(PRIMARY_TARGET_LABELS))

    # Brain -> Body bridge (serial)
    serial_port: str = "/dev/tty.usbmodem1101"
    baud_rate: int = 115200
    serial_timeout_sec: float = 0.1

    # UX / intelligence layer
    command_cooldown_sec: float = 1.25
    enable_closeness: bool = True
    close_area_ratio: float = 0.22
    very_close_area_ratio: float = 0.40
    start_in_scan_mode: bool = True

    # Debug / demo behavior
    enable_overlay: bool = True
    debug: bool = True



def _env_bool(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "y", "on"}



def _env_float(name: str, default: float) -> float:
    raw = os.getenv(name)
    if raw is None:
        return default
    try:
        return float(raw)
    except ValueError:
        return default



def _env_int(name: str, default: int) -> int:
    raw = os.getenv(name)
    if raw is None:
        return default
    try:
        return int(raw)
    except ValueError:
        return default



def get_settings() -> Settings:
    """Loads settings from defaults + optional environment overrides.

    Useful in a hackathon context where COM ports and thresholds can change often.
    """

    target_labels_raw = os.getenv("IRIS_TARGET_LABELS", "")
    target_labels: tuple[str, ...]
    if target_labels_raw.strip():
        target_labels = tuple(
            part.strip().lower() for part in target_labels_raw.split(",") if part.strip()
        )
    else:
        target_labels = tuple(sorted(PRIMARY_TARGET_LABELS))

    return Settings(
        camera_index=_env_int("IRIS_CAMERA_INDEX", 0),
        frame_width=_env_int("IRIS_FRAME_WIDTH", 960),
        frame_height=_env_int("IRIS_FRAME_HEIGHT", 540),
        yolo_model_path=os.getenv("IRIS_YOLO_MODEL", "yolov8n.pt"),
        confidence_threshold=_env_float("IRIS_CONFIDENCE", 0.45),
        target_labels=target_labels,
        serial_port=os.getenv("IRIS_SERIAL_PORT", "/dev/tty.usbmodem1101"),
        baud_rate=_env_int("IRIS_BAUD", 115200),
        serial_timeout_sec=_env_float("IRIS_SERIAL_TIMEOUT", 0.1),
        command_cooldown_sec=_env_float("IRIS_COOLDOWN_SEC", 1.25),
        enable_closeness=_env_bool("IRIS_ENABLE_CLOSENESS", True),
        close_area_ratio=_env_float("IRIS_CLOSE_AREA_RATIO", CLOSE_AREA_RATIO),
        very_close_area_ratio=_env_float("IRIS_VERY_CLOSE_AREA_RATIO", VERY_CLOSE_AREA_RATIO),
        start_in_scan_mode=_env_bool("IRIS_START_SCAN_MODE", True),
        enable_overlay=_env_bool("IRIS_ENABLE_OVERLAY", True),
        debug=_env_bool("IRIS_DEBUG", True),
    )
