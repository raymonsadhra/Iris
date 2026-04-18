/*
  Iris Arduino Firmware (The Body)

  What this file does:
  - Receives semantic commands from the laptop over USB serial.
  - Converts commands like PERSON_LEFT or CHAIR_CENTER into vibration/buzzer patterns.

  Why it exists in Iris:
  - Iris turns computer vision into touch. The laptop is the "brain" and this Arduino
    firmware is the "body" that delivers physical feedback to the user.

  Hardware relation:
  - Arduino Uno Q connected over USB serial to laptop.
  - Moduline Vibro on VIBRO_PIN.
  - Moduline Buzzer on BUZZER_PIN (optional).
  - Optional button on BUTTON_PIN to trigger scan mode from hardware.

  Assumption note:
  - This implementation uses digitalWrite/analogWrite/tone as a clean baseline.
  - If your Moduline modules use dedicated libraries/APIs, replace setVibro(), beep(),
    and pin setup with module-specific calls.
*/

// -------------------- Hardware Configuration --------------------
const int VIBRO_PIN = 5;   // PWM-capable pin recommended
const int BUZZER_PIN = 8;
const int BUTTON_PIN = 2;  // Optional button (active LOW with INPUT_PULLUP)

const bool ENABLE_BUZZER = true;
const bool ENABLE_BUTTON = false;  // Set true when a hardware button is wired

const unsigned long BUTTON_DEBOUNCE_MS = 200;

String serialBuffer;
bool lastButtonState = HIGH;
unsigned long lastButtonToggleAt = 0;

// -------------------- Output Primitives --------------------
void setVibro(bool on, int intensity = 255) {
  // Baseline control for vibro motor. Replace if Moduline requires a library call.
  if (on) {
    analogWrite(VIBRO_PIN, intensity);
  } else {
    analogWrite(VIBRO_PIN, 0);
  }
}

void vibratePulse(int onMs, int offMs, int intensity = 255) {
  setVibro(true, intensity);
  delay(onMs);
  setVibro(false, 0);
  if (offMs > 0) {
    delay(offMs);
  }
}

void beep(int frequency = 1600, int durationMs = 80) {
  if (!ENABLE_BUZZER) {
    return;
  }
  tone(BUZZER_PIN, frequency, durationMs);
  delay(durationMs + 10);
  noTone(BUZZER_PIN);
}

void silenceAll() {
  setVibro(false);
  noTone(BUZZER_PIN);
}

// -------------------- Haptic Language --------------------
// Object mappings:
// - Person: double pulse
// - Chair: long steady pulse
// - Obstacle: rapid pulses
//
// Direction mappings:
// - Left: short lead-in burst
// - Center: stronger central emphasis
// - Right: two quick tail pulses

void directionLeftAccent() {
  vibratePulse(70, 60, 180);
}

void directionCenterAccent() {
  vibratePulse(160, 80, 255);
}

void directionRightAccent() {
  vibratePulse(45, 45, 200);
  vibratePulse(45, 50, 200);
}

void personPattern() {
  // Person -> double pulse
  vibratePulse(120, 90, 220);
  vibratePulse(120, 80, 220);
}

void chairPattern() {
  // Chair -> long steady pulse
  vibratePulse(340, 120, 210);
}

void obstaclePattern() {
  // Obstacle -> rapid pulse train
  vibratePulse(70, 55, 240);
  vibratePulse(70, 55, 240);
  vibratePulse(70, 80, 240);
}

void dangerPattern() {
  // Danger -> urgent repeating bursts + higher beep for reinforcement
  for (int i = 0; i < 3; i++) {
    vibratePulse(90, 40, 255);
    if (ENABLE_BUZZER) {
      beep(2300, 70);
    }
  }
}

void playSemanticPattern(const String& objectType, const String& direction) {
  // Direction cue first, then object cue, so the user feels where and what.
  if (direction == "LEFT") {
    directionLeftAccent();
  } else if (direction == "CENTER") {
    directionCenterAccent();
  } else if (direction == "RIGHT") {
    directionRightAccent();
  }

  if (objectType == "PERSON") {
    personPattern();
  } else if (objectType == "CHAIR") {
    chairPattern();
  } else if (objectType == "OBSTACLE") {
    obstaclePattern();
  }
}

// -------------------- Command Handling --------------------
void runTestPattern() {
  // Hardware bring-up sequence (Phase 1)
  directionLeftAccent();
  personPattern();
  delay(150);
  directionCenterAccent();
  chairPattern();
  delay(150);
  directionRightAccent();
  obstaclePattern();
  beep(1700, 120);
}

void executeCommand(const String& rawCommand) {
  String cmd = rawCommand;
  cmd.trim();
  cmd.toUpperCase();

  if (cmd.length() == 0) {
    return;
  }

  if (cmd == "TEST") {
    runTestPattern();
    Serial.println("ACK TEST");
    return;
  }

  if (cmd == "DANGER") {
    dangerPattern();
    Serial.println("ACK DANGER");
    return;
  }

  if (cmd == "SILENT") {
    silenceAll();
    Serial.println("ACK SILENT");
    return;
  }

  int underscoreIndex = cmd.indexOf('_');
  if (underscoreIndex <= 0) {
    Serial.print("NACK UNKNOWN ");
    Serial.println(cmd);
    return;
  }

  String objectType = cmd.substring(0, underscoreIndex);
  String direction = cmd.substring(underscoreIndex + 1);

  bool knownObject = (objectType == "PERSON" || objectType == "CHAIR" || objectType == "OBSTACLE");
  bool knownDirection = (direction == "LEFT" || direction == "CENTER" || direction == "RIGHT");

  if (knownObject && knownDirection) {
    playSemanticPattern(objectType, direction);
    Serial.print("ACK ");
    Serial.println(cmd);
  } else {
    Serial.print("NACK UNKNOWN ");
    Serial.println(cmd);
  }
}

void pollButtonAndReport() {
  if (!ENABLE_BUTTON) {
    return;
  }

  bool current = digitalRead(BUTTON_PIN);
  unsigned long now = millis();

  if (lastButtonState == HIGH && current == LOW && (now - lastButtonToggleAt) > BUTTON_DEBOUNCE_MS) {
    lastButtonToggleAt = now;
    Serial.println("BUTTON_PRESSED");
  }

  lastButtonState = current;
}

void setup() {
  pinMode(VIBRO_PIN, OUTPUT);
  pinMode(BUZZER_PIN, OUTPUT);

  if (ENABLE_BUTTON) {
    pinMode(BUTTON_PIN, INPUT_PULLUP);
  }

  silenceAll();

  Serial.begin(115200);
  while (!Serial) {
    ; // Wait for serial on boards that require it
  }

  Serial.println("IRIS_READY");
}

void loop() {
  pollButtonAndReport();

  while (Serial.available() > 0) {
    char c = (char)Serial.read();

    if (c == '\n' || c == '\r') {
      if (serialBuffer.length() > 0) {
        executeCommand(serialBuffer);
        serialBuffer = "";
      }
    } else {
      serialBuffer += c;
      if (serialBuffer.length() > 64) {
        serialBuffer = "";  // Avoid runaway malformed packets
      }
    }
  }
}
