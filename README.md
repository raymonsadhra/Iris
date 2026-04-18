# Iris — A Wearable System That Translates Vision Into Touch Using AI

Iris is a hackathon-ready assistive prototype that turns webcam scene understanding into tactile feedback.

Instead of distance numbers, Iris communicates semantic meaning such as:
- person ahead
- chair on the right
- obstacle in center

## Concept: Eye, Brain, Body
- **Eye**: Logitech webcam captures the environment.
- **Brain**: Python + OpenCV + YOLO detect and interpret the scene.
- **Body**: Arduino Uno Q receives serial commands and drives Moduline Vibro/Buzzer.

This architecture keeps heavy AI work on the laptop and makes Arduino output behavior reliable and simple.

## Repository Structure
```text
Iris/
  firmware/
    iris_arduino/
      iris_arduino.ino
  software/
    app/
      __init__.py
      __main__.py
      main.py
      config.py
      constants.py
      models.py
      camera.py
      interpreter.py
      serial_bridge.py
      overlay.py
    scripts/
      test_serial.py
      test_camera.py
      test_interpreter.py
    requirements.txt
  docs/
    architecture.md
    hardware_notes.md
  README.md
```

## Development Phases
### Phase 1: Hardware Output Bring-Up
- Upload `firmware/iris_arduino/iris_arduino.ino` to Arduino Uno Q.
- Use serial test script to send:
  - `TEST`
  - `PERSON_LEFT`
  - `CHAIR_CENTER`
  - `DANGER`

### Phase 2: Vision Bring-Up
- Run camera-only detection script.
- Confirm webcam feed, YOLO labels, and boxes.

### Phase 3: Bridge Bring-Up
- Run serial-only test script.
- Confirm Arduino reacts to known commands.

### Phase 4: Full Semantic Haptic Integration
- Run full app orchestrator.
- Verify loop: detect -> interpret -> send command -> feel output.

### Phase 5: Intelligence / UX Layer
Implemented in current code:
- command cooldown to prevent spam
- object priority system
- confidence thresholding
- optional closeness-based `DANGER`
- scan mode toggle via keyboard (`s`) and optional hardware button event

## Hardware Setup
1. Connect webcam to laptop.
2. Connect Arduino Uno Q to laptop via USB.
3. Connect Moduline Vibro to configured pin (`D5` by default).
4. Connect Moduline Buzzer to configured pin (`D8` by default).
5. Optional: connect button to `D2` and set `ENABLE_BUTTON=true` in firmware.

More detail: `docs/hardware_notes.md`.

## Software Setup
From repo root:

```bash
cd software
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run Commands
### Camera test (Phase 2)
```bash
cd software
python scripts/test_camera.py --camera-index 0 --model yolov8n.pt
```

### Serial test (Phase 3)
```bash
cd software
python scripts/test_serial.py --port /dev/tty.usbmodem1101 --baud 115200
```

### Interpreter test (logic only)
```bash
cd software
python scripts/test_interpreter.py
```

### Full semantic app (Phase 4/5)
```bash
cd software
python -m app.main --serial-port /dev/tty.usbmodem1101
```

Useful flags:
- `--dry-run-serial` prints commands without writing serial.
- `--no-serial` disables serial output (vision-only demo).
- `--no-overlay` hides debug window.
- `--confidence 0.4` adjusts threshold.
- `--cooldown 1.2` adjusts repeat suppression.

## Configuration and Tuning
Core defaults live in `software/app/config.py` and `software/app/constants.py`.

Tuning examples:
- change YOLO model: `IRIS_YOLO_MODEL=yolov8n.pt`
- change port: `IRIS_SERIAL_PORT=/dev/tty.usbmodem1101`
- change classes: `IRIS_TARGET_LABELS=person,chair,bottle`
- change threshold: `IRIS_CONFIDENCE=0.4`

The interpreter is designed so you can quickly adjust priorities and fallback object labels for your environment.

## Haptic Language
### Object meanings
- Person: double pulse
- Chair: long steady pulse
- Obstacle: rapid pulses

### Direction meanings
- Left: short lead accent
- Center: strong accent
- Right: quick twin accent

Commands are emitted by Python (`PERSON_LEFT`, `CHAIR_RIGHT`, `DANGER`) and executed by Arduino patterns.

## Moduline Assumptions
Firmware currently uses standard Arduino APIs (`analogWrite`, `tone`) as practical defaults.

If your Moduline modules require dedicated libraries, update only the low-level actuator functions in firmware while keeping the command protocol unchanged.

## Demo Flow (Target)
1. Webcam sees person/chair.
2. YOLO detects object.
3. Interpreter determines left/center/right and semantic priority.
4. Python sends command over USB serial.
5. Arduino runs matching haptic pattern.
6. User interprets surroundings via touch.
