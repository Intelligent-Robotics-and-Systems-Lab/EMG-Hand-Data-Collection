#include <Wire.h>
#include <Adafruit_PWMServoDriver.h>

// Create the PWM driver instance
Adafruit_PWMServoDriver pwm = Adafruit_PWMServoDriver();

// Servo channels on PCA9685 (0-15)
#define SERVO1_CHANNEL 0
#define SERVO2_CHANNEL 1
#define SERVO3_CHANNEL 2

// Constants for pulse widths
#define SERVO_MIN_PULSE 500   // in microseconds
#define SERVO_MAX_PULSE 2500  // in microseconds
#define SERVO_FREQ 50         // Analog servos run at ~50 Hz

float currentPos[3] = {180.0, 180.0, 180.0};
float targetPos[3]  = {180.0, 180.0, 180.0};

unsigned long previousMillis = 0;
const int moveInterval = 10;
const int moveTime = 3000;
bool movingToPositions = false;

// Array: {servo1, servo2, servo3}
float predefinedPositions[5][3] = {
  {125, 40, 110}, // Open Hand 
  {50, 130, 50},   // Cylinder 
  {35, 40, 45}, // Pinch
  {60, 110, 60},   // Ball
  {40, 110, 55},   // Cone 
};

void setup() {
  Serial.begin(115200);
  delay(1000);

  pwm.begin();
  pwm.setPWMFreq(SERVO_FREQ); // Analog servos at ~50 Hz
  Wire.setClock(400000);      // Optional: faster I2C

  // Set initial positions
  for (int i = 0; i < 3; i++) {
    setServoAngle(i, currentPos[i]);
  }
}

void loop() {
  if (Serial.available() > 0) {
    String input = Serial.readStringUntil('\n');
    input.trim();
    Serial.println(input);

    int positionIndex = input.toInt();

    if (positionIndex >= 0 && positionIndex <= 4) {
      for (int i = 0; i < 3; i++) {
        targetPos[i] = predefinedPositions[positionIndex][i];
      }
      moveServos(targetPos);
    }
  }
}

void moveServos(float target[3]) {
  movingToPositions = true;
  unsigned long startTime = millis();

  while (millis() - startTime < moveTime) {
    unsigned long elapsedTime = millis() - startTime;
    float fraction = (float)elapsedTime / moveTime;
    
    for (int i = 0; i < 3; i++) {
      float newPos = currentPos[i] + (target[i] - currentPos[i]) * fraction;
      setServoAngle(i, newPos);
    }

    unsigned long currentMillis = millis();
    if (currentMillis - previousMillis >= moveInterval) {
      previousMillis = currentMillis;
      // Optional debug:
      // Serial.printf("Pos: %.2f, %.2f, %.2f\n", newPos1, newPos2, newPos3);
    }

    delay(moveInterval);
  }

  for (int i = 0; i < 3; i++) {
    currentPos[i] = target[i];
    setServoAngle(i, currentPos[i]);
  }

  movingToPositions = false;
}

// Helper to map angle to pulse width and send to PWM
void setServoAngle(int servoIndex, float angle) {
  uint16_t pulseLength = map(angle, 0, 180, SERVO_MIN_PULSE, SERVO_MAX_PULSE);
  uint16_t pwmVal = (uint16_t)((pulseLength / 1000000.0) * SERVO_FREQ * 4096);
  pwm.setPWM(servoIndex, 0, pwmVal);
}
