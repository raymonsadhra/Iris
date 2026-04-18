# Iris Hardware Notes

## Hardware Used
- Arduino Uno Q
- Logitech Webcam (connected to laptop)
- Moduline Vibro (haptic output)
- Moduline Buzzer (audio reinforcement, optional)
- Optional Moduline Button
- USB cable from laptop to Arduino (serial link)

## Wiring Assumptions (adjust as needed)
The firmware currently assumes:
- Vibro signal pin: `D5` (PWM-capable)
- Buzzer pin: `D8`
- Optional button pin: `D2` with `INPUT_PULLUP`

Ground and power must be shared correctly between Arduino and modules.

## Why The Laptop Owns Vision
- Webcam input is handled on the laptop where OpenCV + YOLO run.
- Arduino Uno Q does not perform CV inference.
- Arduino only parses command strings and executes output patterns.

## Serial Protocol
Python sends newline-terminated commands such as:
- `PERSON_LEFT`
- `CHAIR_CENTER`
- `OBSTACLE_RIGHT`
- `DANGER`
- `SILENT`

Arduino replies with simple status text:
- `IRIS_READY`
- `ACK <COMMAND>`
- `NACK UNKNOWN <COMMAND>`
- `BUTTON_PRESSED` (optional, if button enabled in firmware)

## Moduline Library Assumptions
Because Moduline-specific APIs vary by board/module revision, firmware uses standard Arduino primitives:
- `analogWrite` for vibro intensity
- `tone` / `noTone` for buzzer

If your Moduline modules require dedicated libraries:
1. Replace `setVibro()` internals.
2. Replace `beep()` internals.
3. Keep command parsing and pattern semantics unchanged.

## Demo Checklist
1. Upload firmware.
2. Confirm serial port in Python config.
3. Run serial test script and feel pattern differences.
4. Run camera test and verify person/chair detections.
5. Run full app and confirm semantic haptic loop.
