#include <Wire.h>
#include <Adafruit_PWMServoDriver.h>

// Create an instance of the PCA9685 driver
Adafruit_PWMServoDriver pwm = Adafruit_PWMServoDriver();

// Servo channel assignments on PCA9685
const int servoChannel1 = 0; // Servo 1 on channel 0
const int servoChannel2 = 1; // Servo 2 on channel 1
const int servoChannel3 = 2; // Servo 3 on channel 2

// Servo motion control variables
float currentPos[3] = {180.0, 180.0, 90};
float targetPos[3] = {180.0, 180.0, 180.0};

unsigned long previousMillis = 0;
const int moveInterval = 10;
const int moveTime = 3000;
bool movingToPositions = false;

// Map angle to PWM value (0–180 degrees to pulse length)
int angleToPWM(float angle) {
  int minPulse = 150;  // Corresponds to 0 degrees
  int maxPulse = 600;  // Corresponds to 180 degrees
  return map(angle, 0, 180, minPulse, maxPulse);
}

// Predefined positions for 3 servos
float predefinedPositions[5][3] = {
  {130, 80, 110}, // Open Hand 
  {40, 77.0, 90}, // Cylinder 
  {30, 155.0, 70}, // Pinch
  {40, 62.4, 50},  // Ball
  {30, 41.6, 30},  // Cone 
};

void setup() {
  Serial.begin(115200);
  delay(1000);
  pwm.begin();
  pwm.setPWMFreq(50); // Set frequency to 50 Hz for servos

  // Set initial positions
  for (int i = 0; i < 3; i++) {
    pwm.setPWM(i, 0, angleToPWM(currentPos[i]));
  }

  Serial.println("ESP32 with PCA9685 ready. Waiting for input...");
}

void loop() {
  if (Serial.available() > 0) {
    String input = Serial.readStringUntil('\n');
    input.trim();

    int index = input.toInt();
    if (index >= 0 && index < 5) {
      for (int i = 0; i < 3; i++) {
        targetPos[i] = predefinedPositions[index][i];
      }

      bool changed = false;
      for (int i = 0; i < 3; i++) {
        if (targetPos[i] != currentPos[i]) {
          changed = true;
          break;
        }
      }

      if (changed) {
        Serial.print("Moving to preset ");
        Serial.println(index);
        moveServos();
      } else {
        Serial.println("Already at target position.");
      }
    } else {
      Serial.println("Invalid input. Enter a number between 0 and 4.");
    }
  }
}

void moveServos() {
  movingToPositions = true;
  unsigned long startTime = millis();

  while (millis() - startTime < moveTime) {
    float fraction = (float)(millis() - startTime) / moveTime;

    for (int i = 0; i < 3; i++) {
      float newPos = currentPos[i] + (targetPos[i] - currentPos[i]) * fraction;
      pwm.setPWM(i, 0, angleToPWM(newPos));
    }

    unsigned long currentMillis = millis();
    if (currentMillis - previousMillis >= moveInterval) {
      previousMillis = currentMillis;
      Serial.print("Moving to: ");
      for (int i = 0; i < 3; i++) {
        float interp = currentPos[i] + (targetPos[i] - currentPos[i]) * fraction;
        Serial.print(interp, 2);
        if (i < 2) Serial.print(" - ");
      }
      Serial.println();
    }

    delay(moveInterval);
  }

  for (int i = 0; i < 3; i++) {
    currentPos[i] = targetPos[i];
    pwm.setPWM(i, 0, angleToPWM(currentPos[i]));
  }

  Serial.print("Final position: ");
  for (int i = 0; i < 3; i++) {
    Serial.print(currentPos[i], 2);
    if (i < 2) Serial.print(" - ");
  }
  Serial.println();

  movingToPositions = false;
}

