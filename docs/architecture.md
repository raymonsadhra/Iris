# Iris Architecture Summary

## Mission
Iris is a wearable assistive prototype that translates camera vision into semantic haptic feedback, so users can feel meaning like "person ahead" or "chair right" instead of raw distance numbers.

## System Split
1. **The Eye (Webcam on laptop)**
- Captures real-world frames.
- Feeds image data into YOLO.

2. **The Brain (Python app on laptop)**
- Detects objects with YOLO (`camera.py`).
- Converts detections into one clear semantic command (`interpreter.py`).
- Sends command strings over serial (`serial_bridge.py`).
- Coordinates timing, cooldown, and demo controls (`main.py`).

3. **The Body (Arduino Uno Q + Moduline outputs)**
- Receives commands via USB serial.
- Runs haptic/buzzer patterns (`iris_arduino.ino`).
- Outputs tactile meaning for the wearer.

## Command Flow
1. Webcam frame arrives.
2. YOLO returns many detections.
3. Interpreter filters by confidence and target classes.
4. Interpreter chooses one best candidate using priority + confidence + optional closeness bonus.
5. Python emits command (example: `PERSON_LEFT`, `CHAIR_CENTER`, `DANGER`, `SILENT`).
6. Arduino parses command and performs matching vibro/buzzer pattern.

## Haptic Language (Core UX)
- **Object meaning**
- Person: double pulse
- Chair: long pulse
- Obstacle: rapid pulse

- **Direction meaning**
- Left: short lead accent
- Center: strong accent
- Right: quick twin accent

This keeps feedback compact and interpretable under real-time movement.

## Development Phases Supported
1. **Phase 1: Hardware Output Bring-Up**
- Upload `firmware/iris_arduino/iris_arduino.ino`.
- Send `TEST`, `PERSON_LEFT`, `DANGER`, etc.

2. **Phase 2: Vision Bring-Up**
- Run `software/scripts/test_camera.py`.
- Verify detections and labels on webcam feed.

3. **Phase 3: Bridge Bring-Up**
- Run `software/scripts/test_serial.py`.
- Verify Arduino receives and acknowledges commands.

4. **Phase 4: Full Integration**
- Run `python -m app.main` from `software/`.
- Confirm end-to-end detection -> command -> haptic output.

5. **Phase 5: UX/Intelligence Layer**
- Cooldown prevents command spam.
- Priority system reduces noisy feedback.
- Optional closeness can trigger `DANGER`.
- Optional scan mode toggle through keyboard (`s`) and firmware button event (`BUTTON_PRESSED`).

## Reliability Choices for Hackathon
- Defaults to lightweight `yolov8n.pt` for real-time performance.
- Graceful handling when serial hardware is unavailable.
- Modular files so camera, interpreter, and serial can be tested independently.
- Constants/config centralized for fast tuning during demos.
