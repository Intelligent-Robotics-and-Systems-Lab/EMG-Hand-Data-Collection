#include <Wire.h>
#include <Adafruit_PWMServoDriver.h>

Adafruit_PWMServoDriver pwm = Adafruit_PWMServoDriver();

// Servo channels on PCA9685 (0-15)
#define SERVO1_CHANNEL 0
#define SERVO2_CHANNEL 1
#define SERVO3_CHANNEL 2

// Pulse width range for typical servos
#define SERVO_MIN_PULSE 500   // in microseconds
#define SERVO_MAX_PULSE 2500  // in microseconds
#define SERVO_FREQ 50         // 50Hz for analog servos

float currentPos[3] = {180.0, 180.0, 180.0};

void setup() {
  Serial.begin(115200);
  delay(1000);

  pwm.begin();
  pwm.setPWMFreq(SERVO_FREQ); 
  Wire.setClock(400000); // Optional: speed up I2C

  // Set initial positions
  for (int i = 0; i < 3; i++) {
    setServoAngle(i, currentPos[i]);
  }

  Serial.println("Enter servo positions as [angle1, angle2, angle3]");
}

void loop() {
  if (Serial.available()) {
    String input = Serial.readStringUntil('\n');
    input.trim();

    // Example input: [90, 45, 135]
    if (parseAndSetPositions(input)) {
      Serial.println("Positions updated.");
    } else {
      Serial.println("Invalid input. Format: [90, 45, 135]");
    }
  }
}

// Parse string like "[90, 45, 135]" and update servo positions
bool parseAndSetPositions(String input) {
  input.replace("[", "");
  input.replace("]", "");

  float angles[3];
  int commaIndex1 = input.indexOf(',');
  int commaIndex2 = input.indexOf(',', commaIndex1 + 1);

  if (commaIndex1 == -1 || commaIndex2 == -1) {
    return false;
  }

  // Extract and convert each angle
  angles[0] = input.substring(0, commaIndex1).toFloat();
  angles[1] = input.substring(commaIndex1 + 1, commaIndex2).toFloat();
  angles[2] = input.substring(commaIndex2 + 1).toFloat();

  // Check bounds and apply
  for (int i = 0; i < 3; i++) {
    if (angles[i] < 0 || angles[i] > 180) {
      return false;
    }
    currentPos[i] = angles[i];
    setServoAngle(i, currentPos[i]);
  }

  return true;
}

// Map angle to PWM and send to PCA9685
void setServoAngle(int servoIndex, float angle) {
  uint16_t pulseLength = map(angle, 0, 180, SERVO_MIN_PULSE, SERVO_MAX_PULSE);
  uint16_t pwmVal = (uint16_t)((pulseLength / 1000000.0) * SERVO_FREQ * 4096);
  pwm.setPWM(servoIndex, 0, pwmVal);
}
