#include <Wire.h>
#include <Adafruit_PWMServoDriver.h>

// Constants for PCA9685 and servos
#define SERVOMIN  125   // Minimum pulse length count (out of 4096)
#define SERVOMAX  575   // Maximum pulse length count (out of 4096)
#define PWM_FREQ  60    // PWM frequency for servos

// Servo definitions
Adafruit_PWMServoDriver pwm = Adafruit_PWMServoDriver();  // PCA9685 driver instance

// Servo channels on PCA9685
int servo1Channel = 0;
int servo2Channel = 1;
int thumbServoChannel = 2;

// Potentiometer pins
int potPin1 = A2;
int potPin2 = A3;
int thumbPotPin = A4;

// Control mode flags
bool potentiometerMode = false;
bool csvInputMode = false;

// Target positions
int targetPos1 = 180;
int targetPos2 = 180;
int targetThumbPos = 180;

// Current positions
int currentPos1 = 180;
int currentPos2 = 180;
int currentThumbPos = 180;

// Timing variables
unsigned long previousMillis = 0;
const long printInterval = 3000;   // Interval for printing positions (3 seconds)
const int moveInterval = 50;       // Interval for moving servos in CSV mode
const int moveTime = 3000;         // Time for servos to reach target positions (CSV mode) - set to 5 seconds

// Function prototypes
int angleToPulse(int angle);
void moveServos(int target1, int target2, int targetThumb);

void setup() {
  Serial.begin(115200);
  delay(1000);                     // Allow time for Serial Monitor
  pwm.begin();
  pwm.setPWMFreq(PWM_FREQ);

  Serial.println("Servo control with potentiometer and CSV input mode");
  potentiometerMode = true;       // Start in potentiometer mode by default
}

void loop() {
  if (Serial.available() > 0) {
    String input = Serial.readStringUntil('\n');
    input.trim();  // Remove whitespace or newline characters

    if (input == "potent") {
      potentiometerMode = true;
      csvInputMode = false;
      Serial.println("Potentiometer mode activated.");
    } else if (input == "CSV") {
      csvInputMode = true;
      potentiometerMode = false;
      Serial.println("CSV input mode activated. Enter num,num,num for positions.");
    } else if (csvInputMode && input.indexOf(',') != -1) {
      // Parse CSV input
      int commaIndex1 = input.indexOf(',');
      int commaIndex2 = input.indexOf(',', commaIndex1 + 1);

      targetPos1 = input.substring(0, commaIndex1).toInt();
      targetPos2 = input.substring(commaIndex1 + 1, commaIndex2).toInt();
      targetThumbPos = input.substring(commaIndex2 + 1).toInt();

      targetPos1 = constrain(targetPos1, 0, 160);
      targetPos2 = constrain(targetPos2, 20, 180);
      targetThumbPos = constrain(targetThumbPos, 0, 125);

      moveServos(targetPos1, targetPos2, targetThumbPos);
    }
  }

  if (potentiometerMode) {
    // Read potentiometer values
    int potValue1 = analogRead(potPin1);
    int potValue2 = analogRead(potPin2);
    int thumbPotValue = analogRead(thumbPotPin);

    currentPos1 = map(potValue1, 0, 4095, 0, 180);
    currentPos2 = map(potValue2, 0, 4095, 0, 180);
    currentThumbPos = map(thumbPotValue, 0, 4095, 0, 180);

    pwm.setPWM(servo1Channel, 0, angleToPulse(currentPos1));
    pwm.setPWM(servo2Channel, 0, angleToPulse(currentPos2));
    pwm.setPWM(thumbServoChannel, 0, angleToPulse(currentThumbPos));

    unsigned long currentMillis = millis();
    if (currentMillis - previousMillis >= printInterval) {
      previousMillis = currentMillis;
      Serial.print(currentPos1);
      Serial.print(",");
      Serial.print(currentPos2);
      Serial.print(",");
      Serial.println(currentThumbPos);
    }
  }
}

int angleToPulse(int angle) {
  return map(angle, 0, 180, SERVOMIN, SERVOMAX);
}

void moveServos(int target1, int target2, int targetThumb) {
  unsigned long startTime = millis();
  unsigned long lastPrintTime = startTime;

  while (millis() - startTime < moveTime) {
    unsigned long elapsedTime = millis() - startTime;
    float fraction = (float)elapsedTime / moveTime;

    int newPos1 = currentPos1 + (target1 - currentPos1) * fraction;
    int newPos2 = currentPos2 + (target2 - currentPos2) * fraction;
    int newThumbPos = currentThumbPos + (targetThumb - currentThumbPos) * fraction;

    pwm.setPWM(servo1Channel, 0, angleToPulse(newPos1));
    pwm.setPWM(servo2Channel, 0, angleToPulse(newPos2));
    pwm.setPWM(thumbServoChannel, 0, angleToPulse(newThumbPos));

    // Print positions every 50 ms
    if (millis() - lastPrintTime >= 50) {
      Serial.print(newPos1);
      Serial.print(",");
      Serial.print(newPos2);
      Serial.print(",");
      Serial.println(newThumbPos);
      lastPrintTime = millis();
    }

    delay(moveInterval);
  }

  currentPos1 = target1;
  currentPos2 = target2;
  currentThumbPos = targetThumb;
  pwm.setPWM(servo1Channel, 0, angleToPulse(currentPos1));
  pwm.setPWM(servo2Channel, 0, angleToPulse(currentPos2));
  pwm.setPWM(thumbServoChannel, 0, angleToPulse(currentThumbPos));

  Serial.print(currentPos1);
  Serial.print(",");
  Serial.print(currentPos2);
  Serial.print(",");
  Serial.println(currentThumbPos);
}
