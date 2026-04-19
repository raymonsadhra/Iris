"""Constants and tweakable mappings for Iris semantic haptics.

This module centralizes labels, priorities, thresholds, and command names so the
team can tune behavior quickly during the hackathon without rewriting logic.
"""

from __future__ import annotations

SILENT_COMMAND = "SILENT"
DANGER_COMMAND = "DANGER"
TEST_COMMAND = "TEST"

PERSON = "PERSON"
CHAIR = "CHAIR"
OBSTACLE = "OBSTACLE"

LEFT = "LEFT"
CENTER = "CENTER"
RIGHT = "RIGHT"

POSITION_ORDER = (LEFT, CENTER, RIGHT)
OBJECT_ORDER = (PERSON, CHAIR, OBSTACLE)

POSITION_LEFT_MAX = 0.35
POSITION_CENTER_MAX = 0.65

CONFIDENCE_SCORE_SCALE = 20.0
CLOSE_BONUS_SCORE = 5.0
VERY_CLOSE_BONUS_SCORE = 12.0

# Priority drives which object "wins" when multiple detections appear.
# Higher value = more likely to become the final haptic message.
OBJECT_PRIORITY = {
    PERSON: 100,
    CHAIR: 75,
    OBSTACLE: 60,
}

# COCO labels considered meaningful for Iris demo behavior.
# person/chair are primary; the rest can map to obstacle-like warnings.
OBSTACLE_FALLBACK_LABELS = {
    "bench",
    "backpack",
    "handbag",
    "suitcase",
    "bottle",
    "cup",
    "potted plant",
    "tv",
    "laptop",
    "traffic light",
    "fire hydrant",
}

PRIMARY_TARGET_LABELS = {"person", "chair"}

DEFAULT_TARGET_LABELS = PRIMARY_TARGET_LABELS | OBSTACLE_FALLBACK_LABELS

# A rough closeness estimate from bounding box area ratio.
CLOSE_AREA_RATIO = 0.22
VERY_CLOSE_AREA_RATIO = 0.40

COMMANDS = {
    TEST_COMMAND,
    DANGER_COMMAND,
    SILENT_COMMAND,
    "PERSON_LEFT",
    "PERSON_CENTER",
    "PERSON_RIGHT",
    "CHAIR_LEFT",
    "CHAIR_CENTER",
    "CHAIR_RIGHT",
    "OBSTACLE_LEFT",
    "OBSTACLE_CENTER",
    "OBSTACLE_RIGHT",
}


def compose_directional_command(object_kind: str, direction: str) -> str:
    """Returns commands like PERSON_LEFT, CHAIR_CENTER, OBSTACLE_RIGHT."""
    return f"{object_kind}_{direction}"
